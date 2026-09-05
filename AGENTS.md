# Anki Lingo agent instructions

Bootstrap plan is approved. Current implementation follows the active task
spec under `.ai/tasks/` and documented wave gates.

## Source of truth

Read these files before changing the repository:

1. `README.md`;
2. `docs/README.md`;
3. the relevant documents under `docs/`;
4. `.ai/README.md`, `.ai/workflow.md`, `.ai/stack.md`, and
   `.ai/conventions.md`;
5. the active task spec under `.ai/tasks/`.

Public product, architecture, testing, operations, and ADR documents live in
`docs/`. Agent workflow and temporary execution state live in `.ai/`. Do not
duplicate a public contract in an agent file; link to its owner instead.

## Working rules

- Use `rtk` for every shell command.
- Treat facts, inferences, and unresolved questions as different things.
- Record missing information as `NOT FOUND`; do not invent contracts, Anki
  deck names, note types, models, credentials, or test evidence.
- Work only within an approved task spec.
- Keep application dependencies pointed inward: domain has no infrastructure,
  CLI, HTTP, subprocess, or Pydantic dependency.
- Prefer the Python standard library until a concrete requirement justifies a
  dependency.
- Never send invalid or partially validated cards to Anki.
- Keep retries bounded and failures explicit.
- Never put credentials, generated card content, or local state in Git.
- Update the relevant documentation when a decision changes.

## Current phase boundary

Application implementation is authorized. Do not skip the active task spec,
quality gates, external-boundary tests, or explicit approval for real Anki
writes and systemd activation.
