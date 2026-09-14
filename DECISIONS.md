# Architecture Decision Records

This file contains accepted foundation decisions. Proposed changes must be added as new ADRs; never edit history to hide a superseded decision.

## ADR-001 — Modular monolith first

- **Status:** Accepted
- **Context:** The ecosystem needs fast validation and clear boundaries without premature distributed-system cost.
- **Decision:** Begin as a modular monolith where practical, with cohesive modules, explicit interfaces and owned data. Extract services only with measured scaling, isolation, regulatory or organisational need.
- **Consequences:** Simpler operation and refactoring now; discipline and contract tests are required to prevent a coupled monolith.

## ADR-002 — Provider-agnostic model layer

- **Status:** Accepted
- **Context:** Model capabilities, economics, availability and policy change quickly.
- **Decision:** Route model use through Core-owned interfaces and provider adapters. Domain code must not depend directly on a provider SDK or provider-specific response shape.
- **Consequences:** Providers can be compared or replaced; capability differences must remain explicit and adapters add modest work.

## ADR-003 — Vertical data isolation

- **Status:** Accepted
- **Context:** Products handle different sensitive domains and may become independent companies.
- **Decision:** Each vertical owns a logically isolated domain store. Shared identity does not confer shared data access, and Core is not a private-data lake.
- **Consequences:** Privacy, accountability and spin-outs are safer; approved sharing requires explicit contracts and may duplicate carefully governed derived data.

## ADR-004 — API/event-based cross-product communication

- **Status:** Accepted
- **Context:** Direct database coupling defeats ownership and independent evolution.
- **Decision:** Cross-product interactions use authenticated, authorised, versioned APIs, service contracts or events. Direct access to another product's private database is prohibited.
- **Consequences:** Boundaries and audit improve; versioning, failure handling and contract testing are mandatory.

## ADR-005 — Human approval for consequential actions

- **Status:** Accepted
- **Context:** Agent actions can create financial, legal, physical, privacy or reputational harm.
- **Decision:** A consequential action requires approval bound to the exact proposal unless explicit, unexpired delegated authority permits it. Permission is rechecked at execution.
- **Consequences:** Safer progressive autonomy and clear accountability; workflows must support pause, expiry, rejection and changed proposals.

## ADR-006 — Core owns generic intelligence; verticals own domain logic

- **Status:** Accepted
- **Context:** Reuse is valuable, but centralising domain meaning creates coupling and weak accountability.
- **Decision:** DeepLearn Core owns generic agent, model, context, memory, tool, workflow, event, permission, approval, audit, evaluation and observability mechanisms. Verticals define domain entities, rules, policy and operations.
- **Consequences:** Reuse without a super-app; placement disputes are resolved by whether behavior is domain-independent.

## ADR-007 — Agents cannot access arbitrary databases

- **Status:** Accepted
- **Context:** Unrestricted data access bypasses policy, validation and audit.
- **Decision:** Agents invoke registered typed tools, repositories and APIs with least privilege. No arbitrary queries, code execution, or credentials are exposed to an agent.
- **Consequences:** Tooling takes deliberate design; security, testability and action-level audit improve.

## ADR-008 — PearlBridge may remain separately deployed

- **Status:** Accepted
- **Context:** Physical logistics has distinct operational, regulatory and company needs.
- **Decision:** Treat PearlBridge Network as a product boundary that may stay outside the monorepo and integrate through machine-readable APIs and events.
- **Consequences:** Independent operation and ownership remain possible; distributed failure and contract compatibility must be designed explicitly.

## ADR-009 — Support future product spin-outs

- **Status:** Accepted
- **Context:** Verticals may become independent companies.
- **Decision:** Preserve separable data ownership, identity/authorisation contexts, service contracts, deployment configuration, economics and operational accountability. This does not require microservices today.
- **Consequences:** Clearer boundaries and optionality; shared shortcuts that prevent separation are disallowed.

## ADR-010 — Architecture documentation is authoritative

- **Status:** Accepted
- **Context:** Multiple AI systems and humans will contribute over time.
- **Decision:** The documented hierarchy in `ENGINEERING_RULES.md` governs work. Implementation must not silently override architecture; disagreements require an explicit ADR.
- **Consequences:** Changes are explainable and reviewable; documentation must remain current.

## ADR-011 — Consequential actions require audit records

- **Status:** Accepted
- **Context:** Trust requires evidence of who or what acted, under which authority, and with what result.
- **Decision:** Record every consequential attempt and outcome with the fields defined in the Core specification, including correlation/trace IDs and failures where applicable.
- **Consequences:** Accountability and investigation improve; audit storage needs strict minimisation, integrity and access controls.

## ADR-012 — Autonomous coding agents do not write directly to main

- **Status:** Accepted
- **Context:** Automated changes need review and recoverability.
- **Decision:** Autonomous coding agents work on focused branches and must not directly commit or push to `main`, merge, force-push, rewrite history, or delete branches.
- **Consequences:** Human review remains a control point; emergency exceptions require explicit human direction and a recorded rationale.
