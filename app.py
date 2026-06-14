"""
app.py
Network Config Diff Reviewer (IM-14)

A small Streamlit prototype that:
1. Takes two network-config text files (upload, or use bundled samples).
2. Diffs them with Python (difflib).
3. Runs a rule-based check for risky change types
   (ACL widened, route added, peer/BGP change, SNMP risk).
4. Sends the diff + flagged changes to the Gemini API, which explains
   each change in plain English and assigns a risk level.
5. Lets the user download a Markdown and/or PDF "approval pack".

Run with:  streamlit run app.py
"""

import csv
import io
import os
import sys

import streamlit as st

# Make sure `src/` is importable when running `streamlit run app.py`
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import importlib
import src.processor
import src.llm_helper
import src.utils

importlib.reload(src.processor)
importlib.reload(src.llm_helper)
importlib.reload(src.utils)

from src.processor import compute_diff, extract_changes, changes_to_csv_rows
from src.llm_helper import review_diff_with_llm, format_llm_result_as_markdown
from src.utils import read_text_file, build_markdown_report, markdown_to_pdf_bytes


SAMPLE_OLD_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_config_old.txt")
SAMPLE_NEW_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_config_new.txt")


st.set_page_config(page_title="Network Config Diff Reviewer", layout="wide")

st.title("🔍 Network Config Diff Reviewer")
st.caption(
    "IM-14 · Infra Maintenance · Diffs two network-config files, explains "
    "each change in plain English, flags risky changes (ACL widened, "
    "route added, peer change), and produces a Markdown/PDF approval pack."
)

# ---------------------------------------------------------------------------
# Sidebar: API key + model settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Get a free key from Google AI Studio (ai.google.dev). "
             "You can also set it as the GEMINI_API_KEY environment variable.",
    )
    model_name = st.selectbox(
        "Gemini model",
        ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        index=0,
    )
    use_samples = st.checkbox("Use bundled sample configs", value=True)

    st.markdown("---")
    st.markdown(
        "**About**\n\n"
        "This is a small prototype. It does **not** push config changes "
        "anywhere - it only reviews and summarizes diffs for human approval."
    )

# ---------------------------------------------------------------------------
# Step 1: Input - two config files
# ---------------------------------------------------------------------------
st.header("1. Input: Two Network Config Files")

col1, col2 = st.columns(2)

old_text, new_text = None, None
old_name, new_name = "old_config.txt", "new_config.txt"

with col1:
    st.subheader("Old / Current Config")
    old_file = st.file_uploader("Upload old config (.txt/.cfg)", type=["txt", "cfg", "conf"], key="old")
    if old_file is not None:
        old_text = read_text_file(old_file)
        old_name = old_file.name
    elif use_samples:
        old_text = read_text_file(SAMPLE_OLD_PATH)
        old_name = "sample_config_old.txt"

    if old_text:
        st.text_area("Old config preview", old_text, height=300, key="old_preview")

with col2:
    st.subheader("New / Proposed Config")
    new_file = st.file_uploader("Upload new config (.txt/.cfg)", type=["txt", "cfg", "conf"], key="new")
    if new_file is not None:
        new_text = read_text_file(new_file)
        new_name = new_file.name
    elif use_samples:
        new_text = read_text_file(SAMPLE_NEW_PATH)
        new_name = "sample_config_new.txt"

    if new_text:
        st.text_area("New config preview", new_text, height=300, key="new_preview")

# ---------------------------------------------------------------------------
# Step 2: Run the review
# ---------------------------------------------------------------------------
st.header("2. Run Diff + AI Review")

run_clicked = st.button("🚀 Run Diff Review", type="primary", disabled=not (old_text and new_text))

if run_clicked:
    with st.spinner("Computing diff..."):
        diff_lines = compute_diff(old_text, new_text, old_name, new_name)
        diff_text = "\n".join(diff_lines)
        changes = extract_changes(diff_lines)

    st.subheader("📄 Unified Diff")
    if diff_lines:
        st.code(diff_text, language="diff")
    else:
        st.info("No differences found between the two files.")

    st.subheader("🚩 Rule-Based Risk Flags")
    if changes:
        st.table(changes_to_csv_rows(changes))
    else:
        st.success("No ACL-widening, new routes, or peer changes detected by the rule-based check.")

    st.subheader("🤖 AI Plain-English Review (Gemini)")
    with st.spinner("Asking Gemini to review the diff..."):
        llm_result = review_diff_with_llm(
            diff_text=diff_text,
            changes=changes,
            api_key=api_key,
            model_name=model_name,
        )

    llm_markdown = format_llm_result_as_markdown(llm_result)
    st.markdown(llm_markdown)

    # -----------------------------------------------------------------------
    # Step 3: Build & download the approval pack
    # -----------------------------------------------------------------------
    st.header("3. Download Approval Pack")

    report_md = build_markdown_report(old_name, new_name, diff_lines, changes, llm_markdown)

    colA, colB, colC = st.columns(3)

    with colA:
        st.download_button(
            "⬇️ Download Markdown Report",
            data=report_md,
            file_name="config_diff_approval_pack.md",
            mime="text/markdown",
        )

    with colB:
        try:
            pdf_bytes = markdown_to_pdf_bytes(report_md)
            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name="config_diff_approval_pack.pdf",
                mime="application/pdf",
            )
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            try:
                with open("outputs/failed_report.md", "w", encoding="utf-8") as f:
                    f.write(report_md)
            except Exception:
                pass
            st.warning(f"PDF export unavailable: {exc}")

    with colC:
        if changes:
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=["risk_type", "change", "config_line", "detail"])
            writer.writeheader()
            writer.writerows(changes_to_csv_rows(changes))
            st.download_button(
                "⬇️ Download Flags (CSV)",
                data=csv_buffer.getvalue(),
                file_name="config_diff_flags.csv",
                mime="text/csv",
            )
        else:
            st.caption("No flags to export as CSV.")

else:
    st.info("Set up your config files above, then click **Run Diff Review**.")
