# ADR-001 — Layered `src/` package

## Status

Proposed; pending bootstrap approval.

## Decision

Use a small `src/anki_lingo/` package divided into `domain`, `application`,
`infrastructure`, and `interfaces`. Use dependency inversion at external
boundaries and keep the domain independent of frameworks and adapters.

## Rationale

The boundaries correspond to real responsibilities in the product: learning
card invariants, generation/synchronization orchestration, OpenCode/
AnkiConnect integration, and CLI/operations adaptation. This provides
testability without creating a generic framework or empty future modules.

## Rejected alternatives

- a flat package with provider and Anki code beside domain rules;
- a framework-heavy web application;
- pre-creating bounded contexts or repositories without a current use case.
