"""
tests/test_basic.py
Happy-path tests for the rule-based diff/processing logic.
These do NOT call the Gemini API, so they run without any API key.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.processor import compute_diff, extract_changes, changes_to_csv_rows
from src.utils import build_markdown_report, read_text_file


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_samples():
    old_text = read_text_file(os.path.join(DATA_DIR, "sample_config_old.txt"))
    new_text = read_text_file(os.path.join(DATA_DIR, "sample_config_new.txt"))
    return old_text, new_text


def test_compute_diff_detects_changes():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    assert len(diff_lines) > 0, "Expected a non-empty diff between sample configs"


def test_extract_changes_flags_acl_widened():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)

    risk_types = {c["risk_type"] for c in changes}
    assert "ACL Widened" in risk_types, "Expected the new 'permit ip any any' line to be flagged as ACL Widened"


def test_extract_changes_flags_route_added():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)

    risk_types = {c["risk_type"] for c in changes}
    assert "Route Added" in risk_types, "Expected the new 172.16.0.0/16 route to be flagged as Route Added"


def test_extract_changes_flags_peer_change():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)

    risk_types = {c["risk_type"] for c in changes}
    assert "Peer Change" in risk_types, "Expected the BGP remote-as change to be flagged as Peer Change"


def test_changes_to_csv_rows_shape():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)
    rows = changes_to_csv_rows(changes)

    assert len(rows) == len(changes)
    for row in rows:
        assert set(row.keys()) == {"risk_type", "change", "config_line", "detail"}


def test_build_markdown_report_contains_sections():
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)

    report = build_markdown_report("old.txt", "new.txt", diff_lines, changes, "AI summary placeholder")

    assert "# Network Config Diff - Approval Pack" in report
    assert "## 1. Risk Summary" in report
    assert "## 2. AI Plain-English Review" in report
    assert "## 3. Raw Unified Diff" in report
    assert "## 4. Approval" in report


def test_markdown_to_pdf_bytes():
    from src.utils import markdown_to_pdf_bytes
    old_text, new_text = _load_samples()
    diff_lines = compute_diff(old_text, new_text, "old.txt", "new.txt")
    changes = extract_changes(diff_lines)
    report = build_markdown_report("old.txt", "new.txt", diff_lines, changes, "AI summary placeholder")

    pdf_bytes = markdown_to_pdf_bytes(report)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-")
