# Login model

For a normal job-seeker account, the preferred authentication model is browser-session reuse rather than professional API `client_id/client_secret`.

1. Launch Chromium with a persistent/profile-backed Playwright context.
2. User signs in to Avito interactively (phone/email, OTP, and any challenge shown by Avito).
3. After successful login, save Playwright storage state locally under `storage/`.
4. Subsequent runs reuse the same storage state and do not request OTP while the Avito session remains valid.
5. If Avito invalidates the session, the application reports `AUTH_REQUIRED` and launches the interactive login flow again.

Secrets, cookies and storage state must never be committed to Git.

Professional API credentials are a separate optional transport and are not treated as a replacement for a normal candidate login.
