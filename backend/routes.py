"""
REST API Routes and UI Controller for Duplicate Record Detection System.
Anna University Regulation 2025 Data Structures Academic Project.
"""
import os
import shutil
from flask import Blueprint, jsonify, render_template, request, send_file
from config import SAMPLE_DATA_FOLDER, ZIP_EXPORT_PATH
from .services import AnalysisService

api_bp = Blueprint("api", __name__)
service = AnalysisService()


@api_bp.route("/")
def index():
    """Renders the main dashboard user interface."""
    return render_template("index.html")


@api_bp.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint confirming API and data structures engine status."""
    return jsonify({
        "status": "healthy",
        "service": "Duplicate Record Detection Using Hashing Technique",
        "regulations": "Anna University R2025",
        "academic_topic": "Data Structures - Hashing & Separate Chaining",
        "version": "1.0.0",
    })


@api_bp.route("/api/upload", methods=["POST"])
def upload_files():
    """
    Accepts single or multi-file uploads (CSV, TSV, XLSX, XLS, JSON, JSONL, PDF, DOCX, TXT).
    """
    if "files" not in request.files and "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_files_list = request.files.getlist("files") or [request.files["file"]]
    added_files = []
    errors = []

    for file in uploaded_files_list:
        if file and file.filename:
            content = file.read()
            success, err, meta = service.add_uploaded_file(file.filename, content)
            if success and meta:
                added_files.append(meta)
            else:
                errors.append({"filename": file.filename, "error": err})

    return jsonify({
        "success": True,
        "files_added": added_files,
        "errors": errors,
        "total_active_files": len(service.uploaded_files),
    })


@api_bp.route("/api/upload/remove", methods=["POST"])
def remove_file():
    """Removes a specific file from current upload set."""
    data = request.get_json() or {}
    filename = data.get("filename", "")
    removed = service.remove_uploaded_file(filename)
    return jsonify({
        "success": removed,
        "total_active_files": len(service.uploaded_files),
    })


@api_bp.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Triggers parsing, normalization, and hashing-based duplicate detection.
    Accepts JSON options: algorithm ('polynomial', 'djb2', 'fnv1a'), initial_capacity (int).
    """
    data = request.get_json() or {}
    algorithm = data.get("algorithm", "polynomial")
    initial_capacity = int(data.get("initial_capacity", 101))

    summary = service.run_analysis(algorithm=algorithm, initial_capacity=initial_capacity)
    if "error" in summary:
        return jsonify({"success": False, "error": summary["error"]}), 400

    return jsonify({
        "success": True,
        "summary": summary,
    })


@api_bp.route("/api/results", methods=["GET"])
def get_results():
    """Returns the latest analysis summary and performance metrics."""
    if not service.analysis_performed or not service.last_summary:
        return jsonify({"success": False, "message": "No analysis performed yet."}), 404
    return jsonify({
        "success": True,
        "summary": service.last_summary,
    })


@api_bp.route("/api/duplicates", methods=["GET"])
def get_duplicates():
    """Returns detected duplicate groups with primary and duplicate records."""
    if not service.analysis_performed:
        return jsonify({"groups": [], "total_groups": 0})

    groups = service.get_duplicate_groups()
    return jsonify({
        "groups": groups,
        "total_groups": len(groups),
    })


@api_bp.route("/api/records", methods=["GET"])
def get_records():
    """
    Returns records with filtering (all, duplicate, unique), pagination, and search.
    Query params: type, page, per_page, search.
    """
    if not service.analysis_performed:
        return jsonify({"records": [], "total_count": 0, "page": 1, "total_pages": 1})

    record_type = request.args.get("type", "all")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    search = request.args.get("search", "")

    result = service.get_records(record_type=record_type, page=page, per_page=per_page, search_query=search)
    return jsonify(result)


@api_bp.route("/api/hash-table", methods=["GET"])
def get_hash_table():
    """
    Returns visual hash table bucket structure with chains, collisions,
    and load factor statistics.
    """
    max_buckets = int(request.args.get("max_buckets", 60))
    res = service.get_hash_table_state(max_buckets=max_buckets)
    if "error" in res:
        return jsonify({"success": False, "error": res["error"]}), 400
    return jsonify({"success": True, "hash_table": res})


@api_bp.route("/api/record/<int:record_id>/trace", methods=["GET"])
def get_record_trace(record_id: int):
    """
    Returns exact mathematical step-by-step hashing trace for a specific record.
    Used for the interactive viva visualization component.
    """
    trace_data = service.get_record_hash_trace(record_id)
    if not trace_data:
        return jsonify({"error": f"Record with ID {record_id} not found."}), 404
    return jsonify({"success": True, "data": trace_data})


@api_bp.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Returns comprehensive theoretical and operational Data Structures statistics."""
    if not service.analysis_performed:
        return jsonify({"error": "No analysis data available."}), 404

    hash_stats = service.detector.primary_table.get_statistics()
    return jsonify({
        "summary": service.last_summary,
        "primary_hash_table": hash_stats,
        "email_hash_table": service.detector.email_table.get_statistics(),
        "phone_hash_table": service.detector.phone_table.get_statistics(),
    })


@api_bp.route("/api/reset", methods=["POST"])
def reset_state():
    """Clears all session uploads, records, and hash tables."""
    service.reset()
    return jsonify({"success": True, "message": "Session reset successfully."})


@api_bp.route("/api/load-sample", methods=["POST"])
def load_sample_datasets():
    """
    One-click loader for the included multi-format test datasets:
    Loads sample CSV, JSON, TSV, TXT, and Excel data containing exact, partial,
    and schema-differing duplicates for instant demonstration.
    """
    service.reset()
    loaded_files = []
    errors = []

    if os.path.exists(SAMPLE_DATA_FOLDER):
        for fname in sorted(os.listdir(SAMPLE_DATA_FOLDER)):
            fpath = os.path.join(SAMPLE_DATA_FOLDER, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as f:
                    content = f.read()
                success, err, meta = service.add_uploaded_file(fname, content)
                if success and meta:
                    loaded_files.append(meta)
                else:
                    errors.append({"filename": fname, "error": err})

    # Automatically run analysis on loaded samples
    summary = service.run_analysis(algorithm="polynomial", initial_capacity=101)

    return jsonify({
        "success": True,
        "loaded_files": loaded_files,
        "errors": errors,
        "summary": summary,
    })


@api_bp.route("/api/download-zip", methods=["GET"])
def download_project_zip():
    """
    Generates and returns the complete duplicate-record-detection-hashing.zip
    containing all source files, models, tests, datasets, and documentation.
    """
    zip_path = service.export_project_zip()
    if not os.path.exists(zip_path):
        return jsonify({"error": "Failed to create project ZIP package."}), 500

    return send_file(
        zip_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name="duplicate-record-detection-hashing.zip",
    )
