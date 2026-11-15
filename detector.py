"""
detector.py - Sensitive Personal Data Detection Engine for PrivacyGuard
Integrates Regex Pattern Recognition with NLP-based Named Entity Recognition (NER)
"""

import re
import html
from typing import List, Dict, Any, Tuple

# Attempt spaCy import gracefully if available
_SPACY_NLP = None
try:
    import spacy
    try:
        _SPACY_NLP = spacy.load("en_core_web_sm")
    except Exception:
        # Fallback to blank model if en_core_web_sm is not downloaded
        try:
            _SPACY_NLP = spacy.blank("en")
        except Exception:
            _SPACY_NLP = None
except ImportError:
    _SPACY_NLP = None


# ---------------------------------------------------------------------------
# Sensitive Category Explanations & Privacy Impact
# ---------------------------------------------------------------------------

CATEGORY_METADATA = {
    "FULL_NAME": {
        "label": "Full Name",
        "icon": "👤",
        "color": "#00E5FF",  # Bright Cyan
        "bg": "rgba(0, 229, 255, 0.2)",
        "risk": "High",
        "reason": "Direct personal identifier protected under GDPR, HIPAA, and DPDP Act. Can be correlated with other leaked datasets for social engineering and identity theft."
    },
    "EMAIL": {
        "label": "Email Address",
        "icon": "✉️",
        "color": "#64FFDA",  # Teal Green
        "bg": "rgba(100, 255, 218, 0.2)",
        "risk": "High",
        "reason": "Direct communication vector frequently targeted for credential harvesting, spear-phishing, and unauthorized account recovery attacks."
    },
    "PHONE": {
        "label": "Phone Number",
        "icon": "📞",
        "color": "#38BDF8",  # Sky Blue
        "bg": "rgba(56, 189, 248, 0.2)",
        "risk": "High",
        "reason": "Confidential contact identifier vulnerable to SMS phishing (smishing), SIM swapping, and unauthorized location tracking."
    },
    "AADHAAR_PATTERN": {
        "label": "Aadhaar Number Pattern",
        "icon": "🪪",
        "color": "#F59E0B",  # Amber
        "bg": "rgba(245, 158, 11, 0.2)",
        "risk": "Critical",
        "reason": "12-digit Indian National Identity pattern. Under Section 29 of Aadhaar Act 2016, unauthorized publication or storage is strictly prohibited."
    },
    "PAN_PATTERN": {
        "label": "PAN Number Pattern",
        "icon": "💳",
        "color": "#EC4899",  # Pink
        "bg": "rgba(236, 72, 153, 0.2)",
        "risk": "Critical",
        "reason": "Permanent Account Number issued by the Indian Income Tax Department. Critical financial identifier vulnerable to tax fraud and credit impersonation."
    },
    "ADDRESS": {
        "label": "Residential Address",
        "icon": "🏠",
        "color": "#A78BFA",  # Purple
        "bg": "rgba(167, 139, 250, 0.2)",
        "risk": "High",
        "reason": "Precise physical location data exposing physical security, stalking risks, and residential demographic profiling."
    },
    "DOB": {
        "label": "Date of Birth",
        "icon": "🎂",
        "color": "#F43F5E",  # Rose
        "bg": "rgba(244, 63, 94, 0.2)",
        "risk": "Medium",
        "reason": "Static identity attribute routinely leveraged as secondary authentication for banking, healthcare, and government identity verification."
    },
    "FINANCIAL_CRED": {
        "label": "Financial / Card Identifier",
        "icon": "💰",
        "color": "#EF4444",  # Red
        "bg": "rgba(239, 68, 68, 0.2)",
        "risk": "Critical",
        "reason": "Payment Card Industry (PCI-DSS) violation risk. Can be exploited for unauthorized transactions and monetary theft."
    },
    "SECRET_KEY": {
        "label": "API Key / Credential Secret",
        "icon": "🔑",
        "color": "#FB7185",  # Coral
        "bg": "rgba(251, 113, 133, 0.2)",
        "risk": "Critical",
        "reason": "Authentication token exposing private infrastructure, database records, and cloud computing environments."
    }
}


# ---------------------------------------------------------------------------
# 1. Regex Pattern Engine
# ---------------------------------------------------------------------------

# Regular expression definitions
REGEX_PATTERNS = {
    # Email: Standard RFC-compliant address
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b",
        re.IGNORECASE
    ),

    # Phone: International + Indian 10-digit formats with separators
    "PHONE": re.compile(
        r"(?:(?:\+?91[\s.-]?)?[6-9]\d{4}[\s.-]?\d{5}\b)|"
        r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
    ),

    # Aadhaar: 12-digit Indian identity pattern (First digit 2-9, optional spaces/hyphens)
    # Stated as pattern match, not genuine verification
    "AADHAAR_PATTERN": re.compile(
        r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b"
    ),

    # PAN: 5 uppercase letters, 4 digits, 1 uppercase letter
    "PAN_PATTERN": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
    ),

    # Credit / Debit Card patterns (16 digits with optional dashes/spaces)
    "FINANCIAL_CRED": re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9]{2})[0-9]{12}|3[47][0-9]{13})\b|"
        r"\b(?:\d{4}[\s-]){3}\d{4}\b"
    ),

    # Sensitive API Keys / Secrets / Passwords
    "SECRET_KEY": re.compile(
        r"\b(?:ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35}|sk_live_[0-9a-zA-Z]{24}|bearer\s+[a-zA-Z0-9_\-\.]{20,})\b|"
        r"(?:api[_-]?key|secret|password|auth_token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?",
        re.IGNORECASE
    ),

    # Date of birth with contextual triggers or explicit formatting
    "DOB": re.compile(
        r"(?:(?:DOB|Date\s+of\s+Birth|Birth\s*Date|Born\s*on)\s*[:=]?\s*)"
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})",
        re.IGNORECASE
    )
}


# ---------------------------------------------------------------------------
# 2. NLP-Based Entity Recognition Engine (Names & Addresses)
# ---------------------------------------------------------------------------

# Common honorifics and title prefixes for Name recognition
HONORIFICS = r"(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Shri|Smt\.|Kumari|Hon\.)"

# Common street and address keywords
ADDRESS_INDICATORS = [
    "flat", "house", "plot", "apt", "apartment", "suite", "sector", "road",
    "street", "st.", "avenue", "ave", "lane", "nagar", "colony", "enclave",
    "block", "floor", "building", "towers", "residency", "vihar", "chowk",
    "pincode", "pin code", "zip"
]


def detect_names_nlp(text: str) -> List[Dict[str, Any]]:
    """
    Extracts person names using a hybrid of spaCy NER (if loaded)
    and context-aware linguistic pattern parsing.
    """
    detected = []

    # 1. Try spaCy model if available
    if _SPACY_NLP is not None:
        try:
            doc = _SPACY_NLP(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean_text = ent.text.strip()
                    # Filter out common false positives (single letters, all-lowercase, stop words)
                    if len(clean_text) >= 3 and any(c.isupper() for c in clean_text):
                        detected.append({
                            "text": clean_text,
                            "category": "FULL_NAME",
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "confidence": "High (spaCy NER)",
                            "method": "NLP Entity Model"
                        })
        except Exception:
            pass

    # 2. Contextual Linguistic Pattern Matcher
    # Matches: "Subject Full Name: Aarav Sharma", "Name: Jane Doe", "Mr. Aarav Sharma"
    context_patterns = [
        # Explicit name keys (strictly within a single line, ending at punctuation, space or newline)
        re.compile(
            r"(?:(?:Full\s*Name|Subject(?:\s*Name)?|Employee(?:\s*Name)?|Candidate(?:\s*Name)?|Patient(?:\s*Name)?|Name)\s*[:=-]\s*)"
            r"([A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){1,3})(?=\r?\n|$|\s{2,}|[,;.])"
        ),
        # Honorific prefixes (e.g., "Dr. Aarav Sharma", "Mr. John Doe")
        re.compile(
            rf"\b({HONORIFICS}[ \t]+[A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){{1,2}})\b"
        )
    ]

    for pattern in context_patterns:
        for match in pattern.finditer(text):
            # Capture the full match or group 1
            matched_str = match.group(1) if match.groups() else match.group(0)
            start_pos = match.start(1) if match.groups() else match.start(0)
            end_pos = match.end(1) if match.groups() else match.end(0)
            detected.append({
                "text": matched_str.strip(),
                "category": "FULL_NAME",
                "start": start_pos,
                "end": end_pos,
                "confidence": "High (Linguistic Pattern)",
                "method": "NLP Context Matcher"
            })

    return detected


def detect_addresses_nlp(text: str) -> List[Dict[str, Any]]:
    """
    Detects residential addresses and physical locations using
    spaCy GPE/LOC entities and structural postal address heuristics.
    """
    detected = []

    # 1. Contextual Address Header Pattern (e.g. "Residential Address: Flat 402, Sector 62...")
    addr_context = re.compile(
        r"(?:(?:Residential\s*Address|Permanent\s*Address|Shipping\s*Address|Address)\s*[:=-]\s*)"
        r"([^\n\r]+)",
        re.IGNORECASE
    )

    for match in addr_context.finditer(text):
        addr_str = match.group(1).strip()
        if len(addr_str) >= 6:
            detected.append({
                "text": addr_str,
                "category": "ADDRESS",
                "start": match.start(1),
                "end": match.end(1),
                "confidence": "High (Contextual Heuristic)",
                "method": "Structural Address Parser"
            })

    # 2. Street/Locality Indicator Pattern
    # Matches: "Flat 402, Cyber Heights, Sector 62, Noida, UP, 201301" (single line)
    street_pattern = re.compile(
        r"\b(?:Flat|House|Plot|Apartment|Apt|Suite|Sector|Road|Street|Lane|Nagar|Colony|Enclave|Block)[ \t]+[A-Za-z0-9\-]+(?:,[ \t]*[A-Za-z0-9 \t\-]+){2,5}(?:,[ \t]*\d{5,6})?\b",
        re.IGNORECASE
    )

    for match in street_pattern.finditer(text):
        detected.append({
            "text": match.group(0).strip(),
            "category": "ADDRESS",
            "start": match.start(0),
            "end": match.end(0),
            "confidence": "High (Street Pattern)",
            "method": "Structural Address Parser"
        })

    # 3. spaCy GPE/LOC (Cities, states, facilities) if loaded
    if _SPACY_NLP is not None:
        try:
            doc = _SPACY_NLP(text)
            for ent in doc.ents:
                if ent.label_ in ("GPE", "LOC", "FAC"):
                    clean = ent.text.strip()
                    if len(clean) >= 4 and not clean.isdigit():
                        detected.append({
                            "text": clean,
                            "category": "ADDRESS",
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "confidence": "Medium (spaCy GPE/LOC)",
                            "method": "NLP Entity Model"
                        })
        except Exception:
            pass

    return detected


# ---------------------------------------------------------------------------
# 3. Main Consolidated Detection Engine
# ---------------------------------------------------------------------------

def detect_sensitive_data(text: str) -> Dict[str, Any]:
    """
    Executes full sensitive information detection pipeline on raw input text.
    Combines Regex patterns and NLP Named Entity Recognition.
    Resolves entity overlaps and generates rich privacy telemetry.
    """
    if not text or not text.strip():
        return {
            "total_detections": 0,
            "category_summary": {},
            "detections": [],
            "risk_score": 0,
            "risk_level": "Safe (No PII Detected)",
            "highlighted_html": html.escape(text or "")
        }

    raw_candidates = []

    # Step A: Apply Regex Patterns
    for cat, pattern in REGEX_PATTERNS.items():
        for match in pattern.finditer(text):
            # If group 1 exists (e.g. for DOB/Secret contextual match), use group 1
            if match.groups() and match.group(1):
                item_text = match.group(1).strip()
                s_idx = match.start(1)
                e_idx = match.end(1)
            else:
                item_text = match.group(0).strip()
                s_idx = match.start(0)
                e_idx = match.end(0)

            # Avoid false positives for Aadhaar (e.g., standard numbers or year ranges)
            if cat == "AADHAAR_PATTERN":
                digits_only = re.sub(r"[\s-]", "", item_text)
                if len(digits_only) != 12:
                    continue

            # Avoid false positives for Phone (must be 10-15 digits)
            if cat == "PHONE":
                digits = re.sub(r"[^\d]", "", item_text)
                if len(digits) < 10 or len(digits) > 15:
                    continue

            raw_candidates.append({
                "text": item_text,
                "category": cat,
                "start": s_idx,
                "end": e_idx,
                "confidence": "High (Regex Pattern Match)",
                "method": "Pattern Recognizer"
            })

    # Step B: Apply NLP NER (Names & Addresses)
    raw_candidates.extend(detect_names_nlp(text))
    raw_candidates.extend(detect_addresses_nlp(text))

    # Step C: Overlap Resolution & Deduplication
    # Sort primarily by start position, then by span length (descending)
    raw_candidates.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

    resolved_detections = []
    last_end = -1

    for cand in raw_candidates:
        s = cand["start"]
        e = cand["end"]

        # Ensure valid non-empty span
        if e <= s or not cand["text"].strip():
            continue

        # Check if overlaps with previously accepted detection
        if s >= last_end:
            # Augment with metadata
            meta = CATEGORY_METADATA.get(cand["category"], {})
            cand["id"] = f"pii_{len(resolved_detections) + 1}"
            cand["label"] = meta.get("label", cand["category"])
            cand["icon"] = meta.get("icon", "🛡️")
            cand["color"] = meta.get("color", "#00E5FF")
            cand["bg"] = meta.get("bg", "rgba(0, 229, 255, 0.2)")
            cand["risk"] = meta.get("risk", "Medium")
            cand["reason"] = meta.get("reason", "Contains identifiable personal markers.")
            
            resolved_detections.append(cand)
            last_end = e
        else:
            # Skip overlapping lower-priority matches
            continue

    # Step D: Compute Category Summary & Risk Metrics
    category_summary = {}
    critical_count = 0
    high_count = 0

    for det in resolved_detections:
        c = det["category"]
        if c not in category_summary:
            category_summary[c] = {
                "label": det["label"],
                "icon": det["icon"],
                "color": det["color"],
                "risk": det["risk"],
                "count": 0,
                "reason": det["reason"]
            }
        category_summary[c]["count"] += 1

        if det["risk"] == "Critical":
            critical_count += 1
        elif det["risk"] == "High":
            high_count += 1

    # Risk Level Assessment
    total_count = len(resolved_detections)
    if critical_count > 0:
        risk_level = "Critical Exposure Risk"
        risk_score = min(100, 75 + critical_count * 5)
    elif high_count > 0:
        risk_level = "High Privacy Risk"
        risk_score = min(74, 50 + high_count * 5)
    elif total_count > 0:
        risk_level = "Moderate Exposure Risk"
        risk_score = 35 + total_count * 5
    else:
        risk_level = "Safe (No Identifiable PII Detected)"
        risk_score = 0

    # Step E: Generate Highlighted HTML Preview
    highlighted_html = generate_highlighted_html(text, resolved_detections)

    return {
        "total_detections": total_count,
        "category_summary": category_summary,
        "detections": resolved_detections,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "critical_count": critical_count,
        "high_count": high_count,
        "highlighted_html": highlighted_html
    }


def generate_highlighted_html(text: str, detections: List[Dict[str, Any]]) -> str:
    """
    Renders the original text with inline visual badges highlighting
    detected sensitive information with category chips.
    """
    if not detections:
        return f"<div style='white-space: pre-wrap; font-family: monospace;'>{html.escape(text)}</div>"

    html_parts = []
    current_idx = 0

    for det in detections:
        s = det["start"]
        e = det["end"]

        # Append safe text before the detection
        if s > current_idx:
            html_parts.append(html.escape(text[current_idx:s]))

        # Highlight detected span with cyber badge
        matched_content = html.escape(det["text"])
        badge_label = html.escape(det["label"])
        color = det["color"]
        bg = det["bg"]

        highlight_markup = (
            f'<mark style="background: {bg}; color: #FFFFFF; border: 1px solid {color}; '
            f'padding: 2px 6px; border-radius: 4px; font-weight: 600; margin: 0 2px; '
            f'display: inline-block;">'
            f'{matched_content} '
            f'<span style="background: {color}; color: #0A192F; font-size: 0.68rem; '
            f'padding: 1px 4px; border-radius: 3px; margin-left: 4px; text-transform: uppercase; font-weight: 800;">'
            f'{badge_label}</span>'
            f'</mark>'
        )
        html_parts.append(highlight_markup)
        current_idx = e

    # Append any remaining text after last detection
    if current_idx < len(text):
        html_parts.append(html.escape(text[current_idx:]))

    inner_html = "".join(html_parts)
    return (
        f'<div style="background: #081220; border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 8px; '
        f'padding: 1.25rem; font-family: \'JetBrains Mono\', monospace; font-size: 0.88rem; '
        f'line-height: 1.8; max-height: 380px; overflow-y: auto; white-space: pre-wrap; word-break: break-word;">'
        f'{inner_html}'
        f'</div>'
    )
