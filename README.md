# Anki Lingo

Local CLI that will generate high-quality English flashcards with an LLM and
synchronize them with Anki for a Brazilian Portuguese speaker.

## Status

The repository is in the bootstrap and architecture-planning phase. This
delivery establishes the project context and implementation plan; application
implementation starts only after explicit approval of the plan.

## Product direction

- Generate 10 English-learning cards per day by default.
- Target Brazilian Portuguese speakers at CEFR C1/C2 initially.
- Validate structured output and learning quality before any Anki write.
- Deduplicate within a batch and against Anki.
- Run locally through a Python CLI, OpenCode, AnkiConnect, and a systemd user
  timer on Pop!_OS.
- Avoid a database unless a concrete requirement proves that Anki alone cannot
  provide the required state.

## Documentation

- [`docs/README.md`](docs/README.md) — documentation map and reading order.
- [`docs/project-scope.md`](docs/project-scope.md) — goals, scope, and
  non-goals.
- [`docs/architecture/overview.md`](docs/architecture/overview.md) — proposed
  layers and dependency boundaries.
- [`docs/planning/implementation-plan.md`](docs/planning/implementation-plan.md)
  — complete wave plan and approval gates.
- [`docs/architecture/ai-development.md`](docs/architecture/ai-development.md)
  — findings from the reference projects and adopted AI workflow.
- [`docs/adr/README.md`](docs/adr/README.md) — proposed architectural
  decisions.
- [`docs/testing/test-strategy.md`](docs/testing/test-strategy.md) — testing
  strategy and quality gates.
- [`docs/operations/systemd.md`](docs/operations/systemd.md) — planned local
  scheduling and operational behavior.

Agent-facing instructions live in [`AGENTS.md`](AGENTS.md) and [`.ai/`](.ai/).

## Planned runtime flow

```text
systemd user timer
        ↓
Python CLI
        ↓
OpenCode CLI → configured LLM
        ↓
Pydantic boundary validation
        ↓
deterministic + semantic quality validation
        ↓
deduplication against Anki
        ↓
AnkiConnect → Anki Desktop
```

See the implementation plan for the order in which these pieces will be
introduced.
