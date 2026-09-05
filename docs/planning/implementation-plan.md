# Implementation plan

This plan sequences implementation through local rollout. Bootstrap approval
was received on 2026-09-04; each wave still requires its own task evidence and
quality gates.

## Dependency graph

```text
Wave 0: context, architecture, decisions, approval
   ↓
Wave 1: Python toolchain and CLI boundary
   ↓
Wave 2: domain model and deterministic validation
   ↓
Wave 3: OpenCode generation and bounded quality review
   ↓
Wave 4: AnkiConnect preflight, lookup, and insertion
   ↓
Wave 5: end-to-end orchestration and operational CLI
   ↓
Wave 6: systemd scheduling, hardening, and local rollout
```

Wave 3 can prepare provider fixtures in parallel with the latter part of Wave
2 after the domain card contract is frozen. Wave 4 must not begin until the
Anki deck and note type are confirmed. The initial note contract uses
`Front` and `Back`; their names remain configurable.

## Wave 0 — bootstrap and approval

### Purpose

Establish repository navigation, project context, proposed architecture,
quality expectations, decisions, and the implementation sequence without
creating application behavior.

### Deliverables

- root agent instructions and `.ai/` workflow context;
- public documentation map and project scope;
- layered architecture and domain/integration contracts;
- proposed ADRs and quality/test strategy;
- AI-assisted development adoption record;
- empty structural directories under `src/`, `tests/`, and `deploy/`;
- active bootstrap task spec with explicit approval boundary.

### Exit gate

Architecture, open decisions, quality policy, and wave plan are approved. No
Python module, dependency, provider call, Anki write, or systemd activation was
part of Wave 0.

## Wave 1 — Python toolchain and executable boundary

### Tasks

- select the environment/packaging workflow and record exact versions;
- create `pyproject.toml` with Python `>=3.12`, runtime/dev dependencies, and
  Ruff/mypy/pytest configuration;
- decide and commit a lockfile policy suitable for this local CLI;
- create the importable `src/anki_lingo` package and minimal CLI entry point;
- validate configuration from environment/CLI without exposing secrets;
- define application-facing failure and exit-code conventions;
- add baseline unit-test and quality command targets.

### Acceptance evidence

Fresh Python 3.12+ environment installs deterministically; CLI help and a
configuration validation command run; Ruff, mypy, and pytest commands are
documented and pass against the baseline package.

### Non-goals

No LLM call, Anki call, card generation, database, or timer.

## Wave 2 — domain model and deterministic validation

### Tasks

- implement immutable `Flashcard` and batch types using standard-library
  domain types;
- freeze the four-value card contract (`front`, translation, meaning, example)
  and boundary normalization rules;
- implement normalized-front identity and intra-batch deduplication;
- implement deterministic validation and typed rejection reasons;
- define explicit size/control-character policies;
- add unit tests for valid cards, empty fields, count mismatch, normalization,
  duplicate fronts, and failure composition.

### Acceptance evidence

Domain tests run without Pydantic, OpenCode, Anki, network, filesystem, or CLI
framework imports. Every deterministic rule has positive, boundary, and
failure tests.

### Non-goals

No claims that deterministic code has judged naturalness, CEFR, or translation
equivalence.

## Wave 3 — OpenCode generation and quality review

### Tasks

- define the smallest application port for LLM generation;
- capture the installed OpenCode JSON/event contract with a fixture;
- implement a subprocess adapter using an argument list, bounded timeout, and
  explicit exit/error handling;
- add Pydantic transport schemas at the infrastructure boundary;
- map parsed transport data into domain cards without leaking Pydantic inward;
- define the generation prompt for count, C1/C2 level, English, and Brazilian
  Portuguese requirements;
- decide whether semantic review is enabled and, if so, define a structured
  review contract and maximum review attempts;
- test malformed JSON, wrong shape, command failure, timeout, and rejected
  quality reports with fakes/fixtures.

### Acceptance evidence

No arbitrary command shelling or unbounded retry exists. Invalid provider
output cannot become a domain batch. Provider integration tests do not require
the real remote model.

## Wave 4 — AnkiConnect gateway

### Prerequisite decisions

- target deck name;
- note type;
- configured `Front`/`Back` field names;
- duplicate lookup scope;
- handling policy for partial insertion responses.

### Tasks

- define the application `AnkiGateway` port;
- implement health check and target verification;
- implement existing-front lookup within the target scope;
- implement deterministic card-to-note mapping;
- implement one-batch insertion and response validation;
- map connection, malformed-response, missing-target, and partial-insertion
  failures;
- test with a local fake HTTP server or transport seam, not a running Anki
  Desktop instance.

### Acceptance evidence

Anki integration tests cover success, unavailable service, invalid response,
missing deck/note type, duplicate lookup, and partial insertion. Infrastructure
details do not cross the application or domain boundary.

## Wave 5 — daily generation use case and CLI

### Tasks

- implement the application orchestration for preflight → generate → parse →
  validate → quality review → Anki lookup → exact-count decision → insert;
- preserve the all-or-nothing pre-insertion rule;
- retry only candidate generation/quality failures with a finite configured
  maximum;
- request a deficit when valid candidates are removed by batch or Anki
  deduplication;
- stop without writing when the exact final count cannot be formed;
- add `generate`/dry-run behavior only if the command contract remains clear;
- emit concise, sanitized logs and deliberate exit codes;
- test the full application with fake provider and Anki ports.

### Acceptance evidence

Application tests prove exact count, no duplicate insertion, bounded retry,
Anki-unavailable failure, invalid-output failure, and no-write behavior for
every pre-insertion failure. The CLI can execute against fakes without
OpenCode or Anki installed.

## Wave 6 — systemd scheduling and local rollout

### Tasks

- add user-service and timer templates under `deploy/systemd/`;
- define environment-file location and permissions without committing secrets;
- add concurrency protection using the selected systemd/OS mechanism;
- define timer time, timezone, missed-run, and Anki-not-running behavior;
- document journald inspection, manual run, dry run, stop/disable, and
  recovery from partial insertion;
- validate unit syntax and run the CLI manually on Pop!_OS;
- perform a controlled end-to-end test with Anki Desktop, then a failure test
  with Anki unavailable;
- record operational limits and post-run observations.

### Acceptance evidence

The service runs once per timer event, concurrent runs are rejected, failures
have useful exit status/logs, secrets stay outside Git, and Anki unavailability
does not create cards or an infinite retry loop.

## Cross-wave quality gates

Every implementation wave must include:

- targeted pytest tests;
- Ruff check/format validation according to the committed configuration;
- mypy validation for typed application code;
- an import-boundary review;
- an updated task spec and evidence record;
- a review of secrets, logs, subprocess arguments, and external error paths.

The final rollout additionally requires a manual approval of the Anki target
configuration and systemd schedule. No release or external synchronization is
implicit from a passing local test suite.

## Implementation status

Wave 1 through Wave 5 are implemented and locally validated. Wave 6 has
versioned systemd templates and documentation, but timer activation and real
Anki synchronization remain pending target-configuration confirmation.
