"""
JSON Lines (JSONL / NDJSON) Record Parser.
Processes files where each line is an independent JSON object.
"""
import io
import json
from typing import Any, Dict, List


class JSONLParser:
    """Parses newline-delimited JSON into a list of record dictionaries."""

    def parse(self, file_path_or_bytes: Any, filename: str = "file.jsonl") -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        if isinstance(file_path_or_bytes, bytes):
            stream = io.StringIO(self._decode_bytes(file_path_or_bytes))
        else:
            with open(file_path_or_bytes, "rb") as f:
                stream = io.StringIO(self._decode_bytes(f.read()))

        for line_num, line in enumerate(stream, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                obj = json.loads(line_str)
                if isinstance(obj, dict):
                    cleaned = {str(k).strip(): v for k, v in obj.items() if k is not None}
                    cleaned["__source_file__"] = filename
                    cleaned["__file_type__"] = "JSONL"
                    cleaned["__line_number__"] = line_num
                    records.append(cleaned)
            except json.JSONDecodeError:
                continue

        return records

    @staticmethod
    def _decode_bytes(b: bytes) -> str:
        for enc in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return b.decode(enc)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", errors="replace")
