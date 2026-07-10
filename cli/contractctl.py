"""contractctl - a tiny CLI for managing data contracts.

Usage:
    python cli/contractctl.py list
    python cli/contractctl.py show example_customer_v1
    python cli/contractctl.py diff example_customer_v1 example_customer_v2
    python cli/contractctl.py validate-sample example_customer_v1 sample.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402

from app.contract_validator import CONTRACTS_DIR, load_contract, validate_record  # noqa: E402


def cmd_list(_args):
    for fname in sorted(os.listdir(CONTRACTS_DIR)):
        if fname.endswith(".yaml"):
            print(fname[: -len(".yaml")])


def cmd_show(args):
    contract = load_contract(args.name)
    print(yaml.safe_dump(contract, sort_keys=False))


def cmd_diff(args):
    a = load_contract(args.name_a)
    b = load_contract(args.name_b)
    a_props = set(a["schema"].get("properties", {}))
    b_props = set(b["schema"].get("properties", {}))
    print(f"Added fields:   {sorted(b_props - a_props)}")
    print(f"Removed fields: {sorted(a_props - b_props)}")
    a_req = set(a["schema"].get("required", []))
    b_req = set(b["schema"].get("required", []))
    print(f"Newly required: {sorted(b_req - a_req)}")


def cmd_validate_sample(args):
    with open(args.sample_path) as f:
        record = json.load(f)
    violations = validate_record(args.name, record)
    if not violations:
        print("OK: record matches contract")
    else:
        print(f"FAILED: {len(violations)} violation(s)")
        for v in violations:
            print(f"  - {v.path}: {v.message}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)

    p_show = sub.add_parser("show")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_show)

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("name_a")
    p_diff.add_argument("name_b")
    p_diff.set_defaults(func=cmd_diff)

    p_validate = sub.add_parser("validate-sample")
    p_validate.add_argument("name")
    p_validate.add_argument("sample_path")
    p_validate.set_defaults(func=cmd_validate_sample)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
