"""
Academic Hash Functions for Data Structures Demonstration.
Implements:
1. Polynomial Rolling Hash (p = 31, 2^32 modulus)
2. DJB2 Hash (Daniel J. Bernstein, 5381 multiplier 33)
3. FNV-1a Hash (Fowler-Noll-Vo 32-bit prime/offset)

Includes step-by-step arithmetic tracing for viva and interactive UI visualization.
"""
from typing import Any, Dict, List, Tuple


def polynomial_rolling_hash(key: str, p: int = 31, m: int = 2**32) -> int:
    """
    Polynomial rolling hash function:
    H(s) = sum(s[i] * p^i) mod m
    Widely used in string matching (Rabin-Karp) and compiler symbol tables.
    """
    hash_val = 0
    p_pow = 1
    for char in key:
        hash_val = (hash_val + (ord(char) * p_pow)) % m
        p_pow = (p_pow * p) % m
    return hash_val


def djb2_hash(key: str, m: int = 2**32) -> int:
    """
    DJB2 algorithm by Dan Bernstein:
    hash = ((hash << 5) + hash) + char = hash * 33 + char
    Excellent bit dispersion and distribution across small and large tables.
    """
    hash_val = 5381
    for char in key:
        hash_val = (((hash_val << 5) + hash_val) + ord(char)) % m
    return hash_val


def fnv1a_hash(key: str, m: int = 2**32) -> int:
    """
    32-bit FNV-1a hash algorithm:
    hash = (hash XOR char) * FNV_PRIME
    Produces high avalanche effect with rapid computation.
    """
    FNV_OFFSET_BASIS = 2166136261
    FNV_PRIME = 16777619
    hash_val = FNV_OFFSET_BASIS
    for char in key:
        hash_val = (hash_val ^ ord(char)) % m
        hash_val = (hash_val * FNV_PRIME) % m
    return hash_val


class HashFunctionEngine:
    """
    Computes hash values and generates step-by-step mathematical trace logs
    for academic demonstration in the UI and viva explanations.
    """

    AVAILABLE_ALGORITHMS = {
        "polynomial": ("Polynomial Rolling Hash", polynomial_rolling_hash),
        "djb2": ("DJB2 (Dan Bernstein)", djb2_hash),
        "fnv1a": ("FNV-1a (32-bit)", fnv1a_hash),
    }

    @classmethod
    def compute_hash(cls, key: str, algorithm: str = "polynomial", table_size: int = 101) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Calculates the raw hash and bucket index, recording arithmetic steps.
        Returns:
            (raw_hash_value, bucket_index, step_samples)
        """
        if not key:
            return 0, 0, []

        p = 31
        m = 2**32
        hash_val = 0
        p_pow = 1
        steps: List[Dict[str, Any]] = []

        if algorithm == "djb2":
            hash_val = 5381
            for idx, char in enumerate(key):
                ascii_code = ord(char)
                prev_val = hash_val
                hash_val = (((hash_val << 5) + hash_val) + ascii_code) % m
                if idx < 6 or idx == len(key) - 1:
                    steps.append({
                        "step": idx + 1,
                        "char": char,
                        "ascii": ascii_code,
                        "formula": f"({prev_val} * 33) + {ascii_code}",
                        "accumulated_hash": hash_val,
                    })
        elif algorithm == "fnv1a":
            hash_val = 2166136261
            FNV_PRIME = 16777619
            for idx, char in enumerate(key):
                ascii_code = ord(char)
                prev_val = hash_val
                hash_val = (hash_val ^ ascii_code) % m
                hash_val = (hash_val * FNV_PRIME) % m
                if idx < 6 or idx == len(key) - 1:
                    steps.append({
                        "step": idx + 1,
                        "char": char,
                        "ascii": ascii_code,
                        "formula": f"({prev_val} ^ {ascii_code}) * {FNV_PRIME}",
                        "accumulated_hash": hash_val,
                    })
        else:  # Default to polynomial rolling hash
            for idx, char in enumerate(key):
                ascii_code = ord(char)
                term = (ascii_code * p_pow) % m
                prev_val = hash_val
                hash_val = (hash_val + term) % m
                if idx < 6 or idx == len(key) - 1:
                    steps.append({
                        "step": idx + 1,
                        "char": char,
                        "ascii": ascii_code,
                        "p_pow": p_pow,
                        "formula": f"{prev_val} + ({ascii_code} * {p}^{idx})",
                        "accumulated_hash": hash_val,
                    })
                p_pow = (p_pow * p) % m

        bucket_index = hash_val % table_size
        return hash_val, bucket_index, steps
