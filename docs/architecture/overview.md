# Architecture overview

## Proposed shape

Anki Lingo uses a small `src/`-layout Python package with four layers:

```text
src/anki_lingo/
├── domain/
├── application/
├── infrastructure/
└── interfaces/
```

The repository also uses these concrete boundaries:

```text
tests/
├── unit/
├── integration/
└── contract/

deploy/
└── systemd/
```

The directories contain the current implementation and its corresponding
tests; systemd files remain versioned templates until rollout approval.

## Dependency direction

```text
interfaces ────────> application ────────> domain
infrastructure ────> application ────────> domain
domain ─────────────> nothing external
```

`application` owns the ports required by use cases. Infrastructure implements
those ports. Interfaces adapt command-line input, configuration, output, and
exit codes. The domain contains card invariants and quality rules that do not
need a process, network, filesystem, CLI framework, or external SDK.

## Responsibility by layer

### Domain

Owns the `Flashcard` model, normalized-front identity, batch invariants, and
deterministic validation rules. The domain uses standard-library types and
does not import Pydantic, subprocess, HTTP, AnkiConnect, OpenCode, or systemd.

### Application

Owns the daily-generation use case and orchestration policy: preflight,
generation, structured validation handoff, quality review, bounded retries,
deduplication, and batch synchronization. It depends on small ports rather
than concrete adapters.

The first implementation should introduce only ports used by this use case:
an LLM completion/generation port, a semantic quality-review port if approved,
and an Anki gateway port. A generic `FlashcardRepository` is deferred because
Anki is the initial source of truth and no second persistence requirement has
been demonstrated.

### Infrastructure

Contains the OpenCode subprocess adapter, Pydantic transport schemas and
mappers, AnkiConnect HTTP client, environment/configuration loading, and
external-error translation. The OpenCode adapter invokes an argument array,
not a shell command string, and has an explicit timeout.

### Interfaces

Contains the CLI entry point, argument/configuration adaptation, human-readable
output, exit-code mapping, and logging setup. It does not contain generation,
quality, or Anki rules.

## Planned module locations

Current implementation locations:

```text
src/anki_lingo/
├── domain/
│   ├── flashcard.py
│   ├── batch.py
│   └── validation.py
├── application/
│   ├── ports.py
│   └── generate_daily_cards.py
├── infrastructure/
│   ├── config.py
│   ├── llm/
│   │   ├── opencode_provider.py
│   │   └── schemas.py
│   └── anki/
│       └── ankiconnect_gateway.py
└── interfaces/
    └── cli.py
```

Names remain subject to the approved task spec for each wave. New abstractions
must be justified by a current boundary, not by a possible future provider or
storage engine.

## End-to-end sequence

1. The CLI loads and validates runtime configuration.
2. The application performs an Anki/OpenCode preflight sufficient to fail
   early.
3. The application asks the LLM gateway for a candidate batch.
4. The infrastructure boundary parses the structured result with Pydantic and
   maps it to domain values.
5. Deterministic domain/application validation runs.
6. Semantic quality review runs if the approved quality policy requires it.
7. The gateway returns existing normalized fronts and the application filters
   candidates without mutating Anki.
8. Only an exact, fully accepted batch is sent in one AnkiConnect insertion
   operation.
9. The CLI reports the result and returns a deliberate exit code.

If any pre-insertion gate fails, the application performs no Anki write. A
partial external response is an error, not a successful batch.
