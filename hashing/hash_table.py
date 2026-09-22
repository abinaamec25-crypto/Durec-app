"""
Custom Hash Table with Separate Chaining Collision Resolution.
Core Data Structure for Anna University R2025 Data Structures Project.

Concepts demonstrated:
- Dynamic Array of Buckets (Size M, prime numbers for uniform distribution)
- Separate Chaining using singly-linked bucket chains
- Time Complexity: O(1) average insertion & search, O(n) worst-case
- Collision Resolution & Tracking
- Load Factor alpha = N / M
- Rehashing when alpha > threshold
"""
from typing import Any, Dict, List, Optional, Tuple
from models.record import HashTrace, Record
from .hash_functions import HashFunctionEngine


class HashNode:
    """
    Node in the separate chaining linked-list structure.
    Each bucket holds a linked chain of HashNodes that resolve to that bucket index.
    """
    def __init__(self, key: str, record: Record, next_node: Optional["HashNode"] = None):
        self.key: str = key
        self.record: Record = record
        self.next: Optional["HashNode"] = next_node

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "record_id": self.record.id,
            "record_source": self.record.source_file,
            "summary": {k: v for k, v in list(self.record.canonical_fields.items())[:3]},
        }


class HashTable:
    """
    Custom Hash Table Data Structure implementing Separate Chaining.
    Tracks deep academic metrics:
    - Number of elements (N)
    - Capacity (M)
    - Load Factor (alpha = N / M)
    - Total collisions encountered
    - Total key comparisons performed
    - Maximum chain length (worst-case bucket depth)
    """

    PRIMES = [31, 53, 101, 211, 401, 809, 1601, 3203, 6421, 12853, 25717, 50021]

    def __init__(self, initial_capacity: int = 101, algorithm: str = "polynomial", auto_rehash: bool = True):
        # Pick closest prime from list if matching
        self.capacity: int = self._find_prime_at_least(initial_capacity)
        self.algorithm: str = algorithm
        self.auto_rehash: bool = auto_rehash
        self.max_load_factor: float = 0.75

        # Array of bucket heads (Separate Chaining)
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity

        # Performance & Academic Statistics
        self.num_elements: int = 0
        self.total_collisions: int = 0
        self.total_comparisons: int = 0
        self.rehash_count: int = 0

    def _find_prime_at_least(self, target: int) -> int:
        for p in self.PRIMES:
            if p >= target:
                return p
        return target if target % 2 != 0 else target + 1

    def _hash(self, key: str) -> Tuple[int, int, List[Dict[str, Any]]]:
        """Calculates hash value and bucket index using chosen academic algorithm."""
        return HashFunctionEngine.compute_hash(key, self.algorithm, self.capacity)

    @property
    def load_factor(self) -> float:
        """alpha = N / M"""
        return self.num_elements / self.capacity if self.capacity > 0 else 0.0

    def insert(self, key: str, record: Record) -> Tuple[Optional[Record], HashTrace]:
        """
        Inserts record with key into the hash table.
        If an identical key already exists in the chain, returns the existing record (exact duplicate detected)
        along with the academic HashTrace.
        If not found, inserts at the head of the chain.
        """
        if self.auto_rehash and self.load_factor >= self.max_load_factor:
            self._rehash()

        hash_val, bucket_idx, step_samples = self._hash(key)
        trace = HashTrace(
            key_string=key,
            algorithm=self.algorithm,
            hash_value=hash_val,
            table_size=self.capacity,
            bucket_index=bucket_idx,
            step_samples=step_samples,
        )

        current = self.buckets[bucket_idx]
        chain_pos = 0
        collision_detected = False

        if current is not None:
            # Bucket is not empty -> at least one item was already hashed to this index
            collision_detected = True
            self.total_collisions += 1
            trace.collision_occurred = True

        # Traverse bucket chain to check for existing record with identical key
        while current is not None:
            self.total_comparisons += 1
            trace.comparisons_made += 1
            trace.comparison_details.append(
                f"Comparing key with Record #{current.record.id} in bucket #{bucket_idx} (chain index {chain_pos})"
            )

            if current.key == key:
                # EXACT DUPLICATE FOUND in hash table!
                trace.chain_position = chain_pos
                record.hash_value = hash_val
                record.bucket_index = bucket_idx
                record.hash_trace = trace
                return current.record, trace

            current = current.next
            chain_pos += 1

        # Key not in chain; insert new node at head of chain (O(1) insertion)
        trace.chain_position = 0
        new_node = HashNode(key=key, record=record, next_node=self.buckets[bucket_idx])
        self.buckets[bucket_idx] = new_node
        self.num_elements += 1

        record.hash_value = hash_val
        record.bucket_index = bucket_idx
        record.hash_trace = trace

        return None, trace

    def search(self, key: str) -> Optional[Record]:
        """
        Searches for a record matching key in O(1) average time.
        Traverses the bucket chain at hash(key) % M.
        """
        hash_val, bucket_idx, _ = self._hash(key)
        current = self.buckets[bucket_idx]
        while current is not None:
            self.total_comparisons += 1
            if current.key == key:
                return current.record
            current = current.next
        return None

    def _rehash(self) -> None:
        """
        Doubles the table size to the next prime and re-inserts all existing elements.
        Maintains O(1) average time complexity by preventing deep chains.
        """
        old_buckets = self.buckets
        old_capacity = self.capacity

        # Find next prime
        next_capacity = self._find_prime_at_least(old_capacity * 2)
        self.capacity = next_capacity
        self.buckets = [None] * next_capacity
        self.num_elements = 0
        self.rehash_count += 1

        for bucket in old_buckets:
            current = bucket
            while current is not None:
                next_node = current.next
                # Reinsert into new table size
                hash_val, bucket_idx, _ = self._hash(current.key)
                current.next = self.buckets[bucket_idx]
                self.buckets[bucket_idx] = current
                self.num_elements += 1
                current = next_node

    def get_statistics(self) -> Dict[str, Any]:
        """Returns comprehensive data structure metrics for academic evaluation."""
        chain_lengths: List[int] = []
        empty_buckets = 0

        for head in self.buckets:
            length = 0
            curr = head
            while curr is not None:
                length += 1
                curr = curr.next
            chain_lengths.append(length)
            if length == 0:
                empty_buckets += 1

        max_chain = max(chain_lengths) if chain_lengths else 0
        avg_chain = (
            sum(chain_lengths) / (self.capacity - empty_buckets)
            if (self.capacity - empty_buckets) > 0
            else 0.0
        )

        return {
            "capacity": self.capacity,
            "num_elements": self.num_elements,
            "load_factor": round(self.load_factor, 3),
            "total_collisions": self.total_collisions,
            "total_comparisons": self.total_comparisons,
            "empty_buckets": empty_buckets,
            "occupied_buckets": self.capacity - empty_buckets,
            "max_chain_length": max_chain,
            "avg_chain_length_occupied": round(avg_chain, 2),
            "rehash_count": self.rehash_count,
            "algorithm": self.algorithm,
            "collision_resolution": "Separate Chaining (Linked Lists)",
            "average_time_complexity": "O(1)",
            "worst_case_time_complexity": "O(n)",
            "space_complexity": "O(n + m)",
        }

    def get_bucket_visualization(self, max_buckets: int = 50) -> List[Dict[str, Any]]:
        """
        Generates serializable bucket representations for interactive UI visualization:
        Bucket index -> Chain of nodes -> Record IDs & summaries.
        """
        vis_buckets: List[Dict[str, Any]] = []
        # Return first max_buckets or occupied buckets
        limit = min(len(self.buckets), max_buckets)
        for idx in range(limit):
            curr = self.buckets[idx]
            chain: List[Dict[str, Any]] = []
            while curr is not None:
                chain.append({
                    "record_id": curr.record.id,
                    "source_file": curr.record.source_file,
                    "key_excerpt": curr.key[:45] + ("..." if len(curr.key) > 45 else ""),
                    "canonical": {k: curr.record.canonical_fields[k] for k in list(curr.record.canonical_fields.keys())[:3]},
                })
                curr = curr.next
            vis_buckets.append({
                "bucket_index": idx,
                "chain_length": len(chain),
                "is_empty": len(chain) == 0,
                "chain": chain,
            })
        return vis_buckets
