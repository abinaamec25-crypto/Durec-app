"""
Intelligent Field Name Normalization & Mapping.
Solves heterogeneous schema challenges where records use different column names:
e.g. name, full_name, student_name, customer_name, employee_name -> canonical 'name'
"""
import re
from typing import Dict, List, Optional, Set


class FieldMapper:
    """
    Maps varied incoming field names from multiple heterogeneous sources
    to canonical semantic field identifiers.
    """

    DEFAULT_CANONICAL_MAPPINGS: Dict[str, List[str]] = {
        "name": [
            "name", "full_name", "fullname", "student_name", "studentname",
            "customer_name", "customername", "employee_name", "employeename",
            "user_name", "username", "first_name", "contact_name", "person_name",
            "candidate_name", "member_name", "client_name", "author"
        ],
        "email": [
            "email", "email_id", "emailid", "mail", "mail_id", "mailid",
            "e_mail", "email_address", "emailaddress", "contact_email",
            "student_email", "official_email", "personal_email"
        ],
        "phone": [
            "phone", "phone_number", "phonenumber", "phone_no", "phoneno",
            "mobile", "mobile_no", "mobileno", "mobile_number", "mobilenumber",
            "contact", "contact_no", "contactno", "contact_number", "tel",
            "telephone", "cell", "cell_phone", "cellphone"
        ],
        "department": [
            "department", "dept", "branch", "stream", "course", "major",
            "division", "faculty", "program", "discipline"
        ],
        "id_code": [
            "id", "roll_no", "rollno", "reg_no", "regno", "register_number",
            "registration_number", "student_id", "studentid", "emp_id", "empid",
            "employee_id", "customer_id", "user_id", "uid", "code", "enrollment_no"
        ],
        "dob": [
            "dob", "date_of_birth", "dateofbirth", "birth_date", "birthdate", "bday"
        ],
        "age": [
            "age", "years"
        ],
        "address": [
            "address", "addr", "location", "city", "residence", "street"
        ],
        "company": [
            "company", "organization", "org", "institution", "college", "university", "workplace"
        ],
        "gender": [
            "gender", "sex"
        ]
    }

    def __init__(self, custom_mappings: Optional[Dict[str, List[str]]] = None):
        self.mappings: Dict[str, List[str]] = dict(self.DEFAULT_CANONICAL_MAPPINGS)
        if custom_mappings:
            for canonical, aliases in custom_mappings.items():
                if canonical in self.mappings:
                    self.mappings[canonical].extend(aliases)
                else:
                    self.mappings[canonical] = list(aliases)
        self._reverse_lookup: Dict[str, str] = self._build_reverse_lookup()

    def _sanitize_name(self, name: str) -> str:
        """Sanitize field name: lowercase, strip, replace non-alphanumeric with underscores."""
        cleaned = name.strip().lower()
        cleaned = re.sub(r'[\s\-]+', '_', cleaned)
        cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
        return cleaned

    def _build_reverse_lookup(self) -> Dict[str, str]:
        lookup: Dict[str, str] = {}
        for canonical, aliases in self.mappings.items():
            canonical_clean = self._sanitize_name(canonical)
            lookup[canonical_clean] = canonical
            for alias in aliases:
                lookup[self._sanitize_name(alias)] = canonical
        return lookup

    def get_canonical_field(self, raw_field_name: str) -> str:
        """
        Translates a raw header/column name into its canonical equivalent.
        If no mapping is found, returns the cleaned version of the raw name.
        """
        sanitized = self._sanitize_name(raw_field_name)
        return self._reverse_lookup.get(sanitized, sanitized)

    def map_record_keys(self, raw_record: Dict[str, any]) -> Dict[str, any]:
        """
        Maps all keys of a dictionary to their canonical names.
        Preserves original values while unifying differing column names.
        """
        canonical_record: Dict[str, any] = {}
        for raw_key, value in raw_record.items():
            if raw_key is None:
                continue
            canonical_key = self.get_canonical_field(str(raw_key))
            # If canonical_key already exists, do not overwrite if new value is empty
            if canonical_key in canonical_record:
                if (value is not None and str(value).strip() != "") and (canonical_record[canonical_key] is None or str(canonical_record[canonical_key]).strip() == ""):
                    canonical_record[canonical_key] = value
            else:
                canonical_record[canonical_key] = value
        return canonical_record

    def get_all_canonical_fields(self) -> Set[str]:
        return set(self.mappings.keys())
