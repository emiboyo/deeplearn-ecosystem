# Engineering Rules

Status: Authoritative. Applies to ChatGPT, Codex, Claude, other automation, and human contributors.

## Source-of-truth hierarchy

1. Applicable law, security obligations, and explicit owner instruction.
2. Accepted architecture decisions in `DECISIONS.md` (newer accepted decisions supersede older ones explicitly).
3. `MASTER_ARCHITECTURE.md` and `DEEPLEARN_CORE_SPEC.md`.
4. `ENGINEERING_RULES.md`.
5. Product specifications, service contracts, and repository-local guidance.
6. Tests and implementation.

When sources conflict, stop, document the conflict, and seek or propose an ADR. Existing code does not silently supersede architecture.

## Mandatory working rules

- Read the architecture documents and relevant product/module documentation before meaningful changes.
- Keep work within the requested scope; preserve unrelated work and meaningful existing content.
- **No AI coding agent may silently redesign the system.** Humans may not do so silently either.
- Make assumptions, trade-offs, and deviations visible. Use an ADR for architectural changes.
- Work on a focused branch; autonomous coding agents must not write directly to `main`, merge, force-push, rewrite history, or delete branches.
- Keep commits cohesive and reviewable. Review the diff and repository status before handoff.
- Do not introduce dependencies, infrastructure, or abstractions without a demonstrated need.

## Architecture and boundaries

- Prefer a modular monolith initially. Enforce cohesion, explicit interfaces, dependency direction, and data ownership inside it.
- Core owns generic intelligence capabilities; verticals own domain business rules.
- Treat each vertical as an autonomous product boundary with its own domain contracts, domain data ownership, migrations, and operational accountability, and its own release lifecycle where practical. Keep boundaries independently replaceable and deployable over time without requiring microservices now.
- A product or module accesses another boundary only through a versioned API, event, repository interface, or service contract.
- No vertical directly reads or writes another vertical's private data store.
- Agents use registered, typed, least-privilege tools; they do not execute arbitrary code or access arbitrary databases.
- Human and machine consumers use the same governed API concepts. Machine delegation must be scoped, attributable, expiring, and revocable.
- Make APIs backward-compatible where practical. Specify authentication, permissions, idempotency, errors, and versioning.

## Provider abstraction

- Put model, storage, messaging, identity, payment, and other provider-specific behavior behind owned interfaces when substitution is strategically relevant.
- Keep provider identifiers and capabilities observable without leaking provider types throughout domain code.
- Do not reduce all providers to a false lowest common denominator; expose optional capabilities through explicit capability discovery.
- Business rules, permissions, prompts, and audit semantics must not depend on one provider unless recorded in an ADR.

## Permissions, safety, and audit

- Authenticate every external principal and authorise at the point of consequential use.
- Default to least privilege and deny when required authority cannot be established.
- Evaluate tenant, product, purpose, resource, action, consent, delegated authority, risk, and relevant limits.
- Cross-product access must be permission-bound and purpose-bound. Carry an explicit declared purpose where relevant, and require the receiving boundary to authorise that purpose; permission alone is insufficient.
- An agent may never grant itself, another agent, or another service more authority than the originating principal possesses and is permitted to delegate. Authority may only narrow or remain equivalent through agent delegation, tool invocation, workflows, cross-product requests, and service calls unless a separate independently authorised principal grants additional authority.
- Require approval for consequential actions unless matching delegated authority exists. Approval requests bind the exact proposed action and expire.
- Record consequential attempts and outcomes with initiator, subject, service identity, agent, model/provider/version when available, tools, appropriate data-access metadata, permission result, approval state, result, timestamp, trace/correlation ID, and failure details.
- Never put secrets or unnecessary sensitive content in prompts, events, telemetry, error messages, or audit payloads.

## Secrets and security

- Never hard-code or commit API keys, passwords, private tokens, payment secrets, or credentials.
- Use environment variables for local development and an approved secrets manager elsewhere; commit only safe examples.
- Validate untrusted input and output at boundaries. Apply rate, cost, size, and timeout limits.
- Treat model output, retrieved content, tool output, events, and agent-to-agent messages as untrusted.
- Use secure defaults, dependency review, encryption appropriate to the data, and least-privilege service identities.
- Report suspected credential exposure or security issues; do not conceal or merely work around them.

## Testing and evaluation

Every meaningful feature includes proportionate unit, integration, permission, isolation, and failure-path tests. Contract changes include consumer/provider contract tests. Consequential operations test approval, idempotency, denial, timeout, partial failure, and audit behavior. Agent features add reproducible evaluation cases before increased autonomy. Tests must not call paid or mutable external systems by default.

## Data and migrations

- A data owner defines schemas, classification, retention, deletion, provenance, tenant boundaries, and allowed purposes.
- Migrations are versioned, reviewed, tested against representative data, observable, and backward-compatible during rollout where feasible.
- Separate schema deployment from irreversible cleanup. Provide a rollback or roll-forward plan and verified backup for destructive migrations.
- Never silently repurpose a field, weaken isolation, or copy private data across products.
- Do not automatically use customer or vertical data for model training, fine-tuning, external-provider training, or cross-product learning datasets. Such use requires explicit governance, lawful basis, declared purpose, approval, and appropriate consent or contractual authority. Treat authorised operational processing as distinct from training, and configure provider settings and contracts to prevent training on customer data wherever product policy or law requires it.

## Documentation and ADRs

Update relevant architecture, contracts, runbooks, and examples in the same change as behavior. Public interfaces document ownership, schemas, errors, permissions, idempotency, compatibility, and emitted events. Create an ADR proposal before changing a non-negotiable principle, ownership boundary, persistence model, provider strategy, trust boundary, or deployment topology. An ADR includes ID, title, status, context, decision, and consequences; only an authorised reviewer accepts it.

## Destructive changes

Do not delete data, APIs, branches, history, or meaningful content without explicit scope and review. Inventory consumers, provide migration and recovery plans, back up material data, prefer deprecation, and verify the exact target immediately before action. Autonomous agents must not execute irreversible production actions without explicit authorisation.

## Definition of done

A change is done when scope and acceptance criteria are met; boundaries and source-of-truth documents remain consistent; permissions, privacy, failure modes, and audit are addressed; tests and evaluations pass; migrations and compatibility are safe; secrets are absent; operational telemetry and documentation are sufficient; the diff is reviewed; and remaining risks or decisions are reported. Deployment or merge is separate unless explicitly authorised.
