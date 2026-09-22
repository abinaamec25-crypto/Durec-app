"""
Analysis Service orchestrating multi-format file ingestion, parsing,
normalization, and hashing-based duplicate detection.
"""
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple
from config import UPLOAD_FOLDER, ZIP_EXPORT_PATH, BASE_DIR
from hashing.duplicate_detector import DuplicateDetector
from parser.parser_manager import ParserManager
from utils.file_utils import sanitize_filename, validate_file_size, package_project_zip


class AnalysisService:
    """
    Stateful service managing uploaded files, executing duplicate analysis,
    and exposing records, duplicate groups, and hash table buckets.
    """

    def __init__(self):
        self.parser_manager = ParserManager()
        self.detector = DuplicateDetector()
        self.uploaded_files: List[Dict[str, Any]] = []
        self.raw_records: List[Dict[str, Any]] = []
        self.analysis_performed: bool = False
        self.last_summary: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Clears all session data and cleans upload folder."""
        self.uploaded_files.clear()
        self.raw_records.clear()
        self.analysis_performed = False
        self.last_summary = None
        self.detector = DuplicateDetector()

        # Clean uploads folder
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass

    def add_uploaded_file(self, filename: str, content: bytes) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Saves uploaded file and validates format and size."""
        valid_size, size_err = validate_file_size(content)
        if not valid_size:
            return False, size_err, None

        clean_name = sanitize_filename(filename)
        detected = self.parser_manager.detect_format(clean_name)
        if not detected:
            ext = os.path.splitext(clean_name)[1]
            return False, f"Unsupported file format '{ext}'.", None

        format_name, _ = detected
        saved_path = os.path.join(UPLOAD_FOLDER, clean_name)
        with open(saved_path, "wb") as f:
            f.write(content)

        file_meta = {
            "id": len(self.uploaded_files) + 1,
            "filename": clean_name,
            "path": saved_path,
            "format": format_name,
            "size_bytes": len(content),
            "size_kb": round(len(content) / 1024, 1),
        }
        self.uploaded_files.append(file_meta)
        return True, None, file_meta

    def remove_uploaded_file(self, filename: str) -> bool:
        """Removes a file from the current upload list."""
        for i, f_meta in enumerate(self.uploaded_files):
            if f_meta["filename"] == filename:
                path = f_meta["path"]
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                self.uploaded_files.pop(i)
                return True
        return False

    def run_analysis(self, algorithm: str = "polynomial", initial_capacity: int = 101) -> Dict[str, Any]:
        """
        Executes end-to-end duplicate detection pipeline across all uploaded files.
        """
        if not self.uploaded_files:
            return {"error": "No files uploaded. Please upload at least one dataset."}

        # Step 1: Parse all files
        files_to_parse: List[Tuple[str, str]] = [
            (f_meta["path"], f_meta["filename"]) for f_meta in self.uploaded_files
        ]
        all_records, reports = self.parser_manager.parse_multiple_files(files_to_parse)
        self.raw_records = all_records

        if not all_records:
            return {
                "error": "No valid records could be extracted from the uploaded files.",
                "file_reports": reports,
            }

        # Step 2: Initialize Duplicate Detector with requested hash settings
        self.detector = DuplicateDetector(
            algorithm=algorithm,
            initial_capacity=initial_capacity,
        )

        # Step 3: Run pipeline
        summary = self.detector.process_records(all_records)
        summary["file_reports"] = reports
        summary["total_files_analyzed"] = len(self.uploaded_files)
        self.analysis_performed = True
        self.last_summary = summary
        return summary

    def get_duplicate_groups(self) -> List[Dict[str, Any]]:
        """Returns structured duplicate groups with primary and duplicate records."""
        return [g.to_dict() for g in self.detector.duplicate_groups]

    def get_records(
        self,
        record_type: str = "all",
        page: int = 1,
        per_page: int = 25,
        search_query: str = "",
    ) -> Dict[str, Any]:
        """Returns filtered and paginated records for UI table inspection."""
        records = self.detector.processed_records

        if record_type == "duplicate":
            records = self.detector.duplicate_records
        elif record_type == "unique":
            records = self.detector.unique_records

        # Apply text search if provided
        if search_query:
            q = search_query.lower()
            records = [
                r for r in records
                if any(q in str(v).lower() for v in r.raw_data.values())
                or (r.primary_hash_key and q in r.primary_hash_key.lower())
            ]

        total_count = len(records)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_records = records[start_idx:end_idx]

        return {
            "records": [r.to_dict() for r in page_records],
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 1,
        }

    def get_hash_table_state(self, max_buckets: int = 50) -> Dict[str, Any]:
        """Returns hash table statistics and bucket chain visualization data."""
        if not self.analysis_performed:
            return {"error": "Analysis has not been run yet."}

        return {
            "statistics": self.detector.primary_table.get_statistics(),
            "buckets": self.detector.primary_table.get_bucket_visualization(max_buckets=max_buckets),
            "email_table_stats": self.detector.email_table.get_statistics(),
            "phone_table_stats": self.detector.phone_table.get_statistics(),
            "id_code_table_stats": self.detector.id_code_table.get_statistics(),
        }

    def get_record_hash_trace(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Finds a specific record and returns its full mathematical hash trace."""
        for r in self.detector.processed_records:
            if r.id == record_id:
                return {
                    "record": r.to_dict(),
                    "trace": r.hash_trace.to_dict() if r.hash_trace else None,
                }
        return None

    def export_project_zip(self) -> str:
        """Packages the complete project into a downloadable ZIP."""
        return package_project_zip(root_dir=BASE_DIR, output_zip_path=ZIP_EXPORT_PATH)
