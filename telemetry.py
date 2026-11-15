"""
telemetry.py - Dynamic Session Telemetry & Statistics Engine for PrivacyGuard
Maintains dynamic metrics for documents analysed, manual entries, detected PII, and protected outputs.
"""

from __future__ import annotations
import hashlib
import streamlit as st
from typing import Dict, Any


def compute_content_fingerprint(source_type: str, title: str, text: str) -> str:
    """
    Computes a deterministic 16-character SHA-256 fingerprint for ingested content.
    Used to prevent double-counting of identical documents or repeated analyses.
    """
    norm = f"{source_type.strip().lower()}||{title.strip().lower()}||{text.strip()}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def init_telemetry():
    """Initializes dynamic session statistics in st.session_state if not already present."""
    if "telemetry" not in st.session_state:
        st.session_state["telemetry"] = {
            "analyzed_docs": {},        # fingerprint -> {"title": str, "detected_items": int, "risk_score": int}
            "analyzed_manual": {},      # fingerprint -> {"title": str, "detected_items": int, "risk_score": int}
            "protected_docs": set(),    # set of fingerprints for protected files
            "protected_manual": set(),  # set of fingerprints for protected manual entries
        }


def record_analysis_event(fingerprint: str, source_type: str, title: str, detected_count: int, risk_score: int):
    """
    Records an analysis event for a unique document or manual entry.
    Updates detection count without duplicate counting.
    """
    init_telemetry()
    t = st.session_state["telemetry"]

    is_doc = (source_type.strip().lower() == "document upload")
    target_dict = t["analyzed_docs"] if is_doc else t["analyzed_manual"]

    target_dict[fingerprint] = {
        "title": title,
        "detected_items": int(detected_count),
        "risk_score": int(risk_score),
    }


def record_protection_event(fingerprint: str, source_type: str):
    """
    Records a successful protection/masking event for a unique document or manual entry.
    """
    init_telemetry()
    t = st.session_state["telemetry"]

    is_doc = (source_type.strip().lower() == "document upload")
    target_set = t["protected_docs"] if is_doc else t["protected_manual"]

    target_set.add(fingerprint)


def reset_telemetry():
    """Resets all dynamic statistics back to initial zero state."""
    st.session_state["telemetry"] = {
        "analyzed_docs": {},
        "analyzed_manual": {},
        "protected_docs": set(),
        "protected_manual": set(),
    }


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Calculates dynamic KPI metrics for the Dashboard based on live session activity.
    Returns:
        docs_analyzed (int)
        manual_analyzed (int)
        sensitive_detected (int)
        docs_protected (int)
        manual_protected (int)
        privacy_status (str)
        status_subtext (str)
        status_color (str)
    """
    init_telemetry()
    t = st.session_state["telemetry"]

    docs_count = len(t["analyzed_docs"])
    manual_count = len(t["analyzed_manual"])
    total_analyzed = docs_count + manual_count

    # Sensitive items detected across all unique analyzed entries
    total_sensitive = (
        sum(item["detected_items"] for item in t["analyzed_docs"].values()) +
        sum(item["detected_items"] for item in t["analyzed_manual"].values())
    )

    # Protected documents and manual records
    docs_protected = len(t["protected_docs"])
    manual_protected = len(t["protected_manual"])
    total_protected = docs_protected + manual_protected

    # Calculate unmasked PII tokens currently exposed
    unmasked_exposed_count = 0
    for fp, item in t["analyzed_docs"].items():
        if fp not in t["protected_docs"]:
            unmasked_exposed_count += item["detected_items"]
    for fp, item in t["analyzed_manual"].items():
        if fp not in t["protected_manual"]:
            unmasked_exposed_count += item["detected_items"]

    # Compute Overall Privacy Protection Status
    if total_analyzed == 0:
        privacy_status = "Standby"
        status_subtext = "🟢 100% Zero-Trust Ready"
        status_color = "#00E5FF"
    elif unmasked_exposed_count > 0:
        privacy_status = "Action Needed"
        status_subtext = f"⚠️ {unmasked_exposed_count} unmasked PII token{'s' if unmasked_exposed_count != 1 else ''}"
        status_color = "#EF4444"
    elif total_sensitive > 0 and unmasked_exposed_count == 0:
        privacy_status = "Optimal"
        status_subtext = "🟢 All detected PII sanitized"
        status_color = "#10B981"
    else:
        # total_sensitive == 0 and total_analyzed > 0
        privacy_status = "Safe"
        status_subtext = "🟢 No sensitive PII detected"
        status_color = "#10B981"

    # Card 1 Subtext: Total Documents Analysed
    if docs_count == 0 and manual_count == 0:
        doc_subtext = "⚡ Ingestion buffer empty"
    elif manual_count > 0:
        doc_subtext = f"📄 {docs_count} file{'s' if docs_count != 1 else ''} • ⌨️ {manual_count} manual"
    else:
        doc_subtext = f"📄 {docs_count} document{'s' if docs_count != 1 else ''} processed"

    # Card 2 Subtext: Sensitive Items Detected
    if total_sensitive == 0:
        sensitive_subtext = "🔍 0 PII items detected"
    else:
        sensitive_subtext = f"🔍 Across {total_analyzed} unique item{'s' if total_analyzed != 1 else ''}"

    # Card 3 Subtext: Documents Protected
    if docs_protected == 0 and manual_protected == 0:
        protected_subtext = "🛡️ 0 protected outputs generated"
    elif manual_protected > 0:
        protected_subtext = f"🛡️ {docs_protected} file{'s' if docs_protected != 1 else ''} • ⌨️ {manual_protected} manual"
    else:
        protected_subtext = f"🛡️ {docs_protected} document{'s' if docs_protected != 1 else ''} sanitized"

    return {
        "docs_analyzed": docs_count,
        "manual_analyzed": manual_count,
        "total_analyzed": total_analyzed,
        "doc_subtext": doc_subtext,
        "sensitive_detected": total_sensitive,
        "sensitive_subtext": sensitive_subtext,
        "docs_protected": docs_protected,
        "manual_protected": manual_protected,
        "total_protected": total_protected,
        "protected_subtext": protected_subtext,
        "privacy_status": privacy_status,
        "status_subtext": status_subtext,
        "status_color": status_color,
    }
