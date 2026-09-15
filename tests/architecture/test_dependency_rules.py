"""Standard-library checks for the explicit M1.2 dependency rules."""

import ast
from collections import defaultdict
from pathlib import Path


SOURCE_ROOT = Path(__file__).parents[2] / "src"
CORE_ROOT = SOURCE_ROOT / "deeplearn" / "core"
FOUNDATIONAL_MODULES = {"registry", "models", "tools", "permissions", "audit"}
CORE_MODULES = FOUNDATIONAL_MODULES | {"contracts", "runtime"}

FORBIDDEN_PRODUCT_PREFIXES = (
    "atlas",
    "pbcoms",
    "pearlbridge",
    "scriptureos",
    "circle",
    "deeplearn.verticals",
    "deeplearn.products",
)
FORBIDDEN_PROVIDER_OR_INFRASTRUCTURE_PREFIXES = (
    "openai",
    "anthropic",
    "google.generativeai",
    "boto3",
    "azure",
    "sqlalchemy",
    "fastapi",
    "django",
    "flask",
    "kubernetes",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _core_files() -> list[Path]:
    return sorted(CORE_ROOT.rglob("*.py"))


def test_foundational_modules_do_not_import_runtime() -> None:
    violations = []
    for module in FOUNDATIONAL_MODULES:
        for path in (CORE_ROOT / module).rglob("*.py"):
            if any(name.startswith("deeplearn.core.runtime") for name in _imports(path)):
                violations.append(path.relative_to(SOURCE_ROOT))
    assert violations == []


def test_core_does_not_import_test_client() -> None:
    violations = [
        path.relative_to(SOURCE_ROOT)
        for path in _core_files()
        if any(name.startswith("deeplearn.test_client") for name in _imports(path))
    ]
    assert violations == []


def test_core_has_no_product_provider_or_infrastructure_imports() -> None:
    forbidden = FORBIDDEN_PRODUCT_PREFIXES + FORBIDDEN_PROVIDER_OR_INFRASTRUCTURE_PREFIXES
    violations = []
    for path in _core_files():
        for name in _imports(path):
            if any(name == prefix or name.startswith(f"{prefix}.") for prefix in forbidden):
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
