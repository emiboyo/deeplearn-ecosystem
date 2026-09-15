# Milestone 1.3 Test Agent

Status: M1.3 synthetic registry fixture. The root architecture documents remain authoritative.

## Purpose and ownership

`test.safe_agent@1.0.0` is owned by `deeplearn.core.test`. It exists only to prove agent-definition validation, immutable registration, exact version resolution, lifecycle representation, and tool allowlist inspection.

It is not a production or vertical agent and contains no financial, commerce, ScriptureOS, Circle, logistics, or other product logic.

## Declarative definition

| Property | M1.3 value |
| --- | --- |
| Agent ID | `test.safe_agent` |
| Version | `1.0.0` |
| Lifecycle | `active` |
| Input | `{ "operation": "echo", "value": "synthetic hello" }` |
| Output | `{ "message": "synthetic hello" }` |
| Allowed tool | `test.safe_echo` |
| Allowed purpose | `test.execute_safe_tool` |
| Required scope | `test.safe_tool.invoke` |
| Autonomy | `assist` (Level 1) |
| Limits | 3 steps, 5,000 ms, 1 synthetic cost unit |
| Model capability | `text_generation` |

The input and output expectations are canonical JSON Schemas under `contracts/v1/agents/`. The versioned fixture under `fixtures/m1/agents/` conforms to `contracts/v1/agent-definition.schema.json`. The definition carries no executable callback, provider, concrete model, credential, or authority grant.

`test.safe_echo` is an allowlist declaration only. It is not registered or implemented, and allowlist membership does not grant permission or cause execution.

## Registry behavior

The M1.3 in-memory registry validates each definition before registration and keys it by exact `(agent_id, version)`. Duplicate registration is rejected rather than overwritten. Unknown agents and unknown versions produce distinct registry errors. There is no `latest` alias or semantic-version selection; `1.0.0` and a future `1.1.0` can coexist and must be requested explicitly.

Definitions and their nested values use frozen dataclasses and immutable tuples. A resolved value cannot mutate stored registry state.

Lifecycle values are limited to `draft`, `active`, `deprecated`, and `retired`. Lifecycle transition workflows are not implemented. A retired definition remains resolvable by exact ID/version for reproducibility and historical interpretation; it is not implicitly eligible for new execution.

## Validation boundary

Registration rejects missing or malformed identifiers, versions, ownership or purpose; unsupported lifecycle/autonomy values; invalid contract references; duplicate or malformed allowlist entries; invalid limits; and provider-specific model bindings. Model requirements describe capabilities only.

## Deferred work

- M1.4 owns model routing, fake/real adapters, and provider behavior.
- M1.5 owns registration and implementation of the first safe tool.
- M1.6 owns permission policy and actual allow/deny decisions.
- M1.7 owns runtime orchestration and limit enforcement.
- M1.8 owns audit persistence.

M1.3 implements none of those behaviors. The registry is process-local and has no database, file persistence, remote service, lifecycle workflow, marketplace, federation, or dynamic plugin system.
