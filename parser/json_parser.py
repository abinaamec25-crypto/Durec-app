"""
JSON Record Parser supporting JSON arrays, root objects, and nested list keys.
"""
import json
from typing import Any, Dict, List


class JSONParser:
    """Parses JSON data (array of objects or dictionary containing a records list)."""

    def parse(self, file_path_or_bytes: Any, filename: str = "file.json") -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        if isinstance(file_path_or_bytes, bytes):
            data_str = self._decode_bytes(file_path_or_bytes)
        else:
            with open(file_path_or_bytes, "rb") as f:
                data_str = self._decode_bytes(f.read())

        parsed = json.loads(data_str)

        # Case 1: Root is a list of records
        if isinstance(parsed, list):
            items = parsed
        # Case 2: Root is a dict containing a known list key like 'data', 'records', 'items', 'students'
        elif isinstance(parsed, dict):
            found_list = None
            for key in ("records", "data", "items", "rows", "students", "employees", "customers", "results"):
                if key in parsed and isinstance(parsed[key], list):
                    found_list = parsed[key]
                    break
            items = found_list if found_list is not None else [parsed]
        else:
            items = []

        for idx, item in enumerate(items, start=1):
            if isinstance(item, dict):
                cleaned = {str(k).strip(): v for k, v in item.items() if k is not None}
                cleaned["__source_file__"] = filename
                cleaned["__file_type__"] = "JSON"
                cleaned["__line_number__"] = idx
                records.append(cleaned)

        return records

    @staticmethod
    def _decode_bytes(b: bytes) -> str:
        for enc in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return b.decode(enc)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", errors="replace")
