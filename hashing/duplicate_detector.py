"""
Multi-Tier Duplicate Detector Using Hashing Techniques.
Anna University R2025 Data Structures Academic Project.

Detects:
1. Exact Duplicates: Identical normalized primary composite key via Primary Hash Table.
2. Partial Duplicates: Shared strong identifiers (Email, Phone, ID) via Secondary Hash Tables.
3. Possible Duplicates: High similarity (Levenshtein / Token overlap) on key fields.
"""
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from models.record import DuplicateGroup, DuplicateType, Record
from normalizer.record_normalizer import RecordNormalizer
from .hash_table import HashTable


class DuplicateDetector:
    """
    Coordinates primary and secondary Hash Tables to detect duplicates
    across heterogeneous records with varying schemas.
    """

    def __init__(
        self,
        algorithm: str = "polynomial",
        initial_capacity: int = 101,
        normalizer: Optional[RecordNormalizer] = None,
    ):
        self.algorithm = algorithm
        self.initial_capacity = initial_capacity
        self.normalizer = normalizer or RecordNormalizer()

        # Primary Hash Table for exact composite key matches
        self.primary_table = HashTable(
            initial_capacity=self.initial_capacity,
            algorithm=self.algorithm,
        )

        # Secondary Hash Tables for field-level partial matches
        self.email_table = HashTable(initial_capacity=53, algorithm=self.algorithm)
        self.phone_table = HashTable(initial_capacity=53, algorithm=self.algorithm)
        self.id_code_table = HashTable(initial_capacity=53, algorithm=self.algorithm)

        # Detection collections
        self.processed_records: List[Record] = []
        self.unique_records: List[Record] = []
        self.duplicate_records: List[Record] = []
        self.duplicate_groups: List[DuplicateGroup] = []
        self._record_map: Dict[int, Record] = {}
        self._group_map: Dict[int, DuplicateGroup] = {}  # primary_id -> DuplicateGroup

        # Statistics
        self.total_comparisons = 0
        self.processing_time_ms = 0.0

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Academic Levenshtein distance implementation for possible duplicate scoring."""
        if len(s1) < len(s2):
            return DuplicateDetector._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev[j + 1] + 1
                deletions = curr[j] + 1
                substitutions = prev[j] + (c1 != c2)
                curr.append(min(insertions, deletions, substitutions))
            prev = curr
        return prev[-1]

    def _similarity_ratio(self, s1: str, s2: str) -> float:
        """Calculates normalized similarity between 0.0 and 1.0."""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        max_len = max(len(s1), len(s2))
        dist = self._levenshtein_distance(s1, s2)
        return max(0.0, 1.0 - (dist / max_len))

    def process_records(self, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main duplicate detection pipeline:
        1. Normalization & Canonical mapping
        2. Primary Key Generation
        3. Primary Hash Table Insertion & Exact Duplicate Checking
        4. Secondary Hash Table Insertion & Partial Duplicate Checking
        5. Near-match Possible Duplicate Checking
        6. Aggregation of Groups and Metrics
        """
        start_time = time.perf_counter()

        self.processed_records.clear()
        self.unique_records.clear()
        self.duplicate_records.clear()
        self.duplicate_groups.clear()
        self._record_map.clear()
        self._group_map.clear()

        # Phase 1: Convert raw dictionaries into Record objects with normalized fields
        for idx, item in enumerate(raw_records, start=1):
            source_file = item.get("__source_file__", "input_data")
            file_type = item.get("__file_type__", "unknown")
            line_num = item.get("__line_number__", idx)

            clean_raw = {k: v for k, v in item.items() if not k.startswith("__")}
            canonical_fields, normalized_data = self.normalizer.normalize_record(clean_raw)
            primary_key = self.normalizer.generate_primary_hash_key(canonical_fields)

            rec = Record(
                id=idx,
                source_file=source_file,
                file_type=file_type,
                raw_data=clean_raw,
                line_number=line_num,
                normalized_data=normalized_data,
                canonical_fields=canonical_fields,
                primary_hash_key=primary_key,
            )
            self.processed_records.append(rec)
            self._record_map[rec.id] = rec

        # Phase 2: Insert into Hash Tables and Detect Duplicates
        for rec in self.processed_records:
            if not rec.primary_hash_key:
                # Empty record or no valid fields
                self.unique_records.append(rec)
                continue

            # Step 1: Check Exact Duplicate via Primary Hash Table
            existing_match, trace = self.primary_table.insert(rec.primary_hash_key, rec)

            if existing_match is not None:
                # EXACT DUPLICATE DETECTED!
                rec.is_duplicate = True
                rec.duplicate_of_id = existing_match.id
                rec.duplicate_type = DuplicateType.EXACT
                rec.confidence_score = 100.0

                matched_fields = list(rec.canonical_fields.keys())
                self._add_to_duplicate_group(
                    primary_rec=existing_match,
                    duplicate_rec=rec,
                    dup_type=DuplicateType.EXACT,
                    matched_fields=matched_fields,
                    confidence=100.0,
                    explanation=(
                        f"Exact match on normalized composite key: '{rec.primary_hash_key}' "
                        f"(Bucket #{rec.bucket_index} collision resolved to identical key)."
                    ),
                )
                self.duplicate_records.append(rec)
                continue

            # Step 2: Check Partial Duplicate via Secondary Hash Tables
            # Check Email Hash Table
            partial_match: Optional[Record] = None
            matched_field_name: Optional[str] = None
            confidence = 0.0

            if "email" in rec.canonical_fields and rec.canonical_fields["email"]:
                email_key = f"email:{rec.canonical_fields['email']}"
                match, _ = self.email_table.insert(email_key, rec)
                if match is not None and match.id != rec.id:
                    partial_match = match
                    matched_field_name = "email"
                    confidence = 95.0

            # Check Phone Hash Table
            if partial_match is None and "phone" in rec.canonical_fields and rec.canonical_fields["phone"]:
                phone_key = f"phone:{rec.canonical_fields['phone']}"
                match, _ = self.phone_table.insert(phone_key, rec)
                if match is not None and match.id != rec.id:
                    partial_match = match
                    matched_field_name = "phone"
                    confidence = 90.0

            # Check Student/Employee ID Code Hash Table
            if partial_match is None and "id_code" in rec.canonical_fields and rec.canonical_fields["id_code"]:
                id_key = f"id_code:{rec.canonical_fields['id_code']}"
                match, _ = self.id_code_table.insert(id_key, rec)
                if match is not None and match.id != rec.id:
                    partial_match = match
                    matched_field_name = "id_code"
                    confidence = 95.0

            if partial_match is not None:
                # PARTIAL DUPLICATE DETECTED!
                rec.is_duplicate = True
                rec.duplicate_of_id = partial_match.id
                rec.duplicate_type = DuplicateType.PARTIAL
                rec.confidence_score = confidence

                common_keys = [
                    k for k in rec.canonical_fields
                    if k in partial_match.canonical_fields
                    and rec.canonical_fields[k] == partial_match.canonical_fields[k]
                ]
                if matched_field_name not in common_keys:
                    common_keys.append(matched_field_name)

                self._add_to_duplicate_group(
                    primary_rec=partial_match,
                    duplicate_rec=rec,
                    dup_type=DuplicateType.PARTIAL,
                    matched_fields=common_keys,
                    confidence=confidence,
                    explanation=(
                        f"Partial match: Identical {matched_field_name} "
                        f"('{rec.canonical_fields.get(matched_field_name, '')}') with varying schema attributes."
                    ),
                )
                self.duplicate_records.append(rec)
                continue

            # Step 3: Check Possible Duplicate (Name similarity with shared context)
            possible_match = self._find_possible_match(rec)
            if possible_match:
                match_rec, score, explanation = possible_match
                rec.is_duplicate = True
                rec.duplicate_of_id = match_rec.id
                rec.duplicate_type = DuplicateType.POSSIBLE
                rec.confidence_score = score

                matched_fields = [
                    k for k in rec.canonical_fields
                    if k in match_rec.canonical_fields
                ]
                self._add_to_duplicate_group(
                    primary_rec=match_rec,
                    duplicate_rec=rec,
                    dup_type=DuplicateType.POSSIBLE,
                    matched_fields=matched_fields,
                    confidence=score,
                    explanation=explanation,
                )
                self.duplicate_records.append(rec)
                continue

            # Unique Record
            self.unique_records.append(rec)

        self.processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return self.get_summary()

    def _find_possible_match(self, candidate: Record) -> Optional[Tuple[Record, float, str]]:
        """Checks for near matches (e.g., Arun Kumar vs Arun K.) against existing unique records."""
        cand_name = candidate.canonical_fields.get("name", "")
        if not cand_name or len(cand_name) < 3:
            return None

        for existing in self.unique_records:
            exist_name = existing.canonical_fields.get("name", "")
            if not exist_name or len(exist_name) < 3:
                continue

            # Same department or company increases likelihood
            same_context = False
            for ctx_field in ["department", "company", "address"]:
                if (
                    ctx_field in candidate.canonical_fields
                    and ctx_field in existing.canonical_fields
                    and candidate.canonical_fields[ctx_field] == existing.canonical_fields[ctx_field]
                ):
                    same_context = True
                    break

            sim = self._similarity_ratio(cand_name, exist_name)
            # Match if similarity >= 0.85, or >= 0.70 with matching department
            if sim >= 0.85 or (same_context and sim >= 0.70):
                conf = round(sim * 100, 1)
                context_msg = " in same department/organization" if same_context else ""
                return (
                    existing,
                    conf,
                    f"Possible match: Name '{cand_name}' is {conf}% similar to '{exist_name}'{context_msg}.",
                )
        return None

    def _add_to_duplicate_group(
        self,
        primary_rec: Record,
        duplicate_rec: Record,
        dup_type: DuplicateType,
        matched_fields: List[str],
        confidence: float,
        explanation: str,
    ) -> None:
        """Groups duplicates under a primary/master record."""
        # Check if primary_rec is already in a group as primary
        if primary_rec.id in self._group_map:
            group = self._group_map[primary_rec.id]
            group.duplicates.append(duplicate_rec)
        else:
            new_group_id = len(self.duplicate_groups) + 1
            group = DuplicateGroup(
                group_id=new_group_id,
                primary_record=primary_rec,
                duplicates=[duplicate_rec],
                duplicate_type=dup_type,
                matched_fields=matched_fields,
                confidence=confidence,
                explanation=explanation,
            )
            self.duplicate_groups.append(group)
            self._group_map[primary_rec.id] = group

    def get_summary(self) -> Dict[str, Any]:
        """Provides total counts and statistics for UI and API consumption."""
        total_records = len(self.processed_records)
        duplicate_count = len(self.duplicate_records)
        unique_count = len(self.unique_records)
        dup_percentage = (
            round((duplicate_count / total_records) * 100, 1) if total_records > 0 else 0.0
        )

        exact_count = sum(1 for r in self.duplicate_records if r.duplicate_type == DuplicateType.EXACT)
        partial_count = sum(1 for r in self.duplicate_records if r.duplicate_type == DuplicateType.PARTIAL)
        possible_count = sum(1 for r in self.duplicate_records if r.duplicate_type == DuplicateType.POSSIBLE)

        hash_stats = self.primary_table.get_statistics()

        return {
            "total_records": total_records,
            "unique_records": unique_count,
            "duplicate_records": duplicate_count,
            "duplicate_percentage": dup_percentage,
            "exact_duplicates": exact_count,
            "partial_duplicates": partial_count,
            "possible_duplicates": possible_count,
            "duplicate_groups_count": len(self.duplicate_groups),
            "processing_time_ms": self.processing_time_ms,
            "hash_table_statistics": hash_stats,
        }
