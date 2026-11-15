"""
components.py - Reusable visual components for PrivacyGuard
"""

import streamlit as st
import pandas as pd
from styles import get_logo_html


def render_pipeline_stepper(current_step: int = 1):
    """
    Renders an interactive workflow progress tracker showing pipeline modules:
    Input -> Detection -> Risk Assessment -> Masking -> Download
    Does not use numbered steps or stages.
    """
    steps = [
        (1, "Input", "Ingestion"),
        (2, "Detection", "PII Scanning"),
        (3, "Risk Assessment", "Risk Scoring"),
        (4, "Masking", "Sanitization"),
        (5, "Download", "Export & Vault"),
    ]

    items_html = []
    for step_num, name, desc in steps:
        if step_num < current_step:
            # Completed stage
            badge = (
                f'<div style="flex: 1; min-width: 130px; background: rgba(16, 185, 129, 0.12); '
                f'border: 1px solid #10B981; border-radius: 8px; padding: 8px 12px; text-align: center;">'
                f'<div style="color: #10B981; font-size: 0.72rem; font-weight: 800; text-transform: uppercase;">✓ COMPLETED</div>'
                f'<div style="color: #FFFFFF; font-size: 0.92rem; font-weight: 700; margin-top: 2px;">{name}</div>'
                f'<div style="color: #94A3B8; font-size: 0.72rem;">{desc}</div>'
                f'</div>'
            )
        elif step_num == current_step:
            # Active stage
            badge = (
                f'<div style="flex: 1; min-width: 130px; background: rgba(0, 229, 255, 0.18); '
                f'border: 2px solid #00E5FF; border-radius: 8px; padding: 8px 12px; text-align: center; '
                f'box-shadow: 0 0 15px rgba(0, 229, 255, 0.35);">'
                f'<div style="color: #00E5FF; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; display: flex; align-items: center; justify-content: center; gap: 5px;">'
                f'<span class="status-dot" style="width: 6px; height: 6px; background-color: #00E5FF;"></span> ACTIVE'
                f'</div>'
                f'<div style="color: #FFFFFF; font-size: 0.95rem; font-weight: 800; margin-top: 2px;">{name}</div>'
                f'<div style="color: #64FFDA; font-size: 0.72rem; font-weight: 600;">{desc}</div>'
                f'</div>'
            )
        else:
            # Upcoming stage
            badge = (
                f'<div style="flex: 1; min-width: 130px; background: rgba(15, 23, 42, 0.6); '
                f'border: 1px solid rgba(136, 146, 176, 0.2); border-radius: 8px; padding: 8px 12px; text-align: center; opacity: 0.7;">'
                f'<div style="color: #8892B0; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">PENDING</div>'
                f'<div style="color: #94A3B8; font-size: 0.9rem; font-weight: 600; margin-top: 2px;">{name}</div>'
                f'<div style="color: #64748B; font-size: 0.72rem;">{desc}</div>'
                f'</div>'
            )
        items_html.append(badge)

    badges_joined = "".join(items_html)
    stepper_html = (
        f'<div style="margin-bottom: 1.5rem; background: #0A192F; border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 10px; padding: 12px 14px;">'
        f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center; justify-content: space-between;">'
        f'{badges_joined}'
        f'</div>'
        f'</div>'
    )
    st.markdown(stepper_html, unsafe_allow_html=True)


def render_cyber_banner(title="Security Operations Dashboard", subtitle="Real-time monitoring and personal data protection engine"):
    """Renders the top cybersecurity banner with system status."""
    banner_html = (
        f'<div class="cyber-header">'
        f'<div>'
        f'<h1 class="cyber-header-title">🛡️ {title}</h1>'
        f'<p class="cyber-header-subtitle">{subtitle}</p>'
        f'</div>'
        f'<div class="status-badge">'
        f'<span class="status-dot"></span> ACTIVE DEFENSE READY'
        f'</div>'
        f'</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, subtext: str, border_color="#00E5FF"):
    """Renders a single metric KPI card with cybersecurity theme."""
    card_html = (
        f'<div class="stat-card" style="border-top-color: {border_color};">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        f'<div class="stat-sub">{subtext}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_risk_meter(score: int, tier: str, color: str):
    """
    Renders an interactive cybersecurity visual risk meter
    segmented into Low (0-30), Medium (31-60), and High (61-100) risk.
    """
    pct = max(0, min(100, score))

    meter_html = (
        f'<div style="background: #0B192E; border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem;">'
        f'<div>'
        f'<span style="color: #8892B0; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">'
        f'Privacy Exposure Meter'
        f'</span>'
        f'<div style="display: flex; align-items: baseline; gap: 10px; margin-top: 4px;">'
        f'<span style="font-size: 2.8rem; font-weight: 800; color: #FFFFFF; font-family: \'JetBrains Mono\', monospace; line-height: 1;">{score}</span>'
        f'<span style="color: #8892B0; font-size: 1.1rem; font-weight: 600;">/100</span>'
        f'<span style="background: {color}22; border: 1px solid {color}; color: {color}; padding: 4px 12px; border-radius: 16px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">{tier}</span>'
        f'</div>'
        f'</div>'
        f'<div style="text-align: right;">'
        f'<span style="color: #8892B0; font-size: 0.78rem;">Compliance Thresholds</span>'
        f'<div style="color: #CBD5E1; font-size: 0.8rem; margin-top: 2px;">'
        f'<span style="color: #10B981;">0-30 Low</span> • '
        f'<span style="color: #F59E0B;">31-60 Medium</span> • '
        f'<span style="color: #EF4444;">61-100 High</span>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div style="position: relative; width: 100%; height: 16px; border-radius: 8px; background: #172A45; overflow: hidden; margin-bottom: 8px; display: flex;">'
        f'<div style="width: 30%; height: 100%; background: linear-gradient(90deg, #059669, #10B981);" title="Low Risk (0-30)"></div>'
        f'<div style="width: 30%; height: 100%; background: linear-gradient(90deg, #D97706, #F59E0B);" title="Medium Risk (31-60)"></div>'
        f'<div style="width: 40%; height: 100%; background: linear-gradient(90deg, #DC2626, #EF4444);" title="High Risk (61-100)"></div>'
        f'</div>'
        f'<div style="position: relative; width: 100%; height: 20px;">'
        f'<div style="position: absolute; left: {pct}%; transform: translateX(-50%); text-align: center; transition: left 0.5s ease;">'
        f'<div style="width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 8px solid {color}; margin: 0 auto;"></div>'
        f'<span style="font-size: 0.72rem; font-weight: 700; color: {color}; font-family: \'JetBrains Mono\', monospace;">▲ {score}%</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(meter_html, unsafe_allow_html=True)


def render_action_card(title: str, description: str, icon: str, page_target: str, button_key: str):
    """Renders an interactive action card with description and navigation trigger."""
    card_html = (
        f'<div class="action-card">'
        f'<div>'
        f'<div class="action-card-icon">{icon}</div>'
        f'<div class="action-card-title">{title}</div>'
        f'<div class="action-card-desc">{description}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
    if st.button(f"Launch {title} →", key=button_key, use_container_width=True):
        st.session_state["current_page"] = page_target
        st.rerun()


def render_how_it_works():
    """Renders the explanation of PrivacyGuard's core pipeline without numbering steps."""
    top_html = (
        '<div class="workflow-container">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.2rem;">'
        '<div>'
        '<h3 style="color: #FFFFFF; margin: 0; font-size: 1.25rem; font-weight: 700;">'
        '⚡ How PrivacyGuard Protects Your Data'
        '</h3>'
        '<p style="color: #8892B0; font-size: 0.88rem; margin: 0.2rem 0 0 0;">'
        'Autonomous multi-stage pipeline designed for proactive PII exposure defense'
        '</p>'
        '</div>'
        '<span style="font-size: 0.8rem; background: rgba(0, 229, 255, 0.1); color: #00E5FF; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(0, 229, 255, 0.2);">'
        'Zero-Knowledge Processing'
        '</span>'
        '</div>'
    )
    st.markdown(top_html, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        s1 = (
            '<div class="workflow-step">'
            '<div class="workflow-step-title" style="margin-top: 0.4rem;">Ingest & Parse</div>'
            '<div class="workflow-step-desc">Accepts unstructured documents (PDF, DOCX, TXT) or raw clipboard text into isolated sandbox buffers.</div>'
            '</div>'
        )
        st.markdown(s1, unsafe_allow_html=True)

    with col2:
        s2 = (
            '<div class="workflow-step">'
            '<div class="workflow-step-title" style="margin-top: 0.4rem;">PII Detection</div>'
            '<div class="workflow-step-desc">Applies contextual NLP models to locate SSNs, credit cards, credentials, medical codes, and personal IDs.</div>'
            '</div>'
        )
        st.markdown(s2, unsafe_allow_html=True)

    with col3:
        s3 = (
            '<div class="workflow-step">'
            '<div class="workflow-step-title" style="margin-top: 0.4rem;">Mask & Tokenize</div>'
            '<div class="workflow-step-desc">Transforms sensitive tokens with irreversible redaction, synthetic replacement, or cryptographic hashes.</div>'
            '</div>'
        )
        st.markdown(s3, unsafe_allow_html=True)

    with col4:
        s4 = (
            '<div class="workflow-step">'
            '<div class="workflow-step-title" style="margin-top: 0.4rem;">Export & Audit</div>'
            '<div class="workflow-step-desc">Generates sanitized, production-ready files with compliance risk scores and privacy protection reports.</div>'
            '</div>'
        )
        st.markdown(s4, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
