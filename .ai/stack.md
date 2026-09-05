# Stack and environment

## Target stack

| Component | Role | Status |
| --- | --- | --- |
| Python 3.12+ | runtime | Python 3.12.14 provisioned with uv; project venv active |
| Pydantic 2.11.7 | external structured-output validation | implemented |
| OpenCode CLI | default LLM provider adapter | implemented; CLI observed locally |
| AnkiConnect | local Anki gateway | implemented; local endpoint manually verified |
| SQLite | optional persistent state | deferred until a demonstrated need |
| systemd user service + timer | daily local scheduling on Pop!_OS | planned; not activated |
| pytest 8.4.1 | tests | implemented in isolated environment |
| Ruff 0.12.8 | lint/format | implemented in isolated environment |
| mypy 1.17.1 | static typing | implemented in isolated environment |

Exact dependency versions are pinned in `pyproject.toml` and `uv.lock`. The
repository now has a Python 3.12+ validation environment; production use still
requires the documented Anki target and rollout checks.

## Bootstrap inspection evidence

Initial inspection on 2026-09-04; host update verified on 2026-09-05:

| Tool | Observation |
| --- | --- |
| `python3` | 3.10.12 |
| `python3.12` | 3.12.14 provisioned via uv |
| `opencode` | 1.17.11 |
| `ruff` | 0.11.0 |
| `pytest` | 8.4.1 in `.venv` |
| `mypy` | 1.17.1 in `.venv` |
| `uv` | 0.12.10 installed through pipx |
| `ai-memory` | 2.0.2 |
| `code-review-graph` | installed; no graph exists for this repository |

The host now uses uv-managed CPython 3.12.14 for this project. The repository
`.venv/bin/python` reports Python 3.12.14 and contains the pinned development
toolchain.
