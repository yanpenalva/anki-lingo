# Test strategy

Testing is a delivery requirement because a bad card is a product defect and a
bad Anki write is difficult to reverse safely.

## Test layout

```text
tests/
├── unit/
│   ├── domain/
│   └── application/
├── integration/
│   └── infrastructure/
└── contract/
    ├── opencode/
    └── ankiconnect/
```

The structure is active; tests are added with the corresponding implementation
wave.

## Unit tests

Domain and application tests must run with no OpenCode executable, network,
Anki Desktop, or external filesystem state.

Cover at least:

- card invariants and normalization;
- batch count and duplicate rules;
- deterministic quality rejection;
- generation retry bounds;
- candidate deficit handling;
- Anki duplicate filtering;
- no-write behavior when a pre-insertion gate fails;
- exit-code mapping for typed failures.

Use fake ports that record observable calls. Do not mock private methods or
reproduce infrastructure implementation details in application tests.

## Integration tests

Integration tests cover the real adapter seams:

- OpenCode subprocess execution with a controlled fake executable or fixture;
- Pydantic parsing of representative structured output and malformed output;
- AnkiConnect request/response behavior through a local fake HTTP server or
  explicit transport seam;
- configuration loading from a controlled environment.

The test suite must not call a remote LLM or mutate a personal Anki collection.

## End-to-end validation

After the application waves, one manual local run verifies:

1. configured count and C1/C2/pt-BR request;
2. accepted cards arrive in the configured deck/note type;
3. rerunning does not insert the same fronts;
4. invalid provider output produces no insertion;
5. stopping Anki produces a clear non-zero result;
6. the systemd timer invokes the same CLI contract.

The manual run uses a dedicated test deck and note type once those names are
approved. No production or personal collection is a test fixture.

## Quality commands

The environment commands are recorded in `Makefile`, `pyproject.toml`, and the
README. The required checks are:

```text
pytest
ruff check
ruff format --check
mypy
```

A command is evidence only when it was actually executed. Failures and
environment limitations remain recorded in the active task artifact.
