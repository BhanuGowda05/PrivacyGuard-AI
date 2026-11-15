"""
risk_assessment.py - Transparent Rule-Based Privacy Risk Assessment Engine
Calculates Privacy Risk Score (0-100), Tiers, Combination Factors, and Personalized Mitigations
"""

from typing import List, Dict, Any, Tuple

# ---------------------------------------------------------------------------
# 1. Category Base Risk Weights & Severity Levels
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS = {
    # Critical Identifiers
    "SECRET_KEY": {"weight": 32, "tier": "Critical", "diminishing": 4},
    "FINANCIAL_CRED": {"weight": 30, "tier": "Critical", "diminishing": 4},
    "AADHAAR_PATTERN": {"weight": 28, "tier": "Critical", "diminishing": 3},
    "PAN_PATTERN": {"weight": 25, "tier": "Critical", "diminishing": 3},
    
    # High-Risk Identifiers
    "ADDRESS": {"weight": 15, "tier": "High", "diminishing": 2},
    "PHONE": {"weight": 14, "tier": "High", "diminishing": 2},
    "FULL_NAME": {"weight": 12, "tier": "High", "diminishing": 2},
    "EMAIL": {"weight": 12, "tier": "High", "diminishing": 2},
    
    # Medium-Risk Identifiers
    "DOB": {"weight": 10, "tier": "Medium", "diminishing": 2},
}


# ---------------------------------------------------------------------------
# 2. Risk Calculation Engine
# ---------------------------------------------------------------------------

def calculate_privacy_risk(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes a transparent rule-based privacy risk score from 0 to 100.
    Evaluates:
      - Individual category weights
      - Volume and repeat occurrences
      - Multi-category compound correlations (co-occurrence risk)
    """
    if not detections:
        return {
            "score": 0,
            "tier": "Low Risk",
            "tier_code": "LOW",
            "color": "#10B981",
            "bg": "rgba(16, 185, 129, 0.15)",
            "summary_breakdown": [],
            "compound_penalties": [],
            "score_factors": {
                "base_score": 0,
                "volume_score": 0,
                "combination_score": 0,
                "total_raw": 0
            },
            "risk_narrative": "No sensitive personal identifiers were identified in the analyzed text. The document is classified as safe from personal data leakage.",
            "recommendations": [
                {
                    "title": "Maintain Baseline Hygiene",
                    "action": "Continue scanning documents prior to external transmission or sharing.",
                    "priority": "Informational"
                }
            ]
        }

    # Group detections by category
    cat_counts: Dict[str, int] = {}
    for d in detections:
        cat = d.get("category", "")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    summary_breakdown = []
    base_category_total = 0
    volume_addition_total = 0

    for cat, count in cat_counts.items():
        cfg = CATEGORY_WEIGHTS.get(cat, {"weight": 8, "tier": "Medium", "diminishing": 1})
        base_w = cfg["weight"]
        # Additional instances add diminishing points (capped at +10 per category)
        extra_instances = count - 1
        vol_add = min(10, extra_instances * cfg["diminishing"]) if extra_instances > 0 else 0
        cat_subtotal = base_w + vol_add

        base_category_total += base_w
        volume_addition_total += vol_add

        summary_breakdown.append({
            "category": cat,
            "count": count,
            "base_weight": base_w,
            "volume_penalty": vol_add,
            "subtotal": cat_subtotal,
            "tier": cfg["tier"]
        })

    # Sort breakdown by subtotal descending
    summary_breakdown.sort(key=lambda x: -x["subtotal"])

    # Compound Combination Risk Analysis
    compound_penalties = []
    has_name = "FULL_NAME" in cat_counts
    has_gov_id = ("AADHAAR_PATTERN" in cat_counts) or ("PAN_PATTERN" in cat_counts)
    has_contact = ("PHONE" in cat_counts) or ("EMAIL" in cat_counts)
    has_address = "ADDRESS" in cat_counts
    has_financial = "FINANCIAL_CRED" in cat_counts
    has_secret = "SECRET_KEY" in cat_counts

    # Rule 1: Identity Impersonation (Full Name + National ID)
    if has_name and has_gov_id:
        compound_penalties.append({
            "name": "Identity Theft Compound Risk",
            "penalty": 15,
            "reason": "Full Name combined with government identity numbers (Aadhaar/PAN) enables direct administrative impersonation and fraudulent loan or SIM registrations."
        })

    # Rule 2: Social Engineering & Spear-Phishing (Name + Contact Details)
    if has_name and has_contact:
        compound_penalties.append({
            "name": "Targeted Spear-Phishing Vulnerability",
            "penalty": 10,
            "reason": "Correlating a person's name with direct contact channels (Phone/Email) significantly increases susceptibility to high-trust pretexting attacks."
        })

    # Rule 3: Direct Financial Fraud Compound (Name/PAN + Payment Cards)
    if (has_name or "PAN_PATTERN" in cat_counts) and has_financial:
        compound_penalties.append({
            "name": "Financial Account Takeover Vector",
            "penalty": 18,
            "reason": "Payment credentials co-located with personal identifiers satisfy common online authentication thresholds, risking unauthorized funds withdrawal."
        })

    # Rule 4: Full KYC Tri-Factor (Name + National ID + Residential Address)
    if has_name and has_gov_id and has_address:
        compound_penalties.append({
            "name": "Complete Synthetic Identity / KYC Triangulation",
            "penalty": 14,
            "reason": "Co-occurrence of Name, National ID, and Physical Address represents a complete Know-Your-Customer (KYC) profile capable of establishing unauthorized accounts."
        })

    # Rule 5: Infrastructure Exposure (API Secret + Identifiers)
    if has_secret:
        compound_penalties.append({
            "name": "Direct Credential Compromise",
            "penalty": 12,
            "reason": "Active tokens or secrets expose operational environments and backend data stores to automated bot crawlers."
        })

    combination_score = sum(p["penalty"] for p in compound_penalties)
    raw_total = base_category_total + volume_addition_total + combination_score

    # Final bounded score: 0 to 100
    final_score = min(100, max(0, round(raw_total)))

    # Classification into required tiers:
    # Low Risk: 0-30
    # Medium Risk: 31-60
    # High Risk: 61-100
    if final_score <= 30:
        tier = "Low Risk"
        tier_code = "LOW"
        color = "#10B981"  # Emerald Green
        bg = "rgba(16, 185, 129, 0.15)"
    elif final_score <= 60:
        tier = "Medium Risk"
        tier_code = "MEDIUM"
        color = "#F59E0B"  # Amber Yellow
        bg = "rgba(245, 158, 11, 0.15)"
    else:
        tier = "High Risk"
        tier_code = "HIGH"
        color = "#EF4444"  # Crimson Red
        bg = "rgba(239, 68, 68, 0.15)"

    # Generate explanatory narrative
    narrative = generate_risk_narrative(
        final_score, tier, cat_counts, compound_penalties
    )

    # Generate personalized mitigation recommendations
    recommendations = generate_recommendations(cat_counts, compound_penalties)

    return {
        "score": final_score,
        "tier": tier,
        "tier_code": tier_code,
        "color": color,
        "bg": bg,
        "summary_breakdown": summary_breakdown,
        "compound_penalties": compound_penalties,
        "score_factors": {
            "base_score": base_category_total,
            "volume_score": volume_addition_total,
            "combination_score": combination_score,
            "total_raw": raw_total
        },
        "risk_narrative": narrative,
        "recommendations": recommendations
    }


# ---------------------------------------------------------------------------
# 3. Narrative & Contextual Explanations
# ---------------------------------------------------------------------------

def generate_risk_narrative(
    score: int, tier: str, cat_counts: Dict[str, int], compound_penalties: List[Dict[str, Any]]
) -> str:
    """Explains why the data received its specific risk score."""
    parts = []
    parts.append(
        f"This analyzed text has been classified as **{tier}** with an overall Privacy Exposure Score of **{score}/100**."
    )

    high_cats = [c for c in cat_counts if c in ("AADHAAR_PATTERN", "PAN_PATTERN", "FINANCIAL_CRED", "SECRET_KEY")]
    if high_cats:
        parts.append(
            f"The assessment is heavily impacted by the presence of critical identifiers: **{', '.join(high_cats)}**, which carry substantial regulatory liabilities and direct financial or identity theft potential."
        )

    if compound_penalties:
        penalty_names = [p["name"] for p in compound_penalties]
        parts.append(
            f"Crucially, **{len(compound_penalties)} compound risk factors** were triggered ({'; '.join(penalty_names)}). "
            f"Exposing these specific attributes together creates an exponential correlation hazard: an adversary can cross-reference names, contact points, and national IDs to reconstruct a full victim profile."
        )
    elif tier == "Medium Risk":
        parts.append(
            "While direct critical government identity codes were limited, the presence of contact channels and demographic details warrants sanitization prior to external publication."
        )
    else:
        parts.append(
            "Individual detected tokens represent limited surface exposure with minimal compound correlation risks."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# 4. Personalized Recommendations Engine
# ---------------------------------------------------------------------------

def generate_recommendations(
    cat_counts: Dict[str, int], compound_penalties: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """Generates tailored cybersecurity and data protection guidance."""
    recs = []

    if "AADHAAR_PATTERN" in cat_counts:
        recs.append({
            "title": "Redact / Mask National Identity (Aadhaar)",
            "action": "Apply irreversible masking to the first 8 digits (e.g. XXXX XXXX 1234) in compliance with UIDAI regulations and Section 29 of the Aadhaar Act.",
            "priority": "Critical"
        })

    if "PAN_PATTERN" in cat_counts:
        recs.append({
            "title": "Tokenize Permanent Account Numbers",
            "action": "Replace plaintext PAN values with contextual pseudonym tokens or irreversible blackout blocks before sharing with third-party processors.",
            "priority": "Critical"
        })

    if "FINANCIAL_CRED" in cat_counts:
        recs.append({
            "title": "PCI-DSS Immediate Sanitization",
            "action": "Ensure card primary account numbers (PAN) are truncated to the last four digits or completely purged from local processing memory.",
            "priority": "Critical"
        })

    if "SECRET_KEY" in cat_counts:
        recs.append({
            "title": "Rotate Exposed Credentials Immediately",
            "action": "Assume exposed API keys or tokens are compromised. Revoke them in your provider dashboard and substitute with secure environment variable references.",
            "priority": "Critical"
        })

    if ("PHONE" in cat_counts) or ("EMAIL" in cat_counts):
        recs.append({
            "title": "Obfuscate Direct Contact Vectors",
            "action": "Transform direct phone numbers and email handles using partial character masking to deter automated web scrapers and telemarketing lists.",
            "priority": "High"
        })

    if "ADDRESS" in cat_counts:
        recs.append({
            "title": "Coarsen Residential Location Data",
            "action": "Replace street-level and flat numbers with generalized geographic identifiers (e.g., city or region only) to protect residential privacy.",
            "priority": "Medium"
        })

    if compound_penalties:
        recs.append({
            "title": "Enforce Separation of Datasets (Decoupling)",
            "action": "Store person names and identity records in distinct pseudonymized databases with separate access control lists (ACLs) to prevent bulk correlation leaks.",
            "priority": "High"
        })

    # Default fallback
    if not recs:
        recs.append({
            "title": "General Data Minimization",
            "action": "Follow the principle of data minimization: retain and process only data strictly necessary for the intended business operation.",
            "priority": "Standard"
        })

    return recs
