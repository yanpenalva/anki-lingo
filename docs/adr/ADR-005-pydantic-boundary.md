# ADR-005 — Pydantic at the structured-data boundary

## Status

Accepted for implementation.

## Decision

Use Pydantic to validate the external structured response from OpenCode. Map
validated transport data into standard-library domain objects immediately.
Pydantic models must not leak into the domain contract.

## Rationale

Pydantic is useful for rejecting malformed provider output while keeping the
domain independent of infrastructure concerns. This creates a clear boundary
where untrusted model output becomes application input.

## Consequence

Schema failures are explicit and testable. Domain tests do not require
Pydantic, and changing provider wire format does not change the card model.
