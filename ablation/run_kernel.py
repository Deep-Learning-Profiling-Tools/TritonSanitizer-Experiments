#!/usr/bin/env python3
"""
Run ablation study with kernel timing across all repositories.
This script measures kernel execution time with 5 different cache configurations.

Python implementation of run_ablation_kernel_time.sh
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
    print("Running Ablation Study with Kernel Timing")
    print("=" * 40)
    print()


def print_configuration_info():
    """Print configuration explanation."""
    print("Ablation Study Cache Configurations:")
    print("  All using triton-sanitizer with ENABLE_TIMING=1")
    print("  Testing cache configurations (symbol, loop, grid, kernel):")
    print("    1. no_cache:          (0, 0, 0, 0)")
    print("    2. symbol_only:       (1, 0, 0, 0)")
    print("    3. symbol_loop:       (1, 1, 0, 0)")
    print("    4. symbol_loop_grid:  (1, 1, 1, 0)")
    print("    5. all_cache:         (1, 1, 1, 1)")
    print()
    print("Repositories: Liger-Kernel, FlagGems, TritonBench")
    print()


def run_tests(output_base):
    """Run all tests using runner.py."""
    print("=" * 40)
    print("Starting Tests")
    print("=" * 40)
    print()

    runner_script = PROJECT_ROOT / "runner.py"

    cmd = [
        sys.executable,
        str(runner_script),
        "--repos", "all",
        "--config-groups", "ablation_studies",
        "--output-dir", str(output_base),
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def run_analysis(output_base, csv_filename="ablation_kernel_timing_results.csv"):
    """Run analysis script and generate CSV."""
    print()
    print("=" * 40)
    print("Analyzing Results and Generating CSV")
    print("=" * 40)
    print()

    analysis_script = PROJECT_ROOT / "analyze_ablation_kernel_time.py"

    cmd = [
        sys.executable,
        str(analysis_script),
        str(output_base),
        "--csv", csv_filename,
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def print_results(output_base, analysis_exit_code):
    """Print final results and status."""
    if analysis_exit_code == 0:
        print()
        print("=" * 40)
        print("Analysis Complete!")
        print("=" * 40)
        print()
        print("Results:")
        print(f"  CSV File:  {output_base}/ablation_kernel_timing_results.csv (ordered by test number)")
        print(f"  Log files: {output_base}/ablation_studies/*/")
        print()
        print("To view CSV:")
        print(f"  cat {output_base}/ablation_kernel_timing_results.csv")
        print("  or")
        print(f"  column -t -s, {output_base}/ablation_kernel_timing_results.csv | less -S")
        print()
    else:
        print()
        print(f"Warning: Analysis script failed, but test logs are still available in {output_base}/")
        print()

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

    # Base output directory
    output_base = PROJECT_ROOT / f"test_outputs_ablation_kernel_time_{timestamp}"

    # Create base output directory
    output_base.mkdir(parents=True, exist_ok=True)

    # Check for whitelists
    check_whitelists()

    # Print configuration info
    print_configuration_info()

    # Run tests
    test_exit_code = run_tests(output_base)

    print()
    print("=" * 40)
    print("Test Runs Complete")
    print("=" * 40)
    print()
    print("Test execution completed. Check the summary below for individual test results.")
    print()
    print(f"Results saved in: {output_base}/")
    print()

    # Run analysis
    analysis_exit_code = run_analysis(output_base)

    # Print results
    print_results(output_base, analysis_exit_code)

    # Exit with analysis status
    sys.exit(analysis_exit_code)


if __name__ == "__main__":
    main()
