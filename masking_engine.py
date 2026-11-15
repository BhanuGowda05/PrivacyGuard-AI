"""
masking_engine.py - Automatic Personal Data Masking Engine for PrivacyGuard
Supports Full Redaction and Context-Preserving Partial Masking with offset-safe replacement
"""

import re
from typing import List, Dict, Any, Set, Tuple

# ---------------------------------------------------------------------------
# Individual Field Masking Implementations
# ---------------------------------------------------------------------------

def mask_email(email_str: str, mode: str = "partial") -> str:
    """
    Masks an email address.
    Full: [REDACTED_EMAIL]
    Partial: rahul.sharma@gmail.com -> r***********@gmail.com
    """
    if mode == "full":
        return "[REDACTED_EMAIL]"
    
    if "@" not in email_str:
        return "[REDACTED_EMAIL]"
    
    parts = email_str.split("@", 1)
    user, domain = parts[0], parts[1]
    
    if len(user) <= 1:
        masked_user = "*"
    elif len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        # Show first letter, star out the rest
        masked_user = user[0] + ("*" * (len(user) - 1))
        
    return f"{masked_user}@{domain}"


def mask_phone(phone_str: str, mode: str = "partial") -> str:
    """
    Masks telephone numbers.
    Full: [REDACTED_PHONE]
    Partial: 9876543210 -> ******3210 (preserves last 4 digits)
    """
    if mode == "full":
        return "[REDACTED_PHONE]"
    
    # Extract digits
    digits = re.findall(r"\d", phone_str)
    if len(digits) < 4:
        return "[REDACTED_PHONE]"
    
    # Keep last 4 digits, mask previous digits
    masked_digit_list = ["*"] * (len(digits) - 4) + digits[-4:]
    
    # Reconstruct preserving formatting structure (+, -, spaces)
    digit_idx = 0
    res = []
    for ch in phone_str:
        if ch.isdigit():
            res.append(masked_digit_list[digit_idx])
            digit_idx += 1
        else:
            res.append(ch)
            
    return "".join(res)


def mask_aadhaar(aadhaar_str: str, mode: str = "partial") -> str:
    """
    Masks 12-digit Indian Aadhaar number pattern.
    Full: [REDACTED_AADHAAR]
    Partial: 2345 6789 0123 -> XXXX XXXX 0123 (Masks first 8 digits in accordance with UIDAI)
    """
    if mode == "full":
        return "[REDACTED_AADHAAR]"
    
    digits = re.findall(r"\d", aadhaar_str)
    if len(digits) != 12:
        return "[REDACTED_AADHAAR]"
    
    masked_digits = ["X"] * 8 + digits[8:]
    digit_idx = 0
    res = []
    for ch in aadhaar_str:
        if ch.isdigit():
            res.append(masked_digits[digit_idx])
            digit_idx += 1
        else:
            res.append(ch)
            
    return "".join(res)


def mask_pan(pan_str: str, mode: str = "partial") -> str:
    """
    Masks 10-character Indian PAN number pattern (e.g. ABCDE1234F).
    Full: [REDACTED_PAN]
    Partial: ABCDE1234F -> ABCXXXX34F or ******1234F
    """
    if mode == "full":
        return "[REDACTED_PAN]"
    
    clean = pan_str.strip()
    if len(clean) != 10:
        return "[REDACTED_PAN]"
    
    # Mask first 5 letters and show last 4 chars, or mask middle
    return clean[:3] + "XXXX" + clean[-3:]


def mask_name(name_str: str, mode: str = "partial") -> str:
    """
    Masks personal full names.
    Full: [REDACTED_NAME]
    Partial: Rahul Sharma -> R**** S*****
    """
    if mode == "full":
        return "[REDACTED_NAME]"
    
    words = name_str.split()
    masked_words = []
    for w in words:
        if len(w) <= 1:
            masked_words.append(w)
        else:
            masked_words.append(w[0] + ("*" * (len(w) - 1)))
            
    return " ".join(masked_words)


def mask_address(address_str: str, mode: str = "partial") -> str:
    """
    Masks residential addresses and physical coordinates.
    Full: [REDACTED_ADDRESS]
    Partial: Retains city/state if available, redacts street/flat
    """
    if mode == "full":
        return "[REDACTED_ADDRESS]"
    
    # If contains commas, retain the last regional components (e.g. Noida, UP)
    parts = [p.strip() for p in address_str.split(",") if p.strip()]
    if len(parts) >= 3:
        # Redact specific house/street, keep city/state
        return "[REDACTED STREET/UNIT], " + ", ".join(parts[-2:])
    
    return "[REDACTED_ADDRESS]"


def mask_dob(dob_str: str, mode: str = "partial") -> str:
    """
    Masks date of birth.
    Full: [REDACTED_DOB]
    Partial: 1992-08-15 -> ****-**-15 (masks birth year and month)
    """
    if mode == "full":
        return "[REDACTED_DOB]"
    
    # Try ISO YYYY-MM-DD
    if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$", dob_str.strip()):
        sep = "-" if "-" in dob_str else "/"
        parts = dob_str.strip().split(sep)
        return f"****{sep}**{sep}{parts[2]}"
    
    # Try DD-MM-YYYY
    if re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$", dob_str.strip()):
        sep = "-" if "-" in dob_str else "/"
        parts = dob_str.strip().split(sep)
        return f"{parts[0]}{sep}**{sep}****"
        
    return "[REDACTED_DOB]"


def mask_financial(card_str: str, mode: str = "partial") -> str:
    """
    Masks credit/debit card numbers.
    Full: [REDACTED_CARD]
    Partial: 4111 2222 3333 4444 -> **** **** **** 4444
    """
    if mode == "full":
        return "[REDACTED_CARD]"
        
    digits = re.findall(r"\d", card_str)
    if len(digits) < 4:
        return "[REDACTED_CARD]"
        
    masked_digits = ["*"] * (len(digits) - 4) + digits[-4:]
    digit_idx = 0
    res = []
    for ch in card_str:
        if ch.isdigit():
            res.append(masked_digits[digit_idx])
            digit_idx += 1
        else:
            res.append(ch)
            
    return "".join(res)


def mask_secret(secret_str: str, mode: str = "partial") -> str:
    """
    Masks secret credentials and API tokens.
    Always irreversible.
    """
    return "[REDACTED_SECRET]"


# Dispatch table for category masking
MASK_DISPATCH = {
    "EMAIL": mask_email,
    "PHONE": mask_phone,
    "AADHAAR_PATTERN": mask_aadhaar,
    "PAN_PATTERN": mask_pan,
    "FULL_NAME": mask_name,
    "ADDRESS": mask_address,
    "DOB": mask_dob,
    "FINANCIAL_CRED": mask_financial,
    "SECRET_KEY": mask_secret,
}


# ---------------------------------------------------------------------------
# Core Document Masking Controller
# ---------------------------------------------------------------------------

def mask_text_payload(
    original_text: str,
    detections: List[Dict[str, Any]],
    selected_categories: Set[str],
    category_modes: Dict[str, str] = None,
    default_mode: str = "partial"
) -> Dict[str, Any]:
    """
    Applies sanitization to original text based on selected categories.
    Sorts detections in reverse order of character offsets (from end to start)
    so replacements do not shift earlier character spans.
    """
    if not original_text or not detections:
        return {
            "original_text": original_text,
            "protected_text": original_text,
            "total_detected": len(detections),
            "masked_count": 0,
            "unmasked_count": 0,
            "masked_items": [],
            "unmasked_items": [],
            "sanitization_ratio": 100.0 if not detections else 0.0
        }

    category_modes = category_modes or {}

    # Filter detections to process
    target_detections = []
    unmasked_detections = []

    for d in detections:
        cat = d.get("category", "")
        if cat in selected_categories:
            target_detections.append(d)
        else:
            unmasked_detections.append(d)

    # Sort descending by start position to prevent offset shift
    # If start is equal, longer span is processed first
    sorted_targets = sorted(
        target_detections,
        key=lambda x: (x["start"], x["end"]),
        reverse=True
    )

    # Perform in-memory string replacement from back to front
    protected_chars = list(original_text)
    masked_records = []
    last_processed_start = len(original_text) + 1

    for det in sorted_targets:
        s = det["start"]
        e = det["end"]
        cat = det["category"]
        raw_val = det["text"]

        # Prevent overlapping collision
        if e > last_processed_start:
            # Overlaps with an already replaced span further down; skip
            continue

        # Determine masking mode for this category
        mode = category_modes.get(cat, default_mode)

        # Apply specific mask function
        mask_fn = MASK_DISPATCH.get(cat, lambda val, m: "[REDACTED]")
        masked_val = mask_fn(raw_val, mode)

        # Splice into string
        protected_chars[s:e] = list(masked_val)
        last_processed_start = s

        masked_records.append({
            "category": cat,
            "label": det.get("label", cat),
            "original_length": e - s,
            "mode": mode,
            "masked_replacement": masked_val
        })

    protected_text = "".join(protected_chars)
    masked_count = len(masked_records)
    unmasked_count = len(unmasked_detections)
    total = len(detections)
    ratio = (masked_count / total * 100.0) if total > 0 else 100.0

    return {
        "original_text": original_text,
        "protected_text": protected_text,
        "total_detected": total,
        "masked_count": masked_count,
        "unmasked_count": unmasked_count,
        "masked_items": masked_records,
        "unmasked_items": unmasked_detections,
        "sanitization_ratio": round(ratio, 1)
    }
