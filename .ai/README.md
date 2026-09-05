# Agent context

`.ai/` contains agent-facing workflow and project-operating context. It does
not replace the public documentation under `docs/` and should link to that
documentation rather than duplicate it.

## Read first

1. `AGENTS.md`;
2. `../README.md`;
3. `../docs/README.md`;
4. `workflow.md`, `stack.md`, and `conventions.md`;
5. the active task spec under `tasks/`;
6. only the relevant public architecture, planning, testing, and operations
   documents.

## Files

- [`workflow.md`](workflow.md) — task lifecycle and approval boundaries.
- [`stack.md`](stack.md) — target stack and inspected tool availability.
- [`conventions.md`](conventions.md) — Python and boundary conventions.
- [`tooling.md`](tooling.md) — RTK, OpenCode, memory, compression, and graph
  usage boundaries.
- [`tasks/`](tasks/) — versioned specs and temporary progress records.

Persistent architecture and product decisions belong in `docs/architecture/`,
`docs/planning/`, or `docs/adr/`. A memory tool may help continuity, but it is
never the source of truth.
