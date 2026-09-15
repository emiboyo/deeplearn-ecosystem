# DeepLearn Ecosystem — Master Architecture

Status: Authoritative foundation

Strategic principle: **One intelligence infrastructure. Many specialised businesses.**

North star: **Build for the world that is arriving, while creating value in the world that exists today.**

## Vision and mission

DeepLearn enables people and authorised machines to express outcomes, have intelligent agents plan and coordinate work, invoke controlled digital or physical capabilities, and learn safely from results. The ecosystem shares generic intelligence infrastructure while each business retains its own domain logic, private data, risk controls, customer relationships, and operational accountability.

The architecture must deliver useful products without requiring AGI. It should serve today's human customers through understandable workflows while progressively making the same governed capabilities available to machine customers.

## Ecosystem model

```text
Human or authorised machine intent
                 |
                 v
     Product experience / product API
                 |
                 v
  Domain agents + domain business rules
                 |
        governed Core contracts
                 v
 Identity | Permissions | Agent Runtime | Models | Context | Memory
 Tools | Workflows | Events | Approvals | Audit | Evals | Observability
                 |
                 v
 Controlled digital services and physical execution networks
                 |
                 v
        Outcomes, evidence, and feedback
```

DeepLearn Core is a shared capability layer, not a shared private-data pool.

## Product roles and boundaries

| Product | Role | Owns | Boundary highlights |
| --- | --- | --- | --- |
| DeepLearn Core | Shared intelligence and agent infrastructure | Generic agent execution, identity, permissions, models, tools, workflows, events, approvals, audit, evaluations and platform concerns | Does not own vertical business meaning or silently pool vertical data |
| ATLAS | Personal financial intelligence | Financial position, budgeting, cashflow, goals, research, decision support and appropriately authorised administration | Elevated consent, approval, audit and regulatory controls |
| PBcoms | Autonomous commerce and business operating system | Merchant, marketing, sales, procurement, pricing, inventory, support, finance and fulfilment domain logic | Requests logistics through PearlBridge contracts, never its database |
| PearlBridge Network | Intelligent logistics and physical execution network | Quotes, capability, bookings, routing, capacity, fleet, driver operations, status and compliance | May remain separately deployed and independently operated |
| ScriptureOS | Christian intelligence and structured biblical knowledge | Scripture, languages, chronology, people, places, events, doctrine, themes, context and teaching resources | Usage is not automatically available for commercial profiling |
| Circle | Relationship intelligence for intentional, long-term outcomes | Compatibility, goals, discovery, conversations, safety and relationship development | Sensitive personal data is isolated and explicitly permissioned |

Verticals own domain policy and business operations. Core owns reusable mechanisms. For example, Core defines how an authorised tool is invoked; PearlBridge defines what a delivery is and whether it may be created.

Each vertical is an autonomous product boundary. It owns its domain contracts, domain data, migrations, and operational accountability, and should have its own release lifecycle where practical. Interfaces and dependency direction must allow each vertical to become independently replaceable or deployable over time without major architectural untangling. This strengthens the modular monolith; it does not require microservices now.

## Shared-core philosophy

Core capabilities are consumed through explicit, versioned interfaces. Provider-specific implementations sit behind adapters. The initial deployment preference is a modular monolith with strong module boundaries, because operational simplicity and fast learning matter more than premature distribution. Boundaries must permit later extraction without pretending every module is already a service.

Shared identity may identify the same principal across products, but authentication does not imply cross-product authorisation. Tenant, product, purpose, resource, action, consent, delegated authority, and risk must be evaluated at the point of use.

## Privacy and data isolation

- Each vertical maintains logically isolated domain data and applies tenant isolation within it.
- No product directly queries or writes another product's private database.
- Cross-product exchange uses authorised APIs, versioned service contracts, or events with least-privilege scopes and purpose limitation. Access must be both permission-bound and purpose-bound: permission alone is insufficient, and the receiving boundary evaluates the declared purpose where relevant.
- User consent is required where appropriate and can be revoked; derived data remains governed by its provenance and purpose.
- Agents receive scoped tools and contextual data, never unrestricted database access.
- Sensitive data should be minimised, classified, retained deliberately, encrypted appropriately, and excluded from logs by default.
- Customer or vertical data is not automatically used for model training, fine-tuning, external-provider training, or cross-product learning datasets. Training use requires explicit governance, lawful basis, declared purpose, approval, and appropriate consent or contractual authority. Operational use to execute an authorised request is distinct from training use, and provider settings and contracts must prevent training on customer data wherever product policy or law requires it.

Correct: `PBcoms Fulfilment Agent -> permission check + purpose: fulfil_customer_order -> PearlBridge Delivery API`.

Incorrect: `PBcoms -> PearlBridge private database`.

Also incorrect: `PBcoms -> reuse PearlBridge customer data for unrelated analytics` without explicit lawful purpose and permission.

## Capability discovery

A **Capability Manifest** is a future-facing, versioned, machine-readable description of capabilities offered by a product, agent, or service. It may describe capability name and version, input/output schemas, required permissions and purpose, risk and side-effect classifications, possible approval requirements, idempotency behavior, and availability or deprecation state. A manifest advertises what can be requested; it never grants authority. Execution still requires authentication, permission and purpose checks, policy evaluation, and approval where applicable. No registry implementation is required at this stage.

## Humans, machines, and agent-to-agent operation

Human users and authorised machine agents will become first-class API consumers. Machine identity must be attributable to an accountable principal, with bounded scopes, budgets, expiry, and revocation. Agent-to-agent messages are treated as untrusted requests: authenticate the caller, authorise the action, validate the schema, propagate correlation IDs, and record consequential outcomes. An agent may delegate only authority it possesses and is permitted to delegate.

## Progressive autonomy

| Level | Behaviour | Default control |
| --- | --- | --- |
| 1 — Assist | Explain, retrieve, or draft | Human initiates and uses output |
| 2 — Recommend | Propose ranked actions with rationale | Human decides |
| 3 — Prepare | Assemble a reversible action for review | Explicit approval before execution |
| 4 — Execute | Act within delegated authority | Policy, limits, monitoring, audit, and revocation |

Autonomy is granted per action and context, not as a blanket property of an agent. Risk, reversibility, financial impact, sensitivity, confidence, and regulation determine the required level. High-risk or consequential actions require human approval unless explicit delegated authority covers that exact action.

Provisionally, a **consequential action** is one that may create a meaningful financial, legal or regulatory, physical-world, privacy or data-sharing, or safety effect; an irreversible or difficult-to-reverse effect; an account, identity, or permission change; or an externally visible commitment or transaction. Product-specific policy may refine this definition, but implementations must not invent incompatible meanings independently.

## Outcome and data flywheels

Useful operation creates evidence: intent, authorised context, decisions, tool results, outcomes, corrections, and feedback. With privacy and purpose controls, this evidence improves evaluations, domain knowledge, workflows, routing, and customer outcomes. Cross-product aggregation is never presumed; use requires a lawful basis, clear permission, minimisation, and a documented contract. Quantity of data alone is not the goal—trusted, representative, outcome-linked data is.

## Defensibility

Code is not the primary moat. Durable advantage should emerge from combinations of proprietary and permissioned data, domain intelligence, evaluation quality, network effects, integrations, trust, safety, regulatory capability, transaction history, customer relationships, community, distribution, and—where relevant—physical infrastructure. Each vertical should build a defensible combination appropriate to its market while benefiting from Core economics.

## Non-goals and explicit exclusions

We will not build one giant super-app; collapse private vertical stores into a shared database; allow agents arbitrary code or database access; couple the ecosystem to one model, cloud, or tool provider; assume all workflows should be autonomous; begin with a microservice estate; or make speculative infrastructure investments before validated demand. We will not treat ScriptureOS behaviour as automatic advertising data, expose Circle data to ATLAS, or expose ATLAS data to Circle. Architecture agents may not silently override these decisions.

## Future group and deployment structure

The ecosystem may evolve into a group in which DeepLearn Core is a platform capability and verticals are separately governed products or companies. Product identity, data ownership, contracts, deployment boundaries, economics, regulatory responsibility, and intellectual property must therefore remain separable. PearlBridge Network may remain an external operational company integrated through APIs and events. The architecture enables spin-outs but does not decide legal structure, ownership, or timing.

## Direction toward 2030 and 2035

By 2030, the aim is a validated shared runtime supporting several valuable vertical workflows, reliable approvals and audit, portable model/tool integrations, measurable evaluations, and selected machine-readable product APIs. By 2035, authorised agent networks may coordinate multi-product digital and physical outcomes with increasing autonomy, while humans retain meaningful control and each business retains its privacy and accountability boundaries.

These are directions, not delivery commitments. Every phase must produce present-day customer value, evidence, and learning. Future readiness comes from durable contracts and governance—not from building speculative scale early.
