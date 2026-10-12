# Super Investing Agent — Test Log

**Status: template only.** No Gemini API execution has been recorded in this file yet. Do not submit it as a completed test log. Run the app using each of the three prompt iterations, review the actual results, enter observations in the app, and download the generated `test_log.md` to replace this file.

Required runs:
- Run 1 — Baseline prompt: record observed failure modes and examples.
- Run 2 — Evidence-aware system prompt: record what improved and what remains incorrect.
- Run 3 — Evidence-aware prompt plus verification pass: record whether the remaining issues were caught or corrected.

Do not claim an issue was fixed unless the corresponding output was checked. The application mechanically checks required headings and citation IDs; the extra model review is not independent verification.

## Reliability check (automated, not one of the three required research runs)
- Automatic fallback selection is tested with simulated 503/high-demand errors.
- Daily quota/spend-cap messages are tested as non-retryable.
- This unit test does not claim the live Gemini service was overloaded or that a live fallback occurred.
