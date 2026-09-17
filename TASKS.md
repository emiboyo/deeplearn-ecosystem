# Prioritised Implementation Backlog

No task in this file is implemented by the architecture-foundation change. Tasks should be completed as small, reviewed changes and must obey `ENGINEERING_RULES.md`.

## P0 — Milestone 1: governed end-to-end walking skeleton

Target flow:

```text
User/Test Client
  -> Test Agent
  -> Model Router
  -> One Safe Tool
  -> Permission Check
  -> Execution
  -> Audit Record
  -> Response
```

### M1.1 — Define acceptance and contracts

- [x] Write success, denial, invalid-input, provider-failure, tool-failure and timeout examples.
- [x] Define versioned `PrincipalContext`, `ExecutionRequest/Result`, `ToolRequest/Result`, `Decision`, error and audit schemas.
- [x] Classify the test data and document what must never enter prompts or logs.
- [x] Define correlation-ID and idempotency behavior.
- **Done when:** Contract fixtures and failure expectations are reviewed without selecting irreversible technology.

### M1.2 — Create the minimal module skeleton

- [x] Establish cohesive Core module boundaries and dependency rules for runtime, registry, model, tool, permission and audit.
- [x] Add a minimal test-client boundary; do not build a production UI.
- [x] Add architectural dependency tests or equivalent checks supported by the chosen stack.
- **Done when:** Modules compile/run with placeholders and no provider or vertical logic leaks across interfaces.

### M1.3 — Define and register the Test Agent

- [x] Create one versioned agent definition with typed input/output, tool allowlist, limits and owner.
- [x] Validate malformed definitions and prohibit unregistered tools.
- [x] Add lifecycle and version-resolution tests.
- **Done when:** The runtime resolves an immutable test-agent version from the registry.

### M1.4 — Implement the Model Router boundary

- [x] Define the owned model request/result and capability contracts.
- [x] Build a deterministic fake adapter for tests.
- [x] Confirm no real provider adapter is authorised or needed for M1.4; keep secrets external.
- [x] Record selected provider/model/version when available, latency and usage.
- **Done when:** Provider substitution requires no domain or agent-runtime change and errors are normalised.

### M1.5 — Implement one safe tool

- [x] Choose a read-only, deterministic, non-sensitive tool such as a bounded calculation or static capability lookup.
- [x] Define schemas, owner, risk, scopes, limits, timeout and side-effect metadata.
- [x] Validate input/output and test malformed, oversized, timeout and unavailable paths.
- **Done when:** Only registered calls with valid arguments can reach the adapter.

### M1.6 — Implement permission checks

- [ ] Define the first explicit role/scope policy and deny-by-default behavior.
- [ ] Evaluate before tool execution and return machine-readable reasons.
- [ ] Test allowed, denied, wrong-tenant, missing-scope and policy-error cases.
- **Done when:** No safe-tool execution path can bypass a recorded permission decision.

### M1.7 — Orchestrate bounded execution

- [ ] Connect request validation, registry, router, tool request, permission and tool result.
- [ ] Enforce step, time and cost limits; reject arbitrary tool or code requests.
- [ ] Propagate cancellation, correlation/trace IDs and typed failures.
- **Done when:** The exact target flow succeeds and every failure exits predictably.

### M1.8 — Create the audit record

- [ ] Define an append-only repository interface and local/test implementation.
- [ ] Capture required identity, agent, model, tool, permission, outcome, time, correlation and failure metadata.
- [ ] Redact secrets and sensitive payloads; test write failure behavior.
- **Done when:** Every consequential attempt has a queryable record correlated with the response.

### M1.9 — Add idempotency and retry safety

- [ ] Persist idempotency key, request fingerprint and outcome at the execution boundary.
- [ ] Return the previous result for identical repeats and reject mismatched reuse.
- [ ] Retry only simulated transient, idempotent failures with bounded backoff.
- **Done when:** Tests demonstrate no duplicate effect under repeat, timeout and retry scenarios.

### M1.10 — Verify and document the slice

- [ ] Add unit, integration, permission, isolation and failure-path tests.
- [ ] Create a small evaluation set for correct tool choice, refusal and response grounding.
- [ ] Document local use, contracts, trace inspection, limitations and threat assumptions.
- [ ] Review against all accepted ADRs and record any proposed deviation.
- **Done when:** Clean setup reproduces the flow and all checks pass without external credentials by default.

## P1 — Select and prove the first vertical

- [ ] Score candidate outcomes by customer value, accessibility, risk, data availability and learning value.
- [ ] Record the selection and rejected alternatives in an ADR or product decision.
- [ ] Define the vertical-owned entity, policy and adapter; keep it out of Core.
- [ ] Run a small user validation with explicit success and safety measures.
- [ ] Add an approval step if the selected action is consequential.

## P2 — Harden only what evidence requires

- [ ] Add durable workflow state and approval binding for the validated workflow.
- [ ] Add context provenance and user-controlled memory only when the use case needs persistence.
- [ ] Establish evaluation gates, SLOs, cost budgets and incident/runbook basics.
- [ ] Add a second model/provider adapter when continuity, cost or quality evidence justifies it.
- [ ] Add a second consumer to validate shared Core abstractions.

## P3 — First cross-product contract

- [ ] Choose one user-consented interaction (for example, PBcoms requesting a PearlBridge quote).
- [ ] Define API/event ownership, scopes, purpose, schemas, idempotency, errors, retention and deprecation.
- [ ] Implement consumer/provider contract, isolation, revocation and end-to-end audit tests.
- [ ] Exercise timeout, duplicate, unavailable and partial-failure recovery.

## Backlog rules

- Do not start a lower-priority platform capability merely because it is interesting.
- Split tasks further when a change cannot be reviewed independently.
- Each task names acceptance criteria, owner, affected boundary, permissions, data, tests, observability and documentation before implementation.
- Mark completion only after evidence is committed; link architectural changes to an ADR.
