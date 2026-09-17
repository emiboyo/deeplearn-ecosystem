# Milestone 1.6 Permission Checks

Status: M1.6 synthetic, deny-by-default permission boundary. The root architecture documents remain authoritative.

## Purpose and separation

The Permission Engine evaluates whether an authenticated originating principal has bounded authority to request `test.safe_echo@1.0.0`. It returns an immutable, machine-readable decision before execution.

M1.6 evaluates permissions only. It does not invoke tools. Runtime orchestration, approval handling, audit persistence, authentication providers, and integration between the evaluator and `ToolDispatcher` remain deferred.

## Synthetic policy

The immutable policy is `test.safe_echo.invoke@1.0.0`. It matches only:

- tool `test.safe_echo@1.0.0`;
- action `test.safe_tool.invoke`;
- required scope `test.safe_tool.invoke`;
- purpose `test.execute_safe_tool` by exact match;
- a non-consequential request; and
- the same tenant as the originating principal.

There are no wildcards, prefixes, fuzzy matches, admin bypasses, superusers, or implicit allows. If no exact tool/version policy exists, the request is denied.

## Principals, tenant, and product boundaries

Human Principals and Service Principals remain distinct controlled types. An optional Agent Execution Identity is attributable context only and contributes no scope or independent authority. An unauthenticated originating principal is denied. An originating principal is bound to both its tenant and product boundary in M1.6: the request tenant and product must exactly equal the corresponding principal values. Cross-tenant and cross-product access are denied, and neither valid scopes nor an agent execution identity can bypass these checks.

The canonical `PrincipalContext` remains the wire authority-fact contract. The owned M1.6 types add the explicit authenticated fact required by this local evaluator and preserve principal, tenant, product, scope, and delegation data without implementing an identity provider.

## Scope and no authority amplification

An allow decision requires the request's scopes to match the policy-required scopes and those scopes to exist in effective originating authority. Additional irrelevant scopes held by a principal do not enter the decision and do not increase authority.

Without delegation, effective scopes are the principal scopes. With delegation, effective scopes are the intersection of principal scopes, delegable scopes, and delegated effective scopes, and the originating-principal reference must match. Policy existence, tool metadata, request fields, and agent identity never manufacture authority.

## Purpose, action, and consequential checks

Purpose and action use exact controlled identifiers. Missing values are malformed; unknown or non-matching values are denied. The test policy permits only `test.execute_safe_tool` and `test.safe_tool.invoke`. Because the safe tool is non-consequential, a request marked consequential is denied. M1.6 does not request or evaluate approvals.

## Decisions and failure behavior

The Python decision preserves canonical Decision naming for `decision`, `reasons`, `policy_version`, `evaluated_action`, `evaluated_purpose`, principal reference, consequential status, and correlation/trace identifiers. The exact policy ID/version and the narrow effective scopes are recorded. The canonical Decision contract has no product field, so this narrow fix evaluates the product boundary without adding a divergent decision field. Outcomes are `allow` and `deny`; policy errors are fail-closed denials.

Stable reason codes are `allowed`, `unauthenticated`, `wrong_tenant`, `wrong_product`, `missing_scope`, `purpose_not_allowed`, `action_not_allowed`, `consequential_not_allowed`, `policy_not_found`, `policy_error`, and `malformed_permission_request`. Messages are bounded and safe. Raw exceptions and internal details never enter decisions.

## Deferred work

There is no generic policy language, RBAC/ABAC framework, OPA/Rego/Cedar/Casbin integration, external policy store, authentication provider, tool execution, runtime chain, approval workflow, audit persistence, cross-product behavior, or vertical policy in M1.6.
