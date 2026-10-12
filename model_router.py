"""Small, testable fallback routing helpers for Gemini model overloads."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")

DEFAULT_FALLBACK_MODELS = ("gemini-3.6-flash", "gemini-3.5-flash-lite")
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
RETRYABLE_TERMS = (
    "resource_exhausted",
    "unavailable",
    "service unavailable",
    "high demand",
    "overloaded",
    "overload",
    "temporarily unavailable",
    "rate limit",
    "too many requests",
    "deadline exceeded",
    "model_not_found",
    "model not found",
    "not found for api version",
)


def build_model_chain(primary: str, fallback_models: str | Iterable[str] | None = None) -> list[str]:
    """Return a de-duplicated primary-first chain of model identifiers."""
    if isinstance(fallback_models, str):
        fallbacks = fallback_models.split(",")
    elif fallback_models is None:
        fallbacks = DEFAULT_FALLBACK_MODELS
    else:
        fallbacks = list(fallback_models)

    result: list[str] = []
    for item in [primary, *fallbacks]:
        model = str(item).strip()
        if model and model not in result:
            result.append(model)
    if not result:
        raise ValueError("At least one Gemini model ID must be configured.")
    return result


def should_try_fallback(exc: Exception) -> bool:
    """Only fall back for transient service/limit errors or an unavailable model.

    Authentication failures, permission errors, invalid request parameters, and
    depleted billing credits should be surfaced instead of retried pointlessly.
    """
    code = getattr(exc, "code", None)
    status_code = getattr(exc, "status_code", None)
    status = str(getattr(exc, "status", "") or "").lower()
    message = str(exc).lower()
    combined = f"{status} {message}"

    # A daily quota or spend cap generally applies beyond a single model. Check
    # this before numeric 429 handling, because both causes may use HTTP 429.
    if any(term in combined for term in ("quota_exceeded", "daily quota", "prepay credit", "spend cap", "billing account")):
        return False

    candidates = {code, status_code}
    for candidate in candidates:
        try:
            if int(candidate) in RETRYABLE_STATUS_CODES:
                return True
        except (TypeError, ValueError):
            pass

    return any(term in combined for term in RETRYABLE_TERMS)


def call_with_model_fallback(
    model_chain: Iterable[str],
    invoke: Callable[[str], T],
    *,
    on_fallback: Callable[[str, Exception, str], None] | None = None,
) -> tuple[T, str, list[str]]:
    """Invoke the first working model and return (result, chosen model, notes)."""
    models = list(model_chain)
    if not models:
        raise ValueError("The model fallback chain is empty.")

    notes: list[str] = []
    last_error: Exception | None = None
    for index, model in enumerate(models):
        try:
            result = invoke(model)
            if index:
                notes.append(f"Fallback succeeded: `{model}` was used after earlier model failure(s).")
            notes.append(f"Successful model: `{model}`.")
            return result, model, notes
        except Exception as exc:
            last_error = exc
            if not should_try_fallback(exc):
                raise RuntimeError(
                    f"Model `{model}` failed with a non-retryable error: {exc}. "
                    "Check the API key, model permissions, request parameters, or project billing/quota."
                ) from exc
            status = getattr(exc, "code", None) or getattr(exc, "status_code", None) or getattr(exc, "status", None)
            note = f"Model `{model}` failed ({status or 'temporary service/model error'}): {exc}"
            notes.append(note)
            if index + 1 < len(models):
                next_model = models[index + 1]
                notes.append(f"Trying fallback model `{next_model}`.")
                if on_fallback:
                    on_fallback(model, exc, next_model)

    attempted = ", ".join(f"`{model}`" for model in models)
    detail = str(last_error) if last_error else "Unknown error"
    raise RuntimeError(
        f"All configured Gemini models failed ({attempted}). Last error: {detail}. "
        "If the error is 503/high demand, wait briefly and retry. If it is 429 daily quota/spend cap, "
        "model fallback cannot override the project's quota or billing limits."
    ) from last_error
