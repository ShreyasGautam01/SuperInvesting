# 2–3 minute screen recording guide

Use this as a cue sheet, not a claim that the run has already happened. Record after the application has successfully completed Run 3.

## 0:00–0:25 — Show it running

Open the local Streamlit app. Show ticker `SRVCABLE`, the included eight-document research pack, and click **Generate research brief** for Run 3. Keep the output visible once generated.

Suggested narration: “This is a document-grounded research agent. The ticker and the supplied research pack are its inputs. Sarvottam Cables is fictional, so I deliberately do not use external search or live market data.”

## 0:25–1:10 — Show the output

Scroll through Snapshot, Bull case, Bear case, Open questions, and Sources. Use the source IDs and source list to show how a reader can trace material claims to the supplied files.

## 1:10–1:50 — Explain the design decision

Show the conflicting Q1 revenue claims: the company press release gives ₹1,248 crore and 18% growth, while Business Daily reports ₹1,428 crore and 35% growth. Explain that the prompt instructs the agent to retain the discrepancy and prioritize direct disclosures for reported company figures, rather than blending the claims.

If the actual output allows, also point out that the promotional blog contains instructions aimed at AI systems. Explain that source content is treated as untrusted evidence, not as an instruction that overrides the system prompt.

## 1:50–2:25 — Show testing and a limitation

Open the three-run test log and briefly explain the observed failure in Run 1, the change made for Run 2, and the result of Run 3. Describe a real observation from the run rather than reading this script as a claim of success.

Limitation to state: structural and citation-ID checks do not establish that every claim is factually true or that its cited source supports it. The second-pass review uses the same model and evidence, so it is not independent verification.

## 2:25–2:35 — Close

Show the download control for the generated Markdown brief and point out that the submitted text will be copied unchanged from the model output.


## Optional reliability moment
If the primary model is overloaded during the recording, show the automatic fallback notice and point out that the UI records the model actually used. Do not force a failure for the demo. If no overload occurs naturally, describe the fallback feature from the sidebar rather than claiming it was triggered.
