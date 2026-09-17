"""Offline M1.6 tests for explicit fail-closed permission evaluation."""

from dataclasses import FrozenInstanceError, asdict
from pathlib import Path

import pytest

from deeplearn.core.permissions import (
    DecisionOutcome,
    DelegatedAuthority,
    DenyByDefaultPermissionEvaluator,
    InMemoryPolicyRegistry,
    PermissionRequest,
    PermissionRequestValidationError,
    PrincipalContext,
    PrincipalType,
    ReasonCode,
    safe_echo_policy,
)


ROOT = Path(__file__).parents[2]


def principal(
    *,
    authenticated: bool = True,
    tenant_id: str = "tenant.test.alpha",
    scopes: tuple[str, ...] = ("test.safe_tool.invoke",),
    delegated_authority: DelegatedAuthority | None = None,
    principal_type: PrincipalType = PrincipalType.HUMAN,
) -> PrincipalContext:
    return PrincipalContext(
        authenticated=authenticated,
        principal_type=principal_type,
        principal_id="human.test_user" if principal_type is PrincipalType.HUMAN else "service.test_client",
        tenant_id=tenant_id,
        product_id="deeplearn.test",
        scopes=scopes,
        delegated_authority=delegated_authority,
    )


def request(**changes) -> PermissionRequest:
    values = {
        "decision_id": "decision_test_0001",
        "principal": principal(),
        "tenant_id": "tenant.test.alpha",
        "product_id": "deeplearn.test",
        "requested_action": "test.safe_tool.invoke",
        "requested_scopes": ("test.safe_tool.invoke",),
        "purpose": "test.execute_safe_tool",
        "tool_id": "test.safe_echo",
        "tool_version": "1.0.0",
        "consequential": False,
        "correlation_id": "corr_test_0001",
        "trace_id": "trace_policy_0001",
        "agent_execution_id": None,
    }
    values.update(changes)
    return PermissionRequest(**values)


def evaluator(*, with_policy: bool = True, policy_error: bool = False):
    registry = InMemoryPolicyRegistry()
    if with_policy:
        registry.register(safe_echo_policy(synthetic_error=policy_error))
    return DenyByDefaultPermissionEvaluator(registry)


def assert_reason(decision, reason: ReasonCode) -> None:
    assert decision.outcome is DecisionOutcome.DENY
    assert decision.reason.code is reason


def test_explicit_allowed_request_records_policy_and_context() -> None:
    decision = evaluator().evaluate(request())
    assert decision.outcome is DecisionOutcome.ALLOW
    assert decision.reason.code is ReasonCode.ALLOWED
    assert decision.policy_id == "test.safe_echo.invoke"
    assert decision.policy_version == "1.0.0"
    assert decision.evaluated_scopes == ("test.safe_tool.invoke",)
    assert decision.correlation_id == "corr_test_0001"
    assert decision.trace_id == "trace_policy_0001"


def test_service_principal_remains_a_distinct_supported_origin() -> None:
    decision = evaluator().evaluate(
        request(principal=principal(principal_type=PrincipalType.SERVICE))
    )
    assert decision.outcome is DecisionOutcome.ALLOW
    assert decision.principal_type is PrincipalType.SERVICE
    assert decision.principal_reference == "principal/service.test_client"


def test_deny_by_default_when_no_policy_exists() -> None:
    assert_reason(
        evaluator(with_policy=False).evaluate(request()),
        ReasonCode.POLICY_NOT_FOUND,
    )


def test_unauthenticated_principal_is_denied() -> None:
    assert_reason(
        evaluator().evaluate(request(principal=principal(authenticated=False))),
        ReasonCode.UNAUTHENTICATED,
    )


def test_wrong_tenant_is_denied() -> None:
    assert_reason(
        evaluator().evaluate(request(tenant_id="tenant.test.beta")),
        ReasonCode.WRONG_TENANT,
    )


def test_matching_product_is_allowed_when_all_other_facts_are_valid() -> None:
    decision = evaluator().evaluate(request(product_id="deeplearn.test"))
    assert decision.outcome is DecisionOutcome.ALLOW
    assert decision.reason.code is ReasonCode.ALLOWED


def test_wrong_product_is_denied_with_stable_reason() -> None:
    assert_reason(
        evaluator().evaluate(request(product_id="other.product")),
        ReasonCode.WRONG_PRODUCT,
    )


def test_matching_tenant_does_not_compensate_for_wrong_product() -> None:
    permission_request = request(
        tenant_id="tenant.test.alpha",
        product_id="other.product",
    )
    assert permission_request.tenant_id == permission_request.principal.tenant_id
    assert_reason(
        evaluator().evaluate(permission_request),
        ReasonCode.WRONG_PRODUCT,
    )


def test_valid_authority_facts_do_not_compensate_for_wrong_product() -> None:
    permission_request = request(product_id="other.product")
    assert permission_request.requested_scopes == ("test.safe_tool.invoke",)
    assert permission_request.purpose == "test.execute_safe_tool"
    assert permission_request.requested_action == "test.safe_tool.invoke"
    assert_reason(
        evaluator().evaluate(permission_request),
        ReasonCode.WRONG_PRODUCT,
    )


def test_agent_execution_identity_cannot_bypass_product_boundary() -> None:
    assert_reason(
        evaluator().evaluate(
            request(
                product_id="other.product",
                agent_execution_id="agentexec_test_0001",
            )
        ),
        ReasonCode.WRONG_PRODUCT,
    )


def test_service_principal_is_also_product_bound() -> None:
    assert_reason(
        evaluator().evaluate(
            request(
                principal=principal(principal_type=PrincipalType.SERVICE),
                product_id="other.product",
            )
        ),
        ReasonCode.WRONG_PRODUCT,
    )


@pytest.mark.parametrize("scopes", [(), ("test.wrong_scope",)])
def test_missing_or_wrong_principal_scope_is_denied(scopes) -> None:
    assert_reason(
        evaluator().evaluate(request(principal=principal(scopes=scopes))),
        ReasonCode.MISSING_SCOPE,
    )


def test_correct_scope_is_accepted_with_irrelevant_principal_scope() -> None:
    result = evaluator().evaluate(
        request(
            principal=principal(
                scopes=("test.safe_tool.invoke", "test.irrelevant_scope")
            )
        )
    )
    assert result.outcome is DecisionOutcome.ALLOW
    assert result.evaluated_scopes == ("test.safe_tool.invoke",)


def test_wrong_purpose_is_denied_by_exact_match() -> None:
    assert_reason(
        evaluator().evaluate(request(purpose="test.execute_safe_tool.extra")),
        ReasonCode.PURPOSE_NOT_ALLOWED,
    )


def test_missing_purpose_is_safely_denied_as_malformed() -> None:
    document = asdict(request())
    document.pop("purpose")
    assert_reason(
        evaluator().evaluate(document),
        ReasonCode.MALFORMED_PERMISSION_REQUEST,
    )


def test_unknown_action_is_denied() -> None:
    assert_reason(
        evaluator().evaluate(request(requested_action="test.unknown_action")),
        ReasonCode.ACTION_NOT_ALLOWED,
    )


def test_consequential_request_is_denied_without_approval_flow() -> None:
    assert_reason(
        evaluator().evaluate(request(consequential=True)),
        ReasonCode.CONSEQUENTIAL_NOT_ALLOWED,
    )


def test_malformed_request_and_context_are_normalized() -> None:
    decision = evaluator().evaluate({"decision_id": "decision_test_0001"})
    assert_reason(decision, ReasonCode.MALFORMED_PERMISSION_REQUEST)
    with pytest.raises(PermissionRequestValidationError):
        principal(principal_type="agent")


def test_duplicate_scope_identifiers_are_rejected() -> None:
    with pytest.raises(PermissionRequestValidationError, match="duplicates"):
        request(requested_scopes=("test.safe_tool.invoke", "test.safe_tool.invoke"))


def test_policy_error_fails_closed_without_raw_exception_detail() -> None:
    decision = evaluator(policy_error=True).evaluate(request())
    assert_reason(decision, ReasonCode.POLICY_ERROR)
    assert "synthetic" not in decision.reason.message
    assert "PolicyEvaluationError" not in decision.reason.message


def test_requested_scope_outside_policy_is_not_amplified() -> None:
    decision = evaluator().evaluate(
        request(requested_scopes=("test.safe_tool.invoke", "test.other_scope"))
    )
    assert_reason(decision, ReasonCode.MISSING_SCOPE)


def test_delegation_intersection_cannot_amplify_originating_authority() -> None:
    delegation = DelegatedAuthority(
        originating_principal_reference="principal/human.test_user",
        delegable_scopes=("test.other_scope",),
        effective_scopes=("test.safe_tool.invoke", "test.other_scope"),
    )
    decision = evaluator().evaluate(
        request(principal=principal(delegated_authority=delegation))
    )
    assert_reason(decision, ReasonCode.MISSING_SCOPE)


def test_mismatched_delegation_origin_is_denied() -> None:
    delegation = DelegatedAuthority(
        originating_principal_reference="principal/service.someone_else",
        delegable_scopes=("test.safe_tool.invoke",),
        effective_scopes=("test.safe_tool.invoke",),
    )
    assert_reason(
        evaluator().evaluate(
            request(principal=principal(delegated_authority=delegation))
        ),
        ReasonCode.MISSING_SCOPE,
    )


def test_agent_execution_identity_has_no_independent_authority() -> None:
    decision = evaluator().evaluate(
        request(
            principal=principal(scopes=()),
            agent_execution_id="agentexec_test_0001",
        )
    )
    assert_reason(decision, ReasonCode.MISSING_SCOPE)


def test_request_policy_and_decision_are_immutable() -> None:
    permission_request = request()
    policy = safe_echo_policy()
    registry = InMemoryPolicyRegistry()
    registry.register(policy)
    decision = DenyByDefaultPermissionEvaluator(registry).evaluate(permission_request)
    with pytest.raises(FrozenInstanceError):
        permission_request.purpose = "changed"
    with pytest.raises(FrozenInstanceError):
        policy.version = "9.9.9"
    with pytest.raises(FrozenInstanceError):
        decision.decision = DecisionOutcome.DENY
    assert registry.resolve("test.safe_echo", "1.0.0") is policy


def test_permission_module_does_not_import_execution_boundaries() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(
            (ROOT / "src" / "deeplearn" / "core" / "permissions").glob("*.py")
        )
    )
    for boundary in ("tools", "runtime", "models", "registry", "audit"):
        assert f"deeplearn.core.{boundary}" not in source
