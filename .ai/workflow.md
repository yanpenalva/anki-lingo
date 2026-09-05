# Agent workflow

## Bootstrap gate

The current repository task is documentation-first:

```text
Inspect → Specify → Plan → Present for approval
                                  ↓
                 Implement → Validate → Review → Wrap up
```

The arrow into implementation is a human authorization boundary. Do not
interpret a plan, an earlier conversation, or a tool availability check as
approval to implement.

## Normal task lifecycle after approval

```text
Specify → Plan → Preflight → Implement → Validate → Review → Wrap up
```

### Specify

Create or update `.ai/tasks/<slug>/spec.md` with objective, scope, non-goals,
affected files, acceptance criteria, and test plan. Read the relevant public
task and architecture documents before planning.

### Plan

Split work into small subtasks with explicit owners, mutable file boundaries,
dependencies, and acceptance evidence. Parallel work is allowed only when
subtasks do not overlap and can be independently verified.

### Preflight

Confirm the repository state, required tools, open decisions, target files,
security implications, and whether the requested change is authorized. Record
`NOT FOUND` instead of guessing.

### Implement

Make small changes inside the approved spec. Keep `.ai/tasks/<slug>/progress.md`
updated for long or interruptible work.

### Validate

Run the affected tests, Ruff, mypy, and any integration checks defined by the
spec. Record the exact commands and results. Do not claim a check passed when
it was not run.

### Review

Compare the request, spec, progress, actual diff, acceptance criteria, and
security/architecture boundaries. Review reports findings; it does not silently
expand scope or approve deployment.

### Wrap up

Promote durable decisions and handoff state into versioned documentation/spec,
remove temporary progress, and report remaining risks. Commit/push and systemd
activation are separate explicit approvals.
