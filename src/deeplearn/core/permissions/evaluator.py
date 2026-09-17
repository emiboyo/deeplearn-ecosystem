"""Deterministic deny-by-default M1.6 permission evaluator."""

from collections.abc import Mapping

from .contracts import (
    DecisionOutcome,
    DecisionReason,
    PermissionDecision,
    PermissionRequest,
    PrincipalType,
    ReasonCode,
)
from .errors import PermissionRequestValidationError
from .policies import InMemoryPolicyRegistry, ToolPermissionPolicy


SAFE_REASONS = {
    ReasonCode.ALLOWED: "The explicit synthetic policy allows this request.",
    ReasonCode.UNAUTHENTICATED: "An authenticated originating principal is required.",
    ReasonCode.WRONG_TENANT: "The request crosses the principal tenant boundary.",
    ReasonCode.MISSING_SCOPE: "The originating authority does not cover the required scope.",
    ReasonCode.PURPOSE_NOT_ALLOWED: "The requested purpose is not allowed.",
    ReasonCode.ACTION_NOT_ALLOWED: "The requested action is not allowed.",
    ReasonCode.CONSEQUENTIAL_NOT_ALLOWED: "Consequential execution is not allowed by this policy.",
    ReasonCode.POLICY_NOT_FOUND: "No explicit policy allows the requested tool version.",
    ReasonCode.POLICY_ERROR: "Permission evaluation failed closed.",
    ReasonCode.MALFORMED_PERMISSION_REQUEST: "The permission request is malformed.",
}


class DenyByDefaultPermissionEvaluator:
    """Evaluate one request without invoking a tool or any other capability."""

    def __init__(self, policies: InMemoryPolicyRegistry) -> None:
        self._policies = policies

    def evaluate(
        self, request: PermissionRequest | Mapping[str, object]
    ) -> PermissionDecision:
        try:
            validated = (
                request
                if isinstance(request, PermissionRequest)
                else PermissionRequest.from_mapping(request)
            )
        except (PermissionRequestValidationError, TypeError, KeyError):
            return self._malformed_decision(request)

        principal = validated.principal
        if not principal.authenticated:
            return self._deny(validated, None, ReasonCode.UNAUTHENTICATED)
        if validated.tenant_id != principal.tenant_id:
            return self._deny(validated, None, ReasonCode.WRONG_TENANT)

        policy = self._policies.resolve(validated.tool_id, validated.tool_version)
        if policy is None:
            return self._deny(validated, None, ReasonCode.POLICY_NOT_FOUND)

        try:
            policy.ensure_evaluable()
            return self._evaluate_policy(validated, policy)
        except Exception:
            return self._deny(validated, policy, ReasonCode.POLICY_ERROR)

    def _evaluate_policy(
        self, request: PermissionRequest, policy: ToolPermissionPolicy
    ) -> PermissionDecision:
        principal = request.principal
        if policy.same_tenant and request.tenant_id != principal.tenant_id:
            return self._deny(request, policy, ReasonCode.WRONG_TENANT)
        if request.requested_action not in policy.allowed_actions:
            return self._deny(request, policy, ReasonCode.ACTION_NOT_ALLOWED)
        if request.purpose not in policy.allowed_purposes:
            return self._deny(request, policy, ReasonCode.PURPOSE_NOT_ALLOWED)
        if request.consequential and not policy.consequential_allowed:
            return self._deny(
                request, policy, ReasonCode.CONSEQUENTIAL_NOT_ALLOWED
            )

        required = frozenset(policy.required_scopes)
        requested = frozenset(request.requested_scopes)
        effective = principal.effective_scopes
        delegated = principal.delegated_authority
        origin_matches = (
            delegated is None
            or delegated.originating_principal_reference == principal.reference
        )
        if not origin_matches or requested != required or not required <= effective:
            return self._deny(request, policy, ReasonCode.MISSING_SCOPE)

        return self._decision(
            request,
            policy,
            DecisionOutcome.ALLOW,
            ReasonCode.ALLOWED,
            tuple(sorted(required)),
        )

    def _deny(
        self,
        request: PermissionRequest,
        policy: ToolPermissionPolicy | None,
        reason: ReasonCode,
    ) -> PermissionDecision:
        return self._decision(
            request,
            policy,
            DecisionOutcome.DENY,
            reason,
            (),
        )

    @staticmethod
    def _decision(
        request: PermissionRequest,
        policy: ToolPermissionPolicy | None,
        outcome: DecisionOutcome,
        reason: ReasonCode,
        scopes: tuple[str, ...],
    ) -> PermissionDecision:
        return PermissionDecision(
            decision_id=request.decision_id,
            decision=outcome,
            reasons=(DecisionReason(reason, SAFE_REASONS[reason]),),
            policy_id=policy.policy_id if policy else "none",
            policy_version=policy.version if policy else "none",
            principal_reference=request.principal.reference,
            principal_type=request.principal.principal_type,
            tenant_id=request.tenant_id,
            evaluated_action=request.requested_action,
            evaluated_purpose=request.purpose,
            evaluated_scopes=scopes,
            consequential=request.consequential,
            correlation_id=request.correlation_id,
            trace_id=request.trace_id,
        )

    @staticmethod
    def _malformed_decision(
        request: PermissionRequest | Mapping[str, object],
    ) -> PermissionDecision:
        def safe_text(field: str, fallback: str) -> str:
            value = request.get(field) if isinstance(request, Mapping) else None
            return value if isinstance(value, str) and value else fallback

        principal = request.get("principal") if isinstance(request, Mapping) else None
        principal_id = (
            principal.get("principal_id") if isinstance(principal, Mapping) else None
        )
        return PermissionDecision(
            decision_id=safe_text("decision_id", "unknown_decision"),
            decision=DecisionOutcome.DENY,
            reasons=(
                DecisionReason(
                    ReasonCode.MALFORMED_PERMISSION_REQUEST,
                    SAFE_REASONS[ReasonCode.MALFORMED_PERMISSION_REQUEST],
                ),
            ),
            policy_id="none",
            policy_version="none",
            principal_reference=(
                f"principal/{principal_id}"
                if isinstance(principal_id, str) and principal_id
                else "principal/unknown"
            ),
            principal_type=None,
            tenant_id=safe_text("tenant_id", "unknown.tenant"),
            evaluated_action=safe_text("requested_action", "unknown.action"),
            evaluated_purpose=safe_text("purpose", "unknown.purpose"),
            evaluated_scopes=(),
            consequential=False,
            correlation_id=safe_text("correlation_id", "unknown_correlation"),
            trace_id=(
                safe_text("trace_id", "")
                if isinstance(request, Mapping) and request.get("trace_id")
                else None
            ),
        )


__all__ = ["DenyByDefaultPermissionEvaluator"]
