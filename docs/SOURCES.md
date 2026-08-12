# Source projects and reuse boundaries

## Functional reference

- `Vlad9572324/hh.ru-clicker` — functional/architectural reference for a job-seeker automation product. No source code is copied into this repository unless an explicit compatible license is identified.

## Avito search reference

- `Duff89/parser_avito` — studied for current Avito search transport behavior, cookie persistence patterns, pagination and anti-block concerns. No source code is vendored or copied because no explicit compatible license was identified during bootstrap.

## Official Avito API SDK

- `18studio/avito_python_api` / PyPI `avito-py` — MIT-licensed SDK. This project may depend on it for official Avito API capabilities such as account and messenger operations.

## Messenger/LLM reference

- `Kustov-Daniil/avito_autoanswer_bot` — studied for messenger workflow, webhook and LLM interaction patterns. No source code is copied unless a compatible license is confirmed.

## Rule

Prefer documented/public APIs and our own adapters. Keep transport-specific code behind capability interfaces so private/mobile/browser implementations can be replaced independently.
