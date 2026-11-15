"""
test_risk.py - Unit Tests for Privacy Risk Assessment Engine (Step 4)
Tests Low (0-30), Medium (31-60), and High (61-100) risk scenarios.
"""

from detector import detect_sensitive_data
from risk_assessment import calculate_privacy_risk

def test_low_risk_scenario():
    print("--- 1. TESTING LOW RISK SCENARIO (0 - 30) ---")
    # Low risk: Single email address in public discussion
    text = "For inquiries regarding the open-source software, contact support@example-org.io"
    res = detect_sensitive_data(text)
    risk = calculate_privacy_risk(res["detections"])
    
    print(f"Detections: {len(res['detections'])}")
    print(f"Risk Score: {risk['score']}/100")
    print(f"Risk Tier: {risk['tier']}")
    
    assert 0 <= risk["score"] <= 30, f"Expected Low Risk (0-30), got {risk['score']}"
    assert risk["tier"] == "Low Risk"
    assert risk["color"] == "#10B981"
    print("✓ Low Risk scenario passed.\n")

def test_medium_risk_scenario():
    print("--- 2. TESTING MEDIUM RISK SCENARIO (31 - 60) ---")
    # Medium risk: Name + Phone number (Contact + Identity correlation bonus: 12 + 14 + 10 = 36 pts)
    text = "Meeting summary for client contact: Name: Rahul Verma, direct mobile +91 98765 43210."
    res = detect_sensitive_data(text)
    risk = calculate_privacy_risk(res["detections"])
    
    print(f"Detections: {len(res['detections'])}")
    print(f"Risk Score: {risk['score']}/100")
    print(f"Risk Tier: {risk['tier']}")
    print(f"Compound Penalties: {[p['name'] for p in risk['compound_penalties']]}")
    
    assert 31 <= risk["score"] <= 60, f"Expected Medium Risk (31-60), got {risk['score']}"
    assert risk["tier"] == "Medium Risk"
    assert risk["color"] == "#F59E0B"
    print("✓ Medium Risk scenario passed.\n")

def test_high_risk_scenario():
    print("--- 3. TESTING HIGH RISK SCENARIO (61 - 100) ---")
    # High risk: Full name + National ID (Aadhaar) + PAN + Card + Address
    text = (
        "CONFIDENTIAL APPLICATION\n"
        "Full Name: Vikramaditya Singhania\n"
        "Aadhaar Number: 4567 8901 2345\n"
        "Permanent Account Number (PAN): ABCDE5678G\n"
        "Residential Address: Flat 101, Palm Grove, Sector 15, Gurgaon, Haryana 122001\n"
        "Corporate Card: 4111 2222 3333 4444\n"
    )
    res = detect_sensitive_data(text)
    risk = calculate_privacy_risk(res["detections"])
    
    print(f"Detections: {len(res['detections'])}")
    print(f"Risk Score: {risk['score']}/100")
    print(f"Risk Tier: {risk['tier']}")
    print(f"Compound Penalties Triggered: {len(risk['compound_penalties'])}")
    
    assert 61 <= risk["score"] <= 100, f"Expected High Risk (61-100), got {risk['score']}"
    assert risk["tier"] == "High Risk"
    assert risk["color"] == "#EF4444"
    assert len(risk["compound_penalties"]) >= 2
    assert len(risk["recommendations"]) >= 3
    print("✓ High Risk scenario passed.\n")

def test_empty_scenario():
    print("--- 4. TESTING ZERO EXPOSURE SCENARIO ---")
    risk = calculate_privacy_risk([])
    assert risk["score"] == 0
    assert risk["tier"] == "Low Risk"
    print("✓ Zero exposure scenario passed.\n")

if __name__ == "__main__":
    test_low_risk_scenario()
    test_medium_risk_scenario()
    test_high_risk_scenario()
    test_empty_scenario()
    print("🎉 ALL STEP 4 RISK ASSESSMENT TESTS PASSED SUCCESSFULLY!")
