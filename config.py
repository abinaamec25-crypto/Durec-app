"""
Application Configuration for Duplicate Record Detection System.
Anna University Regulation 2025 Data Structures Academic Project.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Upload and Output paths
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
SAMPLE_DATA_FOLDER = os.path.join(BASE_DIR, "sample_data")
ZIP_EXPORT_PATH = os.path.join(OUTPUT_FOLDER, "duplicate-record-detection-hashing.zip")

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "csv", "tsv", "json", "jsonl", "ndjson", "xlsx", "xls", "pdf", "docx", "txt"
}

# Max upload limit: 32MB
MAX_CONTENT_LENGTH = 32 * 1024 * 1024

# Default Hashing Configuration
DEFAULT_HASH_ALGORITHM = "polynomial"  # 'polynomial', 'djb2', 'fnv1a'
DEFAULT_HASH_TABLE_CAPACITY = 101

# Server port: 3000 (standard for the web environment proxy)
PORT = 3000
HOST = "0.0.0.0"
DEBUG = False

# Ensure folders exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, SAMPLE_DATA_FOLDER]:
    os.makedirs(folder, exist_ok=True)
