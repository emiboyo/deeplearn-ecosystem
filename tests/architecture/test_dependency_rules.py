"""Standard-library checks for the explicit M1.2 dependency rules."""

import ast
from collections import defaultdict
from importlib.util import resolve_name
from pathlib import Path
from sys import stdlib_module_names


SOURCE_ROOT = Path(__file__).parents[2] / "src"
CORE_ROOT = SOURCE_ROOT / "deeplearn" / "core"
FOUNDATIONAL_MODULES = {"registry", "models", "tools", "permissions", "audit"}
CORE_MODULES = FOUNDATIONAL_MODULES | {"contracts", "runtime"}
ALLOWED_CORE_DEPENDENCIES = {
    "contracts": set(),
    "registry": {"contracts"},
    "models": {"contracts"},
    "tools": {"contracts"},
    "permissions": {"contracts"},
    "audit": {"contracts"},
    "runtime": {"contracts", "registry", "models", "tools", "permissions", "audit"},
}
ALLOWED_TEST_CLIENT_DEPENDENCIES = {"contracts", "runtime"}


def _module_name(path: Path) -> str:
    parts = list(path.relative_to(SOURCE_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    module_name = _module_name(path)
    package = module_name if path.name == "__init__.py" else module_name.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported = node.module or ""
            if node.level:
                imported = resolve_name(f"{'.' * node.level}{imported}", package)
            names.add(imported)
    return names


def _core_files() -> list[Path]:
    return sorted(CORE_ROOT.rglob("*.py"))


def _core_boundary(path: Path) -> str | None:
    relative = path.relative_to(CORE_ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else None


def _deeplearn_target(name: str) -> tuple[str, str | None]:
    parts = name.split(".")
    if parts[:2] == ["deeplearn", "core"]:
        return "core", parts[2] if len(parts) > 2 else None
    if parts[:2] == ["deeplearn", "test_client"]:
        return "test_client", None
    return "unknown", None


def test_core_internal_dependencies_follow_allowlist() -> None:
    violations = []
    for path in _core_files():
        source = _core_boundary(path)
        allowed = ALLOWED_CORE_DEPENDENCIES.get(source, set())
        for name in _imports(path):
            if not name.startswith("deeplearn."):
                continue
            layer, target = _deeplearn_target(name)
            if layer != "core" or target is None:
                violations.append((str(path.relative_to(SOURCE_ROOT)), name))
            elif target != source and target not in allowed:
                violations.append((str(path.relative_to(SOURCE_ROOT)), name))
    assert violations == []


def test_test_client_internal_dependencies_follow_allowlist() -> None:
    violations = []
    client_root = SOURCE_ROOT / "deeplearn" / "test_client"
    for path in sorted(client_root.rglob("*.py")):
        for name in _imports(path):
            if not name.startswith("deeplearn."):
                continue
            layer, target = _deeplearn_target(name)
            same_layer = layer == "test_client"
            allowed_core = layer == "core" and target in ALLOWED_TEST_CLIENT_DEPENDENCIES
            if not (same_layer or allowed_core):
                violations.append((str(path.relative_to(SOURCE_ROOT)), name))
    assert violations == []


def test_core_does_not_import_test_client() -> None:
    violations = [
        path.relative_to(SOURCE_ROOT)
        for path in _core_files()
        if any(name.startswith("deeplearn.test_client") for name in _imports(path))
    ]
    assert violations == []


def test_production_source_has_no_third_party_dependencies() -> None:
    violations = []
    for path in sorted((SOURCE_ROOT / "deeplearn").rglob("*.py")):
        for name in _imports(path):
            root_name = name.partition(".")[0]
            if root_name != "deeplearn" and root_name not in stdlib_module_names:
                violations.append((str(path.relative_to(SOURCE_ROOT)), name))
    assert violations == []


def test_core_boundary_import_graph_is_acyclic() -> None:
    graph: dict[str, set[str]] = defaultdict(set)
    prefix = "deeplearn.core."
    for path in _core_files():
        relative = path.relative_to(CORE_ROOT)
        source_module = relative.parts[0]
        if source_module not in CORE_MODULES:
            continue
        for name in _imports(path):
            if name.startswith(prefix):
                target_module = name.removeprefix(prefix).split(".", 1)[0]
                if target_module in CORE_MODULES and target_module != source_module:
                    graph[source_module].add(target_module)

    visited: set[str] = set()
    active: set[str] = set()

    def visit(module: str) -> None:
        assert module not in active, f"circular Core dependency through {module}"
        if module in visited:
            return
        active.add(module)
        for dependency in graph[module]:
            visit(dependency)
        active.remove(module)
        visited.add(module)

    for module in CORE_MODULES:
        visit(module)
