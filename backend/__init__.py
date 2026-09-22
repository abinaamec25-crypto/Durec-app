"""
Backend package for Duplicate Record Detection.
"""
from .services import AnalysisService
from .routes import api_bp

__all__ = ["AnalysisService", "api_bp"]
