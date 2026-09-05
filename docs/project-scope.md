# Project scope

## Objective

Anki Lingo is a local CLI that generates a configurable daily batch of English
flashcards for a Brazilian Portuguese speaker and synchronizes accepted cards
with Anki Desktop through AnkiConnect. The application is provider-independent;
OpenCode is the default provider adapter.

The initial target is 10 cards per day at CEFR C1/C2. The logical card shape is:

```json
{
  "front": "I need to <b>figure out</b> why the server is down.",
  "meaning": "Figure out: To understand, solve, or discover an answer.",
  "example": "I need to figure out why the server is down."
}
```

When `front` is a sentence, the target term appears exactly once in `<b>` (or
`<strong>`) markup. A bare term is also valid. Anki receives two fields: the
front is written to `Front`, and the target term, English meaning, and English
example are rendered together in `Back`. Cards do not include Portuguese
translations.

## Required behavior

The eventual application must:

- request the configured number of cards from the selected LLM provider;
- parse and validate a structured response with Pydantic at the external
  boundary;
- reject empty, malformed, contradictory, duplicated, or poor-quality cards;
- preserve the exact requested final count or fail without inserting a partial
  batch;
- detect duplicate `front` values within the candidate batch;
- detect cards already present in the configured Anki target;
- insert only a fully accepted batch through AnkiConnect;
- fail safely when the selected provider, AnkiConnect, Anki Desktop, the deck,
  or the note type is unavailable;
- expose useful exit codes and journald-compatible logs;
- run once from the CLI and eventually on a Pop!_OS systemd user timer.

## Initial quality contract

Every accepted card must have non-empty `front`, `meaning`, and `example` values.
The `meaning` value must start with the target term followed by `: ` and its
English definition. The batch must have the exact requested count and unique
normalized learning terms. The English must be natural and appropriate for the
requested CEFR level; the meaning and example must be natural English (US) and
match the target sense; and contradictory content must be rejected.

Deterministic checks and semantic quality checks are separate responsibilities.
The implementation plan includes a bounded semantic review step because code
alone cannot reliably judge naturalness, CEFR suitability, or meaning/example
equivalence.

## Non-goals for the initial product

- web UI or HTTP application server;
- cloud backend, database, queue, or worker platform;
- provider-specific transport and SDK details in the core application;
- mobile application;
- Anki synchronization beyond the local AnkiConnect contract;
- multi-user accounts, authentication, or remote storage;
- automatic deletion or modification of existing Anki notes;
- hidden fallback content or silent recovery after a failed validation.

## Explicit constraints

- Python 3.12 or newer.
- Pydantic for external structured-data validation.
- OpenCode CLI is the default provider adapter.
- Providers implement the application-owned `LLMProvider` contract and are
  selected through `ANKI_LINGO_PROVIDER`.
- AnkiConnect is the initial Anki gateway.
- SQLite is conditional and must not be introduced speculatively.
- systemd service plus timer is the scheduling target on Pop!_OS; cron is not
  the baseline.
- pytest, Ruff, and mypy are mandatory quality tools.
- No feature implementation begins before explicit user approval of the
  bootstrap plan.

## Open decisions

The following facts are `NOT FOUND` in the current repository and must be
confirmed before the integration waves:

- target Anki deck name;
- Anki deck, note type, and exact `Front`/`Back` field names;
- selected provider, provider options, and model-selection policy;
- daily timer time and timezone behavior;
- whether a second LLM quality-review call is acceptable for cost and latency;
- final dependency management and lockfile policy for the Python environment.
