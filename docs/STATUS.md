# Project status canvas

## North Star

A Windows-first Avito Jobs assistant for a normal job-seeker account that can discover relevant vacancies, inspect them, apply safely, track application state, and handle recruiter conversations through an LLM with explicit auditability and transport isolation.

## Current phase

Phase 1 — prove the candidate transport end to end.

## Current state

Working in PR #1:

- interactive normal-user login with Playwright storage-state persistence;
- read-only vacancy search by query or exact filtered URL;
- DOM + JSON-LD normalization;
- SQLite idempotent storage;
- vacancy detail enrichment;
- Windows scripts and Docker runtime;
- capability boundary (`search` and `vacancy_details` enabled; mutations disabled);
- sanitized `trace-apply` probe;
- 9 local tests passing.

GitHub Actions is configured but cannot run because the GitHub account is currently locked for an Actions billing issue.

## Gap

The product does not yet know the real normal-user candidate-side mutation contract for `apply()` or the candidate chat transport.

## Constraint

One real authenticated Avito runtime observation is required before enabling mutations. We will not guess a private endpoint and will not enable `apply()` based only on DOM assumptions.

## SMART goal

On the next real Windows run, prove login/search/details against a normal Avito account and capture one sanitized manual application trace containing enough request/response metadata to choose and implement the candidate-side apply transport.

## Decisions

- Treat `hh.ru-clicker` as a product/architecture reference, not copied source without an explicit compatible license.
- Use `18studio/avito_python_api` only where the official/professional API matches the actual account capability.
- Keep normal-user browser session authentication separate from professional API credentials.
- Prefer exact Avito search URLs for complex filters.
- Keep all mutations disabled until real-account evidence exists.

## Backlog

- Issue #2 — Windows smoke test: login, search, details.
- Issue #3 — capture candidate apply flow and implement apply transport.
- Issue #4 — candidate chats + LLM reply pipeline.

## Risks

- Avito DOM/private endpoints can change.
- Session invalidation may require new OTP/challenge.
- Candidate and professional API capabilities may differ materially.
- Anti-bot behavior may differ between headed Windows and headless Docker runs.

## Next 3 actions

1. Run issue #2 on the target Windows machine and record exact outcomes.
2. Run `trace-apply` once on a real vacancy and retain the sanitized trace, not the storage-state file.
3. Rebuild the apply plan from that trace and implement `Capability.APPLY` only after a successful real-account verification.
