# Python and architecture conventions

## Package layout

- Use the `src/` layout.
- Keep one responsibility per module and names aligned with the main concept.
- Organize infrastructure by actual integration (`llm`, `anki`) rather than
  creating generic `utils`, `common`, or `services` bins.
- Add a directory only when an approved task introduces a concrete element.

## Dependency boundaries

- Domain imports only the Python standard library and domain modules.
- Application owns ports and orchestration; it does not import subprocess,
  HTTP clients, OpenCode, AnkiConnect, or systemd.
- Infrastructure implements application ports and maps external failures.
- Interfaces adapt inputs/outputs and exit codes; they do not own business
  rules.
- Pydantic models stop at the external structured-data boundary.
- No repository abstraction until a real persistent-state consumer exists.

## Python style

- Require Python 3.12+ and strict typing for application code.
- Prefer immutable dataclasses and small pure functions for domain values.
- Use protocols for real dependency-inversion boundaries; do not create an
  interface for a one-line internal function.
- Use explicit exceptions/failure types at boundaries.
- Avoid `Any`, implicit global state, hidden singletons, and mutable default
  arguments.
- Use `subprocess` with an argument list and `shell=False` for OpenCode.
- Use timezone-aware UTC timestamps when timestamps become necessary.
- Keep logs sanitized and metadata-oriented; do not log full card payloads by
  default.

## Validation

- Treat LLM output and environment values as untrusted input.
- Validate before mapping inward and validate domain invariants again where the
  application composes a batch.
- Never silently coerce malformed card data into a placeholder.
- Never insert a batch that is short, duplicated, or semantically rejected.
- Every retry has a visible, finite limit.

## Testing

- Test behavior through public contracts.
- Keep domain/application tests independent from external processes and
  network services.
- Use fixtures for provider wire formats and a local fake for AnkiConnect.
- Test failures, timeouts, malformed responses, duplicate behavior, and
  no-write guarantees—not only successful calls.
- Keep actual commands and limitations in the active task progress/spec.

## Documentation

- Durable decisions belong in `docs/adr/` or the owning architecture/planning
  document.
- Active task scope belongs in `.ai/tasks/<slug>/spec.md`.
- Temporary execution state belongs in `progress.md` and is promoted before
  wrap-up.
- Do not add comments, TODOs, or speculative future code as a substitute for
  a named task or decision.
