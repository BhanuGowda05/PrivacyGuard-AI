"""
test_modules.py - Automated Unit Testing for Module A & Module B
"""

import io
import datetime
import pypdf
import docx
from data_handler import (
    extract_text_from_file,
    validate_manual_entry,
    validate_email,
    validate_phone,
    validate_aadhaar,
    validate_pan,
    get_safe_demonstration_data,
    format_manual_entry_payload,
    stage_data_for_analysis
)

class MockUploadedFile:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data

def test_module_a():
    print("--- TESTING MODULE A: DOCUMENT UPLOAD ---")

    # 1. Plain text extraction
    txt_content = "Confidential Report:\nSubject: Jane Doe\nEmail: jane.doe@example.com\nCredit Card: 4532-1234-5678-9012"
    txt_file = MockUploadedFile("sample_notes.txt", txt_content.encode("utf-8"))
    res_txt = extract_text_from_file(txt_file)
    assert res_txt["success"] is True, f"TXT extraction failed: {res_txt['error']}"
    assert "jane.doe@example.com" in res_txt["text"]
    assert res_txt["metadata"]["word_count"] > 5
    print("✓ Plain text extraction passed.")

    # 2. In-memory DOCX extraction
    doc = docx.Document()
    doc.add_heading("Confidential Employee Record", level=1)
    doc.add_paragraph("Full Name: Rahul Verma")
    doc.add_paragraph("Aadhaar: 9876 5432 1098")
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Tax ID'
    hdr_cells[1].text = 'ABCDE9999Z'
    docx_buf = io.BytesIO()
    doc.save(docx_buf)
    docx_file = MockUploadedFile("employee.docx", docx_buf.getvalue())
    res_docx = extract_text_from_file(docx_file)
    assert res_docx["success"] is True, f"DOCX extraction failed: {res_docx['error']}"
    assert "Rahul Verma" in res_docx["text"]
    assert "ABCDE9999Z" in res_docx["text"]
    print("✓ DOCX extraction passed.")

    # 3. In-memory PDF extraction
    # We can create a simple PDF with pypdf or test error handling
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    pdf_buf = io.BytesIO()
    writer.write(pdf_buf)
    # Blank PDF check
    blank_pdf = MockUploadedFile("blank.pdf", pdf_buf.getvalue())
    res_blank = extract_text_from_file(blank_pdf)
    assert res_blank["success"] is False
    assert "No extractable text" in res_blank["error"]
    print("✓ Blank PDF graceful handling passed.")

    # 4. Empty file (0 bytes) check
    empty_file = MockUploadedFile("empty.txt", b"")
    res_empty = extract_text_from_file(empty_file)
    assert res_empty["success"] is False
    assert "empty" in res_empty["error"].lower()
    print("✓ Empty file detection passed.")

    # 5. Unsupported file format check
    bad_file = MockUploadedFile("image.png", b"\x89PNG\r\n\x1a\n...")
    res_bad = extract_text_from_file(bad_file)
    assert res_bad["success"] is False
    assert "Unsupported format" in res_bad["error"]
    print("✓ Unsupported format rejection passed.")

    # 6. Corrupted file handling
    corrupt_pdf = MockUploadedFile("damaged.pdf", b"NOT_A_REAL_PDF_HEADER_DATA")
    res_corrupt = extract_text_from_file(corrupt_pdf)
    assert res_corrupt["success"] is False
    print("✓ Corrupted file exception caught gracefully.")

def test_module_b():
    print("\n--- TESTING MODULE B: MANUAL PERSONAL DATA ENTRY ---")

    # 1. Format validators
    assert validate_email("user@domain.com") is True
    assert validate_email("invalid-email") is False

    assert validate_phone("+91 9876543210") is True
    assert validate_phone("123") is False

    is_valid_a, _ = validate_aadhaar("1234 5678 9012")
    assert is_valid_a is True
    is_valid_a_bad, _ = validate_aadhaar("1234")
    assert is_valid_a_bad is False

    is_valid_p, _ = validate_pan("ABCDE1234F")
    assert is_valid_p is True
    is_valid_p_bad, _ = validate_pan("12345ABCDE")
    assert is_valid_p_bad is False
    print("✓ Individual format validators passed.")

    # 2. Full manual validation with safe demo data
    demo_data = get_safe_demonstration_data()
    is_valid, errors = validate_manual_entry(demo_data)
    assert is_valid is True, f"Demo data should be valid, errors: {errors}"
    print("✓ Safe demonstration data validation passed.")

    # 3. Validation rejection with missing required fields
    invalid_data = {
        "full_name": "",
        "email": "not-an-email",
        "phone": "",
        "address": ""
    }
    is_valid_inv, errors_inv = validate_manual_entry(invalid_data)
    assert is_valid_inv is False
    assert "full_name" in errors_inv
    assert "email" in errors_inv
    assert "phone" in errors_inv
    assert "address" in errors_inv
    print("✓ Required field and invalid format enforcement passed.")

    # 4. Text payload compilation
    payload = format_manual_entry_payload(demo_data)
    assert "Subject Full Name: Aarav Sharma" in payload
    assert "aarav.sharma.sample@example.com" in payload
    assert "National ID (Aadhaar): 2345 6789 0123" in payload
    assert "Tax Identifier (PAN): ABCDE1234F" in payload
    print("✓ Structured text payload generation passed.")

    # 5. Staging data bridge
    staged = stage_data_for_analysis(
        source_type="Manual Data Entry",
        title="Record: Aarav Sharma",
        raw_text=payload,
        metadata={"subject": "Aarav Sharma"}
    )
    assert staged["source"] == "Manual Data Entry"
    assert staged["metadata"]["word_count"] > 10
    assert staged["metadata"]["character_count"] > 50
    assert staged["status"] == "Ready for AI Analysis"
    print("✓ Staging data bridge passed.")

if __name__ == "__main__":
    test_module_a()
    test_module_b()
    print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
