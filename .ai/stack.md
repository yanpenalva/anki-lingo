# Stack and environment

## Target stack

| Component | Role | Status |
| --- | --- | --- |
| Python 3.12+ | runtime | required target; environment not yet compliant |
| Pydantic | external structured-output validation | required; version to pin in Wave 1 |
| OpenCode CLI | initial LLM gateway | required integration; CLI observed locally |
| AnkiConnect | local Anki gateway | required integration; target contract not confirmed |
| SQLite | optional persistent state | deferred until a demonstrated need |
| systemd user service + timer | daily local scheduling on Pop!_OS | planned; not activated |
| pytest | tests | required; not installed in inspected command paths |
| Ruff | lint/format | required; available locally |
| mypy | static typing | required; not installed in inspected command paths |

Exact dependency versions and lockfile policy are intentionally left to Wave 1
so they can be selected together for Python 3.12+ and recorded reproducibly.

## Bootstrap inspection evidence

Observed on 2026-09-04 in the repository environment:

| Tool | Observation |
| --- | --- |
| `python3` | 3.10.12 |
| `python3.12` | NOT FOUND in checked command path |
| `opencode` | 1.17.11 |
| `ruff` | 0.11.0 |
| `pytest` | NOT FOUND in checked command path |
| `mypy` | NOT FOUND in checked command path |
| `uv` | NOT FOUND in checked command path |
| `ai-memory` | 2.0.2 |
| `code-review-graph` | installed; no graph exists for this repository |

These are inspection results, not a request to install tools or a claim that
the project is executable. The first implementation wave must establish a
Python 3.12+ environment before adding runtime code.
