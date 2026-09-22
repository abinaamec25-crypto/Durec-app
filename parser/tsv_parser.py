"""
TSV Record Parser for tab-separated data files.
"""
import csv
import io
from typing import Any, Dict, List


class TSVParser:
    """Parses tab-separated values into a list of record dictionaries."""

    def parse(self, file_path_or_bytes: Any, filename: str = "file.tsv") -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        if isinstance(file_path_or_bytes, bytes):
            content_str = self._decode_bytes(file_path_or_bytes)
            f = io.StringIO(content_str)
        else:
            with open(file_path_or_bytes, "rb") as bf:
                content_str = self._decode_bytes(bf.read())
            f = io.StringIO(content_str)

        reader = csv.DictReader(f, delimiter="\t")
        for line_num, row in enumerate(reader, start=2):
            if not row:
                continue
            cleaned = {
                (k.strip() if k else f"col_{i}"): (v.strip() if v else "")
                for i, (k, v) in enumerate(row.items())
                if k is not None
            }
            if any(v != "" for v in cleaned.values()):
                cleaned["__source_file__"] = filename
                cleaned["__file_type__"] = "TSV"
                cleaned["__line_number__"] = line_num
                records.append(cleaned)

        return records

    @staticmethod
    def _decode_bytes(b: bytes) -> str:
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return b.decode(enc)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", errors="replace")
