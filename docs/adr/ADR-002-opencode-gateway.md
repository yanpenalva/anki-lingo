# ADR-002 — OpenCode as the initial LLM gateway

## Status

Accepted for implementation.

## Decision

The first LLM integration invokes the OpenCode CLI through an infrastructure
adapter behind an application-owned port. The domain and application layers do
not execute shell commands or depend on OpenCode types.

## Rationale

OpenCode is the requested initial gateway and already supports structured JSON
output. An adapter keeps the domain stable if a direct provider or local model
becomes necessary later.

## Constraints

Use argument arrays, explicit timeouts, controlled environment values, and
bounded retries. The exact JSON/event schema and model configuration must be
verified in the implementation wave.
