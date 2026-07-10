"""PII detection using Microsoft Presidio.

Presidio ships its own NLP-based recognizers (emails, phone numbers, credit
cards, person names, etc.). We flatten the incoming JSON record to
field-path -> string-value pairs, run Presidio's AnalyzerEngine over each
value, and report findings above a minimum confidence score.
"""
from typing import Any, Dict, List, Tuple

from presidio_analyzer import AnalyzerEngine

from app.models import PiiFinding

_analyzer = AnalyzerEngine()

MIN_SCORE = 0.4


def _flatten(record: Dict[str, Any], prefix: str = "") -> List[Tuple[str, str]]:
    """Turn a nested dict into a list of (field_path, string_value) pairs,
    skipping non-string leaves (numbers/bools/None aren't scanned for PII).
    """
    pairs: List[Tuple[str, str]] = []
    for key, value in record.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            pairs.extend(_flatten(value, path))
        elif isinstance(value, str):
            pairs.append((path, value))
    return pairs


def scan_record(record: Dict[str, Any]) -> List[PiiFinding]:
    findings: List[PiiFinding] = []
    for field_path, value in _flatten(record):
        results = _analyzer.analyze(text=value, language="en")
        for r in results:
            if r.score >= MIN_SCORE:
                findings.append(
                    PiiFinding(field=field_path, entity_type=r.entity_type, score=round(r.score, 3))
                )
    return findings


def redact_record(record: Dict[str, Any], findings: List[PiiFinding]) -> Dict[str, Any]:
    """Return a deep-copied record with flagged fields replaced by a
    '[REDACTED:<ENTITY_TYPE>]' placeholder.
    """
    import copy

    redacted = copy.deepcopy(record)
    findings_by_field = {f.field: f.entity_type for f in findings}

    def _walk(node: Dict[str, Any], prefix: str = "") -> None:
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                _walk(value, path)
            elif path in findings_by_field:
                node[key] = f"[REDACTED:{findings_by_field[path]}]"

    _walk(redacted)
    return redacted
