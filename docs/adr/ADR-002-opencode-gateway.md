# ADR-002 — OpenCode as the initial LLM gateway

## Status

Accepted for implementation.

## Decision

OpenCode is the default LLM provider. It is implemented as an infrastructure
adapter behind the application-owned `LLMProvider` port. The domain and
application layers do not execute shell commands or depend on OpenCode types.
Provider selection is resolved by an infrastructure registry, which can load
additional adapters through the `anki_lingo.providers` Python entry-point
group.

## Rationale

OpenCode is the initial gateway and already supports structured JSON output.
Keeping it behind the provider port lets direct APIs, local models, or other
CLIs be added without changing the domain or application orchestration.

## Constraints

Use argument arrays, explicit timeouts, controlled environment values, and
bounded retries. Provider-specific settings and response schemas remain inside
the adapter that owns them.
