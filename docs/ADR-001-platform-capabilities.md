# ADR-001: Capability-based platform client

## Status
Accepted

## Context

Avito exposes different functionality through public pages, normal-user browser sessions, mobile/private endpoints and professional APIs. A single monolithic client would either couple the product to one fragile transport or falsely advertise unsupported operations.

## Decision

Model product operations as independent capabilities and place each transport behind adapters. The application checks capability availability before use.

## Consequences

- Search can ship before apply/chat are proven.
- A browser fallback can coexist with official API adapters.
- Tests can assert that unsupported mutations remain disabled.
- Replacing a transport should not change the product-facing contract.
