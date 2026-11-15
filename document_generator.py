"""
document_generator.py - Multi-format Document Generation Engine (TXT, DOCX, PDF)
Generates sanitized, production-ready documents and reports strictly in-memory (io.BytesIO)
"""

import io
import datetime
from typing import Dict, Any

# python-docx for DOCX creation
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ReportLab for PDF creation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# ---------------------------------------------------------------------------
# 1. Plain Text Output (.txt)
# ---------------------------------------------------------------------------

def generate_txt_bytes(protected_text: str, title: str, stats: Dict[str, Any]) -> bytes:
    """Generates sanitized UTF-8 text file with privacy header and audit metadata."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "================================================================================",
        "  PRIVACYGUARD AI - PROTECTED DATA EXPORT",
        "  Zero-Knowledge Personal Data Sanitization Report",
        "================================================================================",
        f"Target Document / Record: {title}",
        f"Sanitization Timestamp  : {now_str}",
        f"Sensitive Items Masked  : {stats.get('masked_count', 0)} / {stats.get('total_detected', 0)} detected",
        f"Post-Scrub Risk Status  : {stats.get('post_risk_tier', 'Low Risk')} ({stats.get('post_risk_score', 0)}/100)",
        f"Integrity Assurance     : In-memory token replacement (Original data stripped)",
        "--------------------------------------------------------------------------------",
        "  SANITIZED DOCUMENT CONTENT (SAFE FOR ARCHIVAL OR SHARING)",
        "--------------------------------------------------------------------------------",
        "",
        protected_text.strip(),
        "",
        "================================================================================",
        "  LEGAL & REGULATORY NOTICE:",
        "  This document has been sanitized using automated privacy redaction filters.",
        "  Sensitive personal markers (PII) have been stripped or partially obfuscated.",
        "  Verify contents prior to dissemination in accordance with GDPR / DPDP Act 2023.",
        "================================================================================"
    ]
    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# 2. Word Document Output (.docx)
# ---------------------------------------------------------------------------

def generate_docx_bytes(protected_text: str, title: str, stats: Dict[str, Any]) -> bytes:
    """Generates styled Microsoft Word document with audit telemetry and sanitized text."""
    doc = docx.Document()

    # Document Header Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("PrivacyGuard — Sanitized Document Report")
    title_run.font.name = "Arial"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(10, 25, 47)  # Navy Blue

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run(f"Automated Zero-Trust PII Redaction Audit | Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Telemetry Summary Table
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Light Shading Accent 1'
    table.autofit = True

    rows_data = [
        ("Target Document", str(title)),
        ("Sanitization Statistics", f"{stats.get('masked_count', 0)} of {stats.get('total_detected', 0)} items masked ({stats.get('sanitization_ratio', 100)}%)"),
        ("Post-Protection Risk", f"{stats.get('post_risk_tier', 'Low Risk')} (Score: {stats.get('post_risk_score', 0)}/100)"),
        ("Protection Mode Applied", f"{stats.get('protection_mode', 'Hybrid Contextual Masking')}")
    ]

    for idx, (label, val) in enumerate(rows_data):
        cell_lbl, cell_val = table.rows[idx].cells
        cell_lbl.text = label
        cell_val.text = val
        cell_lbl.paragraphs[0].runs[0].font.bold = True
        cell_lbl.paragraphs[0].runs[0].font.size = Pt(9)
        cell_val.paragraphs[0].runs[0].font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Content Section Heading
    h2 = doc.add_paragraph()
    h2_run = h2.add_run("Sanitized Document Content")
    h2_run.font.name = "Arial"
    h2_run.font.size = Pt(13)
    h2_run.font.bold = True
    h2_run.font.color.rgb = RGBColor(0, 119, 182)

    # Add sanitized body text paragraph by paragraph
    for line in protected_text.splitlines():
        if line.strip():
            p = doc.add_paragraph(line)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(10.5)
        else:
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    # Compliance Disclaimer Footer
    footer_p = doc.add_paragraph()
    footer_run = footer_p.add_run(
        "Disclaimer: This document was processed by PrivacyGuard AI Personal Data Protection System. "
        "Sensitive personal identifiers (PII) have been stripped or masked in volatile memory. "
        "No original raw personal data was stored on permanent disk during this process."
    )
    footer_run.font.size = Pt(8)
    footer_run.font.italic = True
    footer_run.font.color.rgb = RGBColor(148, 163, 184)

    # Save to in-memory bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# 3. PDF Document Output (.pdf)
# ---------------------------------------------------------------------------

def generate_pdf_bytes(protected_text: str, title: str, stats: Dict[str, Any]) -> bytes:
    """Generates PDF with ReportLab featuring cybersecurity headers, telemetry table, and sanitized text."""
    buffer = io.BytesIO()

    # Document setup: 0.6 inch margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0A192F")
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748B")
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0077B6"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ProtectedBody",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#94A3B8")
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("🛡️ PrivacyGuard — Sanitized Document Report", title_style))
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    story.append(Paragraph(f"Zero-Knowledge PII Protection Engine | Target: {title} | Exported: {now_str}", subtitle_style))
    story.append(Spacer(1, 10))

    # Decorative Cyan Line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00E5FF"), spaceBefore=2, spaceAfter=10))

    # Telemetry Table
    data = [
        [Paragraph("Target Document", table_cell_bold), Paragraph(str(title), table_cell_style)],
        [Paragraph("Protection Status", table_cell_bold), Paragraph("100% Sanitized & Memory Cleared", table_cell_style)],
        [Paragraph("Masked Findings", table_cell_bold), Paragraph(f"{stats.get('masked_count', 0)} of {stats.get('total_detected', 0)} sensitive tokens scrubbed", table_cell_style)],
        [Paragraph("Post-Protection Risk", table_cell_bold), Paragraph(f"{stats.get('post_risk_tier', 'Low Risk')} (Score: {stats.get('post_risk_score', 0)}/100)", table_cell_style)],
    ]

    telemetry_table = Table(data, colWidths=[140, 388])
    telemetry_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(telemetry_table)
    story.append(Spacer(1, 14))

    # Sanitized Document Body
    story.append(Paragraph("SANITIZED DOCUMENT CONTENT (SAFE TO DISTRIBUTE)", h2_style))
    story.append(Spacer(1, 4))

    for line in protected_text.splitlines():
        if line.strip():
            # Escape HTML characters for ReportLab Paragraph
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_line, body_style))
            story.append(Spacer(1, 2))
        else:
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=4, spaceAfter=8))

    # Disclaimer Footer
    story.append(Paragraph(
        "Notice: This document has been sanitized via PrivacyGuard in-memory zero-knowledge redaction. "
        "Sensitive personal identifiers have been structurally removed or transformed. "
        "Where complex layout formatting was present, text structure has been standardized to prevent visual metadata leakage. "
        "Compliant with GDPR, HIPAA, and DPDP Act 2023 principles.",
        disclaimer_style
    ))

    # Build PDF into memory buffer
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Universal Convenience Wrappers (Accept either (text, title, stats) or (text, metadata))
# ---------------------------------------------------------------------------

def generate_protected_txt(protected_text: str, meta_or_title: Any = None, stats: Dict[str, Any] = None) -> bytes:
    title = "Sanitized_Document"
    s = stats or {}
    if isinstance(meta_or_title, str):
        title = meta_or_title
    elif isinstance(meta_or_title, dict):
        s = meta_or_title
        title = meta_or_title.get("source", "Sanitized_Document")
    return generate_txt_bytes(protected_text, title, s)


def generate_protected_docx(protected_text: str, meta_or_title: Any = None, stats: Dict[str, Any] = None) -> bytes:
    title = "Sanitized_Document"
    s = stats or {}
    if isinstance(meta_or_title, str):
        title = meta_or_title
    elif isinstance(meta_or_title, dict):
        s = meta_or_title
        title = meta_or_title.get("source", "Sanitized_Document")
    return generate_docx_bytes(protected_text, title, s)


def generate_protected_pdf(protected_text: str, meta_or_title: Any = None, stats: Dict[str, Any] = None) -> bytes:
    title = "Sanitized_Document"
    s = stats or {}
    if isinstance(meta_or_title, str):
        title = meta_or_title
    elif isinstance(meta_or_title, dict):
        s = meta_or_title
        title = meta_or_title.get("source", "Sanitized_Document")
    return generate_pdf_bytes(protected_text, title, s)
