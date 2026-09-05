# Wave 1–6 — functional daily flashcard pipeline

## Status

Approved by user on 2026-09-04. Waves 1–5 implemented; Wave 6 rollout pending.

## Objective

Implement the local Anki Lingo pipeline through a tested CLI: generate C1/C2
English-learning cards for a Brazilian Portuguese speaker through OpenCode,
validate and quality-review them, deduplicate against Anki, and expose a safe
Anki insertion boundary.

The card contract is a logical `front`, `translation`, `meaning`, and `example`.
The front may be a bare term or a contextual English sentence with one bold
target term. The Anki adapter renders the three back-side values into a single
`Back` field.

## Scope

- Python packaging and developer commands;
- immutable domain card/batch types and deterministic validation;
- application ports and bounded generation orchestration;
- Pydantic schemas and OpenCode subprocess adapter;
- AnkiConnect HTTP gateway with health, target, lookup, and insertion methods;
- CLI configuration, dry-run, JSON output, and sanitized failures;
- unit and integration tests using fakes/local transports;
- documentation updates for implemented behavior and remaining operational
  decisions.

## Non-goals

- real remote LLM calls during automated tests;
- writes to a personal Anki collection during development;
- SQLite;
- direct OpenAI/Gemini/Ollama adapters;
- systemd activation or timer enablement;
- changing existing Anki notes or deleting cards;
- automatic retries after partial Anki insertion.

## Affected files

- `pyproject.toml`
- `Makefile`
- `src/anki_lingo/`
- `tests/`
- `README.md`, `.ai/`, and affected `docs/`

## Acceptance criteria

- `Flashcard` and batch invariants reject invalid or duplicate content.
- Domain/application tests run without OpenCode, Anki, network, or Pydantic in
  domain imports.
- OpenCode calls use an argument list, explicit timeout, structured Pydantic
  parsing, and bounded failure handling.
- AnkiConnect calls validate transport and response-level errors.
- Application inserts only an exact, quality-accepted, deduplicated batch.
- Pre-insertion failures perform no Anki write.
- CLI supports one-shot generation and dry-run JSON output.
- Versioned systemd service/timer templates do not activate themselves.
- Ruff, mypy, and pytest commands are configured and run where environment
  permits.

## Test plan

- domain unit tests;
- application tests with fake ports;
- OpenCode parser/subprocess tests with deterministic fixtures;
- AnkiConnect tests with a local HTTP server;
- CLI configuration/output tests;
- `make quality` in Python 3.12+ environment;
- manual Anki integration only after deck/note contract approval.

## Versioned handoff

- User authorized implementation on 2026-09-04.
- Target CEFR changed from B1 to C1/C2 before implementation.
- User confirmed the front/back card presentation on 2026-09-05.
- Waves 1–5 validated with 22 passing tests, Ruff, and mypy.
- Initial validation ran in isolated Python 3.10.12 because Python 3.12 was not
  installed on host; host upgrade is part of this implementation update.
- Systemd templates passed `systemd-analyze verify` after temporary extension
  normalization; host emitted unrelated existing unit warnings.
- Open decisions remain: target deck, note type, configured `Front`/`Back` names,
  model,
  timer schedule/timezone, and policy for semantic-review cost.
