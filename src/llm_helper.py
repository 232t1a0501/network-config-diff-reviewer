"""
llm_helper.py
Wraps calls to the Google Gemini API (free tier) to get a plain-English
explanation of a network-config diff, plus a structured risk summary.

The model is asked to return STRICT JSON so the rest of the app can
treat the AI output as structured data (see section 9 / "LLM Structured
Output" in the project guide).
"""

import json
import os
from typing import Dict, List

import google.generativeai as genai


DEFAULT_MODEL = "gemini-2.5-flash"


SYSTEM_INSTRUCTIONS = """You are a senior network security reviewer.
You will be given:
1. A unified diff of two router/firewall configuration files.
2. A list of changes that a rule-based tool already flagged as
   potentially risky (ACL widened, route added, peer/BGP change, etc.)

Your job:
- Explain, in plain English, what changed and why it matters operationally.
- For EACH flagged change, classify its risk level as "Low", "Medium", or "High".
- Call out anything that looks like it widens access, opens routing to new
  networks, or changes trust relationships with external peers.
- Note any assumptions or limitations (e.g. you cannot see live traffic,
  cannot confirm intent of the change).

Return ONLY valid JSON (no markdown fences, no extra commentary) with this
exact structure:

{
  "overall_summary": "<2-4 sentence plain-English summary of the diff>",
  "risk_level_overall": "Low" | "Medium" | "High",
  "findings": [
    {
      "risk_type": "<short label, e.g. ACL Widened>",
      "line": "<the config line involved>",
      "plain_english": "<what this change means in plain English>",
      "risk_level": "Low" | "Medium" | "High",
      "recommended_action": "<what the reviewer should do>"
    }
  ],
  "assumptions_and_limitations": "<short text>"
}
"""


def _build_user_prompt(diff_text: str, changes: List[Dict]) -> str:
    changes_json = json.dumps(changes, indent=2)
    return f"""DIFF:
{diff_text}

RULE-BASED FLAGGED CHANGES:
{changes_json}

Respond with the JSON object described in the system instructions only."""


def configure_gemini(api_key: str = None) -> bool:
    """
    Configure the Gemini client with the given API key (or fall back to
    the GEMINI_API_KEY environment variable). Returns True if a key was
    set, False otherwise.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return False
    genai.configure(api_key=key)
    return True


def review_diff_with_llm(
    diff_text: str,
    changes: List[Dict],
    api_key: str = None,
    model_name: str = DEFAULT_MODEL,
) -> Dict:
    """
    Send the diff + rule-based findings to Gemini and return a parsed
    dict matching the JSON schema described in SYSTEM_INSTRUCTIONS.

    On any failure (no key, network error, bad JSON), returns a dict
    with an "error" key so the UI can show a friendly message instead
    of crashing.
    """
    if not configure_gemini(api_key):
        return {"error": "No Gemini API key configured. Set GEMINI_API_KEY or enter it in the sidebar."}

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )
        prompt = _build_user_prompt(diff_text, changes)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )

        raw_text = response.text.strip()
        # Defensive cleanup in case the model wraps the JSON in fences anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("json"):
                raw_text = raw_text[4:].strip()

        parsed = json.loads(raw_text)
        return parsed

    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON.", "raw_response": raw_text}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Gemini API call failed: {exc}"}


def format_llm_result_as_markdown(result: Dict) -> str:
    """
    Turn the structured LLM result dict into a readable Markdown block
    for embedding in the final approval pack.
    """
    if "error" in result:
        return f"> ⚠️ AI review unavailable: {result['error']}"

    lines = []
    lines.append(f"**Overall risk level:** {result.get('risk_level_overall', 'Unknown')}")
    lines.append("")
    lines.append(result.get("overall_summary", ""))
    lines.append("")

    findings = result.get("findings", [])
    if findings:
        lines.append("### Findings")
        for f in findings:
            lines.append(f"- **{f.get('risk_type', 'Change')}** "
                          f"(`{f.get('line', '').strip()}`) - "
                          f"Risk: **{f.get('risk_level', 'Unknown')}**")
            lines.append(f"  - {f.get('plain_english', '')}")
            lines.append(f"  - *Recommended action:* {f.get('recommended_action', '')}")

    lims = result.get("assumptions_and_limitations")
    if lims:
        lines.append("")
        lines.append(f"**Assumptions / limitations:** {lims}")

    return "\n".join(lines)
