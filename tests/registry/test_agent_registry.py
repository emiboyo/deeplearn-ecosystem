"""Focused M1.3 tests for immutable Test Agent registration."""

from dataclasses import FrozenInstanceError
import json
from pathlib import Path

import pytest

from deeplearn.core.registry import (
    AgentDefinition,
    AutonomyLevel,
    DefinitionValidationError,
    DuplicateDefinitionError,
    InMemoryAgentDefinitionRegistry,
    Lifecycle,
    ModelCapability,
    ToolNotAllowedError,
    UnknownAgentError,
    UnknownAgentVersionError,
)


ROOT = Path(__file__).parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "m1" / "agents" / "test.safe_agent-1.0.0.json"


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _registered() -> tuple[InMemoryAgentDefinitionRegistry, AgentDefinition]:
    registry = InMemoryAgentDefinitionRegistry()
    return registry, registry.register(_fixture())


def test_valid_test_agent_registration() -> None:
    _, definition = _registered()
    assert definition.agent_id == "test.safe_agent"
    assert definition.version == "1.0.0"
    assert definition.lifecycle is Lifecycle.ACTIVE


def test_exact_version_resolution() -> None:
    registry, definition = _registered()
    assert registry.resolve("test.safe_agent", "1.0.0") is definition


def test_unknown_agent_is_rejected() -> None:
    registry, _ = _registered()
    with pytest.raises(UnknownAgentError):
        registry.resolve("test.unknown_agent", "1.0.0")


def test_unknown_version_is_rejected() -> None:
    registry, _ = _registered()
    with pytest.raises(UnknownAgentVersionError):
        registry.resolve("test.safe_agent", "9.9.9")


def test_duplicate_registration_does_not_overwrite() -> None:
    registry, original = _registered()
    with pytest.raises(DuplicateDefinitionError):
        registry.register(_fixture())
    assert registry.resolve("test.safe_agent", "1.0.0") is original


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda item: item.pop("agent_id"), "missing fields: agent_id"),
        (lambda item: item.update(agent_id="INVALID AGENT"), "controlled identifier"),
        (lambda item: item.pop("owner"), "missing fields: owner"),
        (lambda item: item.update(purpose=""), "non-empty string"),
        (lambda item: item.update(input_contract_ref=""), "versioned JSON Schema"),
        (lambda item: item.update(output_contract_ref="not-a-contract"), "versioned JSON Schema"),
        (lambda item: item.update(allowed_tools=["test.safe_echo", "test.safe_echo"]), "duplicates"),
        (lambda item: item.update(allowed_tools=["arbitrary tool"]), "controlled identifier"),
        (lambda item: item["execution_limits"].update(max_steps=0), "positive integer"),
        (lambda item: item.update(autonomy="unbounded"), "autonomy must be one of"),
        (lambda item: item["model_requirements"].update(provider_id="provider.forbidden"), "unsupported fields"),
    ],
)
def test_malformed_definitions_are_rejected(mutation, match: str) -> None:
    document = _fixture()
    mutation(document)
    with pytest.raises(DefinitionValidationError, match=match):
        InMemoryAgentDefinitionRegistry().register(document)


def test_invalid_lifecycle_is_rejected() -> None:
    document = _fixture()
    document["lifecycle"] = "unknown"
    with pytest.raises(DefinitionValidationError, match="lifecycle"):
        InMemoryAgentDefinitionRegistry().register(document)


def test_invalid_version_is_rejected() -> None:
    document = _fixture()
    document["version"] = "latest"
    with pytest.raises(DefinitionValidationError, match="semantic version"):
        InMemoryAgentDefinitionRegistry().register(document)


def test_declared_tool_is_allowed() -> None:
    registry, _ = _registered()
    assert registry.is_tool_allowed("test.safe_agent", "1.0.0", "test.safe_echo")
    registry.require_tool_allowed("test.safe_agent", "1.0.0", "test.safe_echo")


def test_undeclared_or_arbitrary_tool_is_rejected() -> None:
    registry, _ = _registered()
    assert not registry.is_tool_allowed("test.safe_agent", "1.0.0", "test.arbitrary_tool")
    with pytest.raises(ToolNotAllowedError):
        registry.require_tool_allowed("test.safe_agent", "1.0.0", "test.arbitrary_tool")


def test_model_requirement_is_provider_neutral() -> None:
    _, definition = _registered()
    assert definition.model_requirements.capabilities == (ModelCapability.TEXT_GENERATION,)
    assert not hasattr(definition.model_requirements, "provider_id")
    assert not hasattr(definition.model_requirements, "model_id")


def test_agent_definition_schema_controls_model_capabilities() -> None:
    schema_path = ROOT / "contracts" / "v1" / "agent-definition.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    capability_schema = schema["properties"]["model_requirements"]["properties"]["capabilities"]["items"]
    assert capability_schema == {"enum": ["text_generation"]}


@pytest.mark.parametrize(
    "capability",
    ["openai.gpt", "anthropic.claude", "gpt.5"],
)
def test_unsupported_or_provider_specific_model_capability_is_rejected(capability: str) -> None:
    document = _fixture()
    document["model_requirements"]["capabilities"] = [capability]
    with pytest.raises(DefinitionValidationError, match="unsupported capability"):
        InMemoryAgentDefinitionRegistry().register(document)


def test_returned_definition_cannot_mutate_registry_state() -> None:
    registry, definition = _registered()
    with pytest.raises(FrozenInstanceError):
        definition.purpose = "changed"
    with pytest.raises(AttributeError):
        definition.allowed_tools.append("test.arbitrary_tool")
    assert registry.resolve("test.safe_agent", "1.0.0").allowed_tools == ("test.safe_echo",)


def test_two_explicit_versions_can_coexist() -> None:
    registry, first = _registered()
    document = _fixture()
    document["version"] = "1.1.0"
    second = registry.register(document)
    assert registry.resolve("test.safe_agent", "1.0.0") is first
    assert registry.resolve("test.safe_agent", "1.1.0") is second


def test_retired_version_remains_exactly_resolvable() -> None:
    document = _fixture()
    document["lifecycle"] = "retired"
    registry = InMemoryAgentDefinitionRegistry()
    definition = registry.register(document)
    assert registry.resolve("test.safe_agent", "1.0.0") is definition
    assert definition.lifecycle is Lifecycle.RETIRED


def test_test_agent_uses_safest_autonomy_level() -> None:
    _, definition = _registered()
    assert definition.autonomy is AutonomyLevel.ASSIST
