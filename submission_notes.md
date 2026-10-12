# Part B submission helper

Use this as a reminder when completing the form. Do not submit the placeholder sections as if the model had run.

## How did you build it?
Select **Code with an LLM API directly**. The app is a Python + Streamlit interface calling the Gemini API; it does not use an agent framework.

## Which model(s) did you use, and why?
Draft to confirm after your runs:

> I used Gemini 3.8 Flash (`gemini-3.8-flash`) for document-grounded synthesis. I selected one fast model because this task is a small, bounded document-analysis workflow; a multi-agent framework would add setup and orchestration without a clear benefit. Run 3 uses the same model for a second-pass consistency review, so that review is not independent fact-checking.

If you select a different model in the app, replace the model name in this response.

## What does your agent do with unreliable, outdated, or contradictory sources?
Draft based on the implemented behavior:

> The agent assigns a stable source ID to every input document and passes source names, publication dates, URLs, and content into the research prompt. The system prompt distinguishes primary company/exchange disclosures from secondary reporting and promotional opinion, asks the model to qualify old information against 23 September 2026, and requires contradictory numbers to be surfaced rather than silently reconciled. Embedded instructions in documents are treated as untrusted content, and information about an unrelated similarly named entity must be excluded. A mechanical validator checks required sections and citation IDs; Run 3 adds a model-based consistency pass using the same evidence packet. These checks reduce risks but do not prove that every citation supports its claim.

## Brief and hand-edit disclosure

- Paste the text downloaded from **Run 3 — Evidence-aware + verification pass** exactly as generated.
- Answer **No** to hand-editing only if you copy the downloaded text unchanged. If you alter even part of it, disclose what you changed.
- Download the generated test log after recording honest observations for Runs 1, 2, and 3. Do not submit the starter `test_log.md` template before it is completed.

## Bonus
Live data is not implemented. Leave the bonus unclaimed unless you separately add it and actually test real NSE tickers.

## Link checklist

- Repository is public or otherwise set to **Anyone with the link can view**.
- The screen recording is accessible by anyone with the link.
- Open each link in an incognito window before submitting.
