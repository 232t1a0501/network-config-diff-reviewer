# AI Usage Note

## What AI Helped With

- **Scaffolding the project structure** to match the recommended folder
  layout (`app.py`, `src/`, `data/`, `outputs/`, `tests/`, docs).
- **Designing the rule-based risk classifier** (`src/processor.py`) for
  ACL-widening, route-added/removed, BGP peer-change, and SNMP-risk
  patterns in Cisco-style config syntax.
- **Designing the Gemini integration** (`src/llm_helper.py`), including the
  system instruction, JSON schema, and structured-output parsing/validation.
- **Generating sample router configs** (`data/sample_config_old.txt` and
  `data/sample_config_new.txt`) that deliberately contain a realistic set of
  risky changes (ACL widened to `permit ip any any`, a new static route, a
  BGP `remote-as`/description change, and an SNMP community escalated from
  RO to RW) so the rule-based and AI checks have something meaningful to
  flag.
- **Writing the Streamlit UI** (`app.py`) tying input → diff → rule-based
  flags → AI review → downloadable approval pack together.
- **Writing pytest happy-path tests** (`tests/test_basic.py`) for the diff
  and risk-classification logic.
- **Generating sample outputs** (`outputs/sample_output.csv`,
  `outputs/final_report.md`) by running the rule-based pipeline against the
  sample configs (the AI-review section of `final_report.md` is a
  representative sample response, since the sandbox used to generate it had
  no live Gemini API key/network access).
- **Drafting documentation** (README, prompts.md, this file).

## What AI Got Wrong / Had to Be Adjusted

- The first draft of the risk classifier flagged **every** `permit`/`deny`
  line change as "ACL Widened", which was too noisy. It was refined to only
  call something "ACL Widened" when a newly **added** line contains a broad
  `permit ip any any` (or `any any`) pattern, and to use separate labels
  ("ACL Rule Added/Removed") for other ACL line changes.
- The Markdown→PDF helper initially assumed all characters could be encoded
  by FPDF's default Latin-1 fonts; this was adjusted to replace
  non-encodable characters so PDF export doesn't crash on diff symbols.
- Because the sandbox environment used to build this prototype had no
  internet access, the Gemini API could not actually be called during
  development. `outputs/final_report.md` therefore includes a **sample,
  hand-written-style AI review** to illustrate the expected structure/output
  — the live app calls Gemini dynamically once a valid `GEMINI_API_KEY` is
  provided.

## Best Prompts Used

See `prompts.md` for the full system instruction and user-prompt template
used to query Gemini, plus notes on what worked well (forcing strict JSON
output, providing both the raw diff and rule-based flags, and asking for a
per-finding risk level).
