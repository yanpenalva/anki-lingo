# ADR-007 — systemd user service and timer

## Status

Accepted for implementation.

## Decision

Schedule the daily CLI through a systemd user service and timer on Pop!_OS.
Do not use cron as the baseline.

## Rationale

Anki Desktop and AnkiConnect run in the user's session. A user unit matches
that ownership model and provides explicit status, journald logs, exit codes,
dependency ordering, and concurrency controls without a new service platform.

## Consequence

The final schedule, environment-file location, lock mechanism, and behavior
when Anki is not running must be confirmed and tested before activation.
