# Project scope

## Objective

Anki Lingo is a local CLI that generates a configurable daily batch of English
flashcards for a Brazilian Portuguese speaker and synchronizes accepted cards
with Anki Desktop through AnkiConnect.

The initial target is 10 cards per day at CEFR C1/C2. The logical card shape is:

```json
{
  "front": "I need to <b>figure out</b> why the server is down.",
  "translation": "descobrir; entender; resolver",
  "meaning": "To understand, solve, or discover an answer.",
  "example": "I need to figure out why the server is down."
}
```

When `front` is a sentence, the target term appears exactly once in `<b>` (or
`<strong>`) markup. A bare term is also valid. Anki receives two fields: the
front is written to `Front`, and the translation, English meaning, and English
example are rendered together in `Back`.

## Required behavior

The eventual application must:

- request the configured number of cards from an LLM through the OpenCode CLI;
- parse and validate a structured response with Pydantic at the external
  boundary;
- reject empty, malformed, contradictory, duplicated, or poor-quality cards;
- preserve the exact requested final count or fail without inserting a partial
  batch;
- detect duplicate `front` values within the candidate batch;
- detect cards already present in the configured Anki target;
- insert only a fully accepted batch through AnkiConnect;
- fail safely when OpenCode, the LLM, AnkiConnect, Anki Desktop, the deck, or
  the note type is unavailable;
- expose useful exit codes and journald-compatible logs;
- run once from the CLI and eventually on a Pop!_OS systemd user timer.

## Initial quality contract

Every accepted card must have non-empty `front`, `translation`, `meaning`, and
`example` values. The batch must have the exact requested count and unique
normalized learning terms. The English must be natural and appropriate for the
requested CEFR level; the Brazilian Portuguese must be natural; the English
meaning and example must match the translated sense; and obvious false-cognate
or contradictory content must be rejected.

Deterministic checks and semantic quality checks are separate responsibilities.
The implementation plan includes a bounded semantic review step because code
alone cannot reliably judge naturalness, CEFR suitability, or translation
equivalence.

## Non-goals for the initial product

- web UI or HTTP application server;
- cloud backend, database, queue, or worker platform;
- direct provider SDK integration before the OpenCode boundary proves
  insufficient;
- mobile application;
- Anki synchronization beyond the local AnkiConnect contract;
- multi-user accounts, authentication, or remote storage;
- automatic deletion or modification of existing Anki notes;
- hidden fallback content or silent recovery after a failed validation.

## Explicit constraints

- Python 3.12 or newer.
- Pydantic for external structured-data validation.
- OpenCode CLI is the initial LLM gateway.
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
- preferred OpenCode model and model-selection policy;
- daily timer time and timezone behavior;
- whether a second LLM quality-review call is acceptable for cost and latency;
- final dependency management and lockfile policy for the Python environment.
