from app.contract_validator import validate_record


def test_valid_record_has_no_violations():
    record = {"name": "Jane Doe", "email": "jane@example.com", "age": 34}
    violations = validate_record("example_customer_v1", record)
    assert violations == []


def test_missing_required_field_is_flagged():
    record = {"name": "Jane Doe", "email": "jane@example.com"}
    violations = validate_record("example_customer_v1", record)
    assert len(violations) == 1
    assert "age" in violations[0].message


def test_wrong_type_is_flagged():
    record = {"name": "Jane Doe", "email": "jane@example.com", "age": "thirty-four"}
    violations = validate_record("example_customer_v1", record)
    assert len(violations) == 1
    assert violations[0].path == "age"


def test_out_of_range_age_is_flagged():
    record = {"name": "Jane Doe", "email": "jane@example.com", "age": 200}
    violations = validate_record("example_customer_v1", record)
    assert len(violations) == 1
