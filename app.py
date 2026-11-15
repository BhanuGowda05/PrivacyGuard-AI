"""
app.py - PrivacyGuard: AI-Powered Personal Data Protection System
Main Application Entrypoint & Navigation Router
"""

import streamlit as st
from styles import get_custom_css, get_logo_html
from views import (
    render_dashboard_view,
    render_document_protection_view,
    render_manual_data_entry_view,
    render_privacy_analysis_view,
    render_protected_documents_view,
    render_settings_view,
    render_about_view,
)

# 1. Page Configuration
st.set_page_config(
    page_title="PrivacyGuard - AI Personal Data Protection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom Cybersecurity CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 3. State Management for Navigation
PAGES = [
    "Dashboard",
    "Document Protection",
    "Manual Data Entry",
    "Privacy Analysis",
    "Protected Documents",
    "Settings",
    "About",
]

PAGE_ICONS = {
    "Dashboard": "📊",
    "Document Protection": "📄",
    "Manual Data Entry": "⌨️",
    "Privacy Analysis": "🔍",
    "Protected Documents": "🔒",
    "Settings": "⚙️",
    "About": "ℹ️",
}

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# 4. Sidebar Construction
with st.sidebar:
    # Logo Section
    st.markdown(get_logo_html(size=46), unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(0, 229, 255, 0.2); margin: 1.2rem 0;' />", unsafe_allow_html=True)

    st.markdown("<div style='color: #8892B0; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.6rem;'>Navigation Menu</div>", unsafe_allow_html=True)

    current_idx = PAGES.index(st.session_state["current_page"]) if st.session_state["current_page"] in PAGES else 0

    selected_page = st.radio(
        label="Navigation Menu",
        options=PAGES,
        index=current_idx,
        format_func=lambda page: f"{PAGE_ICONS.get(page, '•')}  {page}",
        label_visibility="collapsed",
        key=f"sidebar_nav_{st.session_state['current_page']}"
    )

    if selected_page != st.session_state["current_page"]:
        st.session_state["current_page"] = selected_page
        st.rerun()

    # Sidebar Status & Environment Footer
    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(10, 25, 47, 0.8); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 8px; padding: 12px;">
        <div style="color: #64FFDA; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px;">
            ● SYSTEM ACTIVE
        </div>
        <div style="color: #FFFFFF; font-size: 0.85rem; font-weight: 600;">
            Zero-Trust Sandbox
        </div>
        <div style="color: #8892B0; font-size: 0.75rem; margin-top: 2px;">
            Local Environment • v1.0.0
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Page Router
current = st.session_state["current_page"]

if current == "Dashboard":
    render_dashboard_view()
elif current == "Document Protection":
    render_document_protection_view()
elif current == "Manual Data Entry":
    render_manual_data_entry_view()
elif current == "Privacy Analysis":
    render_privacy_analysis_view()
elif current == "Protected Documents":
    render_protected_documents_view()
elif current == "Settings":
    render_settings_view()
elif current == "About":
    render_about_view()
else:
    render_dashboard_view()

# 6. Global Footer
st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; border-top: 1px solid rgba(136, 146, 176, 0.15); padding-top: 1.2rem; color: #8892B0; font-size: 0.8rem;">
    <strong>PrivacyGuard</strong> — AI-Powered Personal Data Protection System
</div>
""", unsafe_allow_html=True)
