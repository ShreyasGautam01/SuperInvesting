# Super Investing · AI Research Agent

A small Streamlit application that accepts an NSE ticker and a set of company documents, then generates a short Markdown research brief with the required sections: Snapshot, Bull case, Bear case, Open questions, and Sources.

The included `research_pack/` is the supplied fictional Sarvottam Cables Ltd (NSE: SRVCABLE) assignment pack. The assigned reference date is **23 September 2026**. The agent does not browse for SRVCABLE or fetch live market data.

## What it does

- Reads Markdown/TXT, PDF, and DOCX documents, including files inside ZIP archives and nested ZIPs.
- Extracts basic source metadata from Markdown front matter and derives a stable source ID such as `[S1]` for each document.
- Calls the Gemini API directly, without an agent framework.
- Retries transient API failures briefly and automatically tries fallback models when a model is overloaded, rate-limited, or unavailable. The UI and test log record which model succeeded.
- Provides three prompt iterations for honest, reproducible testing: baseline; evidence-aware; evidence-aware plus a second LLM consistency pass.
- Mechanically checks whether all required headings appear, whether citation IDs exist in the input set, and whether the output is roughly one page.
- Lets you download the exact returned brief and a test log from recorded runs.

Mechanical checks cannot establish factual correctness. The optional second pass uses the same evidence packet and model; it is a consistency check, not independent verification. The agent has no live-data tool and should not be treated as investment advice.

## Model choice

Primary model: `gemini-3.8-flash`. Default fallbacks, in order: `gemini-3.6-flash`, then `gemini-3.5-flash-lite`. Configure them through `GEMINI_MODEL` and `GEMINI_FALLBACK_MODELS` or edit the model fields in the sidebar. These are separate model IDs in Google’s current model catalogue; your project still needs access to each model. Run 3 makes a second call for source-grounded review and independently applies the same fallback chain to that call.

**Resilience behavior:** the SDK is configured for a short retry with exponential backoff for transient statuses, then the app moves to the next model if the error appears retryable. Authentication failures and invalid requests are shown immediately. Daily quota exhaustion or spend-cap errors stop rather than cycling through models because another model cannot override a project-wide billing limit. Model fallback improves resilience but cannot guarantee availability if all models are busy or the project has exhausted its quota. See [Gemini API troubleshooting](https://ai.google.dev/gemini-api/docs/troubleshooting) and [API errors](https://ai.google.dev/gemini-api/docs/api-errors).

## Run locally (Windows PowerShell)

Requires Python 3.11 or newer. Use the Python version available on your machine; you do not need to have Python 3.12 specifically.

```powershell
cd path\to\super-investing-agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in VS Code and replace the placeholder with a valid Gemini API key obtained from Google AI Studio. Do not put the key in `app.py`, `README.md`, screenshots, or GitHub. The app also accepts a key in the password field in the sidebar; that key is not added to run logs. You can set `GEMINI_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite` in `.env`, or change the comma-separated fallback list in the app sidebar.

Start the application (this avoids depending on whether the Streamlit executable is on your PATH):

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

It should open a local browser tab. The sample SRVCABLE research pack is selected by default. Enter or confirm your API key, then run the three versions in order.

## Required test procedure

1. Select **Run 1 — Baseline prompt**, generate a brief, and record the specific issues you observe.
2. Select **Run 2 — Evidence-aware system prompt**, generate a new brief, compare it to Run 1, and record what changed.
3. Select **Run 3 — Evidence-aware + verification pass**, generate a new brief, and record which issues remain or were corrected.
4. Enter honest observations in the run-history fields and download `test_log.md`. Replace the template file in the repository with that downloaded file only after the runs have occurred.
5. Download the exact Markdown from Run 3 and save it under `outputs/` if desired. Paste that unedited text into the assignment form. If you hand-edit it, disclose the edits in the form.

Useful test cases in this pack include conflicting Q1 revenue values, a promotional source containing instructions aimed at AI systems, an unrelated business with a similar name, older promoter-pledge reporting, and a GST demand disclosure. Check the generated text itself: a green structural check is not evidence that a claim is true.

## Repository contents

- `app.py` — Streamlit interface and Gemini API integration.
- `agent_core.py` — ingestion, source metadata, evidence formatting, and validation.
- `model_router.py` — model chain, retryable-error classification, and automatic fallback routing.
- `system_prompt.md` — standalone final evidence-grounding system prompt.
- `research_pack/` — eight supplied documents for the required test.
- `test_log.md` — unfilled template; replace after the three actual runs.
- `ASSIGNMENT_BRIEF.md` — copy of the assignment README for reference.
- `submission_notes.md` — draft form-answer guidance; confirm details after running the app.
- `demo_script.md` — 2–3 minute screen-recording cue sheet.

## Run the parser/validator tests

The core tests use Python's standard `unittest` runner and do not need an API key:

```powershell
python -m unittest discover -s tests -v
```

These tests cover bundled-source metadata, source context, citation/section validation, Markdown front matter, nested-ZIP ingestion, and simulated model fallback/error handling. Simulated fallback tests do not prove that a live model was overloaded, and they do not replace the three required live model runs.

## Model fallback limitations

Fallbacks only help when an individual model or endpoint is temporarily unavailable, or when a limit is model-specific. If the API project has depleted daily quota, billing credits, or a project-wide spend cap, switching model IDs will not bypass that restriction. For repeated `503 UNAVAILABLE` / high-demand errors, the app briefly retries and then tries the configured fallbacks.

## Security and limitations

- `.env` and API keys are excluded by `.gitignore`; never commit them.
- Documents are model inputs and may contain adversarial text. The prompt instructs the model to treat document contents as evidence rather than instructions, but prompt injection cannot be guaranteed impossible.
- Citations are generated by the model. The validator detects citation IDs that do not exist but cannot prove the cited source supports a claim.
- The application has no live NSE data or external search. It reports only what the input packet supports and should surface unresolved conflicts instead of silently resolving them.
