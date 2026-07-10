"""Pydantic request/response models for the gateway API."""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ValidateRequest(BaseModel):
    contract: str
    record: Dict[str, Any]
    redact: bool = True


class Verdict(str, Enum):
    ALLOW = "allow"
    REDACT = "redact"
    BLOCK = "block"


class PiiFinding(BaseModel):
    field: str
    entity_type: str
    score: float


class ContractViolation(BaseModel):
    path: str
    message: str


class ValidateResponse(BaseModel):
    verdict: Verdict
    pii_findings: List[PiiFinding]
    contract_violations: List[ContractViolation]
    record: Optional[Dict[str, Any]] = None  # redacted or original record, per verdict
