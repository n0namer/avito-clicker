# Architecture

`avito-clicker` separates product behavior from Avito transport details.

Core capabilities:

- search vacancies
- get vacancy details
- apply as a job seeker
- list applications
- list chats
- list messages
- send messages

Each capability is independently discoverable at runtime. A transport may support only a subset without forcing the rest of the application to pretend that unsupported operations work.

Initial transports:

1. Browser transport for normal job-seeker sessions and public vacancy search.
2. Official API transport (via `avito-py`) for capabilities available to professional API credentials.

The first vertical slice is read-only: search -> normalize -> persist -> inspect.
