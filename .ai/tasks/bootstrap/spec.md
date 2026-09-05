# Bootstrap — project context and implementation plan

## Status

Approved by user on 2026-09-04. Application implementation authorized.

## Objective

Inspect the reference projects and context workflow, adapt the useful
AI-assisted development conventions to this Python CLI, establish the
repository structure, and document a complete implementation plan for Anki
Lingo.

## Scope

- inspect Fuelwise, Plataforma Protesto São Luís, and
  `context-spec-develop`;
- establish root and `.ai/` agent context;
- create public scope, architecture, ADR, testing, operations, and planning
  documentation;
- record observed tooling and unresolved decisions;
- create empty structural directories for future source, tests, and systemd
  templates;
- present the plan for explicit approval.

## Non-goals

- Python application modules or package behavior;
- Pydantic models or dependency installation;
- OpenCode execution or remote LLM calls;
- AnkiConnect requests or Anki writes;
- SQLite schema or persistence;
- systemd unit activation, services, timers, hooks, or global configuration;
- commit, push, or external communication.

## Affected files

- `README.md`
- `AGENTS.md`
- `.gitignore`
- `.ai/`
- `docs/`
- empty structural placeholders under `src/`, `tests/`, and `deploy/`

## Acceptance criteria

- Reference-project patterns and context-kit adaptations are documented.
- Project scope, constraints, open decisions, and quality requirements are
  explicit.
- Layer boundaries and external integration seams are documented.
- Proposed architectural decisions are recorded with rationale and rejected
  alternatives.
- The plan is divided into dependency-safe waves with tasks, acceptance
  evidence, and non-goals.
- AI context explains repository navigation, current state, conventions,
  tooling, task workflow, and approval boundaries without duplicating public
  contracts.
- No application behavior or external state change is introduced.

## Test plan

Documentation-only validation:

- inspect the final file tree;
- search for accidental application implementation files;
- review links and consistency among README, scope, architecture, ADRs, and
  implementation plan;
- run `rtk git diff --check`;
- run `rtk git status --short`.

No pytest, Ruff, mypy, OpenCode, AnkiConnect, or systemd runtime check is
applicable before Wave 1.

## Versioned handoff

- Current step: Wave 1 implementation.
- Completed: read-only inspection, reference comparison, architecture and
  wave-plan drafting, documentation bootstrap, explicit user approval.
- Open decisions: Anki deck/note contract, OpenCode model, semantic-review
  cost policy, timer schedule/timezone, and Python dependency/lockfile policy.
- Next action: execute active implementation spec and record validation.
