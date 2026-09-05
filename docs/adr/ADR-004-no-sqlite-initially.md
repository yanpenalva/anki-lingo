# ADR-004 — No SQLite before a demonstrated need

## Status

Accepted for implementation.

## Decision

Do not introduce SQLite in the initial product. Reconsider it only when a
concrete requirement remains after Anki-backed duplicate detection and the
daily use case are implemented.

## Rationale

The product is local, but local does not automatically mean a second state
store is necessary. Adding one early would create schema, migration, backup,
and consistency responsibilities without a defined consumer.
