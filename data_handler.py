"""
data_handler.py - In-memory parsing, format validation, and safe data staging
for PrivacyGuard (Step 2: Document Upload & Manual Data Entry)
"""

from __future__ import annotations
import os
import io
import re
import datetime
from typing import Dict, Any, Tuple, List, Optional

# In-memory document parsers
import pypdf
import docx

# Maximum permitted file size: 15 MB
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


# ---------------------------------------------------------------------------
# Module A: Document Extraction Engine
# ---------------------------------------------------------------------------

def human_readable_size(size_bytes: int) -> str:
    """Converts raw byte count into human-friendly string (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def extract_text_from_file(uploaded_file) -> Dict[str, Any]:
    """
    Parses PDF, DOCX, or TXT documents strictly in memory.
    Handles corrupted, empty, or password-protected files gracefully.
    """
    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    file_size = len(file_bytes)

    # 1. Size Validation
    if file_size > MAX_FILE_SIZE_BYTES:
        return {
            "success": False,
            "error": f"File exceeds maximum allowed size of 15MB ({human_readable_size(file_size)}).",
            "filename": filename,
            "file_size": human_readable_size(file_size),
            "file_type": filename.split(".")[-1].lower(),
            "text": "",
            "metadata": {}
        }

    if file_size == 0:
        return {
            "success": False,
            "error": "The uploaded file is empty (0 Bytes). Please upload a valid document.",
            "filename": filename,
            "file_size": human_readable_size(file_size),
            "file_type": filename.split(".")[-1].lower(),
            "text": "",
            "metadata": {}
        }

    # 2. Extension Validation
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported format (.{ext}). PrivacyGuard currently accepts .pdf, .txt, and .docx documents.",
            "filename": filename,
            "file_size": human_readable_size(file_size),
            "file_type": ext,
            "text": "",
            "metadata": {}
        }

    extracted_text = ""
    metadata = {}

    # 3. Processing by Extension
    try:
        if ext == "pdf":
            stream = io.BytesIO(file_bytes)
            try:
                reader = pypdf.PdfReader(stream)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Corrupted or invalid PDF file: {str(e)}",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": {}
                }

            # Check if password-protected / encrypted
            if reader.is_encrypted:
                return {
                    "success": False,
                    "error": "This PDF is encrypted or password-protected. Please provide an unlocked document.",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": {"encrypted": True}
                }

            page_texts = []
            num_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                try:
                    txt = page.extract_text()
                    if txt:
                        page_texts.append(txt)
                except Exception:
                    # Ignore single page extraction errors, continue with remaining
                    continue

            extracted_text = "\n\n".join(page_texts).strip()
            metadata = {
                "page_count": num_pages,
                "pages_with_text": len(page_texts)
            }

            if not extracted_text:
                return {
                    "success": False,
                    "error": "No extractable text found in this PDF (it might be a scanned image or empty). OCR integration is planned for future modules.",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": metadata
                }

        elif ext == "docx":
            stream = io.BytesIO(file_bytes)
            try:
                doc = docx.Document(stream)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Corrupted or unreadable DOCX document: {str(e)}",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": {}
                }

            # Extract paragraphs
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

            # Extract tables
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        table_texts.append(row_text)

            full_content = paragraphs + table_texts
            extracted_text = "\n".join(full_content).strip()
            metadata = {
                "paragraphs": len(paragraphs),
                "tables": len(doc.tables)
            }

            if not extracted_text:
                return {
                    "success": False,
                    "error": "The DOCX document is empty or contains no readable paragraphs.",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": metadata
                }

        elif ext == "txt":
            # Attempt decoding with UTF-8 first, fallback to Latin-1
            try:
                extracted_text = file_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                try:
                    extracted_text = file_bytes.decode("latin-1").strip()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Could not decode text file: {str(e)}",
                        "filename": filename,
                        "file_size": human_readable_size(file_size),
                        "file_type": ext,
                        "text": "",
                        "metadata": {}
                    }

            if not extracted_text:
                return {
                    "success": False,
                    "error": "The uploaded text file contains only whitespace or is empty.",
                    "filename": filename,
                    "file_size": human_readable_size(file_size),
                    "file_type": ext,
                    "text": "",
                    "metadata": {}
                }

            metadata = {
                "lines": len(extracted_text.splitlines())
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error while processing document: {str(e)}",
            "filename": filename,
            "file_size": human_readable_size(file_size),
            "file_type": ext,
            "text": "",
            "metadata": {}
        }

    # Word and character count computation
    words = len(extracted_text.split())
    chars = len(extracted_text)
    metadata["word_count"] = words
    metadata["character_count"] = chars

    return {
        "success": True,
        "error": None,
        "filename": filename,
        "file_size": human_readable_size(file_size),
        "file_type": ext.upper(),
        "text": extracted_text,
        "metadata": metadata
    }


def get_available_sample_documents() -> List[Dict[str, str]]:
    """Returns metadata for pre-loaded local demonstration documents."""
    return [
        {
            "filename": "Customer_KYC_Profile.pdf",
            "label": "📄 Customer_KYC_Profile.pdf (PDF Document)",
            "description": "KYC profile with Aadhaar, PAN, Name, Email, Address, Card data"
        },
        {
            "filename": "Employee_Health_Record.docx",
            "label": "📑 Employee_Health_Record.docx (Word Document)",
            "description": "Health intake with DOB, Doctor contact, National ID, Phone, Address"
        },
        {
            "filename": "Financial_Audit_Summary.txt",
            "label": "📝 Financial_Audit_Summary.txt (Plain Text)",
            "description": "Financial audit dossier with Banking, Credit Card, Multiple Phones, IDs"
        }
    ]


def load_sample_document(sample_filename: str) -> Dict[str, Any]:
    """Loads and extracts text from a local sample document."""
    filepath = os.path.join("sample_documents", sample_filename)
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error": f"Sample document '{sample_filename}' could not be located in local sample storage.",
            "filename": sample_filename,
            "file_size": "0 B",
            "file_type": sample_filename.split(".")[-1].upper(),
            "text": "",
            "metadata": {}
        }

    try:
        with open(filepath, "rb") as f:
            file_bytes = f.read()

        class LocalSampleUpload:
            def __init__(self, name: str, data: bytes):
                self.name = name
                self._data = data
                self.size = len(data)

            def getvalue(self) -> bytes:
                return self._data

        dummy_obj = LocalSampleUpload(sample_filename, file_bytes)
        return extract_text_from_file(dummy_obj)
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading sample file: {str(e)}",
            "filename": sample_filename,
            "file_size": "0 B",
            "file_type": sample_filename.split(".")[-1].upper(),
            "text": "",
            "metadata": {}
        }


# ---------------------------------------------------------------------------
# Module B: Manual Data Validation & Safe Sample Engine
# ---------------------------------------------------------------------------

def validate_email(email: str) -> bool:
    """Validates basic email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """Validates standard telephone number format (10-15 digits, optional + prefix)."""
    clean = re.sub(r"[\s\-\(\)]", "", phone.strip())
    pattern = r"^\+?[0-9]{10,15}$"
    return bool(re.match(pattern, clean))


def validate_aadhaar(aadhaar: str) -> Tuple[bool, str]:
    """
    Validates optional Indian Aadhaar card format (12 numeric digits).
    Accepts 1234 5678 9012 or 123456789012.
    """
    if not aadhaar.strip():
        return True, ""  # Optional field
    clean = re.sub(r"[\s\-]", "", aadhaar.strip())
    if not clean.isdigit():
        return False, "Aadhaar must contain numeric digits only."
    if len(clean) != 12:
        return False, "Aadhaar must be exactly 12 digits."
    return True, ""


def validate_pan(pan: str) -> Tuple[bool, str]:
    """
    Validates optional Indian PAN number format (5 uppercase letters, 4 digits, 1 uppercase letter).
    Example: ABCDE1234F
    """
    if not pan.strip():
        return True, ""  # Optional field
    clean = pan.strip().upper()
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    if not re.match(pattern, clean):
        return False, "Invalid PAN format. Standard format: 5 letters, 4 numbers, 1 letter (e.g., ABCDE1234F)."
    return True, ""


def validate_manual_entry(form_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Validates manual entry fields.
    Accepts any combination of entered personal identifiers as long as their
    syntactic format is valid, requiring at least one identifier to continue.
    Returns (is_valid, error_dict).
    """
    errors = {}

    name = form_data.get("full_name", "").strip()
    email = form_data.get("email", "").strip()
    phone = form_data.get("phone", "").strip()
    aadhaar = form_data.get("aadhaar", "").strip()
    pan = form_data.get("pan", "").strip()
    address = form_data.get("address", "").strip()
    other_info = form_data.get("other_info", "").strip()

    # Check that at least one personal data field is provided
    has_any_data = any([name, email, phone, aadhaar, pan, address, other_info])
    if not has_any_data:
        errors["general"] = "Please enter at least one piece of personal information before continuing."
        return False, errors

    # Format validation on fields that were provided
    if name and len(name) < 2:
        errors["full_name"] = "Full name should be at least 2 characters."

    if email and not validate_email(email):
        errors["email"] = "Please enter a valid email address (e.g., name@domain.com)."

    if phone and not validate_phone(phone):
        errors["phone"] = "Enter a valid phone number (10-15 digits, optional + country code)."

    if aadhaar:
        is_valid_aadhaar, aadhaar_err = validate_aadhaar(aadhaar)
        if not is_valid_aadhaar:
            errors["aadhaar"] = aadhaar_err

    if pan:
        is_valid_pan, pan_err = validate_pan(pan)
        if not is_valid_pan:
            errors["pan"] = pan_err

    return (len(errors) == 0), errors


def get_safe_demonstration_data() -> Dict[str, Any]:
    """
    Provides safe, synthetic demonstration values so users/evaluators
    never have to input actual personal or confidential credentials.
    """
    return {
        "full_name": "Aarav Sharma",
        "email": "aarav.sharma.sample@example.com",
        "phone": "+91 98765 43210",
        "aadhaar": "2345 6789 0123",
        "pan": "ABCDE1234F",
        "address": "Flat 402, Cyber Heights, Sector 62, Noida, UP, 201301",
        "dob": datetime.date(1992, 8, 15),
        "other_info": "Sample bank account: 00987654321, IFSC: HDFC0001234. Medical record: Blood Group O+, Allergy: Penicillin."
    }


def format_manual_entry_payload(form_data: Dict[str, Any]) -> str:
    """
    Compiles manual form entries into unified structured text representation
    for the downstream analysis and redaction pipeline.
    """
    lines = [
        "--- PERSONAL DATA IDENTIFIER RECORD ---",
        f"Subject Full Name: {form_data.get('full_name', '').strip()}",
        f"Primary Email: {form_data.get('email', '').strip()}",
        f"Contact Number: {form_data.get('phone', '').strip()}",
        f"Residential Address: {form_data.get('address', '').strip()}",
    ]

    if form_data.get("dob"):
        dob_val = form_data['dob'].strftime("%Y-%m-%d") if isinstance(form_data['dob'], (datetime.date, datetime.datetime)) else str(form_data['dob'])
        lines.append(f"Date of Birth: {dob_val}")

    if form_data.get("aadhaar", "").strip():
        lines.append(f"National ID (Aadhaar): {form_data['aadhaar'].strip()}")

    if form_data.get("pan", "").strip():
        lines.append(f"Tax Identifier (PAN): {form_data['pan'].strip().upper()}")

    other = form_data.get("other_info", "").strip()
    if other:
        lines.append("\nAdditional Personal & Confidential Details:")
        lines.append(other)

    lines.append("--- END OF RECORD ---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Common Data Pipeline Bridge
# ---------------------------------------------------------------------------

def stage_data_for_analysis(source_type: str, title: str, raw_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Packages document or manual input into standard staged data schema
    strictly maintained in memory.
    """
    words = len(raw_text.split())
    chars = len(raw_text)

    # Augment metadata
    meta = dict(metadata)
    meta["word_count"] = words
    meta["character_count"] = chars

    import hashlib
    norm = f"{source_type.strip().lower()}||{title.strip().lower()}||{raw_text.strip()}"
    fingerprint = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]

    return {
        "source": source_type,
        "title": title,
        "raw_text": raw_text,
        "metadata": meta,
        "fingerprint": fingerprint,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Ready for AI Analysis"
    }
