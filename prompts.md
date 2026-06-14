# Prompts Used (Network Config Diff Reviewer)

This document records the prompt(s) used to drive the Gemini API in
`src/llm_helper.py`, following the basic prompt template from the project
guide.

---

## 1. System Instruction (sent as `system_instruction` to Gemini)

```
You are a senior network security reviewer.
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
```

---

## 2. User Prompt Template (built per-request)

```
DIFF:
<unified diff text>

RULE-BASED FLAGGED CHANGES:
<JSON array of changes from src/processor.py, e.g.
 [{"risk_type": "ACL Widened", "line": "permit ip any any", "change": "added", "detail": "..."}]>

Respond with the JSON object described in the system instructions only.
```

---

## 3. Generation Settings

- `temperature`: `0.2` (favor consistent, conservative explanations)
- `response_mime_type`: `application/json` (forces structured JSON output)
- Model: `gemini-2.5-flash` (configurable in the Streamlit sidebar; also
  works with `gemini-2.0-flash` / `gemini-1.5-flash`)

---

## 4. Generic Prototype Prompt Template (from the project guide)

For reference, the general-purpose template from the project guide that
inspired the structure above:

```
You are an AI assistant helping build a prototype for <PROJECT NAME>.

Input data:
<PASTE INPUT OR SUMMARY>

Task:
1. Analyze the input.
2. Produce the required output in structured format.
3. Give a short explanation.
4. Mention assumptions and limitations.

Return output in this format:
- Result:
- Reasoning:
- Recommended Action:
- Output JSON/Markdown/Table:
```

This was adapted into the stricter JSON schema above so the app can
reliably parse and render the AI's response (per-finding risk levels,
recommended actions, etc.) without extra parsing logic.

---

## 5. Best Prompts / Lessons Learned

- Explicitly forcing **strict JSON** (`response_mime_type: application/json`
  + "Return ONLY valid JSON") was essential — without it, Gemini sometimes
  wrapped the JSON in ```json fences or added a short preamble.
- Feeding the model **both** the raw diff *and* the rule-based flags (rather
  than just the raw diff) produced more focused, relevant explanations and
  reduced the chance of the model missing a flagged change.
- Asking for a `risk_level` **per finding** (not just an overall risk level)
  made the approval pack much more actionable for reviewers.
