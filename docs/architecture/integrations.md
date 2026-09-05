# External integrations

## LLM providers

The application depends on the `LLMProvider` protocol and does not know whether
the selected provider is a CLI, hosted API, local model, or direct SDK. The
provider name is selected with `ANKI_LINGO_PROVIDER`; `opencode` is the default.

Provider adapters own their transport, authentication, provider-specific
settings, response parsing, and mapping into the stable `Flashcard` and
`QualityReport` contracts. The built-in registry also discovers external
Python entry points in the `anki_lingo.providers` group.
Their builders receive the resolved `AppConfig`, including the provider
environment, so provider-specific options stay outside the core contract.

### OpenCode

OpenCode is the first built-in provider adapter. Domain and application code do
not know that it runs through a subprocess.

The infrastructure adapter will own:

- executable resolution and configured working directory;
- argument-array construction for `opencode run`;
- structured output mode and parsing of its event/output format;
- timeout, cancellation, exit-status, and stderr handling;
- Pydantic validation of the expected response shape;
- mapping transport failures into application-facing failures.

The current installed CLI exposes `opencode run --format json`; the adapter
parses the tested event contract and the application does not scrape arbitrary
text as if it were valid JSON.

The model is configured outside the domain. OpenAI, Gemini, Ollama, or other
adapters can be added independently through the same provider contract.

## AnkiConnect

AnkiConnect is the initial Anki gateway and Anki is the initial source of truth
for duplicate detection. The application-facing gateway will expose only the
operations needed by the daily batch:

- health/preflight;
- target deck and note-type verification;
- lookup of existing fronts in the target scope;
- insertion of a fully accepted batch;
- explicit mapping of gateway errors and response-level failures.

The initial HTTP implementation should prefer the Python standard library. A
third-party HTTP dependency requires a task-spec justification. Transport
details stay inside infrastructure.

The exact deck name and note type remain user configuration. The Anki note
contract uses two fields: the logical `front` goes to `Front`, while the target
term, `meaning`, and `example` are rendered together as labeled HTML in `Back`.
The `meaning` value starts with the target term followed by its English (US)
definition. Cards contain English (US) content only; no Portuguese translation
field is added.

## Insertion safety

The application performs all local and lookup validation before insertion and
sends one batch request. AnkiConnect does not provide a general transaction
rollback contract for this workflow, so a partial insertion response is
reported as a distinct operational failure and is never retried automatically.
Recovery must be documented after the target note contract is confirmed.

## Persistence decision

No SQLite database is part of the initial architecture. Anki already stores
the cards and supplies the duplicate lookup boundary. SQLite becomes eligible
only if a demonstrated requirement remains after the CLI, quality, and Anki
contracts are implemented—for example, durable run idempotency or audit state
that Anki cannot safely represent. Such a change requires a new spec and ADR.
