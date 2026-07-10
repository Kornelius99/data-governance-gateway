"""Data contract loading and validation.

A 'contract' is a YAML file in CONTRACTS_DIR (default: ./contracts) named
<contract_name>.yaml, containing a top-level 'schema' key holding a
standard JSON Schema. See contracts/example_customer_v1.yaml.
"""
import os
from functools import lru_cache
from typing import Any, Dict, List

import jsonschema
import yaml

from app.models import ContractViolation

CONTRACTS_DIR = os.environ.get("CONTRACTS_DIR", "contracts")


class ContractNotFoundError(Exception):
    pass


@lru_cache(maxsize=64)
def load_contract(contract_name: str) -> Dict[str, Any]:
    path = os.path.join(CONTRACTS_DIR, f"{contract_name}.yaml")
    if not os.path.exists(path):
        raise ContractNotFoundError(f"No contract file found at {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def validate_record(contract_name: str, record: Dict[str, Any]) -> List[ContractViolation]:
    contract = load_contract(contract_name)
    schema = contract["schema"]

    validator = jsonschema.Draft202012Validator(schema)
    violations = []
    for error in validator.iter_errors(record):
        path = ".".join(str(p) for p in error.path) or "<root>"
        violations.append(ContractViolation(path=path, message=error.message))
    return violations
