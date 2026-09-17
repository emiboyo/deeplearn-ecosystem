# Milestone 1.5 Safe Tool

Status: M1.5 deterministic test-tool boundary. The root architecture documents remain authoritative.

## Purpose and ownership

`test.safe_echo@1.0.0` was chosen because it proves typed registration, validation, dispatch, limits, and failure handling without accessing external state. It returns bounded synthetic text supplied by the caller and is not a production or domain capability.

All implementation behavior is owned by `deeplearn.core.tools`. The module depends only on shared contracts and the Python standard library. M1.5 does not implement permission decisions; declared scopes and purposes are metadata for later policy evaluation.

## Declarative metadata

| Property | M1.5 value |
| --- | --- |
| Tool ID/version | `test.safe_echo@1.0.0` |
| Owner | `deeplearn.core.test` |
| Lifecycle | `active` |
| Risk | `low` |
| Side effect | `none` |
| Required scope | `test.safe_tool.invoke` |
| Allowed purpose | `test.execute_safe_tool` |
| Timeout | 1,000 ms |
| Maximum input/output | 256 characters each |
| Idempotent | `true` |
| Consequential | `false` |

The immutable fixture is validated against the concepts in `contracts/v1/tool-definition.schema.json`. The input and output schemas accept only `{ "value": string }` and `{ "message": string }`, respectively, with no additional properties.

## Registry and dispatch

The process-local registry accepts explicit definition/adapter pairs keyed by exact tool ID and semantic version. It rejects duplicates, mismatched adapter identities, unknown tools, and unknown versions. Multiple explicit versions may coexist; there is no `latest` alias, discovery, plugin loading, remote registry, or persistence.

The canonical M1 `ToolRequest` and `ToolResult` schemas remain the external wire envelopes. The owned frozen Python request is the validated tool-boundary projection needed for dispatch: request/tool identifiers, immutable arguments, correlation/optional trace identifiers, and timeout. Principal, permission, approval, and idempotency orchestration remain outside M1.5.

Dispatch validates the request, resolves the exact registered version, validates arguments and size before invocation, invokes only that adapter, validates the bounded output, and returns a normalized result. Unknown, malformed, or oversized calls cannot reach an adapter. The Python result permits only `succeeded` with output or `failed` with failure. The v1 wire schema enforces the same payload binding while retaining its published `timed_out` and `denied` non-success statuses, all of which require failure and prohibit result.

## Deterministic adapter and failures

The default adapter returns the input value unchanged as `{ "message": value }` with a fixed synthetic latency of 5 ms. It reads no network, filesystem, environment, database, credential, or mutable external state and executes no arbitrary code. Its deterministic test modes simulate unavailable, timeout, and generic failure paths.

Failures are safe and machine-readable: `invalid_tool_request`, `tool_not_registered`, `tool_version_not_found`, `tool_unavailable`, `tool_timeout`, `tool_failure`, and `input_too_large`. Raw exception text and stack traces do not cross the boundary.

## Deferred work

M1.5 does not implement permission decisions, agent allowlist orchestration, model-directed tool selection, runtime orchestration, audit or idempotency persistence, dynamic plugins, real external tools, network/database access, or vertical logic. Those remain subject to later milestones and review.
