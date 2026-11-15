"""
test_detector.py - Synthetic Test Suite for Step 3 Sensitive Data Detection Engine
"""

from detector import detect_sensitive_data

def test_sensitive_detection():
    print("--- TESTING STEP 3: SENSITIVE DATA DETECTION ENGINE ---")

    # Synthetic test payload with all target categories
    synthetic_payload = (
        "EMPLOYEE PRIVACY AUDIT RECORD\n"
        "Full Name: Vikramaditya Singhania\n"
        "Email Address: vikram.singhania.test@enterprise-cyber.org\n"
        "Mobile Phone: +91 98765 12345\n"
        "Alternative Contact: (555) 789-0123\n"
        "Aadhaar Number: 4567 8901 2345\n"
        "Permanent Account Number (PAN): ABCDE5678G\n"
        "Date of Birth: 1988-11-24\n"
        "Residential Address: Flat 101, Palm Grove, Sector 15, Gurgaon, Haryana 122001\n"
        "Corporate Card: 4111 2222 3333 4444\n"
        "Service Secret: api_key = 'sk_live_99887766554433221100aa'\n"
    )

    result = detect_sensitive_data(synthetic_payload)

    print(f"Total Detections: {result['total_detections']}")
    print(f"Assessed Risk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}")

    # 1. Total detections assertion
    assert result["total_detections"] >= 7, f"Expected at least 7 detections, got {result['total_detections']}"

    # 2. Check each target category
    detected_categories = set(result["category_summary"].keys())
    print("Detected Categories:", detected_categories)

    assert "FULL_NAME" in detected_categories, "Missing Full Name detection"
    assert "EMAIL" in detected_categories, "Missing Email detection"
    assert "PHONE" in detected_categories, "Missing Phone detection"
    assert "AADHAAR_PATTERN" in detected_categories, "Missing Aadhaar Pattern detection"
    assert "PAN_PATTERN" in detected_categories, "Missing PAN Pattern detection"
    assert "DOB" in detected_categories, "Missing Date of Birth detection"
    assert "ADDRESS" in detected_categories, "Missing Address detection"

    # 3. Check individual values and offsets
    detections = result["detections"]
    for det in detections:
        # Verify slice matches text exactly
        sliced = synthetic_payload[det["start"]:det["end"]]
        assert sliced == det["text"] or sliced.strip() == det["text"].strip(), (
            f"Offset mismatch for {det['category']}: slice '{sliced}' != '{det['text']}'"
        )
        print(f"✓ [{det['category']}] '{det['text']}' at [{det['start']}:{det['end']}] ({det['confidence']})")

    # 4. Check Risk Level
    assert "Critical" in result["risk_level"], "Aadhaar/PAN/Card should trigger Critical Exposure Risk"

    # 5. Check Highlighted HTML contains tags
    html_output = result["highlighted_html"]
    assert "<mark" in html_output
    assert "FULL NAME" in html_output or "Full Name" in html_output
    assert "EMAIL" in html_output or "Email" in html_output

    # 6. Test Safe Empty Text
    safe_result = detect_sensitive_data("This is a completely public description of python algorithms.")
    assert safe_result["total_detections"] == 0
    assert "Safe" in safe_result["risk_level"]
    print("✓ Safe non-PII text correctly evaluated.")

    print("\n🎉 ALL DETECTION ENGINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_sensitive_detection()
