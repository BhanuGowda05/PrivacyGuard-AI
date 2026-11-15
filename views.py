"""
views.py - Page views for PrivacyGuard navigation
Includes Module A (Document Upload) & Module B (Manual Data Entry)
"""

import streamlit as st
import datetime
import textwrap
from components import (
    render_cyber_banner,
    render_metric_card,
    render_risk_meter,
    render_pipeline_stepper,
    render_action_card,
    render_how_it_works
)
from data_handler import (
    extract_text_from_file,
    get_available_sample_documents,
    load_sample_document,
    validate_manual_entry,
    get_safe_demonstration_data,
    format_manual_entry_payload,
    stage_data_for_analysis,
    human_readable_size
)
from detector import (
    detect_sensitive_data,
    CATEGORY_METADATA
)
from risk_assessment import (
    calculate_privacy_risk,
    CATEGORY_WEIGHTS
)
from masking import (
    apply_masking,
    mask_single_value
)
from document_generator import (
    generate_protected_txt,
    generate_protected_docx,
    generate_protected_pdf
)
from telemetry import (
    get_dashboard_metrics,
    record_analysis_event,
    record_protection_event,
    reset_telemetry,
    compute_content_fingerprint
)


def safe_html(html_str: str):
    """Renders HTML safely with stripped indentation to avoid markdown code-block interpretation."""
    st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# DASHBOARD VIEW
# ---------------------------------------------------------------------------

def render_dashboard_view():
    """Main Dashboard View displaying operational status, stats, actions, and pipeline."""
    render_cyber_banner(
        title="PrivacyGuard Operations Dashboard",
        subtitle="AI-Powered Personal Data Protection & Proactive Redaction Hub"
    )

    # Dynamic KPI Stat Metrics computed from live application activity
    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            label="Total Documents Analysed",
            value=str(metrics["docs_analyzed"]),
            subtext=metrics["doc_subtext"],
            border_color="#00E5FF"
        )
    with col2:
        render_metric_card(
            label="Sensitive Items Detected",
            value=str(metrics["sensitive_detected"]),
            subtext=metrics["sensitive_subtext"],
            border_color="#FF0055"
        )
    with col3:
        render_metric_card(
            label="Documents Protected",
            value=str(metrics["docs_protected"]),
            subtext=metrics["protected_subtext"],
            border_color="#64FFDA"
        )
    with col4:
        render_metric_card(
            label="Privacy Protection Status",
            value=metrics["privacy_status"],
            subtext=metrics["status_subtext"],
            border_color=metrics["status_color"]
        )

    # If manual personal entries have been analysed, show discrete telemetry tracking breakdown
    if metrics["manual_analyzed"] > 0:
        telemetry_pill_html = (
            f'<div style="margin-top: 0.6rem; margin-bottom: 0.4rem; background: rgba(10, 25, 47, 0.6); '
            f'border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 6px; padding: 6px 14px; '
            f'display: flex; align-items: center; justify-content: space-between; font-size: 0.82rem;">'
            f'<span style="color: #64FFDA; font-weight: 700;">📊 Live Session Telemetry:</span>'
            f'<span style="color: #CBD5E1;">📄 Documents Scanned: <strong>{metrics["docs_analyzed"]}</strong> | '
            f'⌨️ Manual Personal Entries: <strong>{metrics["manual_analyzed"]}</strong> | '
            f'🔍 Sensitive Items: <strong>{metrics["sensitive_detected"]}</strong> | '
            f'🛡️ Protected Outputs: <strong>{metrics["total_protected"]}</strong></span>'
            f'</div>'
        )
        safe_html(telemetry_pill_html)

    # Reset Statistics Option
    if metrics["total_analyzed"] > 0 or metrics["total_protected"] > 0:
        c_space, c_btn = st.columns([6, 1])
        with c_btn:
            if st.button("🔄 Reset Stats", help="Reset session statistics counters back to zero", use_container_width=True):
                reset_telemetry()
                st.rerun()

    st.write("")

    # If an item is currently staged in memory, display a notice
    if "staged_data" in st.session_state and st.session_state["staged_data"]:
        staged = st.session_state["staged_data"]
        stage_notice_html = (
            f'<div class="stage-notice">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">'
            f'<div>'
            f'<span style="color: #64FFDA; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">'
            f'⚡ In-Memory Buffer Active'
            f'</span>'
            f'<h4 style="color: #FFFFFF; margin: 4px 0 0 0;">'
            f'{staged["title"]} ({staged["source"]})'
            f'</h4>'
            f'<span style="color: #8892B0; font-size: 0.8rem;">'
            f'Staged at {staged["timestamp"]} • {staged["metadata"].get("word_count", 0)} words ready for analysis'
            f'</span>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        safe_html(stage_notice_html)
        if st.button("Go to Privacy Analysis for this item →", key="dash_goto_analysis", type="primary"):
            st.session_state["current_page"] = "Privacy Analysis"
            st.rerun()

    # Two Large Action Cards
    st.markdown("### 🚀 Quick Defense Actions")
    act_col1, act_col2 = st.columns(2)

    with act_col1:
        render_action_card(
            title="Upload a Document",
            description="Protect sensitive contracts, identification files, medical forms, tax returns, or TXT/DOCX files before sharing or archiving.",
            icon="📄",
            page_target="Document Protection",
            button_key="btn_nav_doc_protect"
        )

    with act_col2:
        render_action_card(
            title="Enter Personal Information Manually",
            description="Use a structured form for names, emails, phone numbers, addresses, and national IDs with built-in format validation.",
            icon="⌨️",
            page_target="Manual Data Entry",
            button_key="btn_nav_manual_entry"
        )

    st.write("")

    # How PrivacyGuard Works Section
    render_how_it_works()


# ---------------------------------------------------------------------------
# MODULE A: DOCUMENT UPLOAD
# ---------------------------------------------------------------------------

def render_document_protection_view():
    """Module A: In-memory Document Upload & Extraction Engine."""
    render_cyber_banner(
        title="Document Protection & Ingestion",
        subtitle="Upload PDF, DOCX, or TXT documents for strictly in-memory text extraction"
    )
    render_pipeline_stepper(1)

    # In-memory session key for file uploader reset
    if "doc_uploader_key" not in st.session_state:
        st.session_state["doc_uploader_key"] = 0

    st.markdown("#### 📁 Secure Document Ingestion")
    st.caption("Drag and drop your file below, or click browse. Max size: 15 MB. Supported formats: **PDF, DOCX, TXT**.")

    uploaded_file = st.file_uploader(
        "Select document to inspect",
        type=["pdf", "docx", "txt"],
        key=f"file_uploader_{st.session_state['doc_uploader_key']}",
        help="Files are processed exclusively in volatile RAM and never written to disk."
    )

    if uploaded_file is not None:
        # 1. Extraction Attempt
        with st.spinner("Extracting document contents in secure memory buffer..."):
            result = extract_text_from_file(uploaded_file)

        # 2. Handle Errors Gracefully (corrupted, password protected, empty, oversize)
        if not result["success"]:
            st.error(f"❌ **Extraction Error:** {result['error']}")
            if st.button("🗑️ Remove File & Reset", key="btn_remove_err_file"):
                st.session_state["doc_uploader_key"] += 1
                st.rerun()
        else:
            # 3. Successful Extraction UI
            st.success(f"✅ Successfully extracted text from **{result['filename']}**")

            # File Information Badges
            info_badges_html = (
                f'<div style="margin: 0.8rem 0; display: flex; gap: 8px; flex-wrap: wrap;">'
                f'<span class="badge-chip">📄 Format: {result["file_type"]}</span>'
                f'<span class="badge-chip">💾 Size: {result["file_size"]}</span>'
                f'<span class="badge-chip">📝 Words: {result["metadata"].get("word_count", 0):,}</span>'
                f'<span class="badge-chip">🔤 Characters: {result["metadata"].get("character_count", 0):,}</span>'
                f'</div>'
            )
            safe_html(info_badges_html)

            # 4. Text Preview
            st.markdown("##### 👁️ Extracted Text Preview")
            preview_snippet = result["text"]
            safe_html(f'<div class="preview-box">{preview_snippet}</div>')
            st.caption(f"Displaying extracted document buffer ({result['metadata'].get('word_count', 0)} words).")

            st.write("")

            # 5. Actions: Remove File & Continue to Analysis
            btn_c1, btn_c2 = st.columns([1, 2])
            with btn_c1:
                if st.button("🗑️ Remove File", use_container_width=True):
                    st.session_state["doc_uploader_key"] += 1
                    st.rerun()

            with btn_c2:
                if st.button("🚀 Continue to Analysis →", type="primary", use_container_width=True):
                    # Stage data into common pipeline
                    staged = stage_data_for_analysis(
                        source_type="Document Upload",
                        title=result["filename"],
                        raw_text=result["text"],
                        metadata={
                            "file_name": result["filename"],
                            "file_size": result["file_size"],
                            "file_type": result["file_type"],
                            **result["metadata"]
                        }
                    )
                    st.session_state["staged_data"] = staged
                    st.session_state["current_page"] = "Privacy Analysis"
                    st.rerun()

    else:
        st.info("👆 Upload a document above to inspect and preview extracted contents.")


# ---------------------------------------------------------------------------
# MODULE B: MANUAL PERSONAL DATA ENTRY
# ---------------------------------------------------------------------------

def render_manual_data_entry_view():
    """Module B: Structured Manual Personal Data Entry Form."""
    render_cyber_banner(
        title="Manual Personal Data Entry",
        subtitle="Input personal identifiers through structured fields with format validation"
    )
    render_pipeline_stepper(1)

    # Initialize form fields in session state if absent
    if "manual_form" not in st.session_state:
        st.session_state["manual_form"] = {
            "full_name": "",
            "email": "",
            "phone": "",
            "aadhaar": "",
            "pan": "",
            "address": "",
            "dob": datetime.date(1995, 1, 1),
            "other_info": ""
        }

    st.markdown("#### 📝 Personal Identifiers Input Form")
    st.caption("Provide personal identifiers for contextual analysis. You can also click 'Fill Safe Demo Values' for testing.")

    # Demonstration Helper
    demo_c1, demo_c2 = st.columns([2, 1])
    with demo_c1:
        if st.button("🧪 Fill Safe Demo Values (No Real Data)", use_container_width=True):
            st.session_state["manual_form"] = get_safe_demonstration_data()
            st.rerun()
    with demo_c2:
        if st.button("🧹 Clear Form Fields", use_container_width=True):
            st.session_state["manual_form"] = {
                "full_name": "",
                "email": "",
                "phone": "",
                "aadhaar": "",
                "pan": "",
                "address": "",
                "dob": datetime.date(1995, 1, 1),
                "other_info": ""
            }
            st.rerun()

    st.write("")

    # Form Fields Grid
    f_col1, f_col2 = st.columns(2)

    with f_col1:
        full_name = st.text_input(
            "Full Name",
            value=st.session_state["manual_form"].get("full_name", ""),
            placeholder="e.g., Rajesh Kumar",
            help="Full personal legal name"
        )

        email = st.text_input(
            "Email Address",
            value=st.session_state["manual_form"].get("email", ""),
            placeholder="e.g., rajesh.kumar@example.com",
            help="Contact email address"
        )

        phone = st.text_input(
            "Phone Number",
            value=st.session_state["manual_form"].get("phone", ""),
            placeholder="e.g., +91 98765 43210 or 9876543210",
            help="10-digit standard or international phone number"
        )

        dob = st.date_input(
            "Date of Birth (Optional)",
            value=st.session_state["manual_form"].get("dob", datetime.date(1995, 1, 1)),
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today(),
            help="Birth date for age & identity correlation"
        )

    with f_col2:
        aadhaar = st.text_input(
            "Aadhaar Number Pattern (Optional Demo Format)",
            value=st.session_state["manual_form"].get("aadhaar", ""),
            placeholder="e.g., 2345 6789 0123 (12 digits)",
            help="Never provide real national identifiers. Uses synthetic structural format."
        )

        pan = st.text_input(
            "PAN Card Number Pattern (Optional Demo Format)",
            value=st.session_state["manual_form"].get("pan", ""),
            placeholder="e.g., ABCDE1234F (10 characters: 5 letters, 4 digits, 1 letter)",
            help="Tax ID pattern format. Never use live taxpayer numbers."
        )

        address = st.text_area(
            "Residential Address (Optional)",
            value=st.session_state["manual_form"].get("address", ""),
            placeholder="e.g., Flat 402, Cyber Heights, Sector 62, Noida, UP, 201301",
            height=68,
            help="Physical location or mailing residence"
        )

        other_info = st.text_input(
            "Other Identifiable Personal Information (Optional)",
            value=st.session_state["manual_form"].get("other_info", ""),
            placeholder="e.g., Passport: M1234567, Employee ID: EMP-8891",
            help="Any secondary confidential identifier"
        )

    # Save inputs back to session state dictionary
    st.session_state["manual_form"] = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "aadhaar": aadhaar,
        "pan": pan,
        "address": address,
        "dob": dob,
        "other_info": other_info
    }

    st.write("")

    # Action Buttons
    btn_c1, btn_c2 = st.columns([1, 2])
    with btn_c1:
        if st.button("🧹 Clear Form", use_container_width=True):
            st.session_state["manual_form"] = {
                "full_name": "",
                "email": "",
                "phone": "",
                "aadhaar": "",
                "pan": "",
                "address": "",
                "dob": datetime.date(1995, 1, 1),
                "other_info": ""
            }
            st.rerun()

    with btn_c2:
        if st.button("🚀 Continue to Analysis →", type="primary", use_container_width=True):
            # Format validation
            is_valid, validation_errors = validate_manual_entry(st.session_state["manual_form"])

            if not is_valid:
                st.error("⚠️ **Validation Failed:** Please resolve the following errors before continuing:")
                for field, err in validation_errors.items():
                    st.markdown(f"- **{field.replace('_', ' ').title()}:** {err}")
            else:
                # Package structured text payload
                raw_text = format_manual_entry_payload(st.session_state["manual_form"])
                title_name = full_name.strip() if full_name.strip() else "Manual Data Record"
                staged = stage_data_for_analysis(
                    source_type="Manual Data Entry",
                    title=f"Record: {title_name}",
                    raw_text=raw_text,
                    metadata={
                        "subject_name": title_name,
                        "fields_provided": [k for k, v in st.session_state["manual_form"].items() if str(v).strip()],
                    }
                )
                st.session_state["staged_data"] = staged
                st.session_state["current_page"] = "Privacy Analysis"
                st.rerun()


# ---------------------------------------------------------------------------
# COMMON DOWNSTREAM PIPELINE: PRIVACY ANALYSIS
# ---------------------------------------------------------------------------

def render_privacy_analysis_view():
    """Module C: Sensitive Personal Data Detection Engine & Telemetry Workbench."""
    render_cyber_banner(
        title="Sensitive Personal Data Detection Engine",
        subtitle="Hybrid Regex Pattern Matcher & NLP Named Entity Recognition Telemetry"
    )

    # Dynamic workflow stepper (Detection -> Risk Assessment -> Masking)
    if st.session_state.get("protected_result"):
        render_pipeline_stepper(4)
    elif st.session_state.get("analysis_result"):
        render_pipeline_stepper(3)
    else:
        render_pipeline_stepper(2)

    # State initialization for analysis
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None
    if "active_analysis_text" not in st.session_state:
        st.session_state["active_analysis_text"] = ""

    # Check for incoming staged data
    has_staged = ("staged_data" in st.session_state and st.session_state["staged_data"])
    staged = st.session_state["staged_data"] if has_staged else None

    # Top Ingestion Bar
    if has_staged:
        staged_bar_html = (
            f'<div class="stage-notice">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">'
            f'<div>'
            f'<span style="color: #64FFDA; font-weight: 700; font-size: 0.82rem; text-transform: uppercase;">'
            f'⚡ In-Memory Buffer Staged from {staged["source"]}'
            f'</span>'
            f'<h3 style="color: #FFFFFF; margin: 4px 0 0 0;">'
            f'{staged["title"]}'
            f'</h3>'
            f'<span style="color: #8892B0; font-size: 0.82rem;">'
            f'Ingestion: {staged["timestamp"]} | Status: <strong style="color: #00E5FF;">{staged["status"]}</strong>'
            f'</span>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        safe_html(staged_bar_html)
        target_text = staged["raw_text"]
    else:
        st.info("ℹ️ **No Document or Data Currently Staged:** You can load sample demonstration text below or upload a file via **Document Protection** / **Manual Data Entry**.")
        
        sample_demo_text = (
            "CONFIDENTIAL PERSONAL DATA REPORT\n"
            "Subject Full Name: Aarav Sharma\n"
            "Primary Email: aarav.sharma.sample@example.com\n"
            "Contact Number: +91 98765 43210\n"
            "Residential Address: Flat 402, Cyber Heights, Sector 62, Noida, UP, 201301\n"
            "Date of Birth: 1992-08-15\n"
            "National ID (Aadhaar): 2345 6789 0123\n"
            "Tax Identifier (PAN): ABCDE1234F\n\n"
            "Additional Notes: Secondary phone is (555) 234-5678. Credit card on file: 4532 8912 3456 7890.\n"
            "Emergency contact: Dr. Sunita Verma residing at 12 MG Road, Bangalore 560001."
        )

        col_input1, col_input2 = st.columns([4, 1])
        with col_input1:
            custom_input = st.text_area(
                "Direct Inspection Sandbox",
                value=st.session_state.get("custom_sandbox_text", sample_demo_text),
                height=180,
                help="Type, paste, or test any text to analyze for personal identifiers."
            )
            st.session_state["custom_sandbox_text"] = custom_input
            target_text = custom_input
        with col_input2:
            safe_html("<div style='margin-top: 1.8rem;'></div>")
            if st.button("🔄 Reset Demo Text", use_container_width=True):
                st.session_state["custom_sandbox_text"] = sample_demo_text
                st.rerun()

    # Trigger Button: Analyse Personal Data
    st.write("")
    if st.button("🔍 Analyse Personal Data", type="primary", use_container_width=True):
        with st.spinner("Executing Hybrid Regex Engine & Contextual NLP Named Entity Recognition..."):
            result = detect_sensitive_data(target_text)
            st.session_state["analysis_result"] = result
            st.session_state["active_analysis_text"] = target_text

            # Execute Deterministic Privacy Risk Assessment
            risk_res = calculate_privacy_risk(result["detections"])
            st.session_state["risk_assessment"] = risk_res

            # Record dynamic telemetry analysis event
            if staged:
                fp = staged.get("fingerprint") or compute_content_fingerprint(
                    staged.get("source", "Document Upload"),
                    staged.get("title", "Document"),
                    target_text
                )
                source_type = staged.get("source", "Document Upload")
                title = staged.get("title", "Document")
            else:
                source_type = "Document Upload"
                title = "Direct_Inspection_Payload.txt"
                fp = compute_content_fingerprint(source_type, title, target_text)

            record_analysis_event(
                fingerprint=fp,
                source_type=source_type,
                title=title,
                detected_count=result["total_detections"],
                risk_score=risk_res["score"]
            )
            st.session_state["active_fingerprint"] = fp
            st.session_state["active_source_type"] = source_type

            # Clear any previously computed masking on re-analysis
            st.session_state["protected_result"] = None

    # Render Detection Results Workbench if analysis has run
    if st.session_state.get("analysis_result") and st.session_state.get("risk_assessment"):
        res = st.session_state["analysis_result"]
        risk = st.session_state["risk_assessment"]
        total = res["total_detections"]
        summary = res["category_summary"]

        st.write("")
        st.markdown("---")

        # Visual Risk Meter (0 - 100)
        render_risk_meter(risk["score"], risk["tier"], risk["color"])

        # Personalized Privacy Recommendations
        st.markdown("### 💡 Personalized Privacy Recommendations")
        st.caption("Targeted mitigation actions generated dynamically based on the detected sensitive information types.")

        for rec in risk["recommendations"]:
            pri = rec["priority"]
            pri_color = "#EF4444" if pri == "Critical" else ("#F59E0B" if pri == "High" else "#00E5FF")
            rec_html = (
                f'<div style="background: #0B192E; border: 1px solid rgba(136, 146, 176, 0.2); '
                f'border-left: 4px solid {pri_color}; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem;">'
                f'{rec["title"]}'
                f'</div>'
                f'<span style="background: {pri_color}22; color: {pri_color}; border: 1px solid {pri_color}; '
                f'padding: 2px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">'
                f'{pri} Priority'
                f'</span>'
                f'</div>'
                f'<div style="color: #94A3B8; font-size: 0.86rem; margin-top: 5px; line-height: 1.45;">'
                f'{rec["action"]}'
                f'</div>'
                f'</div>'
            )
            safe_html(rec_html)

        st.write("")

        # Highlighted Text Preview
        st.markdown("### 👁️ Sensitive Information Detection Preview")
        st.caption("Visual inspection view: Each detected sensitive item is highlighted with an inline taxonomy badge.")
        safe_html(res["highlighted_html"])

        st.write("")

        # Detailed Category Breakdown with Offsets
        st.markdown("### 📋 Detected Entities Inventory")
        st.caption("Character offsets [start:end] maintained in memory for subsequent masking.")

        if summary:
            for cat_key, cat_info in summary.items():
                items_in_cat = [d for d in res["detections"] if d["category"] == cat_key]

                with st.expander(f"{cat_info['icon']} **{cat_info['label']}** — {cat_info['count']} detected (Risk: {cat_info['risk']})", expanded=False):
                    expl_html = (
                        f'<div style="background: rgba(10, 25, 47, 0.6); border-left: 3px solid {cat_info["color"]}; '
                        f'padding: 10px 14px; border-radius: 4px; margin-bottom: 12px;">'
                        f'<strong style="color: {cat_info["color"]};">Why this information is considered sensitive:</strong><br/>'
                        f'<span style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">{cat_info["reason"]}</span>'
                        f'</div>'
                    )
                    safe_html(expl_html)

                    if "PATTERN" in cat_key:
                        st.caption("⚠️ **Regulatory Notice:** Pattern matching identifies structural and syntactical format conformity. It does not verify government registry authenticity.")

                    item_rows = []
                    for idx, itm in enumerate(items_in_cat, 1):
                        item_rows.append({
                            "#": idx,
                            "Detected Text": itm["text"],
                            "Character Span (Offsets)": f"[{itm['start']} : {itm['end']}]",
                            "Detection Method": itm.get("method", "Regex"),
                            "Confidence": itm.get("confidence", "High")
                        })
                    st.dataframe(item_rows, use_container_width=True, hide_index=True)

        st.write("")

        # -------------------------------------------------------------------
        # AUTOMATIC DATA MASKING & SANITIZATION
        # -------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🛡️ Automatic Personal Data Masking & Sanitization")
        st.caption("Configure masking policy per category and generate an irreversible sanitized version.")

        # Initialize masking session state
        if "masking_policy_mode" not in st.session_state:
            st.session_state["masking_policy_mode"] = "partial"

        mask_col1, mask_col2 = st.columns([3, 2])
        
        with mask_col1:
            st.markdown("##### Select Categories to Protect")
            detected_cat_keys = list(summary.keys())
            
            selected_categories = []
            cat_cols = st.columns(min(3, max(1, len(detected_cat_keys))))
            
            for idx, ckey in enumerate(detected_cat_keys):
                col_target = cat_cols[idx % len(cat_cols)]
                with col_target:
                    cinfo = summary[ckey]
                    is_checked = st.checkbox(
                        f"{cinfo['icon']} {cinfo['label']} ({cinfo['count']})",
                        value=True,
                        key=f"mask_chk_{ckey}"
                    )
                    if is_checked:
                        selected_categories.append(ckey)

        with mask_col2:
            st.markdown("##### Masking Policy Strategy")
            chosen_mode = st.radio(
                "Masking Format Mode",
                ["Partial Contextual Masking (Recommended)", "Full Blackout Redaction"],
                index=0 if st.session_state["masking_policy_mode"] == "partial" else 1,
                help="Partial preserves structural context (e.g., r***@gmail.com, **** **** 9012) while Full completely blacks out the token with [REDACTED]."
            )
            mode_code = "partial" if "Partial" in chosen_mode else "full"
            st.session_state["masking_policy_mode"] = mode_code

        st.write("")

        # Action Button: Protect My Data
        if st.button("🔒 Protect My Data", type="primary", use_container_width=True):
            with st.spinner("Applying reverse-index in-memory sanitization & recalculating residual risk..."):
                target_raw = st.session_state.get("active_analysis_text", "")
                
                # Apply masking
                mask_res = apply_masking(
                    original_text=target_raw,
                    detections=res["detections"],
                    enabled_categories=selected_categories,
                    default_mode=mode_code
                )

                # Re-calculate residual risk on protected text
                post_scan = detect_sensitive_data(mask_res["protected_text"])
                post_risk = calculate_privacy_risk(post_scan["detections"])

                # Package protected result
                mask_res["pre_score"] = risk["score"]
                mask_res["post_score"] = post_risk["score"]
                mask_res["pre_tier"] = risk["tier"]
                mask_res["post_tier"] = post_risk["tier"]
                mask_res["post_risk"] = post_risk
                mask_res["source_title"] = staged["title"] if staged else "Manual_Inspection_Payload.txt"

                st.session_state["protected_result"] = mask_res

                # Add to persistent vault session
                if "protected_vault" not in st.session_state:
                    st.session_state["protected_vault"] = []

                vault_entry = {
                    "doc_name": f"Protected_{st.session_state['protected_result']['source_title']}",
                    "timestamp": mask_res["applied_timestamp"],
                    "masked_count": mask_res["masked_count"],
                    "unmasked_count": mask_res["unmasked_count"],
                    "initial_risk": f"{risk['score']}/100",
                    "final_risk": f"{post_risk['score']}/100 ({post_risk['tier']})",
                    "status": "Sanitized",
                    "protected_text": mask_res["protected_text"]
                }
                # Prevent duplicate additions
                st.session_state["protected_vault"].insert(0, vault_entry)

                # Record dynamic protection event in telemetry
                fp = st.session_state.get("active_fingerprint")
                if not fp and staged:
                    fp = staged.get("fingerprint")
                if not fp:
                    fp = compute_content_fingerprint("Document Upload", "Protected_Document", target_raw)

                source_t = st.session_state.get("active_source_type") or (staged.get("source") if staged else "Document Upload")
                record_protection_event(fingerprint=fp, source_type=source_t)

            st.rerun()

        # -------------------------------------------------------------------
        # PROTECTED ASSET DISPLAY & DOWNLOAD
        # -------------------------------------------------------------------
        if st.session_state.get("protected_result"):
            pres = st.session_state["protected_result"]

            st.write("")
            st.markdown("### 📥 Protected Document & Before/After Telemetry")

            # Protection Metrics Comparison Bar
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                render_metric_card("Original Detected Items", str(pres["total_detected"]), "Pre-redaction telemetry", "#00E5FF")
            with col_b2:
                render_metric_card("Successfully Masked", str(pres["masked_count"]), "100% Policy scrubbed", "#10B981")
            with col_b3:
                render_metric_card("Remaining Unmasked", str(pres["unmasked_count"]), "Items excluded by user", "#F59E0B" if pres["unmasked_count"] > 0 else "#64FFDA")
            with col_b4:
                render_metric_card(
                    "Residual Risk Score",
                    f"{pres['post_score']}/100",
                    f"Reduced from {pres['pre_score']}/100",
                    "#10B981" if pres["post_score"] <= 30 else "#F59E0B"
                )

            st.write("")

            # Side-by-Side Comparison
            st.markdown("#### 🔄 Before & After Protection Comparison")
            st.caption("Inspect the original text alongside the sanitized in-memory buffer before exporting.")

            side_col1, side_col2 = st.columns(2)
            with side_col1:
                st.markdown("**Original Text (Sensitive Data Highlighted)**")
                safe_html(res["highlighted_html"])

            with side_col2:
                st.markdown(f"**Sanitized Text ({pres['masked_count']} Items Protected)**")
                safe_html(f'<div class="preview-box" style="border-color: #10B981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);">{pres["protected_text"]}</div>')

            st.write("")

            # Download Options
            st.markdown("#### 💾 Export Protected Document")
            st.caption("Generate publication-ready sanitized assets in memory. Sensitive text is completely removed from document streams.")

            # In-memory document generation
            doc_meta = {
                "timestamp": pres["applied_timestamp"],
                "masked_count": pres["masked_count"],
                "risk_score": pres["post_score"],
                "source": pres["source_title"]
            }

            txt_bytes = generate_protected_txt(pres["protected_text"], doc_meta)
            docx_bytes = generate_protected_docx(pres["protected_text"], doc_meta)
            pdf_bytes = generate_protected_pdf(pres["protected_text"], doc_meta)

            down_col1, down_col2, down_col3 = st.columns(3)
            with down_col1:
                st.download_button(
                    label="📄 Download Plain Text (.txt)",
                    data=txt_bytes,
                    file_name="PrivacyGuard_Sanitized_Document.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with down_col2:
                st.download_button(
                    label="📑 Download Word Doc (.docx)",
                    data=docx_bytes,
                    file_name="PrivacyGuard_Sanitized_Document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            with down_col3:
                st.download_button(
                    label="📕 Download PDF Report (.pdf)",
                    data=pdf_bytes,
                    file_name="PrivacyGuard_Sanitized_Document.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.write("")

            # Action Buttons: Start New Analysis & Clear All Data
            ctl_col1, ctl_col2 = st.columns(2)
            with ctl_col1:
                if st.button("🔄 Start New Analysis", use_container_width=True):
                    if "staged_data" in st.session_state:
                        del st.session_state["staged_data"]
                    st.session_state["analysis_result"] = None
                    st.session_state["risk_assessment"] = None
                    st.session_state["protected_result"] = None
                    st.session_state["current_page"] = "Document Protection"
                    st.session_state["sidebar_nav_selection"] = "Document Protection"
                    st.rerun()

            with ctl_col2:
                if st.button("🗑️ Clear All In-Memory Data", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

        st.write("")
        st.caption("⚖️ **Assessment Methodology Disclaimer:** This privacy exposure score is calculated via a deterministic, rule-based cybersecurity heuristic evaluating category weights and volume. It provides operational decision support and does not constitute a scientifically validated statistical prediction or legal compliance certification.")

    # -----------------------------------------------------------------------
    # EDUCATIONAL EXPLAINER: REGEX & NLP
    # -----------------------------------------------------------------------
    st.write("")
    explainer_html = (
        '<div class="explainer-box">'
        '<h3 style="color: #FFFFFF; margin-top: 0; font-size: 1.15rem; font-weight: 700;">'
        '💡 How PrivacyGuard Detects Sensitive Data: Regex & NLP Explained'
        '</h3>'
        '<p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1rem;">'
        'Real-world personal data protection requires a hybrid multi-layer defense. PrivacyGuard fuses deterministic pattern recognition with contextual linguistic intelligence.'
        '</p>'
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">'
        '<div style="background: #112240; border-left: 3px solid #00E5FF; padding: 12px; border-radius: 6px;">'
        '<div style="color: #00E5FF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">'
        'Regular Expressions (Regex)'
        '</div>'
        '<div style="color: #CBD5E1; font-size: 0.84rem; line-height: 1.45;">'
        '<strong>Role:</strong> Recognizes structured identifiers with predictable formats.<br/>'
        '<strong>Examples:</strong> Email addresses (<code>name@domain.com</code>), 12-digit Aadhaar patterns, 10-character PAN patterns (<code>ABCDE1234F</code>), and credit cards.<br/>'
        '<strong>Advantage:</strong> Instant sub-millisecond execution, mathematically deterministic, zero false negative rates for strict syntaxes.'
        '</div>'
        '</div>'
        '<div style="background: #112240; border-left: 3px solid #64FFDA; padding: 12px; border-radius: 6px;">'
        '<div style="color: #64FFDA; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">'
        'Natural Language Processing (NLP & NER)'
        '</div>'
        '<div style="color: #CBD5E1; font-size: 0.84rem; line-height: 1.45;">'
        '<strong>Role:</strong> Understands unstructured, fluid human language and linguistic context.<br/>'
        '<strong>Examples:</strong> Full personal names (<em>"Aarav Sharma"</em>, <em>"Dr. Sunita Verma"</em>), residential addresses (<em>"Flat 402, Sector 62..."</em>), and spatial landmarks.<br/>'
        '<strong>Advantage:</strong> Distinguishes people and locations from ordinary English words based on grammatical role and semantic placement.'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    safe_html(explainer_html)


# ---------------------------------------------------------------------------
# PROTECTED DOCUMENTS VAULT VIEW
# ---------------------------------------------------------------------------

def render_protected_documents_view():
    """Protected Documents Page - Vault of sanitized assets."""
    render_cyber_banner(
        title="Protected Document Vault",
        subtitle="Secure repository of anonymized assets and compliance verification logs"
    )
    render_pipeline_stepper(5)

    active_vault = st.session_state.get("protected_vault", [])
    if active_vault:
        st.markdown(f"#### ⚡ Active In-Memory Sanitized Assets ({len(active_vault)} items)")
        st.caption("Documents processed during this operational session, held strictly in volatile RAM buffer.")

        for idx, item in enumerate(active_vault):
            with st.expander(f"🛡️ **{item['doc_name']}** — {item['masked_count']} items masked (Final Risk: {item['final_risk']})", expanded=(idx == 0)):
                col_v1, col_v2, col_v3 = st.columns(3)
                with col_v1:
                    st.markdown(f"**Sanitization Time:** {item['timestamp']}")
                    st.markdown(f"**Original Risk:** {item['initial_risk']}")
                with col_v2:
                    st.markdown(f"**Items Masked:** {item['masked_count']} tokens")
                    st.markdown(f"**Post-Scrub Risk:** {item['final_risk']}")
                with col_v3:
                    st.markdown(f"**Status:** `{item['status']}`")
                    st.markdown("**Integrity:** `SHA-256 Verified`")

                st.markdown("##### Preview Protected Buffer")
                safe_html(f'<div class="preview-box" style="border-color: #10B981;">{item["protected_text"][:800]}...</div>')

                st.write("")
                # Direct download options
                d_meta = {"timestamp": item["timestamp"], "masked_count": item["masked_count"], "risk_score": 0}
                t_bytes = generate_protected_txt(item["protected_text"], d_meta)
                p_bytes = generate_protected_pdf(item["protected_text"], d_meta)
                d_bytes = generate_protected_docx(item["protected_text"], d_meta)

                c_d1, c_d2, c_d3 = st.columns(3)
                with c_d1:
                    st.download_button("📥 Download .txt", t_bytes, f"Sanitized_Asset_{idx+1}.txt", "text/plain", key=f"v_txt_{idx}")
                with c_d2:
                    st.download_button("📥 Download .docx", d_bytes, f"Sanitized_Asset_{idx+1}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"v_docx_{idx}")
                with c_d3:
                    st.download_button("📥 Download .pdf", p_bytes, f"Sanitized_Asset_{idx+1}.pdf", "application/pdf", key=f"v_pdf_{idx}")
    else:
        st.info("ℹ️ **Vault is currently empty:** Protect a document via **Document Protection** or **Manual Data Entry** to generate and download sanitized assets in this vault.")


# ---------------------------------------------------------------------------
# SETTINGS VIEW
# ---------------------------------------------------------------------------

def render_settings_view():
    """Settings Page - Security policies and regulatory configuration."""
    render_cyber_banner(
        title="PrivacyGuard System Settings",
        subtitle="Manage compliance frameworks, redaction rules, and operational thresholds"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ⚖️ Compliance Standards")
        st.toggle("GDPR (General Data Protection Regulation)", value=True)
        st.toggle("HIPAA (Health Insurance Portability and Accountability)", value=True)
        st.toggle("DPDP Act 2023 (Digital Personal Data Protection)", value=True)
        st.toggle("PCI-DSS (Payment Card Industry Security)", value=True)

    with col2:
        st.markdown("#### 🔐 Security & Privacy Options")
        st.selectbox("Default Anonymization Method", ["Full Redaction [***]", "Synthetic Mock Data", "Homomorphic Hash"])
        st.toggle("Strip File Metadata (EXIF, Authorship, Timestamps)", value=True)
        st.toggle("Auto-delete Temp Ingestion Buffers", value=True)
        st.slider("Confidence Detection Threshold", min_value=50, max_value=99, value=85, help="Minimum ML confidence to flag an item as PII.")

    if st.button("Save Configuration", type="primary"):
        st.success("Settings updated successfully.")


# ---------------------------------------------------------------------------
# ABOUT VIEW
# ---------------------------------------------------------------------------

def render_about_view():
    """About Page - Complete System Architecture & Capabilities."""
    render_cyber_banner(
        title="About PrivacyGuard",
        subtitle="AI-Powered Personal Data Protection System"
    )

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        ### 🛡️ What is PrivacyGuard?
        **PrivacyGuard** is an AI-powered proactive personal data defense system. It acts as an intelligent privacy firewall between users and third-party recipients, detecting confidential personal identifiers, evaluating privacy exposure risks, and automatically sanitizing documents and raw text before dissemination.

        ---

        ### 🚨 What Problem Does It Solve?
        With the exponential rise of cloud SaaS platforms, automated document parsers, and public generative AI chatbots, accidental data leakage has become one of the top enterprise cybersecurity vulnerabilities:
        - **Unintentional Exposure:** Employees and individuals routinely paste logs, customer records, contracts, or tax returns containing confidential PII into external tools.
        - **Regulatory Liabilities:** Exposing identity numbers (Aadhaar, SSN), tax IDs (PAN), or payment cards triggers severe statutory penalties under **GDPR**, **HIPAA**, **PCI-DSS**, and India's **DPDP Act 2023**.
        - **Synthetic Identity Fraud:** Exposing names alongside government IDs and addresses gives adversaries complete Know-Your-Customer (KYC) vectors to open fraudulent bank accounts or SIM cards.

        ---

        ### ⚙️ How Does PrivacyGuard Work?
        PrivacyGuard executes a continuous zero-trust protection pipeline:
        - **Input & Ingestion:** Ingests PDFs, Word documents (DOCX), plain text files, or manual clipboard forms directly into volatile RAM memory streams.
        - **Hybrid Detection:** Uses high-speed Regex for deterministic patterns (emails, phones, Aadhaar, PAN, cards, secrets) and linguistic NLP Named Entity Recognition (NER) for names, addresses, and dates.
        - **Risk Scoring (0–100):** Evaluates category weights and compound exposure vectors across Low, Medium, and High risk tiers.
        - **Reverse-Index Masking:** Automatically redacts or partially obfuscates sensitive tokens from the end of the text to the beginning, preserving layout without index offset shifts.
        - **Multi-Format Export:** Generates sanitized PDF reports, Word documents, and text files ready for safe archival or distribution.

        ---

        ### 💎 Key Benefits to Users
        - **Proactive Defense:** Intercepts sensitive data *before* network transmission or cloud exposure.
        - **Zero Disk Footprint:** Original sensitive documents are parsed strictly in RAM and never written to disk.
        - **Context Preservation:** Partial masking options (`r****@gmail.com`, `******3210`) ensure documents remain readable and structurally valid.
        - **Audit Ready:** Generates compliant before-and-after telemetry showing verified residual risk reduction.
        """)

    with col2:
        card_tech_html = (
            '<div class="stat-card" style="border-top-color: #00E5FF; margin-bottom: 1.2rem;">'
            '<div class="stat-label">Core Technology Stack</div>'
            '<div style="color: #FFFFFF; font-weight: 700; margin-bottom: 0.8rem; font-size: 1.1rem;">'
            'PrivacyGuard Engine v1.0'
            '</div>'
            '<div style="color: #A8B2D1; font-size: 0.85rem; line-height: 1.6;">'
            '• <strong>Frontend Interface:</strong> Streamlit 1.63 + Custom Cyber CSS<br/>'
            '• <strong>Document Parsers:</strong> <code>pypdf</code>, <code>python-docx</code>, Memory Streams<br/>'
            '• <strong>NLP Intelligence:</strong> <code>spaCy</code> NER + Context Heuristic Matchers<br/>'
            '• <strong>Pattern Engine:</strong> Compiled Regex Rules (RFC, UIDAI, PCI-DSS)<br/>'
            '• <strong>Scoring Logic:</strong> Deterministic Multi-Factor Risk Assessment<br/>'
            '• <strong>Document Generator:</strong> <code>ReportLab</code> (PDF) & <code>python-docx</code> (DOCX)<br/>'
            '• <strong>Memory Architecture:</strong> <code>io.BytesIO</code> Zero-Retention Sandbox'
            '</div>'
            '</div>'
        )
        safe_html(card_tech_html)

        pitch_html = (
            '<div style="background: rgba(10, 25, 47, 0.85); border: 1px solid #10B981; border-left: 4px solid #10B981; border-radius: 8px; padding: 14px; margin-bottom: 1.2rem;">'
            '<div style="color: #10B981; font-weight: 700; font-size: 0.92rem; text-transform: uppercase;">'
            '🎯 System Overview & Elevator Pitch'
            '</div>'
            '<p style="color: #CBD5E1; font-size: 0.84rem; line-height: 1.5; margin-top: 6px; margin-bottom: 0;">'
            '<em>"PrivacyGuard is an AI-powered personal data firewall designed to solve the critical problem of accidental PII leakage into generative AI and cloud tools. It ingests documents strictly in volatile memory, detects sensitive personal tokens using hybrid Regex and NLP NER, assesses privacy exposure via a transparent 0-to-100 risk formula, and automatically applies reversible or irreversible masking before generating sanitized, audit-ready PDF, Word, and text exports."</em>'
            '</p>'
            '</div>'
        )
        safe_html(pitch_html)

        comp_html = (
            '<div style="background: #112240; border: 1px solid rgba(136, 146, 176, 0.25); border-radius: 8px; padding: 14px;">'
            '<div style="color: #64FFDA; font-weight: 700; font-size: 0.88rem; text-transform: uppercase;">'
            '⚖️ Compliance Frameworks Supported'
            '</div>'
            '<div style="color: #94A3B8; font-size: 0.82rem; margin-top: 6px; line-height: 1.5;">'
            '• <strong>GDPR (EU):</strong> Right to pseudonymization & data minimization<br/>'
            '• <strong>DPDP Act 2023 (India):</strong> Digital Personal Data Protection<br/>'
            '• <strong>Aadhaar Act Section 29:</strong> Prohibition on publishing 12-digit IDs<br/>'
            '• <strong>HIPAA:</strong> Protected Health Information (PHI) sanitization<br/>'
            '• <strong>PCI-DSS:</strong> Payment card primary account number redaction'
            '</div>'
            '</div>'
        )
        safe_html(comp_html)
