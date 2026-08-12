# Candidate-side apply research

## Constraint

The project must not claim `apply()` works until we can reproduce the action for a normal job-seeker account and verify the resulting application in Avito.

## Candidate transports to test

1. Official Avito API / `avito-py` — preferred if a candidate-side operation exists for normal user credentials.
2. Authenticated web/mobile endpoint used by the normal Avito UI — acceptable behind an isolated transport if reproducible and stable enough.
3. Playwright UI action — fallback when no usable endpoint is available.

## Evidence required before enabling the capability

- exact request or deterministic browser flow;
- authenticated session requirements;
- required resume/application fields;
- idempotency / duplicate-application behavior;
- successful application visible in the user's Avito account;
- negative test for an already-applied vacancy;
- no mutation during search-only scans.

Until this evidence exists, `Capability.APPLY = false`.

## Runtime probe

After `login`, run a single manual apply flow while the project records sanitized XHR/fetch metadata:

```powershell
python -m avito_clicker trace-apply --url "https://www.avito.ru/...vacancy..."
```

The default output is `storage/traces/apply-trace.json`. Request headers are not stored; common sensitive query/body fields (tokens, OTP, phone, email, message text) are redacted. The trace is evidence for implementing an automated candidate-side transport.
