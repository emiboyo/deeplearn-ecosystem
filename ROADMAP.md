# Ecosystem Roadmap

This roadmap sequences learning and customer value, not speculative scale. Phase gates are evidence-based; phases may overlap only where boundaries and safety remain clear. Dates are intentionally omitted.

## NOW

### Phase 0 — Architecture/Foundation

- Ratify the six foundation documents and assign architecture ownership.
- Resolve the open choices listed below only when needed for the first slice.
- Define first-slice contracts, threat model, data classification and evaluation cases.
- Establish lightweight review, branching, ADR and documentation checks.
- **Exit evidence:** Architecture reviewed; first slice has acceptance tests, named owners and bounded risk.

### Phase 1 — Core Runtime

- Deliver one end-to-end walking skeleton: test client to test agent, model router, one safe tool, permission check, execution, audit record and response.
- Use one provider through an owned adapter without claiming multi-provider maturity.
- Add structured errors, idempotency, correlation, limits, telemetry and deterministic test doubles.
- **Exit evidence:** Repeatable local/test execution; permission denials and failures are tested; every run is traceable.

## NEXT

### Phase 2 — First Vertical Proof

- Select one narrow, valuable, low-risk vertical outcome using explicit criteria.
- Implement its domain logic in the vertical, with an adapter to Core.
- Validate with real users, consented feedback, outcome measures and an agent evaluation suite.
- **Exit evidence:** Demonstrated user value and reliability; no cross-product private-data shortcut.

### Phase 3 — Shared Agent Infrastructure

- Generalise only capabilities proven by the first vertical: registry, context, controlled memory, workflows, approvals, evaluations, observability and usage accounting.
- Add a second workflow or vertical to test that shared abstractions are genuinely reusable.
- **Exit evidence:** Two consumers use stable Core contracts without moving their domain logic into Core.

## LATER

### Phase 4 — Cross-Product Orchestration

- Introduce one consented API/event interaction across product boundaries.
- Add contract tests, delegated scopes, outbox/inbox reliability and end-to-end audit.
- Pilot bounded agent-to-agent delegation without authority amplification.
- **Exit evidence:** Cross-product outcome works under denial, revocation, timeout and partial failure.

### Phase 5 — Increasing Autonomy

- Progress selected actions from Assist to Recommend to Prepare and, where justified, Execute.
- Gate each increase with outcome evidence, risk analysis, evaluations, monitoring, limits, approval/delegation and rollback.
- **Exit evidence:** Defined reliability and safety thresholds are met in the intended population and environment.

### Phase 6 — Platform / External API Expansion

- Productise stable APIs for authorised external human and machine customers.
- Add developer onboarding, capability discovery, credentials, quotas, billing/usage, compatibility and abuse controls.
- **Exit evidence:** External integrations can operate securely without privileged internal knowledge.

### Phase 7 — Mature Ecosystem

- Operate multiple independently accountable verticals on shared intelligence contracts.
- Support federated agent coordination, company spin-outs and physical/digital execution where economically validated.
- Continuously improve trust, evaluation, regulatory posture and outcome-linked data flywheels.
- **Exit evidence:** Shared Core produces measurable leverage without weakening vertical isolation or autonomy.

## DO NOT BUILD YET

- A giant super-app or universal cross-product customer profile.
- A microservice estate, Kubernetes platform, multi-cloud abstraction or global event mesh.
- General autonomous agent swarms, open-ended recursive delegation or arbitrary code execution.
- Production databases, payment systems, broad authentication platform or provider marketplace before a validated slice needs them.
- Full multi-provider routing, durable long-term memory or external developer platform before their contracts are proven.
- Cross-product analytics or model training on private data without explicit governance, consent and purpose.
- Infrastructure sized for 2035 rather than present evidence.

## Open roadmap choices

- Which vertical and customer outcome should be the first proof after the neutral test-agent slice?
- What makes an action “consequential” in each vertical, and who can delegate it?
- Which jurisdictions, data-residency constraints and regulated activities enter initial scope?
- What availability, latency and cost targets are justified by the first user workflow?
