"""
PDF Document Parser extracting structured records from text tables or key-value cards.
Uses pypdf for clean, safe text extraction without external binaries.
"""
import io
import re
from typing import Any, Dict, List


class PDFParser:
    """Extracts record dictionaries from structured PDF documents."""

    def parse(self, file_path_or_bytes: Any, filename: str = "document.pdf") -> List[Dict[str, Any]]:
        import pypdf

        if isinstance(file_path_or_bytes, bytes):
            reader = pypdf.PdfReader(io.BytesIO(file_path_or_bytes))
        else:
            reader = pypdf.PdfReader(file_path_or_bytes)

        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

        if not full_text.strip():
            return []

        return self._extract_records_from_text(full_text, filename)

    def _extract_records_from_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Strategy 1: Check for Key: Value block patterns (e.g., Record 1 \n Name: Arun \n Email: ...)
        card_records: List[Dict[str, Any]] = []
        current_record: Dict[str, Any] = {}

        kv_pattern = re.compile(r'^([A-Za-z0-9_\s]{2,25})\s*[:=\-]\s*(.+)$')

        for idx, line in enumerate(lines, start=1):
            # Check for record separator delimiter like "---", "Record #", "===", etc.
            if re.match(r'^(?:[-=_*]{3,}|record\s*#?\d+|student\s*#?\d+|employee\s*#?\d+)', line, re.IGNORECASE):
                if current_record:
                    current_record["__source_file__"] = filename
                    current_record["__file_type__"] = "PDF"
                    current_record["__line_number__"] = idx
                    card_records.append(current_record)
                    current_record = {}
                continue

            m = kv_pattern.match(line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                # If key repeats in current record, it indicates start of a new record
                if k.lower() in [k_exist.lower() for k_exist in current_record.keys()]:
                    if current_record:
                        current_record["__source_file__"] = filename
                        current_record["__file_type__"] = "PDF"
                        current_record["__line_number__"] = idx
                        card_records.append(current_record)
                        current_record = {}
                current_record[k] = v

        if current_record:
            current_record["__source_file__"] = filename
            current_record["__file_type__"] = "PDF"
            current_record["__line_number__"] = len(lines)
            card_records.append(current_record)

        if card_records:
            return card_records

        # Strategy 2: Tabular or comma/pipe separated lines inside PDF
        for line_num, line in enumerate(lines, start=1):
            parts = re.split(r'[,|\t]', line)
            if len(parts) >= 2:
                row_dict = {f"field_{i+1}": p.strip() for i, p in enumerate(parts) if p.strip()}
                if row_dict:
                    row_dict["__source_file__"] = filename
                    row_dict["__file_type__"] = "PDF"
                    row_dict["__line_number__"] = line_num
                    records.append(row_dict)

        return records
