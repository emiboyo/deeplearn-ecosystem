# Milestone 1.2 Module Boundaries

Status: Implementation guidance for the M1.2 skeleton. The root architecture documents remain authoritative.

## Minimal stack

M1.2 uses Python 3.12+, pytest, and the standard library first. Python 3.12 provides mature `Protocol`, typing, dataclass, `ast`, and packaging support sufficient to express and test boundaries without selecting an application framework or infrastructure platform.

The package has no application dependencies. Pytest is the sole test dependency. There is no HTTP framework, database, broker, container platform, cloud SDK, model/auth provider SDK, observability vendor, workflow engine, or dependency-injection framework.

## Contract authority

The JSON Schemas under `contracts/v1/` remain the canonical M1 wire and data contracts. Python's `WireDocument` alias is intentionally only a generic read-only mapping annotation used at interfaces. It does not validate, duplicate, or replace the schemas, and it is not a parallel domain model.

## Dependency direction

```text
test_client
    |
    v
runtime
    |
    +--> registry interface
    +--> models interface
    +--> tools interface
    +--> permissions interface
    +--> audit interface

registry/models/tools/permissions/audit --> contracts annotation only
```

Foundational modules must not import `runtime`. Core must not import `test_client`. Core imports must not target vertical/product namespaces, provider SDKs, or infrastructure SDKs. The graph must remain acyclic. Tests enforce these source-level rules with Python's standard-library AST.

## Ownership and exclusions

| Module | Owns in M1.2 | Explicitly does not own in M1.2 |
| --- | --- | --- |
| `runtime` | Orchestration entry-point protocol and dependency interface bundle | Orchestration behavior, direct storage, provider calls, arbitrary code execution, or vertical logic |
| `registry` | Versioned agent-definition lookup protocol | Test Agent definition, persistence, registration, or lifecycle behavior |
| `models` | Provider-neutral model invocation protocol | Routing, fake/real models, provider adapters, or provider response types |
| `tools` | Registered-tool invocation protocol | Tool implementation, dispatch, arbitrary functions, or credentials |
| `permissions` | Permission-decision protocol | Role/scope policy, allow/deny behavior, or an authorisation framework |
| `audit` | Append/query evidence protocols | File/database storage, persistent repository, redaction behavior, or audit processing |
| `test_client` | Programmatic forwarding boundary for an external test caller | UI, CLI, HTTP API, orchestration, permission logic, tool/model calls, or audit access |

## Deferred work

- M1.3 defines and registers the first Test Agent.
- M1.4 implements Model Router behavior and its first test double or adapter when authorised.
- M1.5 implements the first registered safe tool.
- M1.6 implements the first explicit permission policy.
- M1.7 composes bounded orchestration.
- M1.8 implements the audit test repository/persistence boundary.

No item above is implemented by this skeleton.
