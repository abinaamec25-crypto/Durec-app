"""
Tests for Custom Hash Functions and HashTable with Separate Chaining.
"""
import pytest
from hashing.hash_functions import polynomial_rolling_hash, djb2_hash, fnv1a_hash, HashFunctionEngine
from hashing.hash_table import HashTable
from models.record import Record


def test_hash_functions_deterministic():
    """Hash functions must return deterministic, non-zero results for identical inputs."""
    key = "name:arun kumar|dept:cse"
    h1 = polynomial_rolling_hash(key)
    h2 = polynomial_rolling_hash(key)
    assert h1 == h2
    assert h1 > 0

    d1 = djb2_hash(key)
    d2 = djb2_hash(key)
    assert d1 == d2
    assert d1 > 0

    f1 = fnv1a_hash(key)
    f2 = fnv1a_hash(key)
    assert f1 == f2
    assert f1 > 0


def test_hash_function_engine_trace():
    """HashFunctionEngine must produce trace steps for viva demonstration."""
    raw_hash, bucket, steps = HashFunctionEngine.compute_hash("arun", "polynomial", 101)
    assert 0 <= bucket < 101
    assert len(steps) == 4  # 4 characters in 'arun'
    assert steps[0]["char"] == "a"


def test_hash_table_insert_and_search():
    """Hash table insertion and searching should retrieve the correct record."""
    table = HashTable(initial_capacity=53, algorithm="polynomial")
    r1 = Record(id=1, source_file="test.csv", file_type="CSV", raw_data={"name": "Arun"})
    
    existing, trace = table.insert("name:arun", r1)
    assert existing is None
    assert table.num_elements == 1
    assert trace.comparisons_made == 0

    found = table.search("name:arun")
    assert found is not None
    assert found.id == 1

    not_found = table.search("name:unknown")
    assert not_found is None


def test_hash_table_duplicate_detection_via_chaining():
    """Inserting identical key should return existing record (duplicate detection)."""
    table = HashTable(initial_capacity=53, algorithm="polynomial")
    r1 = Record(id=1, source_file="f1.csv", file_type="CSV", raw_data={"name": "Arun"})
    r2 = Record(id=2, source_file="f2.json", file_type="JSON", raw_data={"name": "Arun"})

    table.insert("name:arun", r1)
    existing, trace = table.insert("name:arun", r2)

    assert existing is not None
    assert existing.id == 1
    assert trace.comparisons_made >= 1


def test_hash_table_collision_tracking():
    """When two distinct keys map to the same bucket, separate chaining handles collision."""
    table = HashTable(initial_capacity=7, algorithm="polynomial", auto_rehash=False)
    # Insert multiple items into a small table to force bucket collisions
    for i in range(15):
        rec = Record(id=i, source_file="data.csv", file_type="CSV", raw_data={"val": i})
        table.insert(f"key_{i}", rec)

    assert table.num_elements == 15
    assert table.total_collisions > 0
    stats = table.get_statistics()
    assert stats["max_chain_length"] > 1
    assert stats["occupied_buckets"] > 0
