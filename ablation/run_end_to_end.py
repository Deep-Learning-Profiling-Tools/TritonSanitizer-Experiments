#!/usr/bin/env python3
"""
Run ablation study experiments for all repositories.
This script runs end-to-end tests with 5 different cache configurations.

Python implementation of run_ablation_end_to_end.sh
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_python():
    """Check if Python3 is available (always true if running this script)."""
    return True


def check_triton_sanitizer():
    """Check if triton-sanitizer is available in PATH."""
    return shutil.which("triton-sanitizer") is not None


def prompt_continue():
    """Prompt user to continue or abort."""
    try:
        response = input("Continue? (y/n) ").strip().lower()
        return response in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def check_whitelists():
    """Check for whitelist files and print status."""
    print("Checking for whitelists...")

    whitelist_files = {
        "utils/liger_kernel_whitelist.txt": "Liger-Kernel whitelist detected (27 tests)",
        "utils/flag_gems_whitelist.txt": "FlagGems whitelist detected (20 tests)",
        "utils/tritonbench_whitelist.txt": "TritonBench whitelist detected (64 files)",
    }

    found_any = False
    for filepath, message in whitelist_files.items():
        full_path = PROJECT_ROOT / filepath
        if full_path.exists():
            print(f"  * {message}")
            found_any = True

    if not found_any:
        print("  No whitelists found, will run all tests")

    print()


def print_header():
    """Print script header."""
    print("=" * 40)
    print("Running Ablation Study Experiments")
    print("=" * 40)
    print()


def print_configuration_info():
    """Print configuration explanation."""
    print("Starting ablation study tests...")
    print("Tool: Triton Sanitizer with cache ablation configurations")
    print("Configuration: 5 cache configurations testing different cache combinations")
    print("  - no_cache: All caches disabled (0,0,0,0)")
    print("  - symbol_only: Only symbol cache enabled (1,0,0,0)")
    print("  - symbol_loop: Symbol and loop cache enabled (1,1,0,0)")
    print("  - symbol_loop_grid: Symbol, loop and grid cache enabled (1,1,1,0)")
    print("  - all_cache: All caches enabled (1,1,1,1)")
    print("Repositories: liger_kernel, flag_gems, tritonbench")
    print()


def run_tests(output_dir):
    """Run all tests using runner.py."""
    runner_script = PROJECT_ROOT / "runner.py"

    cmd = [
        sys.executable,
        str(runner_script),
        "--repos", "all",
        "--config-groups", "ablation_studies",
        "--output-dir", str(output_dir),
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def print_success(output_dir):
    """Print success message."""
    print()
    print("=" * 40)
    print("Ablation study experiments completed successfully!")
    print(f"Results saved in: {output_dir}/")
    print(f"CSV results: {output_dir}/results_*.csv")
    print()
    print("To analyze the timing results:")
    print("  Check the CSV file for execution time comparison across different cache configurations")
    print("=" * 40)


def print_failure(output_dir):
    """Print failure message."""
    print()
    print("=" * 40)
    print("Ablation study experiments failed or were interrupted")
    print(f"Partial results may be in: {output_dir}/")
    print("=" * 40)


def main():
    """Main entry point."""
    # Print header
    print_header()

    # Check Python (always succeeds if we're running)
    if not check_python():
        print("Error: Python3 is not installed or not in PATH")
        sys.exit(1)

    # Check triton-sanitizer
    if not check_triton_sanitizer():
        print("Warning: triton-sanitizer not found in PATH")
        print("Make sure triton-sanitizer is installed and available in PATH")
        if not prompt_continue():
            print("Aborted.")
            sys.exit(1)

    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Timestamp: {timestamp}")
    print()

    # Check for whitelists
    check_whitelists()

    # Print configuration info
    print_configuration_info()

    # Output directory
    output_dir = PROJECT_ROOT / f"test_outputs_ablation_{timestamp}"

    # Run tests
    exit_code = run_tests(output_dir)

    # Print result
    if exit_code == 0:
        print_success(output_dir)
    else:
        print_failure(output_dir)
        sys.exit(1)


if __name__ == "__main__":
    main()
