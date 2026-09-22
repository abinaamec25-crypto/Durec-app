"""
File and system utilities: sanitization, size validation, temporary cleanup, and ZIP packaging.
"""
import os
import re
import shutil
import zipfile
from typing import List, Optional, Tuple


def sanitize_filename(filename: str) -> str:
    """Sanitizes file name to prevent path traversal or unsafe file writes."""
    clean = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean)
    clean = re.sub(r'_+', '_', clean)
    return clean or "uploaded_data"


def validate_file_size(content_bytes: bytes, max_bytes: int = 25 * 1024 * 1024) -> Tuple[bool, Optional[str]]:
    """Checks file size limit (default 25 MB)."""
    if len(content_bytes) > max_bytes:
        mb = max_bytes / (1024 * 1024)
        return False, f"File exceeds maximum allowed size of {mb:.0f} MB."
    return True, None


def package_project_zip(
    root_dir: str,
    output_zip_path: str,
    exclude_dirs: Optional[List[str]] = None,
    exclude_exts: Optional[List[str]] = None,
) -> str:
    """
    Creates duplicate-record-detection-hashing.zip bundling the entire
    working source code, tests, sample datasets, templates, static assets,
    and documentation.
    """
    if exclude_dirs is None:
        exclude_dirs = [
            ".git", "__pycache__", ".pytest_cache", ".gradle", "gradle", "build",
            ".build-outputs", "node_modules", "dist", "control-plane-api",
            ".idea", ".vscode_cache", ".kotlin", "uploads"
        ]
    if exclude_exts is None:
        exclude_exts = [
            ".pyc", ".pyo", ".log", ".tmp", ".keystore", ".base64", ".kts", ".properties"
        ]

    included_top_level = {
        "app.py", "config.py", "requirements.txt", "README.md", "metadata.json",
        "models", "normalizer", "hashing", "parser", "backend", "utils",
        "templates", "static", "sample_data", "tests"
    }

    parent_dir = os.path.dirname(output_zip_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            rel_root = os.path.relpath(root, root_dir)
            top_part = rel_root.split(os.sep)[0]

            if rel_root != "." and top_part not in included_top_level:
                continue

            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_exts:
                    continue

                if rel_root == "." and file not in included_top_level:
                    continue

                full_path = os.path.join(root, file)
                if os.path.abspath(full_path) == os.path.abspath(output_zip_path):
                    continue

                rel_path = os.path.relpath(full_path, root_dir)
                arcname = os.path.join("duplicate-record-detection", rel_path)
                zipf.write(full_path, arcname=arcname)

    return output_zip_path
