"""
Record data models and duplicate classification types.
Anna University R2025 Data Structures Academic Project.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DuplicateType(str, Enum):
    EXACT = "Exact Duplicate"
    PARTIAL = "Partial Duplicate"
    POSSIBLE = "Possible Duplicate"


@dataclass
class HashTrace:
    """
    Detailed hash calculation trace for academic and viva explanation.
    Demonstrates exact mathematical steps:
    1. Key string representation
    2. Character-by-character polynomial rolling hash or DJB2 steps
    3. Final 32-bit unsigned integer hash value
    4. Modulo arithmetic: hash_val % table_size -> bucket_index
    5. Collision occurrence & chain traversal steps
    """
    key_string: str
    algorithm: str
    hash_value: int
    table_size: int
    bucket_index: int
    step_samples: List[Dict[str, Any]] = field(default_factory=list)
    collision_occurred: bool = False
    chain_position: int = 0
    comparisons_made: int = 0
    comparison_details: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_string": self.key_string,
            "raw_key": self.key_string,
            "algorithm": self.algorithm,
            "algorithm_name": self.algorithm,
            "hash_value": self.hash_value,
            "raw_hash": self.hash_value,
            "table_size": self.table_size,
            "table_capacity": self.table_size,
            "bucket_index": self.bucket_index,
            "step_samples": self.step_samples,
            "calculation_steps": self.step_samples,
            "collision_occurred": self.collision_occurred,
            "chain_position": self.chain_position,
            "comparisons_made": self.comparisons_made,
            "comparison_details": self.comparison_details,
        }


@dataclass
class Record:
    """
    Universal internal representation of a record parsed from any input format
    (CSV, TSV, Excel, JSON, PDF, DOCX, TXT).
    """
    id: int
    source_file: str
    file_type: str
    raw_data: Dict[str, Any]
    line_number: Optional[int] = None
    normalized_data: Dict[str, Any] = field(default_factory=dict)
    canonical_fields: Dict[str, Any] = field(default_factory=dict)
    primary_hash_key: str = ""
    hash_value: Optional[int] = None
    bucket_index: Optional[int] = None
    hash_trace: Optional[HashTrace] = None
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None
    duplicate_type: Optional[DuplicateType] = None
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_file": self.source_file,
            "file_type": self.file_type,
            "raw_data": self.raw_data,
            "line_number": self.line_number,
            "normalized_data": self.normalized_data,
            "canonical_fields": self.canonical_fields,
            "primary_hash_key": self.primary_hash_key,
            "hash_value": self.hash_value,
            "bucket_index": self.bucket_index,
            "hash_trace": self.hash_trace.to_dict() if self.hash_trace else None,
            "is_duplicate": self.is_duplicate,
            "duplicate_of_id": self.duplicate_of_id,
            "duplicate_type": self.duplicate_type.value if self.duplicate_type else None,
            "confidence_score": round(self.confidence_score, 2),
        }


@dataclass
class DuplicateGroup:
    """
    A cluster of records identified as duplicates of a master/primary record.
    """
    group_id: int
    primary_record: Record
    duplicates: List[Record]
    duplicate_type: DuplicateType
    matched_fields: List[str]
    confidence: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "primary_record": self.primary_record.to_dict(),
            "duplicates": [d.to_dict() for d in self.duplicates],
            "total_records_in_group": 1 + len(self.duplicates),
            "duplicate_type": self.duplicate_type.value,
            "matched_fields": self.matched_fields,
            "confidence": round(self.confidence, 1),
            "explanation": self.explanation,
        }
