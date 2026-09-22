# Duplicate Record Detection Using Hashing Technique

**Anna University Regulation 2025 | B.E. Computer Science and Engineering**  
**Course:** Data Structures (CS25C08/ R2025 Laboratory & Mini-Project)  
**Title:** *Duplicate Record Detection Using Hashing Technique with Separate Chaining*

---

## 1. Abstract & Problem Statement

In contemporary data-intensive environments (academic registries, hospital archives, enterprise customer relation databases), massive amounts of heterogeneous records are ingested from diverse sources such as spreadsheets (Excel, CSV, TSV), API payloads (JSON, JSON Lines), scanned administrative forms (PDF), and text documents (Word DOCX, plain text).

Traditional record comparison algorithms operate with **O(n²)** worst-case time complexity, comparing each record against every other record. Sorting-based approaches require **O(n log n)** operations and struggle with multi-attribute, cross-schema matching. 

This project implements an **academic-grade, production-ready Data Structures solution** that achieves **O(1) average-case insertion and lookup time** (overall **O(n)** deduplication) utilizing **Custom Hash Tables with Separate Chaining** collision resolution, automated schema normalization via canonical mapping, and multi-tier fuzzy/partial collision detection.

---

## 2. Key Features

- **Custom Hashing Engine:**
  - **Polynomial Rolling Hash:** $H(s) = \left(\sum_{i=0}^{k-1} s[i] \cdot 31^i\right) \pmod{2^{32}}$
  - **DJB2 Hash:** Bitwise hash function ($hash \times 33 + char$)
  - **FNV-1a Hash:** 32-bit Fowler–Noll–Vo prime XOR folding
- **Collision Resolution via Separate Chaining:**
  - Singly linked list nodes allocated dynamically at each array bucket.
  - Comprehensive collision metrics tracking (empty buckets, occupied buckets, max chain length, average chain length, total collisions).
  - Dynamic rehashing mechanism when load factor $\alpha = \frac{N}{M}$ exceeds threshold ($0.75$).
- **Multi-Format Document Ingestion:**
  - Automated detection and parsing for **CSV**, **TSV**, **Excel (.xlsx, .xls)**, **JSON**, **JSON Lines (.jsonl)**, **PDF documents**, **Word documents (.docx)**, and **Plain Text (.txt)**.
- **Heterogeneous Schema Normalization:**
  - Canonical header mapping (`student_name`, `full_name`, `customer_name` $\rightarrow$ `name`).
  - Whitespace collapsing, case folding, phone sanitization (country code and delimiter removal).
  - Order-independent composite primary key generation.
- **Hierarchical Duplication Tiers:**
  - **Exact Duplicates:** 100% hash key identity.
  - **Partial Duplicates:** Shared identifiers (email, phone, student roll code) with differing secondary fields.
  - **Possible Duplicates:** Near-match edit similarity.
- **Interactive Academic Web Dashboard:**
  - Visual hash table bucket arrays with connected chain nodes.
  - Mathematical character-by-character hash trace simulator for viva voce demonstrations.
  - One-click sample dataset loader and project ZIP exporter.

---

## 3. System Architecture

```text
[Input Files: CSV / TSV / XLSX / JSON / PDF / DOCX / TXT]
                         │
                         ▼
             ┌───────────────────────┐
             │     ParserManager     │
             │ Format Sniffer & Parse│
             └───────────┬───────────┘
                         │ Raw Record Dicts
                         ▼
             ┌───────────────────────┐
             │      FieldMapper      │
             │ Canonical Header Maps │
             └───────────┬───────────┘
                         │ Canonical Dicts
                         ▼
             ┌───────────────────────┐
             │   RecordNormalizer    │
             │ Case / Whitespace /   │
             │ Order-Independent Key │
             └───────────┬───────────┘
                         │ Normalized Hash Key: "dept:cse|email:arun@gmail.com|name:arun"
                         ▼
             ┌────────────────────────────────────────────────────────┐
             │       DuplicateDetector (Multi-Tier Hashing)           │
             │                                                        │
             │  ┌──────────────────────────────────────────────────┐  │
             │  │   Primary Hash Table (Separate Chaining)         │  │
             │  │   Bucket [H(key) % M] -> Node 1 -> Node 2        │  │
             │  └──────────────────────────────────────────────────┘  │
             │                                                        │
             │  ┌──────────────────────────────────────────────────┐  │
             │  │   Secondary Identifier Hash Tables               │  │
             │  │   EmailTable | PhoneTable | RollNumberTable      │  │
             │  └──────────────────────────────────────────────────┘  │
             └───────────┬────────────────────────────────────────────┘
                         │
                         ▼
        ┌───────────────────────────────────┐
        │        Analysis Summary           │
        │ - Master Unique Records           │
        │ - Duplicate Groups with Reason    │
        │ - Bucket Chains & Collision Trace │
        └───────────────────────────────────┘
```

---

## 4. Complexity Analysis

| Operation / Algorithm | Best Case | Average Case | Worst Case | Space Complexity |
| :--- | :---: | :---: | :---: | :---: |
| **Hash Value Computation $H(s)$** | $O(k)$ | $O(k)$ | $O(k)$ | $O(1)$ |
| **Hash Table Insertion** | $O(1)$ | $O(1 + \alpha)$ | $O(N)$ (all collide) | $O(1)$ per node |
| **Hash Table Search / Lookup** | $O(1)$ | $O(1 + \frac{\alpha}{2})$ | $O(N)$ | $O(1)$ |
| **Overall Hashing Deduplication** | $O(N \cdot k)$ | **$O(N \cdot k)$** | $O(N^2 \cdot k)$ | $O(N + M)$ |
| **Brute Force (Nested Loop)** | $O(N^2 \cdot k)$ | $O(N^2 \cdot k)$ | $O(N^2 \cdot k)$ | $O(1)$ |
| **Sorting-Based Deduplication** | $O(N \log N \cdot k)$ | $O(N \log N \cdot k)$ | $O(N \log N \cdot k)$ | $O(N)$ |

*Where $N$ is the number of records, $M$ is the number of hash table buckets, $\alpha = \frac{N}{M}$ is the load factor, and $k$ is the average composite string key length.*

---

## 5. Project Directory Structure

```text
duplicate-record-detection/
├── app.py                      # Flask Application Server Entry Point
├── config.py                   # System Constants, Prime Capacities, and Paths
├── requirements.txt            # Python Dependencies
├── README.md                   # Academic Documentation & Viva Guide
│
├── models/                     # Core Data Structure Entities
│   ├── __init__.py
│   └── record.py               # Record, HashTrace, and DuplicateGroup Models
│
├── normalizer/                 # Schema & Value Normalization
│   ├── __init__.py
│   ├── field_mapper.py         # Canonical Field Dictionary Mapping
│   └── record_normalizer.py    # Order-Independent Composite Key Generator
│
├── hashing/                    # Academic Hashing Implementations
│   ├── __init__.py
│   ├── hash_functions.py       # Polynomial Rolling Hash, DJB2, FNV-1a
│   ├── hash_table.py           # HashTable with Separate Chaining (Linked Lists)
│   └── duplicate_detector.py   # Multi-Tier Duplicate Detection Engine
│
├── parser/                     # Multi-Format Ingestion Parsers
│   ├── __init__.py
│   ├── parser_manager.py       # Format Sniffer & Multi-File Coordinator
│   ├── csv_parser.py           # RFC 4180 CSV Parser
│   ├── tsv_parser.py           # Tab-Separated Values Parser
│   ├── json_parser.py          # JSON Array & Object Parser
│   ├── jsonl_parser.py         # JSON Lines / NDJSON Parser
│   ├── excel_parser.py         # Excel Workbook Parser (.xlsx & .xls)
│   ├── pdf_parser.py           # PDF Text & Key-Value Extractor
│   ├── docx_parser.py          # Word Document Table & Text Extractor
│   └── text_parser.py          # Delimited & Key-Value Plain Text Parser
│
├── backend/                    # Web Application Controller
│   ├── __init__.py
│   ├── routes.py               # REST API Routes & Endpoints
│   └── services.py             # Analysis Service & Session Cache
│
├── templates/                  # Frontend HTML Views
│   └── index.html              # Responsive Academic Dashboard
│
├── static/                     # Assets & Modular Client Scripts
│   ├── css/
│   │   └── style.css           # Clean, High-Contrast UI Styling
│   └── js/
│       ├── app.js              # Application Controller & Tab Navigation
│       ├── upload.js           # Drag & Drop File Upload Manager
│       ├── dashboard.js        # Metrics, Tables, and Pagination
│       └── visualization.js    # Interactive Bucket Array & Trace Visualizer
│
├── sample_data/                # Built-in Heterogeneous Evaluation Datasets
│   ├── students.csv            # Student Records with Exact & Whitespace Duplicates
│   ├── employees.tsv           # Differing Field Names (emp_id, mail_id)
│   ├── customers.json          # JSON Customer Records with Phone Formats
│   ├── records.jsonl           # JSONL Stream Records
│   ├── students_register.xlsx  # Excel Spreadsheet with Register Numbers
│   ├── records.docx            # Word Document with Student Table
│   ├── report.pdf              # PDF Administrative Report
│   └── data.txt                # Plain Text Formatted Record Cards
│
├── tests/                      # Automated Verification Test Suite
│   ├── __init__.py
│   ├── test_hashing.py         # Hash Functions & Collision Resolution Tests
│   ├── test_normalizer.py      # Schema Mapping & Cleaning Tests
│   ├── test_parser.py          # Format Parser Tests
│   └── test_duplicate_detection.py # Exact & Cross-Schema Detection Tests
│
└── utils/                      # Helper Utilities
    ├── __init__.py
    ├── file_utils.py           # Sanitization & Project ZIP Packager
    └── statistics.py           # Academic Performance Calculations
```

---

## 6. Local Setup and Execution Guide

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12
- `pip` package manager
- Visual Studio Code (recommended) or any modern terminal

### Step 1: Clone or Extract the Project
Open terminal or PowerShell in the project directory:
```bash
cd duplicate-record-detection
```

### Step 2: Create a Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Automated Test Suite
Verify that all unit tests for hashing, normalization, parsers, and duplicate detection pass:
```bash
pytest -v tests/
```
Expected output:
```text
============================== 16 passed in 0.08s ==============================
```

### Step 5: Start the Web Application
```bash
python app.py
```
Open your web browser and navigate to:
```text
http://localhost:3000
```

---

## 7. How to Use the Application for Demonstration

1. **One-Click Instant Demo:**
   - Click the **"Load Sample Datasets"** button on the top-right header.
   - The application automatically ingests all 8 heterogeneous files (`.csv`, `.tsv`, `.json`, `.jsonl`, `.xlsx`, `.docx`, `.pdf`, `.txt`), parses 51 records, detects 24 duplicates, and populates the dashboard metrics instantly.
2. **Inspect Duplicate Groups:**
   - Click the **"Duplicate Groups"** tab.
   - View grouped duplicate records alongside their master/primary record, matched identifying attributes, and confidence score.
3. **Interactive Hash Table Visualization:**
   - Switch to the **"Hashing Visualization"** tab.
   - Examine the array of hash buckets (Buckets 0 to 50).
   - Observe how buckets with multiple items display linked list nodes joined by collision arrows.
   - Select any record in the dropdown simulator to watch the step-by-step mathematical trace ($H(s)$ calculation, modulo arithmetic, bucket index, and chain traversal).
4. **Custom File Ingestion:**
   - Go to the **"Upload & Datasets"** tab.
   - Drag and drop your own CSV, Excel, or JSON files.
   - Click **"Run Duplicate Analysis"** to execute detection on your custom records.
5. **Download Complete Project:**
   - Click the **"Download Project ZIP"** button to export `duplicate-record-detection-hashing.zip` for submission or GitHub repository upload.

---

## 8. Anna University Viva Voce Preparation Guide

### Q1: Why is Separate Chaining preferred over Open Addressing (Linear Probing)?
**Answer:**
Separate chaining handles high load factors gracefully without primary clustering. When collisions occur in open addressing, deleted records leave "tombstones", and clusters grow, rapidly degrading lookup times to $O(n)$. With separate chaining, even if the table temporarily exceeds capacity ($N > M$), average lookup remains $O(1 + \alpha)$ where $\alpha = \frac{N}{M}$.

### Q2: What is the role of prime numbers in Hash Table capacity?
**Answer:**
Using a prime table size ($M \in \{31, 53, 101, 211, 401\}$) ensures that keys with patterns or common divisors do not repeatedly collide into a small subset of buckets. In the modulo operation $H(s) \pmod M$, a prime $M$ minimizes common factors with the hash function's multiplier base ($p=31$), ensuring uniform distribution across all buckets.

### Q3: How do you detect duplicates across files with completely different column names?
**Answer:**
We use a two-step normalization pipeline:
1. `FieldMapper` utilizes a dictionary of aliases to map varied field headers (e.g., `student_name`, `full_name`, `customer_name`, `emp_name`) to a single standardized canonical key (`name`).
2. `RecordNormalizer` cleans values (lowercasing, whitespace trimming, phone prefix removal) and sorts the canonical keys alphabetically to construct a deterministic, order-independent composite hash key (`email:...|name:...|phone:...`).

### Q4: What happens if a duplicate record has a missing phone number or different address?
**Answer:**
The system uses a **multi-tier hashing strategy**:
- **Tier 1 (Exact):** Primary composite hash table matches records with identical complete profiles.
- **Tier 2 (Partial):** Secondary hash tables indexed on strong unique keys (canonical email, canonical phone, register ID) capture cross-schema duplicates where auxiliary fields are missing or renamed.
- **Tier 3 (Possible):** Normalized token overlap identifies variations such as abbreviation of names.

---

## 9. Contributors & Acknowledgements

- **Student Developer:** B.E. Computer Science and Engineering, 2nd Year
- **Academic Regulation:** Anna University Regulation 2025
- **Department:** Department of Computer Science and Engineering
