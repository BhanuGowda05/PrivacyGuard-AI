"""
test_masking_and_download.py - Comprehensive Unit Testing for Step 5 & Step 6
Tests all masking categories, reverse-index slicing, and TXT/DOCX/PDF generation.
"""

from detector import detect_sensitive_data
from masking import apply_masking, mask_single_value
from document_generator import (
    generate_protected_txt,
    generate_protected_docx,
    generate_protected_pdf
)

def test_individual_masking_rules():
    print("--- 1. TESTING INDIVIDUAL MASKING RULES ---")

    # Email
    assert mask_single_value("rahul@gmail.com", "EMAIL", mode="partial") == "r****@gmail.com"
    assert mask_single_value("rahul@gmail.com", "EMAIL", mode="full") == "[REDACTED: EMAIL]"
    print("✓ Email masking passed.")

    # Phone
    masked_phone = mask_single_value("9876543210", "PHONE", mode="partial")
    assert "3210" in masked_phone and "*" in masked_phone
    print("✓ Phone masking passed.")

    # Aadhaar
    masked_aadhaar = mask_single_value("1234 5678 9012", "AADHAAR_PATTERN", mode="partial")
    assert masked_aadhaar == "**** **** 9012"
    print("✓ Aadhaar masking passed.")

    # PAN
    masked_pan = mask_single_value("ABCDE1234F", "PAN_PATTERN", mode="partial")
    assert masked_pan == "*****1234*"
    print("✓ PAN masking passed.")

    # Name
    masked_name = mask_single_value("Rahul Sharma", "FULL_NAME", mode="partial")
    assert masked_name == "R**** S*****"
    assert mask_single_value("Rahul Sharma", "FULL_NAME", mode="full") == "[REDACTED: FULL_NAME]"
    print("✓ Name masking passed.")

    # Financial / Card
    masked_card = mask_single_value("4111 2222 3333 4444", "FINANCIAL_CRED", mode="partial")
    assert masked_card == "**** **** **** 4444"
    print("✓ Financial Card masking passed.")

    # Secret
    masked_sec = mask_single_value("sk_live_1234567890", "SECRET_KEY", mode="partial")
    assert "REDACTED" in masked_sec
    print("✓ Secret Key masking passed.")

def test_reverse_index_slicing_integrity():
    print("\n--- 2. TESTING REVERSE-INDEX SLICING INTEGRITY ---")

    text = (
        "CONFIDENTIAL AUDIT:\n"
        "Employee: Vikramaditya Singhania\n"
        "Email: vikram.singhania.test@enterprise-cyber.org\n"
        "Mobile: +91 98765 12345\n"
        "Aadhaar: 4567 8901 2345\n"
        "PAN: ABCDE5678G\n"
        "END OF RECORD."
    )

    det_res = detect_sensitive_data(text)
    detections = det_res["detections"]
    assert len(detections) >= 5

    # Apply partial masking
    mask_res = apply_masking(text, detections, default_mode="partial")

    protected = mask_res["protected_text"]
    print("Protected Output:\n", protected)

    # Assure non-sensitive text is untouched
    assert "CONFIDENTIAL AUDIT:" in protected
    assert "END OF RECORD." in protected
    assert "Employee:" in protected
    assert "Email:" in protected
    assert "Mobile:" in protected

    # Assure raw sensitive strings are scrubbed
    assert "vikram.singhania.test@enterprise-cyber.org" not in protected
    assert "4567 8901 2345" not in protected
    assert "ABCDE5678G" not in protected
    assert mask_res["masked_count"] >= 5
    print("✓ In-memory slicing correctly removed sensitive tokens without breaking structure.")

def test_document_generation():
    print("\n--- 3. TESTING DOCUMENT GENERATION (TXT, DOCX, PDF) ---")

    sample_protected_text = (
        "CONFIDENTIAL AUDIT:\n"
        "Employee: V**** S*****\n"
        "Email: v****@enterprise-cyber.org\n"
        "Mobile: ******2345\n"
        "Aadhaar: **** **** 2345\n"
        "PAN: *****5678*\n"
        "END OF RECORD."
    )
    metadata = {
        "timestamp": "2026-11-14 11:30:00",
        "masked_count": 5,
        "risk_score": 0,
        "source": "Sample_Audit.txt"
    }

    # 1. TXT Generation
    txt_bytes = generate_protected_txt(sample_protected_text, metadata)
    assert isinstance(txt_bytes, bytes)
    assert len(txt_bytes) > 100
    assert "PRIVACYGUARD" in txt_bytes.decode("utf-8")
    assert "V**** S*****" in txt_bytes.decode("utf-8")
    print(f"✓ TXT generated ({len(txt_bytes)} bytes).")

    # 2. DOCX Generation
    docx_bytes = generate_protected_docx(sample_protected_text, metadata)
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500
    # Check DOCX zip magic header (PK\x03\x04)
    assert docx_bytes[:4] == b"PK\x03\x04"
    print(f"✓ DOCX generated ({len(docx_bytes)} bytes).")

    # 3. PDF Generation
    pdf_bytes = generate_protected_pdf(sample_protected_text, metadata)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    # Check PDF magic header (%PDF)
    assert pdf_bytes[:4] == b"%PDF"
    print(f"✓ PDF generated ({len(pdf_bytes)} bytes).")

if __name__ == "__main__":
    test_individual_masking_rules()
    test_reverse_index_slicing_integrity()
    test_document_generation()
    print("\n🎉 ALL STEP 5 & STEP 6 TESTS PASSED SUCCESSFULLY!")
