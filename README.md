# Network Config Diff Reviewer (IM-14)

A small AI-assisted prototype that helps an infra/network team review config
changes **before** they go through email-based "casual" approval.

It takes two network-config text files (old vs. new), diffs them, runs a
rule-based risk check, and asks the Gemini API to explain each change in
plain English with a risk level — then exports a Markdown/PDF "approval
pack" the team can attach to a change ticket.

---

🚀 **Live Web App:** [Streamlit Cloud Deployment](https://network-config-diff-reviewer-uhh7tvqxbvx4tsrbfzr2do.streamlit.app/)

---

## 1. Problem Statement

Network config changes (ACLs, routes, BGP peers) currently go through casual
email approval with no structured diff or risk review. This prototype gives
reviewers a quick, AI-assisted diff + risk summary + approval checklist.

---

## 2. Features Implemented

- Upload two network-config text files (or use bundled sample configs).
- Python-based unified diff (`difflib`) between old and new configs.
- Rule-based detection of risky change types:
  - **ACL Widened** – new broad `permit ip any any` (or similar) rules
  - **Route Added / Removed** – new or removed `ip route` lines
  - **Peer Change** – BGP `neighbor ... remote-as / description / password` changes
  - **SNMP Risk** – SNMP community string changes (e.g. RO → RW)
- Gemini API call that returns **structured JSON** with:
  - overall summary, overall risk level
  - per-change plain-English explanation, risk level, recommended action
  - assumptions & limitations
- Markdown "approval pack" combining the diff, rule-based flags, and AI
  review, with an approval checklist.
- Download buttons for **Markdown**, **PDF**, and a **CSV** of flagged
  changes.

---

## 3. Architecture Overview

```
Streamlit UI (app.py)
   │
   ├── src/processor.py   -> diff (difflib) + rule-based risk classification
   ├── src/llm_helper.py   -> Gemini API call, structured JSON output
   └── src/utils.py        -> file reading, Markdown report builder, PDF export
```

**Flow (Agent-loop style):**

1. **Input**: user uploads/selects two config files.
2. **Processing**: Python diffs the files and flags risky lines.
3. **AI Layer**: Gemini explains the diff + flags in plain English and
   assigns risk levels (structured JSON output).
4. **Validation**: app checks the JSON shape; falls back to an error
   message if the model output is malformed.
5. **Output**: Markdown / PDF / CSV approval pack, shown in the UI and
   downloadable.

---

## 4. Tools & Technologies Used

| Area       | Tool                                                |
| ---------- | --------------------------------------------------- |
| Language   | Python                                              |
| UI         | Streamlit                                           |
| AI Model   | Google Gemini (free tier) via `google-generativeai` |
| Diffing    | Python `difflib`                                    |
| PDF export | `fpdf2`                                             |
| Testing    | `pytest`                                            |

---

## 5. Setup Instructions

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd network-config-diff-reviewer

# 2. (Recommended) create a virtual environment
python3 -m venv .venv
.venv\Scripts\activate        # on Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Gemini API key (get a free key at https://ai.google.dev)
export GEMINI_API_KEY="your-key-here"     # on Windows: set GEMINI_API_KEY=your-key-here
```

You can also paste the API key directly into the Streamlit sidebar at
runtime instead of using an environment variable.

---

## 6. Run Instructions

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

1. Either upload two config files, or leave **"Use bundled sample configs"**
   checked to use `data/sample_config_old.txt` and `data/sample_config_new.txt`.
2. Click **🚀 Run Diff Review**.
3. Review the unified diff, rule-based risk flags, and the AI's plain-English
   review.
4. Download the Markdown / PDF approval pack and/or the CSV of flagged
   changes.

---

## 7. Sample Input and Sample Output

- **Sample input configs**: `data/sample_config_old.txt`, `data/sample_config_new.txt`
  (a Cisco-style router config with a deliberately risky set of changes:
  an ACL widened to `permit ip any any`, a new static route, a BGP peer
  AS/description change, and an SNMP community escalated to RW).
- **Sample output**:
  - `outputs/sample_output.csv` – rule-based risk flags for the sample configs
  - `outputs/final_report.md` – full Markdown approval pack (including a
    sample AI review section) for the sample configs

---

## 8. AI Capability Demonstrated

- **LLM Structured Output**: Gemini is asked to return strict JSON with
  fixed fields (`overall_summary`, `risk_level_overall`, `findings[]` with
  `risk_type`, `plain_english`, `risk_level`, `recommended_action`, and
  `assumptions_and_limitations`).
- **Agent-style loop**: read input → diff/analyze → ask LLM → validate JSON
  → build approval pack → save/export file.

---

## 9. Assumptions and Limitations

- This is a **review aid**, not an automated approval/deployment tool — a
  human must still tick the approval checklist and approve the change.
- Rule-based checks use simple keyword/pattern matching on Cisco-style
  config syntax; other vendor syntaxes (Juniper, Palo Alto, etc.) may need
  additional patterns.
- The Gemini API requires a free API key and an internet connection; without
  a key, the diff and rule-based flags still work, but the AI review section
  will show a friendly "AI review unavailable" message.
- PDF export is a simple text-based rendering (via `fpdf2`), not a fully
  styled document.
- The tool does not connect to live network devices; it only compares two
  provided text files.

---

## 10. Demo Video

- 🎥 **Watch the Demo Video:** [Loom Video - Network Configuration Difference Reviewer with AI](https://www.loom.com/share/9af403bdb6e64d0992ae23556a04d1bb)
- 📝 **Full Transcript and Chapters:** Available in [demo_video/README.md](file:///c:/Users/DELL/Downloads/network-config-diff-reviewer%20(2)/network-config-diff-reviewer/demo_video/README.md)

---

## 11. Team

### Team Name
**Team 6**

### Team Members

| S.No | Name |
| :--- | :--- |
| 1 | A Ishwarya |
| 2 | BCP Radhika |
| 3 | D Harshitha |
| 4 | E Geethanjali |

### Resumes

- A Ishwarya Resume: [View Resume](./Team%20resumes/Addanki_Ishwarya_Resume-3.pdf)
- BCP Radhika Resume: [View Resume](./Team%20resumes/RADHIKA.resume.pdf)
- D Harshitha Resume: [View Resume](./Team%20resumes/Harshitha%20resume.pdf)
- E Geethanjali Resume: [View Resume](./Team%20resumes/Geethajali_Ediga_Resume.pdf)
### PPT
https://docs.google.com/presentation/d/12y3QN00w0meYWh6F8F90l1Xxx7Iuwq5X/edit?usp=drivesdk&ouid=115090261101482200608&rtpof=true&sd=true
