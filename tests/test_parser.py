"""
Tests for ParserManager and individual format parsers.
"""
from parser.parser_manager import ParserManager
from parser.csv_parser import CSVParser
from parser.tsv_parser import TSVParser
from parser.json_parser import JSONParser
from parser.jsonl_parser import JSONLParser


def test_parser_manager_detection():
    """ParserManager detects supported extensions correctly."""
    pm = ParserManager()
    assert pm.detect_format("data.csv")[0] == "CSV"
    assert pm.detect_format("records.json")[0] == "JSON"
    assert pm.detect_format("students.xlsx")[0] == "Excel"
    assert pm.detect_format("report.pdf")[0] == "PDF"
    assert pm.detect_format("notes.docx")[0] == "Word (.docx)"
    assert pm.detect_format("items.txt")[0] == "Plain Text"
    assert pm.detect_format("unknown.xyz") is None


def test_csv_parser():
    """CSV parser extracts rows into dictionaries."""
    csv_bytes = b"name,email\nArun,arun@gmail.com\nPriya,priya@gmail.com\n"
    parser = CSVParser()
    records = parser.parse(csv_bytes, "test.csv")
    assert len(records) == 2
    assert records[0]["name"] == "Arun"
    assert records[1]["email"] == "priya@gmail.com"


def test_tsv_parser():
    """TSV parser handles tab-separated lines."""
    tsv_bytes = b"roll\tname\n101\tArun\n102\tPriya\n"
    parser = TSVParser()
    records = parser.parse(tsv_bytes, "test.tsv")
    assert len(records) == 2
    assert records[0]["name"] == "Arun"


def test_json_parser():
    """JSON parser supports JSON arrays and root objects."""
    json_bytes = b'[{"name": "Arun", "age": 20}, {"name": "Priya", "age": 21}]'
    parser = JSONParser()
    records = parser.parse(json_bytes, "test.json")
    assert len(records) == 2
    assert records[0]["name"] == "Arun"


def test_jsonl_parser():
    """JSONL parser parses newline-delimited JSON."""
    jsonl_bytes = b'{"name": "Arun"}\n{"name": "Priya"}\n'
    parser = JSONLParser()
    records = parser.parse(jsonl_bytes, "test.jsonl")
    assert len(records) == 2
    assert records[0]["name"] == "Arun"
