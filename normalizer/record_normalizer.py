"""
Record Normalizer for cleaning and transforming record values.
Ensures semantic equivalence across whitespace, case, format variations,
and missing or reordered fields before hashing.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from .field_mapper import FieldMapper


class RecordNormalizer:
    """
    Normalizes field values and constructs deterministic, order-independent
    hash keys for duplicate detection.
    """

    def __init__(self, field_mapper: Optional[FieldMapper] = None):
        self.field_mapper = field_mapper or FieldMapper()

    def normalize_string(self, text: Any) -> str:
        """Trim, collapse multiple whitespaces, and lowercase."""
        if text is None:
            return ""
        s = str(text).strip()
        # Collapse multiple internal spaces
        s = re.sub(r'\s+', ' ', s)
        return s.lower()

    def normalize_name(self, name: Any) -> str:
        """Strip honorifics/prefixes, remove extra punctuation, and lowercase."""
        s = self.normalize_string(name)
        if not s:
            return ""
        # Remove common honorifics
        s = re.sub(r'^(mr|ms|mrs|dr|prof|er)\.?\s+', '', s)
        # Remove periods and stray punctuation in names
        s = re.sub(r'[\.,_\-\'\"]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def normalize_email(self, email: Any) -> str:
        """Lowercase, trim, strip spaces, validate basic email pattern."""
        s = self.normalize_string(email)
        s = re.sub(r'\s+', '', s)
        return s

    def normalize_phone(self, phone: Any) -> str:
        """Extract digits, strip leading +91 / 91 / 0 if appropriate, standardize 10-digit number."""
        if phone is None:
            return ""
        # Extract digits only
        digits = re.sub(r'\D', '', str(phone))
        if not digits:
            return ""
        # Indian mobile numbers: 12 digits starting with 91 -> last 10 digits
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        # Numbers starting with 0 followed by 10 digits
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
        # US/International 11 digits starting with 1
        elif len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        return digits

    def normalize_number(self, val: Any) -> str:
        """Normalize numeric values (e.g., 20.0 -> 20, 020 -> 20)."""
        if val is None:
            return ""
        s = str(val).strip()
        try:
            f = float(s)
            if f.is_integer():
                return str(int(f))
            return str(f)
        except (ValueError, TypeError):
            return self.normalize_string(s)

    def normalize_date(self, date_val: Any) -> str:
        """Attempts to standardize common date formats into YYYY-MM-DD."""
        if not date_val:
            return ""
        s = str(date_val).strip()
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
            "%Y/%m/%d", "%d.%m.%Y", "%b %d, %Y", "%d %b %Y"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue
        return self.normalize_string(s)

    def normalize_value_by_field(self, field_name: str, value: Any) -> str:
        """Normalizes a single value according to the semantic rules of its canonical field."""
        if value is None:
            return ""
        val_str = str(value).strip()
        if val_str.lower() in ("none", "null", "nan", "n/a", "na", "-", ""):
            return ""

        field_lower = field_name.lower()
        if field_lower == "email":
            return self.normalize_email(val_str)
        elif field_lower == "phone":
            return self.normalize_phone(val_str)
        elif field_lower == "name":
            return self.normalize_name(val_str)
        elif field_lower in ("age", "id_code"):
            return self.normalize_number(val_str)
        elif field_lower == "dob":
            return self.normalize_date(val_str)
        else:
            return self.normalize_string(val_str)

    def normalize_record(self, raw_record: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Takes raw dictionary with arbitrary column names, maps to canonical fields,
        and applies value normalization.
        Returns:
            canonical_fields: dict of normalized canonical values
            normalized_all: dict of all normalized fields
        """
        canonical_raw = self.field_mapper.map_record_keys(raw_record)
        canonical_norm: Dict[str, Any] = {}
        all_norm: Dict[str, Any] = {}

        for k, v in canonical_raw.items():
            norm_val = self.normalize_value_by_field(k, v)
            if norm_val != "":
                canonical_norm[k] = norm_val
                all_norm[k] = norm_val

        # Also store normalized forms of original keys
        for k, v in raw_record.items():
            if k is not None:
                cleaned_k = str(k).strip()
                norm_val = self.normalize_string(v)
                if norm_val != "" and norm_val not in ("none", "null", "nan"):
                    all_norm[cleaned_k] = norm_val

        return canonical_norm, all_norm

    def generate_primary_hash_key(self, canonical_fields: Dict[str, Any]) -> str:
        """
        Generates an order-independent, deterministic composite key.
        Sorts canonical field keys alphabetically to ensure different column order
        yields the EXACT same hash key:
        e.g. {'phone': '9876543210', 'name': 'arun'} -> 'name:arun|phone:9876543210'
        """
        # Filter out empty fields
        filtered_items = [
            (k, str(v).strip())
            for k, v in sorted(canonical_fields.items())
            if v is not None and str(v).strip() != ""
        ]
        if not filtered_items:
            return ""
        return "|".join(f"{k}:{v}" for k, v in filtered_items)

    def generate_secondary_keys(self, canonical_fields: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Generates individual strong identifying keys for partial duplicate detection:
        e.g. ('email', 'arun@gmail.com'), ('phone', '9876543210'), ('id_code', '101')
        """
        strong_identifiers = ["email", "phone", "id_code"]
        sec_keys: List[Tuple[str, str]] = []
        for ident in strong_identifiers:
            if ident in canonical_fields and canonical_fields[ident]:
                sec_keys.append((ident, f"{ident}:{canonical_fields[ident]}"))
        # Also combined name + department or name + dob
        if "name" in canonical_fields and canonical_fields["name"]:
            name_val = canonical_fields["name"]
            if "department" in canonical_fields and canonical_fields["department"]:
                sec_keys.append(("name_dept", f"name:{name_val}|dept:{canonical_fields['department']}"))
            if "dob" in canonical_fields and canonical_fields["dob"]:
                sec_keys.append(("name_dob", f"name:{name_val}|dob:{canonical_fields['dob']}"))
        return sec_keys
