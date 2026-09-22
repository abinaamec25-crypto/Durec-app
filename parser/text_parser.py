"""
Plain Text (.txt) Record Parser.
Supports delimiter-separated records (comma, tab, pipe) and Key: Value record cards.
"""
import io
import re
from typing import Any, Dict, List


class TextParser:
    """Parses plain text files into record dictionaries."""

    def parse(self, file_path_or_bytes: Any, filename: str = "data.txt") -> List[Dict[str, Any]]:
        if isinstance(file_path_or_bytes, bytes):
            text = self._decode_bytes(file_path_or_bytes)
        else:
            with open(file_path_or_bytes, "rb") as f:
                text = self._decode_bytes(f.read())

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        # Strategy 1: Check for Key: Value format
        card_records: List[Dict[str, Any]] = []
        current: Dict[str, Any] = {}
        kv_pattern = re.compile(r'^([A-Za-z0-9_\s]{2,25})\s*[:=\-]\s*(.+)$')

        for idx, line in enumerate(lines, start=1):
            if re.match(r'^(?:[-=_*]{3,}|record\s*#?\d+|student\s*#?\d+|employee\s*#?\d+)', line, re.IGNORECASE):
                if current:
                    current["__source_file__"] = filename
                    current["__file_type__"] = "TXT"
                    current["__line_number__"] = idx
                    card_records.append(current)
                    current = {}
                continue

            m = kv_pattern.match(line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                if k.lower() in [k_exist.lower() for k_exist in current.keys()]:
                    current["__source_file__"] = filename
                    current["__file_type__"] = "TXT"
                    current["__line_number__"] = idx
                    card_records.append(current)
                    current = {}
                current[k] = v

        if current:
            current["__source_file__"] = filename
            current["__file_type__"] = "TXT"
            current["__line_number__"] = len(lines)
            card_records.append(current)

        if card_records:
            return card_records

        # Strategy 2: Delimited lines (comma, pipe, tab)
        header_line = lines[0]
        delimiter = None
        for d in [",", "|", "\t", ";"]:
            if d in header_line:
                delimiter = d
                break

        if delimiter:
            headers = [h.strip() for h in header_line.split(delimiter)]
            records: List[Dict[str, Any]] = []
            for idx, line in enumerate(lines[1:], start=2):
                parts = [p.strip() for p in line.split(delimiter)]
                if not any(parts):
                    continue
                item: Dict[str, Any] = {}
                for col_idx, val in enumerate(parts):
                    key = headers[col_idx] if col_idx < len(headers) else f"col_{col_idx}"
                    item[key] = val
                item["__source_file__"] = filename
                item["__file_type__"] = "TXT"
                item["__line_number__"] = idx
                records.append(item)
            return records

        return []

    @staticmethod
    def _decode_bytes(b: bytes) -> str:
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return b.decode(enc)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", errors="replace")
