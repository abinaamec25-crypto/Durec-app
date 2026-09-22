"""
Parser package for multi-format record extraction.
Supports CSV, TSV, Excel (.xlsx, .xls), JSON, JSONL, PDF, DOCX, TXT.
"""
from .parser_manager import ParserManager
from .csv_parser import CSVParser
from .tsv_parser import TSVParser
from .json_parser import JSONParser
from .excel_parser import ExcelParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .text_parser import TextParser

__all__ = [
    "ParserManager",
    "CSVParser",
    "TSVParser",
    "JSONParser",
    "ExcelParser",
    "PDFParser",
    "DOCXParser",
    "TextParser",
]
