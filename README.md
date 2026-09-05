# Anki Lingo

Local, provider-agnostic flashcard generation for advanced English learners.
Anki Lingo uses OpenCode by default, validates every generated card, removes
duplicates, and sends only a complete approved batch to Anki Desktop through
AnkiConnect.

```text
┌──────────────┐    ┌─────────────────┐    ┌────────────────┐
│ Python CLI   │───▶│ LLM provider    │───▶│ C1/C2 cards    │
└──────────────┘    │ OpenCode*       │    └───────┬────────┘
                    │ other adapters │            │
                    └─────────────────┘            │
                              validate · review · deduplicate
                                                │
                                        ┌───────▼────────┐
                                        │ AnkiConnect    │
                                        │ Anki Desktop   │
                                        └────────────────┘

* OpenCode is the default provider, not the application contract.
```

## What it does

Anki Lingo prepares a configurable daily batch of English-learning cards for
Brazilian Portuguese speakers. The default target is 10 cards at CEFR `C1/C2`.
The provider receives the requested level and native language, generates
structured content, and performs a semantic quality review before anything is
written to Anki.

The application depends on a small `LLMProvider` contract rather than on
OpenCode itself. OpenCode is the first built-in adapter; other local, hosted,
or direct SDK providers can be added behind the same contract and selected by
configuration.

## Card format

Each card has one front and two structured back-side values:

```json
{
  "front": "I need to <b>figure out</b> why the server is down.",
  "meaning": "Figure out: To understand, solve, or discover an answer.",
  "example": "I need to figure out why the server is down."
}
```

`front` can be the term alone (`figure out`) or an English sentence with the
target term highlighted exactly once using `<b>...</b>`. The Anki adapter maps
the logical card to two note fields:

- `Front`: the English term or contextual sentence;
- `Back`: the target term and its English meaning, followed by an English example.

## Runtime flow

1. The CLI loads `.env` and process environment values.
2. The configured provider receives the card count, CEFR level, and native
   language.
3. Pydantic validates the provider's structured response at the boundary.
4. Domain rules validate fields, highlighting, count, and duplicate terms.
5. The provider reviews naturalness, C1/C2 suitability, and semantic coherence.
6. AnkiConnect checks availability, deck, note type, and existing cards.
7. Only an exact, approved batch is inserted in one operation.

Pre-insertion failures never write partial content to Anki. Retries are finite,
and a partial AnkiConnect response is treated as an operational failure rather
than retried automatically.

## Requirements

- Python 3.12 or newer;
- `uv` for the Python environment;
- OpenCode CLI or another installed provider adapter;
- Anki Desktop with AnkiConnect for real insertion;
- an Anki deck and note type containing `Front` and `Back` fields.

## Quick start

Create local configuration from the committed template:

```bash
cp .env.example .env
```

Edit `.env`, especially `ANKI_DECK_NAME` and `ANKI_NOTE_TYPE`. The application
loads `.env` automatically when commands run from the project root. Exported
process variables take precedence, and `.env` is ignored by Git.

Set up the environment and install the project:

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -e '.[dev]'
```

Check the effective non-secret configuration:

```bash
.venv/bin/anki-lingo config-check
```

Generate cards without reading or changing Anki:

```bash
.venv/bin/anki-lingo generate --dry-run --output json
```

Generate and insert a batch into Anki:

```bash
.venv/bin/anki-lingo generate --output json
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `ANKI_LINGO_PROVIDER` | `opencode` | Provider adapter name |
| `ANKI_LINGO_COUNT` | `10` | Number of cards per run |
| `ANKI_LINGO_CEFR_LEVEL` | `C1/C2` | English level for the questions |
| `ANKI_LINGO_NATIVE_LANGUAGE` | `pt-BR` | Learner profile for provider context |
| `ANKI_LINGO_MAX_ATTEMPTS` | `3` | Maximum generation attempts |
| `ANKI_DECK_NAME` | — | Target deck; required for insertion |
| `ANKI_NOTE_TYPE` | — | Target note type; required for insertion |
| `ANKI_CONNECT_URL` | `http://127.0.0.1:8765` | AnkiConnect endpoint |
| `ANKI_FIELD_FRONT` | `Front` | Anki front field |
| `ANKI_FIELD_BACK` | `Back` | Anki back field |
| `ANKI_CONNECT_TIMEOUT_SECONDS` | `10` | AnkiConnect timeout |
| `OPENCODE_BIN` | `opencode` | OpenCode executable |
| `OPENCODE_MODEL` | — | Optional OpenCode model |
| `OPENCODE_TIMEOUT_SECONDS` | `120` | OpenCode timeout |
| `OPENCODE_WORKING_DIRECTORY` | — | Optional OpenCode working directory |

The level can also be overridden for one run:

```bash
.venv/bin/anki-lingo generate --cefr-level C2
```

Provider-specific variables should be documented by the corresponding adapter
and kept out of the core application contract.

## Adding a provider

An adapter implements the `LLMProvider` protocol:

```python
class LLMProvider(Protocol):
    def generate(self, request: GenerationRequest) -> tuple[Flashcard, ...]: ...

    def review(
        self, request: GenerationRequest, cards: Sequence[Flashcard]
    ) -> QualityReport: ...
```

Register the adapter as a Python entry point in the `anki_lingo.providers`
group. Its builder receives `AppConfig` and returns an `LLMProvider`:

```toml
[project.entry-points."anki_lingo.providers"]
my-provider = "my_package.provider:build_provider"
```

Resolved `.env` and process variables are available to the builder through
`config.provider_environment`, so provider-specific options do not need to be
added to the core application configuration.

Then select it without changing the domain or application layers:

```dotenv
ANKI_LINGO_PROVIDER=my-provider
```

This keeps provider transport, authentication, model options, and response
normalization inside infrastructure adapters while the use case remains
provider-independent.

## Example Anki note payload

```json
{
  "deckName": "English",
  "modelName": "Basic",
  "fields": {
    "Front": "I need to <b>figure out</b> why the server is down.",
    "Back": "Meaning: Figure out: To understand, solve, or discover an answer.<br><br>Example: I need to figure out why the server is down."
  }
}
```

## Development

Run the complete local quality gate:

```bash
make quality
```

It runs Ruff, format checks, mypy, and pytest. The source layout keeps
distribution concerns separate from the project package:

```text
src/anki_lingo/
├── domain/           # card rules and deduplication
├── application/      # use cases and ports
├── infrastructure/   # provider adapters, AnkiConnect, configuration
└── interfaces/       # CLI and output
```

Systemd service and timer templates are versioned in `deploy/systemd/` but are
not enabled automatically. Real rollout requires confirming the Anki target
and schedule.

## Documentation

- [`docs/project-scope.md`](docs/project-scope.md) — product scope and rules;
- [`docs/architecture/overview.md`](docs/architecture/overview.md) — layers
  and dependency boundaries;
- [`docs/architecture/integrations.md`](docs/architecture/integrations.md) —
  provider and Anki integration contracts;
- [`docs/architecture/domain-model.md`](docs/architecture/domain-model.md) —
  card contract;
- [`docs/operations/systemd.md`](docs/operations/systemd.md) — local operation;
- [`docs/testing/test-strategy.md`](docs/testing/test-strategy.md) — test
  strategy;
- [`docs/adr/README.md`](docs/adr/README.md) — architectural decisions.
