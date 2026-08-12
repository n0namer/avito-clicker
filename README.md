# avito-clicker

Windows-first automation and analytics layer for a **job seeker's** workflow on Avito Jobs.

The product target is the workflow shape demonstrated by `Vlad9572324/hh.ru-clicker` — search, applications and recruiter conversations — but the implementation is transport-independent and does not copy unlicensed source code from reference repositories.

## Current status

Implemented vertical slice:

- ✅ interactive normal-user Avito login via Chromium;
- ✅ persistent Playwright storage state (cookies/local storage stay local);
- ✅ public/authenticated Avito Jobs search by query or exact filtered URL;
- ✅ normalization of vacancy cards;
- ✅ SQLite upsert/deduplication;
- ✅ Windows CLI scripts;
- ✅ Docker search/runtime;
- ✅ unit tests + GitHub Actions;
- ✅ vacancy detail enrichment for stored vacancies;
- 🚧 candidate-side `apply()` research;
- 🚧 applications history;
- 🚧 messenger + LLM replies.

Check the machine-readable boundary:

```powershell
python -m avito_clicker capabilities
```

## Login

For a normal candidate account we do **not** use professional API `client_id/client_secret` as the primary login.

```powershell
.\scripts\windows_setup.ps1
.\scripts\windows_login.ps1
```

Chromium opens. Log in to Avito normally (phone/email, OTP and any challenge Avito shows), then return to PowerShell and press Enter. The browser storage state is saved to:

```text
storage/avito-storage-state.json
```

The file is ignored by Git. Later runs reuse it until Avito invalidates the session.

Initial login is intentionally a host/Windows action because Docker normally has no interactive desktop. The resulting `storage/` directory can then be mounted into Docker.

## Search

Query mode:

```powershell
python -m avito_clicker search --query "project manager" --city-slug moskva --limit 50
```

Exact URL mode is preferable for complex filters. Configure filters in Avito, copy the resulting search URL, then:

```powershell
python -m avito_clicker search --url "https://www.avito.ru/..." --limit 100
```

Show stored vacancies:

```powershell
python -m avito_clicker list --limit 100
```

Enrich one stored vacancy by opening its detail page:

```powershell
python -m avito_clicker details 123456789
```

Diagnostics:

```powershell
python -m avito_clicker doctor
```

Probe the real candidate-side apply flow without storing cookies/tokens in the trace:

```powershell
python -m avito_clicker trace-apply --url "https://www.avito.ru/...vacancy..."
```

The sanitized trace is written under `storage/traces/` and is the input for implementing `apply()` against the real account flow.

## Docker

After host login has created `storage/avito-storage-state.json`:

```powershell
docker compose build
docker compose run --rm avito-clicker doctor
docker compose run --rm avito-clicker search --query "операционный директор" --city-slug moskva --limit 50
```

## Architecture

Product code sees capabilities, not implementation details:

```text
AvitoClicker
  ├─ search            -> Browser/PublicSearch transport     ✅
  ├─ vacancy_details   -> browser/JSON-LD enrichment         ✅
  ├─ apply             -> candidate mutation transport       🚧
  ├─ applications      -> candidate history transport        🚧
  └─ chats/messages    -> official/browser messenger         🚧
```

See `docs/ADR-001-platform-capabilities.md` and `docs/APPLY_RESEARCH.md`.

## Source boundaries

- `18studio/avito_python_api` / `avito-py`: MIT-licensed, may be used as an optional official API SDK.
- `Duff89/parser_avito`: protocol/behavior reference only unless a compatible license is identified.
- `Kustov-Daniil/avito_autoanswer_bot`: workflow reference only unless a compatible license is identified.
- `Vlad9572324/hh.ru-clicker`: product/architecture reference only unless a compatible license is identified.

See `docs/SOURCES.md`.

## Safety boundary

Search is read-only. Mutating capabilities such as `apply()` and `send_message()` remain disabled until their transports are explicitly implemented and tested. This prevents an incomplete adapter from accidentally sending applications or messages.
