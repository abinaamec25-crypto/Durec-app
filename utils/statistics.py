"""
Statistics and performance calculation utilities for academic evaluation.
"""
from typing import Any, Dict


def compute_performance_metrics(
    total_records: int,
    duplicate_count: int,
    collisions: int,
    comparisons: int,
    table_size: int,
    elapsed_ms: float,
) -> Dict[str, Any]:
    """Computes academic Data Structures metrics for demonstration and viva."""
    alpha = total_records / table_size if table_size > 0 else 0.0
    collision_rate = (collisions / total_records * 100) if total_records > 0 else 0.0
    avg_comps_per_insert = (comparisons / total_records) if total_records > 0 else 0.0

    return {
        "load_factor": round(alpha, 3),
        "collision_rate_percent": round(collision_rate, 2),
        "avg_comparisons_per_insert": round(avg_comps_per_insert, 2),
        "records_per_second": round((total_records / (elapsed_ms / 1000.0)), 1) if elapsed_ms > 0 else 0.0,
        "theoretical_complexity": {
            "average_insert": "O(1)",
            "average_search": "O(1)",
            "worst_case_search": f"O({total_records}) (if all keys hash to same bucket)",
            "space_overhead": f"O({table_size} buckets + {total_records} nodes)",
        }
    }
