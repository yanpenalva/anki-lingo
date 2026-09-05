# ADR-006 — Fail-safe batches and bounded retries

## Status

Accepted for implementation.

## Decision

Never insert a partial or invalid batch. Retry generation/quality failures only
within an explicit maximum. Do not automatically retry an Anki insertion after
a partial insertion response.

## Rationale

Exact count and content quality are product requirements, while an external
Anki write may not be transactionally reversible. Infinite retries could
duplicate content, hide an outage, or create unbounded cost.

## Consequence

The application may fail a run even when some valid cards exist. The failure
must explain whether the cause was provider quality, duplication, target
configuration, or external availability.
