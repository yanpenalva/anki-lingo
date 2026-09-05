# AI-assisted development approach

This project was bootstrapped after inspecting the local Fuelwise and
Plataforma Protesto São Luís repositories and the public
[`context-spec-develop`](https://github.com/yanpenalva/context-spec-develop)
kit. The goal is to keep the useful engineering controls while matching a
small Python CLI instead of copying Flutter, Laravel, or vendor-specific
files.

## Findings from the reference projects

### Fuelwise

Fuelwise keeps public product/architecture/testing documentation under `docs/`
and agent-facing workflow, stack, conventions, and task specs under `.ai/`.
Its workflow is explicit: Specify → Plan → Implement → Validate → Review →
Wrap up. Task specs define scope, non-goals, affected files, acceptance
criteria, and tests; temporary progress records execution and is removed at
wrap-up. This is the closest structural match for Anki Lingo.

### Plataforma Protesto São Luís

The project separates a small root `AGENTS.md` contract from a larger `.ai/`
knowledge base. It records architecture, quality, security, project structure,
planning waves, subtasks, decisions, and operational runbooks. It also treats
AI-memory as a watcher with explicit installation, status, data classification,
and global-configuration boundaries. That caution is useful, but the full
watcher setup is not required for this empty local CLI.

### context-spec-develop

The kit treats context as a versioned engineering dependency. Its core loop is
Intake → Specify → Plan → Preflight → Execute/Test → Verify/Review →
Release/Observe/Close. It uses structured work items, dependency-safe waves,
bounded delegation, actual validation evidence, explicit human approval, and
`NOT FOUND` for missing facts. Its optional RTK, memory, and review-graph
guidance explicitly says those tools never replace canonical artifacts.

## Adopted

- `AGENTS.md` as a small entrypoint to canonical repository context;
- `docs/` as the source of truth for product, architecture, decisions, tests,
  and operations;
- `.ai/` for agent workflow, stack, conventions, and task artifacts;
- versioned task specs with objective, scope, non-goals, acceptance criteria,
  affected files, and test plan;
- temporary progress records with durable decisions promoted into the spec;
- dependency-safe implementation waves with one owner per mutable boundary;
- facts/inferences/unknowns separation and `NOT FOUND` for gaps;
- validation evidence consisting of actual commands and results;
- explicit approval before implementation, external synchronization, commit,
  push, or operational activation.

## Adapted

| Reference concept | Anki Lingo adaptation |
| --- | --- |
| `.context/` canonical kit | `.ai/` remains the lighter local convention; public contracts stay in `docs/` |
| Product/support intake tracks | A local CLI currently needs product task specs; support/incident artifacts are added only if operational work appears |
| JSON `work-item.json` | Task spec metadata is Markdown until multiple work items justify a machine-readable schema |
| Preflight/release/observe artifacts | Required for integration and rollout waves, represented in the active task spec and evidence sections |
| Agent profiles and orchestration config | Scope/ownership tables in plans; no orchestrator runtime is added to the app repository |
| Context validator | Ruff, mypy, pytest, import-boundary review, and future small scripts; a generic validator is deferred |
| Code-review graph | Optional when code relationships or parallel waves justify it; dependency tables remain canonical |

## Intentionally not adopted

- copying the entire `.context/` template and its generic schemas;
- installing or enabling ai-memory hooks, MCP integrations, or a background
  watcher as part of bootstrap;
- adding global harness configuration or modifying user-level services;
- adding Caveman as a project dependency or compressing durable contracts;
- adding deployment/CI machinery before the local CLI and target environment
  are defined;
- copying Flutter, Laravel, Figma, or client-specific structures from the
  references.

These are not rejections of the tools. They are scope decisions for a local
CLI with no application code and no current need for multi-agent automation.
If the project grows, the decision can be revisited through an ADR or task
spec with an owner and concrete benefit.

## Current tooling observations

At bootstrap inspection time, the host reported Python 3.10.12, OpenCode
1.17.11, Ruff 0.11.0, and ai-memory 2.0.2. `pytest`, `mypy`, `uv`, and
Python 3.12 were not available through the checked command paths. The host
therefore does not yet satisfy the target Python toolchain. These observations
are environment evidence, not project dependencies or approval to install
anything.
