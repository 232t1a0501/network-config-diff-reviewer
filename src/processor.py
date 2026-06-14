"""
processor.py
Core "Processing" stage of the pipeline:
1. Compute a unified diff between two network-config text files.
2. Apply simple rule-based checks to flag risky change types:
   - ACL widened (e.g. a new broad 'permit ... any any' rule)
   - Route added (a new 'ip route' line)
   - Peer change (a changed 'neighbor ... remote-as' / BGP peer line)
"""

import difflib
from typing import List, Dict, Tuple


def compute_diff(old_text: str, new_text: str, old_name: str, new_name: str) -> List[str]:
    """
    Return a unified diff (list of lines) between old_text and new_text.
    """
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=old_name,
        tofile=new_name,
        lineterm="",
    )
    return list(diff)


def _classify_line(line: str, added: bool) -> Tuple[str, str]:
    """
    Given a single config line (without the leading +/-), return a
    (risk_type, detail) tuple if it matches a known risky pattern,
    otherwise ("", "").
    """
    stripped = line.strip().lower()

    # --- ACL related ---
    if stripped.startswith("permit") or stripped.startswith("deny"):
        if "any any" in stripped or stripped == "permit ip any any":
            if added and stripped.startswith("permit"):
                return ("ACL Widened", "A broad 'permit ip any any' rule was added to an ACL.")
        if added and stripped.startswith("permit"):
            return ("ACL Rule Added", "A new permit rule was added to an ACL.")
        if not added and stripped.startswith("permit"):
            return ("ACL Rule Removed", "A permit rule was removed from an ACL - access may be tightened or broken.")

    # --- Routing related ---
    if stripped.startswith("ip route"):
        if added:
            return ("Route Added", "A new static route was added.")
        else:
            return ("Route Removed", "An existing static route was removed.")

    # --- BGP / Peer related ---
    if "neighbor" in stripped and ("remote-as" in stripped or "description" in stripped or "password" in stripped):
        if "remote-as" in stripped:
            return ("Peer Change", "A BGP neighbor's remote-as (peer AS number) was changed - this can change trust/routing relationships.")
        if "description" in stripped:
            return ("Peer Change", "A BGP neighbor's description was changed.")
        if "password" in stripped:
            return ("Peer Change", "A BGP neighbor's authentication password line was changed.")

    # --- SNMP / management related (extra safety net) ---
    if stripped.startswith("snmp-server community"):
        if "rw" in stripped:
            return ("SNMP Risk", "SNMP community was set to RW (read-write) - this is a significant security risk.")
        return ("SNMP Change", "SNMP community configuration was changed.")

    return ("", "")


def extract_changes(diff_lines: List[str]) -> List[Dict]:
    """
    Walk the unified diff output and return a list of dicts describing
    each detected risky change:
        {
            "risk_type": "ACL Widened" | "Route Added" | "Peer Change" | ...,
            "line": "<the changed config line>",
            "change": "added" | "removed",
            "detail": "<human readable detail>"
        }
    """
    changes = []
    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") :
            risk_type, detail = _classify_line(line[1:], added=True)
            if risk_type:
                changes.append({
                    "risk_type": risk_type,
                    "line": line[1:],
                    "change": "added",
                    "detail": detail,
                })
        elif line.startswith("-"):
            risk_type, detail = _classify_line(line[1:], added=False)
            if risk_type:
                changes.append({
                    "risk_type": risk_type,
                    "line": line[1:],
                    "change": "removed",
                    "detail": detail,
                })
    return changes


def changes_to_csv_rows(changes: List[Dict]) -> List[Dict]:
    """
    Convert the changes list into flat rows suitable for writing to CSV.
    """
    rows = []
    for c in changes:
        rows.append({
            "risk_type": c["risk_type"],
            "change": c["change"],
            "config_line": c["line"].strip(),
            "detail": c["detail"],
        })
    return rows
