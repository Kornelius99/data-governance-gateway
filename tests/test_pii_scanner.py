from app.pii_scanner import redact_record, scan_record


def test_scan_record_detects_email():
    record = {"contact": {"email": "jane.doe@example.com"}}
    findings = scan_record(record)
    entity_types = {f.entity_type for f in findings}
    assert "EMAIL_ADDRESS" in entity_types


def test_scan_record_ignores_non_string_fields():
    record = {"age": 34, "active": True, "score": 4.5}
    findings = scan_record(record)
    assert findings == []


def test_redact_record_masks_flagged_field():
    record = {"contact": {"email": "jane.doe@example.com"}, "name": "Jane"}
    findings = scan_record(record)
    redacted = redact_record(record, findings)
    assert redacted["contact"]["email"] != record["contact"]["email"]
    assert redacted["contact"]["email"].startswith("[REDACTED:")


def test_redact_record_does_not_mutate_original():
    record = {"contact": {"email": "jane.doe@example.com"}}
    findings = scan_record(record)
    redact_record(record, findings)
    assert record["contact"]["email"] == "jane.doe@example.com"
