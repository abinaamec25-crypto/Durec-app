"""
Parser Manager for format detection, delegation, and multi-file processing.
Anna University R2025 Data Structures Academic Project.
"""
import os
from typing import Any, Dict, List, Optional, Tuple
from .csv_parser import CSVParser
from .tsv_parser import TSVParser
from .json_parser import JSONParser
from .jsonl_parser import JSONLParser
from .excel_parser import ExcelParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .text_parser import TextParser


class ParserManager:
    """
    Coordinates and delegates file parsing across all supported structured
    and document data formats.
    """

    SUPPORTED_EXTENSIONS = {
        ".csv": ("CSV", CSVParser),
        ".tsv": ("TSV", TSVParser),
        ".json": ("JSON", JSONParser),
        ".jsonl": ("JSONL", JSONLParser),
        ".ndjson": ("JSONL", JSONLParser),
        ".xlsx": ("Excel (.xlsx)", ExcelParser),
        ".xls": ("Excel (.xls)", ExcelParser),
        ".pdf": ("PDF Document", PDFParser),
        ".docx": ("Word Document", DOCXParser),
        ".txt": ("Plain Text", TextParser),
    }

    def __init__(self):
        self.parsers: Dict[str, Any] = {
            "csv": CSVParser(),
            "tsv": TSVParser(),
            "json": JSONParser(),
            "jsonl": JSONLParser(),
            "excel": ExcelParser(),
            "pdf": PDFParser(),
            "docx": DOCXParser(),
            "text": TextParser(),
        }

    def detect_format(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        Determines format type and parser key from file extension.
        Returns: (format_display_name, parser_key) or None if unsupported.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext in (".csv",):
            return "CSV", "csv"
        elif ext in (".tsv",):
            return "TSV", "tsv"
        elif ext in (".json",):
            return "JSON", "json"
        elif ext in (".jsonl", ".ndjson"):
            return "JSONL", "jsonl"
        elif ext in (".xlsx", ".xls"):
            return "Excel", "excel"
        elif ext in (".pdf",):
            return "PDF", "pdf"
        elif ext in (".docx",):
            return "Word (.docx)", "docx"
        elif ext in (".txt",):
            return "Plain Text", "text"
        return None

    def parse_file(self, file_path_or_bytes: Any, filename: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Parses a single file using the appropriate parser.
        Returns (records_list, error_message).
        """
        detected = self.detect_format(filename)
        if not detected:
            ext = os.path.splitext(filename)[1]
            return [], f"Unsupported file extension '{ext}'. Supported: CSV, TSV, XLSX, XLS, JSON, JSONL, PDF, DOCX, TXT."

        _, parser_key = detected
        parser = self.parsers[parser_key]

        try:
            records = parser.parse(file_path_or_bytes, filename=filename)
            if not records:
                return [], f"No records could be extracted from '{filename}'. The file may be empty or unformatted."
            return records, None
        except Exception as e:
            return [], f"Error parsing '{filename}': {str(e)}"

    def parse_multiple_files(self, files: List[Tuple[Any, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parses a batch of files (heterogeneous formats allowed).
        Returns:
            (all_records, file_processing_reports)
        """
        all_records: List[Dict[str, Any]] = []
        reports: List[Dict[str, Any]] = []

        for file_content, filename in files:
            records, error = self.parse_file(file_content, filename)
            report = {
                "filename": filename,
                "record_count": len(records),
                "status": "success" if not error else "error",
                "error": error,
            }
            if not error:
                all_records.extend(records)
            reports.append(report)

        return all_records, reports
