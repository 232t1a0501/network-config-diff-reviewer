"""
utils.py
Small helper utilities shared across the app:
- reading uploaded / sample files as text
- building the final Markdown approval pack
- exporting the approval pack as a simple PDF
"""

from datetime import datetime
from typing import List, Dict
from fpdf import FPDF


def read_text_file(uploaded_file) -> str:
    """
    Read a Streamlit UploadedFile (or a plain file path) and return its
    text content as a UTF-8 string.
    """
    if hasattr(uploaded_file, "read"):
        content = uploaded_file.read()
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return content

    # fallback: treat as a file path
    with open(uploaded_file, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def build_markdown_report(
    old_name: str,
    new_name: str,
    diff_lines: List[str],
    changes: List[Dict],
    llm_summary: str,
) -> str:
    """
    Build the final Markdown "approval pack" combining the raw diff,
    the rule-based change list, and the LLM's plain-English explanation.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []
    md.append("# Network Config Diff - Approval Pack")
    md.append("")
    md.append(f"**Generated:** {timestamp}")
    md.append(f"**Old config:** `{old_name}`")
    md.append(f"**New config:** `{new_name}`")
    md.append("")

    md.append("## 1. Risk Summary")
    md.append("")
    if changes:
        md.append("| # | Risk Type | Line | Detail |")
        md.append("|---|-----------|------|--------|")
        for i, c in enumerate(changes, start=1):
            detail = c["detail"].replace("|", "\\|")
            md.append(f"| {i} | {c['risk_type']} | `{c['line'].strip()}` | {detail} |")
    else:
        md.append("_No high-risk patterns (ACL widened / route added / peer change) detected._")
    md.append("")

    md.append("## 2. AI Plain-English Review")
    md.append("")
    md.append(llm_summary if llm_summary else "_No AI summary available._")
    md.append("")

    md.append("## 3. Raw Unified Diff")
    md.append("")
    md.append("```diff")
    md.extend(line.rstrip("\n") for line in diff_lines)
    md.append("```")
    md.append("")

    md.append("## 4. Approval")
    md.append("")
    md.append("- [ ] Reviewed by Network Engineer")
    md.append("- [ ] Reviewed by Security Team")
    md.append("- [ ] Approved for deployment")
    md.append("")
    md.append("_This pack was generated automatically as a prototype aid. "
               "Final approval must be made by a human reviewer._")

    return "\n".join(md)


def markdown_to_pdf_bytes(markdown_text: str) -> bytes:
    """
    Very lightweight Markdown -> PDF conversion (text only, no rich
    rendering). Good enough for an approval-pack PDF export.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    # Effective printable width (works across fpdf2 versions)
    epw = getattr(pdf, "epw", pdf.w - pdf.l_margin - pdf.r_margin)

    for raw_line in markdown_text.split("\n"):
        line = raw_line.replace("\t", "    ")
        # Strip characters FPDF's default fonts cannot encode
        line = line.encode("latin-1", errors="replace").decode("latin-1")
        if not line.strip():
            pdf.ln(4)
            continue
        # Ensure X is at the left margin so remaining width is correct
        pdf.set_x(pdf.l_margin)
        # Simple heading emphasis
        if line.startswith("# "):
            pdf.set_font("Courier", "B", 14)
            pdf.multi_cell(epw, 8, line.replace("# ", ""), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Courier", size=10)
        elif line.startswith("## "):
            pdf.set_font("Courier", "B", 12)
            pdf.multi_cell(epw, 7, line.replace("## ", ""), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Courier", size=10)
        else:
            pdf.multi_cell(epw, 5, line, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
