# Milestone 1.1 Contracts and Acceptance

Status: M1.1 technology-neutral contract baseline

## Purpose and scope

These contracts define the boundary shapes and acceptance expectations for the governed Milestone 1 walking skeleton. They describe data, meaning, and failure behavior only; they are not a runtime implementation.

The default M1 path uses the synthetic `test.safe_agent` version `1.0.0`, the registered synthetic `test.safe_echo` tool, and non-consequential test data. The contracts can also represent consequential actions and approval state without implementing approval execution.

## Ownership

| Contract | Owning Core boundary | Intent |
| --- | --- | --- |
| `PrincipalContext` | Identity and Permission Engine | Carry authenticated principal, product/tenant, consent, purpose, and structured authority facts for evaluation |
| `ExecutionRequest` / `ExecutionResult` | Agent Runtime | Start and report a bounded versioned agent execution |
| `ToolRequest` / `ToolResult` | Tool Registry | Request and report one registered, typed tool invocation |
| `Decision` | Permission Engine | Explain an allow, deny, or approval-required result and its constraints |
| `Error` | Shared Core contract | Return safe machine-readable failure information across boundaries |
| `AuditRecord` | Audit System | Record minimised attributable evidence of an auditable attempt and outcome |

Owning boundaries govern their contracts. Consumers may propose additive changes, but do not assume ownership or bypass the owning interface.

## Versioning and compatibility

Schemas use JSON Schema Draft 2020-12 and an explicit `1.0` document version. Published v1 contracts should evolve additively where practical. Consumers must ignore neither unknown fields nor incompatible versions silently: schema validation and negotiated compatibility apply at boundaries. Breaking semantic or structural changes require a new major contract path such as `contracts/v2/`; compatible clarifications or optional fields may remain in v1 with review and fixtures.

Schema `$id` values are stable logical identifiers, not a commitment to host schemas at that example domain.

## Purpose semantics

`purpose` is a machine-readable identifier matching a controlled identifier shape, not arbitrary descriptive prose. M1 examples use `test.execute_safe_tool` and `test.read_capability`. The receiving policy boundary evaluates the purpose independently of permissions; possession of a scope is not sufficient by itself. A later controlled vocabulary may govern registration and lifecycle without changing this representation.

## Authority and delegation

`PrincipalContext.delegated_authority` preserves an originating principal reference, a delegation reference, structured delegable and effective scopes, policy references, and optional expiry. These fields deliberately permit later machine comparison and attenuation. They do not define a complete permission algebra or grant authority.

Effective delegated authority remains the intersection of originating principal authority, delegable authority, requested action and purpose, policy constraints, and tool or service constraints. Each receiving boundary re-evaluates authentication, permission, purpose, and policy. Delegation and idempotency never amplify authority.

## Consequential actions and approval

The `consequential` flag applies the architecture's provisional definition: an action may be consequential when it creates meaningful financial, legal/regulatory, physical-world, irreversible, privacy/data-sharing, safety, account/identity/permission, or externally visible effects. Product policy may refine that classification.

Requests, decisions, and audit records can state whether an action is consequential and whether approval is required, plus approval status/reference where relevant. The M1 fixture path is deliberately safe and non-consequential. Approval workflow behavior is not implemented or decided here.

## Correlation, tracing, and causation

- Ingress creates a correlation ID when the caller does not supply one.
- The correlation ID remains stable throughout the end-to-end request, including decisions, tools, results, errors, and audit records.
- Trace and span IDs may change at each hop but remain linked by the tracing system; schemas carry the current trace reference where relevant.
- Causation IDs preserve which prior request or event caused later work and prepare contracts for future events.
- Identifiers are opaque and must never contain sensitive or customer information.

The success fixtures demonstrate `corr_test_0001` propagating across the complete contract sequence while hop-specific trace IDs may differ.

## Idempotency

- A caller supplies an idempotency key where required; an ingress boundary may generate one when its contract permits.
- The key is scoped at least to the authenticated principal and operation/action, with tenant/product context included where needed.
- The system records a canonical request fingerprint and durable outcome when persistence is later implemented.
- The same key with a materially identical request may safely return the prior result.
- The same key with a materially different request is rejected as `idempotency_conflict`.
- An idempotency key does not grant permission. Authentication, permission, purpose, consent, delegation, and policy remain independently evaluated or re-evaluated according to the authoritative architecture.

M1.1 specifies these semantics only; it does not implement an idempotency store.

## Error semantics

`Error` separates stable machine-readable `category` and `code` values from a bounded safe message. Categories distinguish invalid input, authentication, permission, approval, provider/tool failure and timeout, policy failure, limits, idempotency conflict, and internal failure. `retryable` is explicit and does not itself authorise a retry.

Public errors never expose secrets, credentials, full sensitive payloads, stack traces, or raw provider errors. Protected diagnostic systems may retain separately governed references correlated through safe identifiers.

## Acceptance fixture catalogue

| Fixture | Expected acceptance behavior |
| --- | --- |
| `success/` | Request is valid; permission allows the purpose/action; the safe tool and execution succeed; correlation propagates; a minimised audit record is present |
| `denial/decision.json` | Purpose is denied even if a potentially relevant scope exists; no tool execution follows |
| `invalid-input/` | The intentionally invalid request fails schema validation and returns the safe `invalid_input` error |
| `provider-failure/execution-result.json` | Provider failure is normalised, safe, attributable, and marked retryable without leaking raw details |
| `tool-failure/tool-result.json` | Tool failure is normalised at the tool boundary and carries correlation/timing metadata |
| `timeout/execution-result.json` | A provider deadline becomes the distinct `provider_timeout` category and a timed-out execution |
| `idempotent-replay/` | Original and replay requests are materially identical and may return the recorded prior result |
| `idempotency-conflict/` | The same scoped key with different input is rejected as `idempotency_conflict` |

The invalid request is the only fixture intentionally not valid against its named request schema. Its paired expected error is valid against `error.schema.json`.

## Intentionally undecided

M1.1 does not select a programming language, application framework, database, queue or broker, cloud, model provider, authentication provider, or observability vendor. It does not select an authorisation framework, implement persistence, create an agent/module skeleton, register a real tool, execute approvals, or begin M1.2.
