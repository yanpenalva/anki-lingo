# Task artifacts

Implementation work is organized by small task specs and dependency-safe waves
from [`planning/implementation-plan.md`](../planning/implementation-plan.md).

## Task workflow

Each task has a versioned spec under `.ai/tasks/<slug>/spec.md` containing:

- objective and scope;
- non-goals;
- affected files;
- acceptance criteria;
- test plan;
- decisions and versioned handoff state when needed.

During implementation, `.ai/tasks/<slug>/progress.md` records commands,
results, decisions, deviations, and unresolved issues. It is temporary and is
removed only after the task's wrap-up state has been promoted into the spec.

The current bootstrap task is `.ai/tasks/bootstrap/spec.md`. It is a planning
task and explicitly blocks application implementation until the user approves
the plan.
