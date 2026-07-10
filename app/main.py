"""FastAPI application exposing the /validate gateway endpoint.

Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
(the docker-compose service / Dockerfile do this automatically).
"""
import logging

from fastapi import FastAPI, HTTPException

from app.contract_validator import ContractNotFoundError, validate_record
from app.models import ValidateRequest, ValidateResponse, Verdict
from app.pii_scanner import redact_record, scan_record

app = FastAPI(
    title="data-governance-gateway",
    description="PII detection + data contract enforcement for data pipelines",
    version="0.1.0",
)

logger = logging.getLogger("data_governance_gateway")
logger.setLevel(logging.INFO)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest):
    try:
        contract_violations = validate_record(req.contract, req.record)
    except ContractNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    pii_findings = scan_record(req.record)

    if contract_violations:
        verdict = Verdict.BLOCK
        output_record = None
    elif pii_findings and req.redact:
        verdict = Verdict.REDACT
        output_record = redact_record(req.record, pii_findings)
    elif pii_findings:
        verdict = Verdict.BLOCK
        output_record = None
    else:
        verdict = Verdict.ALLOW
        output_record = req.record

    logger.info(
        "validate contract=%s verdict=%s pii=%d contract_violations=%d",
        req.contract,
        verdict.value,
        len(pii_findings),
        len(contract_violations),
    )

    return ValidateResponse(
        verdict=verdict,
        pii_findings=pii_findings,
        contract_violations=contract_violations,
        record=output_record,
    )
