"""
Tests for DuplicateDetector across heterogeneous schemas and multiple tiers.
"""
from hashing.duplicate_detector import DuplicateDetector
from models.record import DuplicateType


def test_exact_duplicate_detection():
    """Exact duplicate detection via Primary Hash Table."""
    detector = DuplicateDetector(algorithm="polynomial", initial_capacity=53)
    raw_data = [
        {"name": "Arun Kumar", "email": "arun@gmail.com", "phone": "9876543210"},
        {"name": "Priya Sharma", "email": "priya@gmail.com", "phone": "9841023456"},
        {"name": "ARUN KUMAR", "email": "arun@gmail.com", "phone": "9876543210"},  # Duplicate of record 1
    ]

    summary = detector.process_records(raw_data)
    assert summary["total_records"] == 3
    assert summary["unique_records"] == 2
    assert summary["duplicate_records"] == 1
    assert summary["exact_duplicates"] == 1

    group = detector.duplicate_groups[0]
    assert group.primary_record.id == 1
    assert group.duplicates[0].id == 3
    assert group.duplicate_type == DuplicateType.EXACT


def test_heterogeneous_schema_partial_duplicate():
    """
    Validates user requirement 3:
    Record A: name, age, email
    Record B: full_name, email, phone
    Should match as duplicate on shared canonical email/name.
    """
    detector = DuplicateDetector(algorithm="polynomial", initial_capacity=53)
    raw_data = [
        {"name": "Arun", "age": 20, "email": "arun@gmail.com"},
        {"full_name": "Arun", "email": "arun@gmail.com", "phone": "9876543210"},
    ]

    summary = detector.process_records(raw_data)
    assert summary["total_records"] == 2
    assert summary["unique_records"] == 1
    assert summary["duplicate_records"] == 1
    assert summary["partial_duplicates"] == 1

    group = detector.duplicate_groups[0]
    assert group.duplicate_type == DuplicateType.PARTIAL
    assert "email" in group.matched_fields


def test_multi_file_heterogeneous_workflow():
    """Tests multi-file simulation with mixed formats."""
    detector = DuplicateDetector(algorithm="polynomial", initial_capacity=101)
    raw_data = [
        {"__source_file__": "students.csv", "__file_type__": "CSV", "student_name": "Arun Kumar", "email_id": "arun@gmail.com"},
        {"__source_file__": "employees.tsv", "__file_type__": "TSV", "full_name": "Arun Kumar", "mail": "arun@gmail.com"},
        {"__source_file__": "customers.json", "__file_type__": "JSON", "customer_name": "Vijay", "email": "vijay@gmail.com"},
    ]

    summary = detector.process_records(raw_data)
    assert summary["total_records"] == 3
    assert summary["duplicate_records"] == 1
    assert summary["unique_records"] == 2
