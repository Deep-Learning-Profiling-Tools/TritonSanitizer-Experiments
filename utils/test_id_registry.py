#!/usr/bin/env python3
"""
Global test ID registry - assigns fixed unique IDs to each test.

This module provides persistent test IDs that remain constant regardless of
which subset of tests are run. IDs are 1-based and sorted by repository order
then test name.

Usage:
    # Rebuild the registry (run when tests change):
    python -m utils.test_id_registry --rebuild

    # In code:
    from utils.test_id_registry import get_test_id, get_max_test_id
    test_id = get_test_id("liger_kernel/test_cross_entropy/test_correctness")
"""

import json
import ast
import argparse
from pathlib import Path

# Registry file location
REGISTRY_FILE = Path(__file__).parent / "test_id_registry.json"

# Order of repositories for ID assignment
REPO_ORDER = ["liger_kernel", "tritonbench", "flag_gems"]


def load_registry() -> dict:
    """Load the test ID registry from JSON file.

    Returns:
        Dictionary mapping test_name -> global_test_id
    """
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {}


def save_registry(registry: dict):
    """Save the test ID registry to JSON file.

    Args:
        registry: Dictionary mapping test_name -> global_test_id
    """
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)


def get_test_id(test_name: str) -> int:
    """Get the global ID for a test name.

    Args:
        test_name: Full test name (e.g., "liger_kernel/test_cross_entropy/test_correctness")

    Returns:
        Global test ID (1-based)

    Raises:
        KeyError: If test is not in the registry
    """
    registry = load_registry()
    if test_name not in registry:
        raise KeyError(
            f"Test '{test_name}' not in registry. "
            f"Run: python -m utils.test_id_registry --rebuild"
        )
    return registry[test_name]


def get_max_test_id() -> int:
    """Get the maximum test ID in the registry.

    Returns:
        Maximum test ID, or 0 if registry is empty
    """
    registry = load_registry()
    return max(registry.values()) if registry else 0


def _discover_test_functions(test_file: Path) -> list:
    """Discover individual test functions in a pytest file using AST parsing.

    Args:
        test_file: Path to the test file

    Returns:
        List of test function names, or None if parsing fails
    """
    test_functions = []

    try:
        with open(test_file, 'r') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_functions.append(node.name)
    except Exception:
        return None

    return test_functions if test_functions else None


def _load_whitelist(whitelist_path: Path, repo_name: str) -> dict:
    """Load test whitelist from file.

    Args:
        whitelist_path: Path to the whitelist file
        repo_name: Name of the repository

    Returns:
        Dictionary mapping test file stem -> list of test functions
    """
    whitelist = {}

    if not whitelist_path.exists():
        return None

    with open(whitelist_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            if repo_name == "tritonbench":
                file_name = Path(line).stem
                whitelist[file_name] = []
            elif "::" in line:
                test_file, test_function = line.split("::")
                test_file = Path(test_file).stem
                if test_file not in whitelist:
                    whitelist[test_file] = []
                whitelist[test_file].append(test_function)

    return whitelist if whitelist else None


def discover_all_tests(project_root: Path) -> list:
    """Discover all tests from all repositories.

    Args:
        project_root: Root directory of the project

    Returns:
        List of test info dictionaries with 'repository' and 'test_name' keys
    """
    # Import here to avoid circular imports
    from utils.test_registry import REPO_CONFIGS

    test_list = []

    for repo_name in REPO_ORDER:
        if repo_name not in REPO_CONFIGS:
            continue

        config = REPO_CONFIGS[repo_name]
        test_dir = project_root / config["test_dir"]

        if not test_dir.exists():
            print(f"Warning: Test directory {test_dir} does not exist for {repo_name}")
            continue

        # Load whitelist
        whitelist_file = config.get("whitelist_file")
        whitelist = None
        if whitelist_file:
            whitelist = _load_whitelist(project_root / whitelist_file, repo_name)

        # Discover test files
        test_files = []
        if repo_name == "tritonbench":
            benchmark_dirs = [
                test_dir / "data" / "TritonBench_G_v1",
                test_dir / "LLM_generated",
                test_dir / "EVAL"
            ]
            for bench_dir in benchmark_dirs:
                if bench_dir.exists():
                    for py_file in bench_dir.glob("**/*.py"):
                        if "__pycache__" not in str(py_file) and not py_file.name.startswith("__"):
                            test_files.append(py_file)
        else:
            pattern = config["test_pattern"]
            test_files = list(test_dir.glob(pattern))

        # Filter by skip_tests
        test_files = [f for f in test_files if f.name not in config.get("skip_tests", [])]

        # Process each test file
        for test_file in test_files:
            test_file_stem = test_file.stem

            if whitelist and test_file_stem in whitelist:
                if repo_name == "tritonbench":
                    test_list.append({
                        "repository": repo_name,
                        "test_name": f"{repo_name}/{test_file_stem}"
                    })
                else:
                    for test_function in whitelist[test_file_stem]:
                        test_list.append({
                            "repository": repo_name,
                            "test_name": f"{repo_name}/{test_file_stem}/{test_function}"
                        })
            elif whitelist and repo_name == "tritonbench":
                # Skip tritonbench files not in whitelist
                continue
            elif not whitelist and repo_name in ["liger_kernel", "flag_gems"]:
                # Discover test functions for pytest-based repos
                test_functions = _discover_test_functions(test_file)
                if test_functions:
                    for test_function in test_functions:
                        test_list.append({
                            "repository": repo_name,
                            "test_name": f"{repo_name}/{test_file_stem}/{test_function}"
                        })
                else:
                    test_list.append({
                        "repository": repo_name,
                        "test_name": f"{repo_name}/{test_file_stem}"
                    })
            elif not whitelist:
                test_list.append({
                    "repository": repo_name,
                    "test_name": f"{repo_name}/{test_file_stem}"
                })

    return test_list


def build_registry(project_root: Path) -> dict:
    """Build registry from discovered tests.

    Tests are sorted by repository order (liger_kernel, tritonbench, flag_gems)
    then by test name. IDs are 1-based.

    Args:
        project_root: Root directory of the project

    Returns:
        Registry dictionary mapping test_name -> global_test_id
    """
    tests = discover_all_tests(project_root)

    # Sort by repo order, then by test name
    def sort_key(t):
        repo_idx = REPO_ORDER.index(t["repository"]) if t["repository"] in REPO_ORDER else 999
        return (repo_idx, t["test_name"])

    tests.sort(key=sort_key)

    # Assign 1-based IDs
    registry = {}
    for idx, test in enumerate(tests, start=1):
        registry[test["test_name"]] = idx

    save_registry(registry)

    # Print summary by repository
    print(f"\nBuilt registry with {len(registry)} tests:")
    for repo in REPO_ORDER:
        repo_tests = [t for t in tests if t["repository"] == repo]
        if repo_tests:
            first_id = registry[repo_tests[0]["test_name"]]
            last_id = registry[repo_tests[-1]["test_name"]]
            print(f"  {repo}: {len(repo_tests)} tests (IDs {first_id}-{last_id})")

    return registry


def main():
    parser = argparse.ArgumentParser(
        description="Global test ID registry management"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the registry from discovered tests"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all tests in the registry"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    if args.rebuild:
        build_registry(project_root)
    elif args.list:
        registry = load_registry()
        if not registry:
            print("Registry is empty. Run with --rebuild first.")
        else:
            # Sort by ID
            sorted_tests = sorted(registry.items(), key=lambda x: x[1])
            for test_name, test_id in sorted_tests:
                print(f"{test_id:4d}: {test_name}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
