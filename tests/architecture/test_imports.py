"""Import checks for the M1.2 package boundaries."""

import importlib

import pytest


CORE_MODULES = (
    "deeplearn.core.contracts",
    "deeplearn.core.runtime",
    "deeplearn.core.registry",
    "deeplearn.core.models",
    "deeplearn.core.tools",
    "deeplearn.core.permissions",
    "deeplearn.core.audit",
    "deeplearn.test_client",
)


@pytest.mark.parametrize("module_name", CORE_MODULES)
def test_boundary_module_imports(module_name: str) -> None:
    assert importlib.import_module(module_name) is not None
