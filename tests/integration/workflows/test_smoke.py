"""
Smoke test – verifies that the project’s import tree is syntactically valid.

Context:
    * Serves as a placeholder until real unit tests are added.
    * Keeps CI / pytest from failing with exit-code 5 ("no tests collected").
"""

def test_imports() -> None:
    import importlib
    import pkgutil
    import pathlib

    pkg_root = pathlib.Path(__file__).parents[1] / "poc"
    for module in pkgutil.walk_packages([str(pkg_root)]):
        importlib.import_module(f"poc.{module.name}")
