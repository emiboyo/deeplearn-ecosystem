# DeepLearn Core — Initial Specification

Status: Initial authoritative specification. Details intentionally remain reversible until validated.

## Scope and invariants

DeepLearn Core supplies generic governed intelligence capabilities. It does not own vertical business semantics or pool vertical private data. All calls carry an authenticated principal, tenant and product context, requested action, correlation/trace ID, and—when relevant—delegated authority and purpose. Interfaces below are logical contracts; they do not prescribe language, framework, database, broker, or deployment provider.

An **agent definition** is a versioned declarative contract containing identity, owner, purpose, allowed autonomy, input/output schemas, instructions or policy references, model requirements, registered tools, memory/context policy, permission scopes, budgets/limits, evaluation suite, and lifecycle status. A running agent is an execution of one definition version; it is never authority by itself.

Three identity types must remain distinct:

- **Human Principal:** the authenticated human ultimately responsible for an action.
- **Service Principal:** an authenticated backend service or trusted system identity accountable for a request.
- **Agent Execution Identity:** the specific running agent instance and definition version performing work.

An Agent Execution Identity does not independently own authority. Its authority always derives from an authenticated Human Principal or Service Principal plus explicit delegation and policy. An agent may never grant itself, another agent, or another service more authority than the originating principal possesses and is permitted to delegate. Across agent-to-agent delegation, tool invocation, workflow delegation, cross-product requests, and service-to-service calls, authority may only narrow or remain equivalent unless a separate independently authorised principal grants additional authority.

## Common contract vocabulary

- `PrincipalContext`: authenticated Human Principal or Service Principal, tenant, product, roles, consent and delegation references.
- `AgentExecutionIdentity`: execution ID, agent definition/version, owning product/service and accountable originating principal reference; it is not an independent authority source.
- `ExecutionRequest/Result`: Agent Execution Identity, typed input/output, policy and budget envelope, timestamps and status.
- `ToolRequest/Result`: registered tool/version, validated arguments/result, idempotency key and evidence.
- `Decision`: allow, deny, or require approval, plus reasons, constraints and policy version.
- `EventEnvelope`: event ID/type/version, producer, subject, occurred-at, tenant/product, trace/correlation/causation IDs, classification and payload reference.
- Contracts are versioned, schema-validated, authenticated, authorised, observable, and documented with compatibility and error semantics.

### Capability Manifest

A `CapabilityManifest` is a versioned, machine-readable description of what a product, agent, or service can do. A manifest may include capability name and version, input/output schema, required permissions, required purpose, risk classification, side-effect classification, whether approval may be required, idempotency behavior, and availability or deprecation state. For example, PBcoms may advertise `create_order`, `get_inventory`, and `request_fulfilment`, while PearlBridge may advertise `quote_delivery`, `book_delivery`, and `track_delivery`.

A manifest supports discovery only and does not grant authority. Every invocation still requires authentication, permission checks, purpose checks, policy evaluation, and approval where applicable. Registry implementation is deferred.

## Module specifications

### Agent Runtime

- **Purpose:** Safely orchestrate one agent execution.
- **Responsibilities:** Validate requests; load a registry definition; obtain context; select a model; run bounded plan/tool loops; check permissions and approvals; enforce time/cost/step limits; return typed results; emit audit and telemetry.
- **Non-responsibilities:** Domain policy, arbitrary code execution, direct database access, provider-specific business logic.
- **Public interface:** `execute`, `resume`, `cancel`, `getStatus`; streaming is an optional capability.
- **Dependencies/data:** Registry, router, context, tools, permissions, approvals, audit, evaluations and observability; accesses only execution metadata and data explicitly supplied by authorised dependencies.
- **Security/permissions:** Authenticate caller; constrain tools, data, models and budgets; isolate tenant execution; treat model output as untrusted.
- **Events:** Emits execution started/paused/completed/failed/cancelled and tool requested; consumes approval resolved, cancellation and tool completion.
- **MVP / later:** MVP supports one bounded synchronous agent and safe tool. Later supports durable, concurrent, resumable and delegated executions.

### Agent Registry

- **Purpose:** Authoritative catalogue of agent definitions and versions.
- **Responsibilities:** Validate, version, activate/deprecate, discover and resolve definitions; retain ownership and evaluation status.
- **Non-responsibilities:** Execute agents, store conversations, grant runtime authority.
- **Public interface:** `registerVersion`, `getVersion`, `resolveActive`, `listCapabilities`, `changeLifecycle`.
- **Dependencies/data:** Identity, permissions, evaluation metadata and audit; stores definitions and lifecycle metadata only.
- **Security/permissions:** Separate read/use/publish/activate rights; immutable published versions; signed or integrity-checked artifacts later.
- **Events:** Emits registered/activated/deprecated; consumes evaluation-qualified and owner/lifecycle commands.
- **MVP / later:** File or simple repository-backed definitions with manual activation; later governed catalogue, staged rollout and provenance.

### Model Router

- **Purpose:** Select and invoke models without binding domain code to a provider.
- **Responsibilities:** Normalise requests/results; capability discovery; routing by policy, quality, latency, cost, region and availability; enforce budgets; capture provider/model metadata; fallback where safe.
- **Non-responsibilities:** Decide business actions, own prompts or conceal semantic differences between models.
- **Public interface:** `complete`, `stream`, `embed` where supported, `capabilities`, `estimate`.
- **Dependencies/data:** Provider adapters, configuration/secrets, policy, telemetry and evaluation scores; transient authorised prompt/context only.
- **Security/permissions:** Provider allowlists, residency/classification controls, secret isolation, prompt minimisation and redaction. Provider settings and contracts prevent training on customer data wherever product policy or law requires it.
- **Events:** Emits model invocation completed/failed/rerouted and budget exceeded; consumes provider health/config changes.
- **MVP / later:** One adapter behind an owned interface and explicit model selection; later policy routing, multiple providers, hedging and continuous quality/cost optimisation.

### Tool Registry

- **Purpose:** Catalogue controlled capabilities agents may request.
- **Responsibilities:** Register versioned schemas, ownership, risk, scopes, side-effect and idempotency metadata; validate input/output; dispatch to adapters.
- **Non-responsibilities:** Grant permission, infer authority, expose arbitrary functions or credentials.
- **Public interface:** `register`, `describe`, `listAllowed`, `validate`, `invoke`.
- **Dependencies/data:** Permissions, approvals, adapters, audit and observability; only request/result data defined by each tool contract.
- **Security/permissions:** Least-privilege credentials; allowlisted destinations; input/output validation; rate, cost and timeout limits; sandboxing where relevant.
- **Events:** Emits invocation requested/succeeded/failed; consumes tool lifecycle and revocation events.
- **MVP / later:** One read-only or reversible safe tool; later remote tools, capability negotiation and delegated tool ecosystems.

### Permission Engine

- **Purpose:** Make explainable, consistent authorisation decisions.
- **Responsibilities:** Evaluate principal, tenant, product, purpose, resource, action, consent, delegation, risk and limits; return allow/deny/approval with constraints and policy version.
- **Non-responsibilities:** Authenticate identities, execute actions, assume consent, encode all domain regulation centrally.
- **Public interface:** `evaluate`, `explain`, `validateDelegation`, `listEffectiveScopes`.
- **Dependencies/data:** Identity/authorisation attributes, product policy adapters, consent/delegation records and audit; minimal policy facts only.
- **Security/permissions:** Deny by default, fail closed for consequential operations, policy change controls and decision integrity.
- **Events:** Emits decision made and policy changed; consumes identity, consent, delegation and policy updates.
- **MVP / later:** Explicit role/scope rules for first slice; later attribute/risk-aware policies, simulation and formal policy testing.

### Memory Architecture

- **Purpose:** Retain permitted information across interactions with provenance and lifecycle controls.
- **Responsibilities:** Separate working, episodic, semantic and preference memory; write/read via policy; track source, purpose, confidence, tenancy, retention and deletion.
- **Non-responsibilities:** Act as an unrestricted transcript dump, shared vertical database, source of authority, or automatic training corpus.
- **Public interface:** `put`, `retrieve`, `correct`, `forget`, `expire`, `explainProvenance`.
- **Dependencies/data:** Permissions, data access, knowledge, audit and product-owned stores; only scoped memory records or references.
- **Security/permissions:** Product/tenant isolation, consent, purpose limitation, sensitive-class controls, deletion propagation and injection-resistant retrieval.
- **Events:** Emits memory written/corrected/expired/deleted; consumes consent revoked, retention elapsed and source corrected.
- **MVP / later:** Execution-scoped working memory only; later durable user-approved memory, consolidation and provenance-aware retrieval.

### Context Engine

- **Purpose:** Assemble the smallest authorised, relevant, traceable context for an execution.
- **Responsibilities:** Resolve sources, permissions and freshness; rank, budget and package context; attach citations/provenance; resist malicious retrieved instructions.
- **Non-responsibilities:** Persist system-of-record data, bypass permissions, decide outcomes.
- **Public interface:** `buildContext`, `refresh`, `explainSources`, `invalidate`.
- **Dependencies/data:** Memory, knowledge, data-access adapters, permissions and model token estimates; authorised excerpts/references only.
- **Security/permissions:** Re-authorise at retrieval, minimise sensitive data, preserve source trust labels and tenant boundaries.
- **Events:** Emits context built/failed/invalidated; consumes source changed, permission changed and memory lifecycle events.
- **MVP / later:** Static trusted context plus request data; later ranked multi-source, freshness-aware and adaptive context.

### Workflow Engine

- **Purpose:** Coordinate deterministic, durable multi-step work around agent decisions.
- **Responsibilities:** Version workflow definitions; manage state, timers, branching, compensation, approvals, retries and resumability.
- **Non-responsibilities:** Replace agent reasoning, define vertical meaning, hide side effects.
- **Public interface:** `start`, `signal`, `resume`, `cancel`, `getState`.
- **Dependencies/data:** Runtime, tools, events, approvals, permissions, audit and state repository; workflow state and references, not copied domain stores.
- **Security/permissions:** Re-check authority before delayed side effects; immutable definition version per run; protect signals.
- **Events:** Emits workflow/step lifecycle and compensation events; consumes signals, approvals, tool results and timers.
- **MVP / later:** Simple explicit sequence for first slice; later durable long-running workflows, compensation and visual inspection.

### Event Bus

- **Purpose:** Decouple authorised state-change notifications across modules and products.
- **Responsibilities:** Version envelopes, publish/subscribe, delivery policy, deduplication support, dead-letter handling and contract governance.
- **Non-responsibilities:** Become a private-data dump, guarantee business-level exactly-once effects, replace request/response APIs.
- **Public interface:** `publish`, `subscribe`, `acknowledge`, `replay` subject to policy.
- **Dependencies/data:** Identity, permissions, schema registry, transport adapter and observability; minimal event facts or protected references.
- **Security/permissions:** Topic and field-level access, tenant partitioning, integrity, retention and replay controls.
- **Events:** Carries versioned domain/platform events; consumes transport health and subscription lifecycle signals.
- **MVP / later:** In-process events with durable contract tests; later broker adapter, outbox/inbox, replay and cross-company delivery.

### Human Approval Engine

- **Purpose:** Obtain informed human authority for a precisely defined consequential action.
- **Responsibilities:** Create tamper-evident requests; present action, rationale, risk and expiry; authenticate approver; approve/reject/revoke; bind decision to action hash and constraints.
- **Non-responsibilities:** Manufacture consent, approve changed actions, replace permission checks.
- **Public interface:** `requestApproval`, `decide`, `getStatus`, `revoke`, `verifyBinding`.
- **Dependencies/data:** Identity, permissions, notifications, workflow and audit; proposal, evidence, decision and minimal display data.
- **Security/permissions:** Eligible approvers only, separation of duties where needed, expiry, replay prevention and re-authorisation at execution.
- **Events:** Emits approval requested/granted/rejected/expired/revoked; consumes proposal changed, identity revoked and timeout.
- **MVP / later:** Single approver and synchronous/manual resolution; later multi-party, thresholds, escalation and policy-driven delegation.

### Audit System

- **Purpose:** Provide attributable, queryable evidence of consequential activity.
- **Responsibilities:** Append records for initiator, identity, agent/version, model/provider/version, tools, appropriate data-access facts, permission/approval, outcome, timestamp, trace/correlation and failures; control retention and access.
- **Non-responsibilities:** Store secrets/full sensitive payloads by default, substitute for operational logs, retroactively invent evidence.
- **Public interface:** `append`, `query`, `exportEvidence`, `verifyIntegrity`.
- **Dependencies/data:** All consequential modules, identity, clock and protected store; structured metadata plus protected references/hashes.
- **Security/permissions:** Append-only semantics, integrity protection, restricted queries, redaction, retention/legal hold and tenant isolation.
- **Events:** Emits audit write failed/integrity warning where safe; consumes consequential attempt/outcome events.
- **MVP / later:** Structured local record for full first slice; later tamper evidence, regulated exports, tiered retention and anomaly detection.

### Evaluation System

- **Purpose:** Measure agent quality, safety, policy compliance and operational fitness before and during release.
- **Responsibilities:** Version datasets/rubrics, run deterministic and model-assisted checks, compare models/agents, gate promotion, monitor regressions and collect authorised feedback.
- **Non-responsibilities:** Declare subjective truth without governance, automatically use customer or vertical data for training, fine-tuning, external-provider training, or cross-product learning datasets, replace tests or monitoring.
- **Public interface:** `runSuite`, `compare`, `recordFeedback`, `qualificationStatus`.
- **Dependencies/data:** Registry, router, tool mocks, audit samples and product-owned evaluation sets; de-identified/minimised cases where possible.
- **Security/permissions:** Dataset access controls, contamination tracking, reproducibility, reviewer provenance and protected red-team cases.
- **Events:** Emits evaluation started/completed/regression/qualified; consumes definition/model/tool changes and feedback.
- **MVP / later:** Small fixed suite for first agent, permissions and tool behavior; later continuous, adversarial and outcome-linked evaluation.

### Observability

- **Purpose:** Reveal health, performance, cost and behavior without leaking protected content.
- **Responsibilities:** Correlated metrics, logs and traces; service-level indicators; model/tool latency and cost; alerts and dashboards.
- **Non-responsibilities:** Serve as audit authority, collect prompts/content by default, make business decisions.
- **Public interface:** telemetry emitters, trace propagation, metrics query and alert hooks.
- **Dependencies/data:** Every runtime module and telemetry adapters; redacted operational metadata.
- **Security/permissions:** Access controls, sampling, retention, redaction and data-residency policy.
- **Events:** Emits operational alerts; consumes execution lifecycle and health signals.
- **MVP / later:** Structured logs, trace/correlation IDs, latency/error/cost metrics; later distributed traces, SLOs and anomaly detection.

### Identity and Authentication

- **Purpose:** Establish verifiable Human Principals and Service Principals, and bind distinct Agent Execution Identities to them, without implying authority.
- **Responsibilities:** Authenticate human and service principals; issue/validate sessions or credentials; create or validate agent execution bindings containing the specific instance and definition version; represent tenant/product membership and accountability; and support revocation.
- **Non-responsibilities:** Make resource-level permission decisions, own vertical profiles, or merge identities across products without governance.
- **Public interface:** `authenticate`, `validateCredential`, `resolvePrincipal`, `revoke`, and lifecycle hooks behind provider-neutral contracts.
- **Dependencies/data:** Identity-provider adapters, protected credential/session stores and audit; identifiers and necessary authentication attributes only.
- **Security/permissions:** Never conflate human, service, and agent execution identities. An agent execution receives authority only through explicit delegation and policy from an authenticated Human Principal or Service Principal. Apply strong credential protection, phishing/replay resistance appropriate to risk, machine credential rotation, session limits and recovery controls.
- **Events:** Emits identity/session created, authenticated, failed, revoked and membership changed; consumes provider and account lifecycle events.
- **MVP / later:** Test human/service identities with deterministic authentication; later federated identity, stronger factors and governed cross-product account linking.

### Knowledge Layer

- **Purpose:** Provide curated, provenance-aware generic and product-owned knowledge access.
- **Responsibilities:** Ingest through owner-approved pipelines, index, retrieve, version, cite, correct and expire knowledge while preserving source and classification.
- **Non-responsibilities:** Treat generated claims as facts, absorb private vertical data automatically, replace source systems or define vertical doctrine/business rules in Core.
- **Public interface:** `ingestReference`, `search`, `getSource`, `correct`, `invalidate`; vertical knowledge is reached through owning adapters.
- **Dependencies/data:** Data access, context, permissions, memory and indexing/storage adapters; governed documents, structured facts or references.
- **Security/permissions:** Source allowlists, provenance, product/tenant isolation, licence and retention controls, prompt-injection labelling and access-time authorisation.
- **Events:** Emits source ingested/updated/invalidated and index completed/failed; consumes owner, permission and source lifecycle events.
- **MVP / later:** Static trusted test knowledge if needed; later hybrid structured/search retrieval, temporal facts and vertical-owned knowledge graphs.

### Safety and Policy Layer

- **Purpose:** Apply cross-cutting operational safety constraints in addition to permissions and domain policy.
- **Responsibilities:** Classify request/action risk, enforce content/action constraints, limits and escalation, expose policy reasons, and support policy testing/versioning.
- **Non-responsibilities:** Replace legal review, vertical regulation, human judgment or resource authorisation.
- **Public interface:** `assessInput`, `assessPlan`, `assessOutput`, `getConstraints`, `explain`.
- **Dependencies/data:** Permissions, vertical policy adapters, evaluations, runtime and audit; minimised request/action features and policy metadata.
- **Security/permissions:** Fail safely according to action risk, control policy changes, resist policy injection and restrict sensitive policy/test artifacts.
- **Events:** Emits policy assessed/blocked/escalated and policy changed; consumes risk, incident and evaluation signals.
- **MVP / later:** Explicit allow/deny and operational limits for the test slice; later adaptive risk signals, red teaming and jurisdiction-aware policy packs.

### Billing and Usage

- **Purpose:** Attribute resource consumption and enforce authorised budgets without coupling to a payment provider.
- **Responsibilities:** Meter model/tool/runtime usage, attribute it to tenant/product/principal, enforce quotas and budgets, and expose reconciliable records.
- **Non-responsibilities:** Set vertical pricing, move money in MVP, or treat estimates as financial ledgers.
- **Public interface:** `checkBudget`, `recordUsage`, `getUsage`, `reserve`, `reconcile`.
- **Dependencies/data:** Gateway, runtime, model router, tools, identity and provider billing adapters; usage dimensions, rates/estimates and ownership metadata.
- **Security/permissions:** Prevent tenant leakage and meter tampering; restrict cost visibility; never expose payment secrets to agents.
- **Events:** Emits usage recorded, threshold reached, budget denied and reconciliation variance; consumes execution/provider usage outcomes.
- **MVP / later:** Capture model/tool usage and enforce a test budget; later quotas, cost allocation, invoicing adapters and product-specific commercial models.

### API Gateway

- **Purpose:** Govern external human and machine access to ecosystem APIs.
- **Responsibilities:** Authentication handoff, routing, versioning, validation, rate/usage limits, idempotency forwarding, policy enforcement, response shaping and trace creation.
- **Non-responsibilities:** Own domain rules, store domain data, turn authentication into authorisation.
- **Public interface:** Versioned HTTP/event-facing contracts; protocol choice remains reversible.
- **Dependencies/data:** Identity, permissions, product APIs, billing/usage, audit and observability; request metadata and transient payloads.
- **Security/permissions:** TLS, abuse controls, schema/size limits, machine scopes, tenant routing and safe errors.
- **Events:** Emits request accepted/rejected/completed and limit exceeded; consumes route, policy and credential lifecycle changes.
- **MVP / later:** One authenticated internal/test endpoint; later developer portal, external credentials, quotas and compatibility governance.

### Vertical Adapters and Data Access Layer

- **Purpose:** Translate generic Core contracts into product-owned capabilities and authorised data access.
- **Responsibilities:** Implement typed repositories/service clients, map domain schemas, enforce product policy, preserve provenance and isolate providers/products.
- **Non-responsibilities:** Move domain logic into Core, bypass product APIs, create a universal cross-product database.
- **Public interface:** Versioned capability, repository and event contracts owned jointly through explicit service agreements.
- **Dependencies/data:** Product services/stores, permission engine, audit and contract schemas; only data authorised by the owning vertical.
- **Security/permissions:** Per-product service identities, least privilege, tenant/purpose checks, output minimisation and contract tests.
- **Events:** Emits adapter call outcome and product-defined events; consumes contract lifecycle and authorised domain events.
- **MVP / later:** In-process adapter for the first chosen vertical; later remote adapters, anti-corruption layers and spin-out-ready contracts.

### Agent-to-Agent Communication

- **Purpose:** Allow governed delegation and coordination between independently owned agents.
- **Responsibilities:** Capability discovery, authenticated typed messages, delegation chains, budgets/deadlines, correlation, status and cancellation.
- **Non-responsibilities:** Implicit trust, authority amplification, unrestricted peer memory access, hidden recursive delegation.
- **Public interface:** `discoverCapability`, `requestTask`, `getTask`, `cancelTask`; asynchronous responses may use events.
- **Dependencies/data:** Registry, gateway, permissions, events, audit and identity; task envelope and authorised references only.
- **Security/permissions:** Verify every hop; attenuate delegated scopes; bound depth/cost/time; prevent confused-deputy behavior.
- **Events:** Emits task requested/accepted/completed/failed/cancelled; consumes capability and authority changes.
- **MVP / later:** Not in first implementation milestone; later one bounded internal delegation, then cross-product/external federation.

## Failure, retry, and idempotency policy

Failures are typed as validation, authentication, permission, approval-required, policy, dependency, timeout, rate/budget, conflict, unavailable, and internal. User-facing errors are safe and actionable; diagnostic detail remains protected and correlated.

Retry only transient failures, with bounded attempts, exponential backoff and jitter, deadlines, and circuit breaking where useful. Never blindly retry model-generated plans, permission denials, validation failures, or non-idempotent side effects. Respect provider retry guidance. After uncertainty, reconcile observed state before another attempt.

Every consequential request carries a stable idempotency key scoped to principal, operation and target. Store the request fingerprint and durable outcome; identical repeats return the prior outcome, while key reuse with different input fails. Consumers deduplicate events by event ID and make handlers idempotent. “Exactly once” is a business effect achieved through these controls, not assumed transport behavior.

## Correlation and security boundaries

Create a correlation ID at ingress and a trace ID/span chain across synchronous and asynchronous work; preserve causation IDs for events. Do not encode sensitive information in identifiers. Audit, logs, tool calls and outcomes must be joinable through these identifiers.

Trust boundaries exist at every user/device, model provider, tool, product, tenant, data store, event subscriber, adapter and external company. Authenticate, authorise and validate on each crossing. Vertical stores remain under vertical ownership; shared Core stores contain only generic platform data and explicitly governed references.

## Service-contract requirements

Every service contract states owner and consumers; version and compatibility policy; request/response or event schemas; authentication and permissions; declared purpose and data classification; consent and retention; idempotency; timeout/retry/rate limits; error model; audit obligations; SLO expectations; deprecation process; and test fixtures. Cross-product requests carry an explicit declared purpose where relevant, and the receiving service evaluates whether both permission and purpose are authorised. Cross-product contracts require approval from both owning boundaries. Contract evolution should favour additive changes and consumer-driven verification.

Customer or vertical data is not automatically available for model training, fine-tuning, external-provider training, or cross-product learning datasets. Those uses require explicit governance, lawful basis, declared purpose, approval, and appropriate consent or contractual authority. Operational processing needed to execute an authorised request is a separate purpose and does not imply permission for training.
