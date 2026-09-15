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
- **Decision:** Preserve each vertical's separable domain contracts, domain data ownership, migrations, identity/authorisation contexts, deployment configuration, economics and operational accountability, with its own release lifecycle where practical and independently replaceable or deployable boundaries over time. This does not require microservices today.
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

## ADR-013 — Cross-product access is purpose-bound

- **Status:** Accepted
- **Context:** A principal may hold a permission that is valid for one workflow but not for unrelated reuse of another product's data or capability. Authentication and broad permission alone cannot establish that a particular cross-product use is authorised.
- **Decision:** Cross-product access must be both permission-bound and purpose-bound. Each request carries an explicit declared purpose where relevant, and the receiving product evaluates whether that purpose is authorised alongside principal, tenant, product, resource, action, consent, delegation, risk, and limits. For example, PBcoms may request PearlBridge fulfilment with purpose `fulfil_customer_order`; it may not reuse PearlBridge customer data for unrelated analytics without explicit lawful purpose and permission.
- **Consequences:** Contracts and policy decisions must represent purpose and audit the decision. Callers cannot treat possession of a credential or scope as permission for secondary use, and receiving products remain accountable for enforcing their data purposes.

## ADR-014 — No authority amplification

- **Status:** Accepted
- **Context:** Delegated agents, workflows, tools, and services can create confused-deputy paths if a downstream actor gains authority that the accountable originator did not possess or could not delegate.
- **Decision:** An agent may never grant itself, another agent, or another service more authority than the originating principal possesses and is permitted to delegate. Authority must narrow or remain equivalent through agent-to-agent delegation, tool invocation, workflow delegation, cross-product requests, and service-to-service calls. Additional authority requires a separate independently authorised principal and a recorded policy decision.
- **Consequences:** Delegation chains must preserve the originating principal, validate delegability at every hop, attenuate effective scopes where needed, and remain auditable. Convenience service credentials cannot silently amplify caller authority.

## ADR-015 — Customer data is not an automatic training corpus

- **Status:** Accepted
- **Context:** Operational access to customer or vertical data for an authorised request does not establish a lawful or expected basis for model training or secondary cross-product learning.
- **Decision:** Customer or vertical data must not be automatically used for model training, fine-tuning, external-provider training, or cross-product learning datasets. Any such use requires explicit governance, lawful basis, declared purpose, approval, and appropriate consent or contractual authority. Provider settings and contracts must prevent training on customer data wherever product policy or law requires it.
- **Consequences:** Operational and training purposes remain separate; datasets require provenance and governance; model-provider selection and configuration must enforce applicable non-training commitments. Evaluation and improvement workflows cannot silently convert production data into training material.
