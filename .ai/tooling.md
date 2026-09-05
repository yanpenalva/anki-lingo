# Development tooling boundaries

## RTK

RTK is the required shell wrapper in this repository. Use its native commands
when available and `rtk run -- <command>` for generic commands. RTK reduces
noise; it does not change the command's meaning and its output remains the
validation evidence.

## OpenCode

OpenCode is both a planned runtime integration and an optional development
harness. The application must call it only through the infrastructure adapter
specified in `docs/architecture/integrations.md`. Development use of OpenCode
does not authorize changing application files outside the active task spec.

The locally inspected CLI is version 1.17.11 and exposes
`opencode run --format json`; the provider event contract remains to be tested.

## ai-memory

ai-memory 2.0.2 is available locally, but this repository does not enable a
watcher, install hooks, change global configuration, or create a marker file
in the bootstrap phase. If continuity tooling is adopted later, it may store
only approved summaries and decisions; versioned repository artifacts remain
canonical and secrets/card payloads must not be captured.

## Caveman

Caveman-style compression is an optional communication aid. It must never
compress code, durable architecture, acceptance criteria, security warnings,
approval decisions, or validation evidence.

## Code-review graph

The graph is optional until implementation creates meaningful relationships.
The current inspection found no graph for this repository. A future multi-file
or multi-agent wave may build/update it, but a dependency table in the active
plan remains authoritative and the graph cannot approve its own change.
