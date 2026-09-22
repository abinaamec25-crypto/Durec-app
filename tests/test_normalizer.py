"""
Tests for FieldMapper and RecordNormalizer.
"""
from normalizer.field_mapper import FieldMapper
from normalizer.record_normalizer import RecordNormalizer


def test_field_mapper():
    """FieldMapper unifies heterogeneous schema headers to canonical names."""
    mapper = FieldMapper()
    assert mapper.get_canonical_field("student_name") == "name"
    assert mapper.get_canonical_field("full_name") == "name"
    assert mapper.get_canonical_field("employee_name") == "name"
    assert mapper.get_canonical_field("customer_name") == "name"
    assert mapper.get_canonical_field("mail_id") == "email"
    assert mapper.get_canonical_field("email_address") == "email"
    assert mapper.get_canonical_field("contact_no") == "phone"
    assert mapper.get_canonical_field("mobile") == "phone"
    assert mapper.get_canonical_field("dept") == "department"
    assert mapper.get_canonical_field("roll_no") == "id_code"


def test_record_normalizer_value_cleaning():
    """RecordNormalizer cleans strings, phones, emails, and numbers."""
    norm = RecordNormalizer()
    assert norm.normalize_string("  Arun   Kumar  ") == "arun kumar"
    assert norm.normalize_name("Mr. Arun Kumar,") == "arun kumar"
    assert norm.normalize_email("  Arun@Gmail.COM  ") == "arun@gmail.com"
    assert norm.normalize_phone("+91-98765-43210") == "9876543210"
    assert norm.normalize_phone("09876543210") == "9876543210"
    assert norm.normalize_number("20.0") == "20"


def test_order_independent_hash_key():
    """Primary hash key must be identical regardless of dictionary key insertion order."""
    norm = RecordNormalizer()
    rec1 = {"email": "arun@gmail.com", "name": "Arun", "phone": "9876543210"}
    rec2 = {"phone": "9876543210", "name": "arun", "email": "arun@gmail.com"}

    canon1, _ = norm.normalize_record(rec1)
    canon2, _ = norm.normalize_record(rec2)

    key1 = norm.generate_primary_hash_key(canon1)
    key2 = norm.generate_primary_hash_key(canon2)

    assert key1 == key2
    assert "email:arun@gmail.com" in key1
    assert "name:arun" in key1
    assert "phone:9876543210" in key1
