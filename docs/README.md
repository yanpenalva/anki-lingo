# Anki Lingo documentation

This directory is the versioned source of truth for product scope, proposed
architecture, implementation planning, operational behavior, testing, and
architectural decisions.

## Reading order

1. [`project-scope.md`](project-scope.md)
2. [`architecture/overview.md`](architecture/overview.md)
3. [`architecture/domain-model.md`](architecture/domain-model.md)
4. [`architecture/integrations.md`](architecture/integrations.md)
5. [`planning/implementation-plan.md`](planning/implementation-plan.md)
6. [`testing/test-strategy.md`](testing/test-strategy.md)
7. [`operations/systemd.md`](operations/systemd.md)
8. [`architecture/ai-development.md`](architecture/ai-development.md)
9. [`adr/README.md`](adr/README.md)
10. [`tasks/README.md`](tasks/README.md)

## Documentation ownership

| Concern | Owner |
| --- | --- |
| Product behavior and boundaries | `docs/project-scope.md` |
| Layering and domain contracts | `docs/architecture/` |
| Decisions and rejected alternatives | `docs/adr/` |
| Delivery sequence and wave gates | `docs/planning/` |
| Tests and validation evidence | `docs/testing/` and task artifacts |
| Scheduling and local operations | `docs/operations/` |
| Agent workflow and task mechanics | `.ai/` |

The `.ai/` directory references these documents instead of copying their
content. A task spec records the scope for one change; it does not replace the
project architecture or product documentation.
