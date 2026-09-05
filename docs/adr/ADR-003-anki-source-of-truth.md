# ADR-003 — Anki as the initial source of truth

## Status

Accepted for implementation.

## Decision

Use AnkiConnect for health checks, duplicate lookup, and insertion. Do not
duplicate card state in a local repository or database during the initial
implementation.

## Rationale

Anki already owns the collection that the user studies. Reading the target
scope before insertion keeps duplicate detection close to the actual data and
avoids synchronization semantics that the project does not yet need.

## Consequence

The exact deck, note type, and `Front`/`Back` field names are configuration
decisions. SQLite can be reconsidered only through a new requirement and
decision record.
