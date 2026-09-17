"""Tests for immutable M1.5 tool metadata and exact registration."""

from dataclasses import FrozenInstanceError
import json
from pathlib import Path

import pytest

from deeplearn.core.tools import (
    DuplicateToolError,
    InMemoryToolRegistry,
    RiskClass,
    SafeEchoAdapter,
    SideEffectClass,
    ToolDefinition,
    ToolDefinitionValidationError,
    UnknownToolError,
    UnknownToolVersionError,
)


ROOT = Path(__file__).parents[2]
FIXTURE = ROOT / "fixtures" / "m1" / "tools" / "test.safe_echo-1.0.0.json"


def definition_document() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def registered() -> tuple[InMemoryToolRegistry, ToolDefinition, SafeEchoAdapter]:
    registry = InMemoryToolRegistry()
    adapter = SafeEchoAdapter()
    definition = registry.register(definition_document(), adapter)
    return registry, definition, adapter


def test_valid_tool_definition_registration_and_metadata() -> None:
    _, definition, _ = registered()
    assert (definition.tool_id, definition.version) == ("test.safe_echo", "1.0.0")
    assert definition.owner == "deeplearn.core.test"
    assert definition.risk is RiskClass.LOW
    assert definition.side_effect is SideEffectClass.NONE
    assert definition.required_scopes == ("test.safe_tool.invoke",)
    assert definition.allowed_purposes == ("test.execute_safe_tool",)
    assert definition.idempotent is True
    assert definition.consequential is False


def test_exact_version_resolution() -> None:
    registry, definition, adapter = registered()
    assert registry.resolve("test.safe_echo", "1.0.0") == (definition, adapter)


def test_duplicate_registration_is_rejected() -> None:
    registry, _, _ = registered()
    with pytest.raises(DuplicateToolError):
        registry.register(definition_document(), SafeEchoAdapter())


def test_unknown_tool_and_version_are_distinct() -> None:
    registry, _, _ = registered()
    with pytest.raises(UnknownToolError):
        registry.resolve("test.unknown", "1.0.0")
    with pytest.raises(UnknownToolVersionError):
        registry.resolve("test.safe_echo", "9.9.9")


def test_multiple_explicit_versions_can_coexist_without_latest_alias() -> None:
    registry, first, _ = registered()
    document = definition_document()
    document["version"] = "1.1.0"
    second_adapter = SafeEchoAdapter(version="1.1.0")
    second = registry.register(document, second_adapter)
    assert registry.resolve("test.safe_echo", "1.0.0")[0] is first
    assert registry.resolve("test.safe_echo", "1.1.0")[0] is second
    with pytest.raises(UnknownToolVersionError):
        registry.resolve("test.safe_echo", "latest")


def test_registered_adapter_identity_is_read_only_and_exact() -> None:
    registry, definition, adapter = registered()

    with pytest.raises(AttributeError):
        adapter.tool_id = "test.changed"
    with pytest.raises(AttributeError):
        adapter.version = "9.9.9"

    resolved_definition, resolved_adapter = registry.resolve(
        "test.safe_echo", "1.0.0"
    )
    assert resolved_definition is definition
    assert resolved_adapter is adapter
    assert (resolved_adapter.tool_id, resolved_adapter.version) == (
        definition.tool_id,
        definition.version,
    )


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda item: item.pop("tool_id"), "missing fields: tool_id"),
        (lambda item: item.update(tool_id="INVALID TOOL"), "controlled identifier"),
        (lambda item: item.update(version="latest"), "semantic version"),
        (lambda item: item.pop("owner"), "missing fields: owner"),
        (lambda item: item.update(purpose=""), "non-empty string"),
        (lambda item: item.update(lifecycle="unknown"), "lifecycle"),
        (lambda item: item.update(risk="high"), "risk"),
        (lambda item: item.update(side_effect="write"), "side_effect"),
        (lambda item: item.update(required_scopes=["bad scope"]), "controlled identifier"),
        (lambda item: item.update(required_scopes=["test.scope", "test.scope"]), "duplicates"),
        (lambda item: item.update(allowed_purposes=["test.purpose", "test.purpose"]), "duplicates"),
        (lambda item: item.update(input_contract_ref="bad"), "JSON Schema"),
        (lambda item: item.update(timeout_ms=0), "positive integer"),
        (lambda item: item.update(max_input_chars=0), "positive integer"),
        (lambda item: item.update(max_output_chars=0), "positive integer"),
        (lambda item: item.update(consequential="false"), "boolean"),
        (lambda item: item.update(consequential=True), "non-consequential"),
        (lambda item: item.update(idempotent="true"), "boolean"),
        (lambda item: item.update(idempotent=False), "idempotent"),
    ],
)
def test_invalid_definition_is_rejected(mutation, match: str) -> None:
    document = definition_document()
    mutation(document)
    with pytest.raises(ToolDefinitionValidationError, match=match):
        InMemoryToolRegistry().register(document, SafeEchoAdapter())


def test_resolved_definition_is_immutable() -> None:
    registry, definition, _ = registered()
    with pytest.raises(FrozenInstanceError):
        definition.purpose = "changed"
    with pytest.raises(AttributeError):
        definition.required_scopes.append("test.other")
    assert registry.resolve("test.safe_echo", "1.0.0")[0].purpose == definition.purpose
