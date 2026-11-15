"""
masking.py - Automatic Personal Data Masking Module for PrivacyGuard
Supports Full Masking ([REDACTED]) and Partial Contextual Masking
Processes in-memory via reverse-index slicing to guarantee exact position replacement
"""

import re
import datetime
from typing import List, Dict, Any, Tuple


# ---------------------------------------------------------------------------
# Individual Value Masking Rules
# ---------------------------------------------------------------------------

def mask_single_value(value: str, category: str, mode: str = "partial") -> str:
    """
    Applies either full redaction or contextual partial masking to a detected token.
    
    Modes:
      - "full": [REDACTED] or [REDACTED: CATEGORY]
      - "partial":
          - Email: rahul@gmail.com -> r*****@gmail.com
          - Phone: 9876543210 -> ******3210
          - Aadhaar: 1234 5678 9012 -> **** **** 9012
          - PAN: ABCDE1234F -> *****1234F
          - Financial: 4111 2222 3333 4444 -> **** **** **** 4444
          - Name: Rahul Sharma -> R**** S*****
          - Address: Flat 101, Sector 15... -> [REDACTED: ADDRESS]
          - DOB: 1992-08-15 -> ****-**-**
          - Secrets: -> [REDACTED: CREDENTIAL]
    """
    val = value.strip()
    if not val:
        return "[REDACTED]"

    if mode == "full":
        cat_clean = category.replace("_PATTERN", "").replace("_CRED", "")
        return f"[REDACTED: {cat_clean}]"

    # PARTIAL MASKING LOGIC
    if category == "EMAIL":
        if "@" in val:
            user_part, domain_part = val.split("@", 1)
            if len(user_part) <= 1:
                masked_user = "*"
            elif len(user_part) <= 2:
                masked_user = user_part[0] + "*"
            else:
                masked_user = user_part[0] + ("*" * (len(user_part) - 1))
            return f"{masked_user}@{domain_part}"
        return val[0] + ("*" * (len(val) - 1))

    elif category == "PHONE":
        # Keep country code if present, mask middle, show last 4 digits
        digits = re.findall(r"\d", val)
        if len(digits) >= 10:
            last4 = "".join(digits[-4:])
            masked_prefix = "*" * (len(digits) - 4)
            # If standard formatting with space/dash, return standard format
            return f"{masked_prefix}{last4}"
        elif len(val) > 4:
            return ("*" * (len(val) - 4)) + val[-4:]
        return "*" * len(val)

    elif category == "AADHAAR_PATTERN":
        # Indian Aadhaar: Mask first 8 digits, show last 4 digits
        digits = re.sub(r"[\s-]", "", val)
        if len(digits) == 12:
            last4 = digits[-4:]
            return f"**** **** {last4}"
        return "**** **** ****"

    elif category == "PAN_PATTERN":
        # Indian PAN (10 chars): Mask first 5 alphabets, show 4 digits, mask last letter
        clean = val.replace(" ", "")
        if len(clean) == 10:
            return f"*****{clean[5:9]}*"
        return "**********"

    elif category == "FINANCIAL_CRED":
        # Credit Card: Keep last 4 digits visible
        digits = re.findall(r"\d", val)
        if len(digits) >= 12:
            last4 = "".join(digits[-4:])
            return f"**** **** **** {last4}"
        return "**** **** **** ****"

    elif category == "FULL_NAME":
        # Name: Keep initial of each word, mask rest (e.g. Rahul Sharma -> R**** S*****)
        words = val.split()
        masked_words = []
        for w in words:
            if len(w) <= 1:
                masked_words.append(w)
            else:
                masked_words.append(w[0] + ("*" * (len(w) - 1)))
        return " ".join(masked_words) if masked_words else "[REDACTED: NAME]"

    elif category == "DOB":
        # Date of birth: Mask year and month or full numbers
        return re.sub(r"\d", "*", val)

    elif category == "ADDRESS":
        # Addresses are coarse-grained; full masking preserves physical safety
        return "[REDACTED: RESIDENTIAL ADDRESS]"

    elif category == "SECRET_KEY":
        return "[REDACTED: API CREDENTIAL]"

    else:
        # Fallback default masking
        if len(val) > 4:
            return val[:2] + ("*" * (len(val) - 4)) + val[-2:]
        return "[REDACTED]"


# ---------------------------------------------------------------------------
# Core Slicing Engine (Reverse-Index Substitution)
# ---------------------------------------------------------------------------

def apply_masking(
    original_text: str,
    detections: List[Dict[str, Any]],
    enabled_categories: List[str] = None,
    default_mode: str = "partial",
    category_modes: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Masks sensitive items in text using exact character offsets [start:end].
    
    IMPORTANT TECHNICAL GUARANTEE:
    Substitutions are processed in REVERSE order (from highest start index to lowest).
    This ensures that replacing a substring with a replacement of different length
    never shifts or invalidates the character offsets of preceding detections!
    """
    if not original_text:
        return {
            "original_text": "",
            "protected_text": "",
            "total_detected": 0,
            "masked_count": 0,
            "unmasked_count": 0,
            "masked_items": [],
            "unmasked_items": [],
            "applied_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    category_modes = category_modes or {}
    
    # If no category filter specified, enable all
    if enabled_categories is None:
        enabled_categories = list({d["category"] for d in detections})

    # Partition detections into to-mask and unmasked
    to_mask = []
    unmasked = []

    for d in detections:
        cat = d.get("category", "")
        if cat in enabled_categories:
            to_mask.append(d)
        else:
            unmasked.append(d)

    # Sort descending by start position to prevent index offset disruption
    to_mask.sort(key=lambda x: x["start"], reverse=True)

    protected_chars = list(original_text)
    masked_items_summary = []

    for det in to_mask:
        s = det["start"]
        e = det["end"]
        raw_val = original_text[s:e]
        cat = det["category"]

        # Determine mode for this category
        mode = category_modes.get(cat, default_mode)
        masked_val = mask_single_value(raw_val, cat, mode=mode)

        # Substitute in string buffer
        protected_chars[s:e] = list(masked_val)

        masked_items_summary.append({
            "original": raw_val,
            "masked": masked_val,
            "category": cat,
            "mode": mode,
            "span": f"[{s}:{e}]"
        })

    protected_text = "".join(protected_chars)

    # Sort masked items summary chronologically for user review
    masked_items_summary.reverse()

    return {
        "original_text": original_text,
        "protected_text": protected_text,
        "total_detected": len(detections),
        "masked_count": len(to_mask),
        "unmasked_count": len(unmasked),
        "masked_items": masked_items_summary,
        "unmasked_items": unmasked,
        "enabled_categories": enabled_categories,
        "applied_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
