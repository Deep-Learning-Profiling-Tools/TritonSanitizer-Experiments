#!/usr/bin/env python3
"""
Run ablation study with kernel timing across all repositories.
This script measures kernel execution time with 5 different cache configurations.

Output structure:
  results/
  ├── kernel_time/
  │   ├── no_cache/
  │   ├── symbol_only/
  │   ├── symbol_loop/
  │   ├── symbol_loop_grid/
  │   └── all_cache/
  └── ablation_kernel_time.csv
"""

import os
import sys
import re
import csv
import subprocess
import shutil
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output directories
RESULTS_DIR = SCRIPT_DIR / "results"
KERNEL_TIME_DIR = RESULTS_DIR / "kernel_time"
CSV_FILENAME = "ablation_kernel_time.csv"

# Configuration names in order
CONFIG_NAMES = ['no_cache', 'symbol_only', 'symbol_loop', 'symbol_loop_grid', 'all_cache']


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
    print(f"Output directory: {RESULTS_DIR}")
    print(f"Logs directory:   {KERNEL_TIME_DIR}")
    print(f"CSV file:         {RESULTS_DIR / CSV_FILENAME}")
    print()


def run_tests():
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
        "--output-dir", str(KERNEL_TIME_DIR),
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


# ============================================================================
# CSV Generation (integrated from analyze_ablation_kernel_time.py)
# ============================================================================

def parse_triton_sanitizer(log_file):
    """
    Parse triton-sanitizer log file for execution time.

    Example line:
    Triton-Viz: execution time for _jsd_kernel: 3.326 ms

    Returns:
        dict: {test_name: [list of execution_time values], ...}
    """
    pattern = r'Triton-Viz:\s+execution time for\s+(\S+):\s+([\d.]+)\s+ms'

    results = defaultdict(list)
    test_name = None
    test_number = None

    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Extract test number from header
                number_match = re.search(r'Test Number:\s+(\d+)', line)
                if number_match:
                    test_number = number_match.group(1)

                # Extract test name from header
                name_match = re.search(r'Test:\s+(.+)', line)
                if name_match:
                    test_name = name_match.group(1).strip()
                    if test_number and test_name:
                        test_name = f"{test_number}_{test_name}"

                # Also support pytest format
                pytest_match = re.search(r'(test_\w+\.py::\S+)', line)
                if pytest_match:
                    test_name = pytest_match.group(1)

                # Extract execution time
                match = re.search(pattern, line)
                if match and test_name:
                    kernel_name = match.group(1)
                    exec_time = float(match.group(2))
                    results[test_name].append({
                        'kernel': kernel_name,
                        'exec_time_ms': exec_time
                    })
    except FileNotFoundError:
        print(f"Warning: File not found: {log_file}")
        return {}
    except Exception as e:
        print(f"Error parsing {log_file}: {e}")
        return {}

    return results


def find_log_files(config_name):
    """
    Find all log files for a given configuration.

    Args:
        config_name: configuration name (no_cache, symbol_only, etc.)

    Returns:
        list of Path objects sorted by file number
    """
    # Try multiple possible directory structures
    possible_paths = [
        KERNEL_TIME_DIR / config_name,
        KERNEL_TIME_DIR / "ablation_studies" / config_name,
    ]

    config_path = None
    for path in possible_paths:
        if path.exists():
            config_path = path
            break

    if config_path is None:
        return []

    # Look for log files in the configuration directory
    log_files = []

    run_log = config_path / "run.log"
    if run_log.exists():
        log_files.append(run_log)

    for pattern in ['*.log', '**/*.log']:
        log_files.extend(config_path.glob(pattern))

    log_files = list(set(log_files))

    def extract_number(path):
        match = re.search(r'(\d+)_', path.name)
        if match:
            return int(match.group(1))
        return float('inf')

    log_files.sort(key=extract_number)

    return log_files


def analyze_configuration(config_name):
    """
    Analyze all log files for a configuration.

    Args:
        config_name: configuration name

    Returns:
        dict: {file_number: {'file_name': str, 'total_ms': float, 'count': int}}
    """
    log_files = find_log_files(config_name)

    if not log_files:
        print(f"  No log files found for {config_name}")
        return None

    print(f"  Found {len(log_files)} log file(s)")

    file_totals = {}

    for log_file in log_files:
        match = re.search(r'^(\d+)_(.+)\.log$', log_file.name)
        if not match:
            continue

        file_number = int(match.group(1))
        base_name = match.group(2)

        results = parse_triton_sanitizer(log_file)

        total_ms = 0.0
        total_count = 0
        for test_name, measurements in results.items():
            for m in measurements:
                total_ms += m['exec_time_ms']
                total_count += 1

        file_totals[file_number] = {
            'file_name': base_name,
            'total_ms': total_ms,
            'count': total_count
        }

    return file_totals


def format_test_name(file_name):
    """
    Convert file name to formatted test name with slashes.

    Examples:
        liger_kernel_test_fused_linear_jsd_test_correctness_functional
        -> liger_kernel/test_fused_linear_jsd/test_correctness_functional
    """
    repos = ['liger_kernel', 'flag_gems', 'tritonbench']

    repo = None
    for r in repos:
        if file_name.startswith(r + '_'):
            repo = r
            remainder = file_name[len(r) + 1:]
            break

    if repo is None:
        return file_name

    if repo == 'tritonbench':
        return f"{repo}/{remainder}"

    test_positions = []
    i = 0
    while i < len(remainder):
        if remainder[i:].startswith('test_'):
            test_positions.append(i)
            i += 5
        else:
            i += 1

    if len(test_positions) == 0:
        return f"{repo}/{remainder}"
    elif len(test_positions) == 1:
        return f"{repo}/{remainder}"
    else:
        split_pos = test_positions[-1]
        test_file = remainder[:split_pos - 1]
        test_func = remainder[split_pos:]
        return f"{repo}/{test_file}/{test_func}"


def export_to_csv(config_results):
    """
    Export results to CSV file.

    Args:
        config_results: dict mapping config names to their file_totals

    Returns:
        Path to CSV file or None on error
    """
    all_file_numbers = set()
    for config_name in CONFIG_NAMES:
        file_totals = config_results.get(config_name)
        if file_totals:
            all_file_numbers.update(file_totals.keys())

    if not all_file_numbers:
        print("No test results to export")
        return None

    sorted_file_numbers = sorted(all_file_numbers)

    csv_data = []
    for file_number in sorted_file_numbers:
        file_name = None
        for config_name in CONFIG_NAMES:
            file_totals = config_results.get(config_name, {})
            if file_number in file_totals:
                file_name = file_totals[file_number]['file_name']
                break

        if file_name is None:
            continue

        formatted_name = format_test_name(file_name)
        row = {'Test_Name': formatted_name}

        for config_name in CONFIG_NAMES:
            file_totals = config_results.get(config_name, {})
            time_ms = file_totals.get(file_number, {}).get('total_ms', 0.0)
            row[f'ablation_kernel_time_{config_name}'] = f"{time_ms:.3f}"

        csv_data.append(row)

    csv_path = RESULTS_DIR / CSV_FILENAME
    try:
        fieldnames = ['Test_Name'] + [f'ablation_kernel_time_{name}' for name in CONFIG_NAMES]
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        print(f"\nCSV exported to: {csv_path}")
        print(f"  Total tests: {len(csv_data)}")

        return csv_path
    except Exception as e:
        print(f"\nError exporting CSV: {e}")
        return None


def run_analysis():
    """Run analysis and generate CSV."""
    print()
    print("=" * 40)
    print("Analyzing Results and Generating CSV")
    print("=" * 40)
    print()

    configs = [
        ('no_cache', 'No Cache (0,0,0,0)'),
        ('symbol_only', 'Symbol Only (1,0,0,0)'),
        ('symbol_loop', 'Symbol + Loop (1,1,0,0)'),
        ('symbol_loop_grid', 'Symbol + Loop + Grid (1,1,1,0)'),
        ('all_cache', 'All Cache (1,1,1,1)'),
    ]

    config_results = {}

    for config_name, config_desc in configs:
        print(f"Analyzing {config_desc}...")
        totals = analyze_configuration(config_name)
        config_results[config_name] = totals

    # Print summary
    print()
    print("=" * 40)
    print("SUMMARY")
    print("=" * 40)

    summary_data = []
    for config_name, config_desc in configs:
        totals = config_results.get(config_name)
        if totals:
            total_ms = sum(t['total_ms'] for t in totals.values())
            summary_data.append((config_desc, total_ms))
            print(f"  {config_desc:30s} {total_ms:>12.3f} ms")

    if summary_data and summary_data[0][0] == 'No Cache (0,0,0,0)':
        baseline_total = summary_data[0][1]
        baseline_totals = config_results.get('no_cache', {})
        print()
        print("  Speedup vs No Cache:")
        print(f"    {'Configuration':<28s} {'Avg':>8} {'Min':>8} {'Max':>8}")
        print("    " + "-" * 56)

        config_keys = ['symbol_only', 'symbol_loop', 'symbol_loop_grid', 'all_cache']
        for i, (config_desc, total_ms) in enumerate(summary_data[1:]):
            config_key = config_keys[i]
            config_totals = config_results.get(config_key, {})

            # Calculate per-test speedups
            speedups = []
            for file_number in baseline_totals:
                baseline_ms = baseline_totals[file_number]['total_ms']
                if file_number in config_totals:
                    config_ms = config_totals[file_number]['total_ms']
                    if baseline_ms > 0 and config_ms > 0:
                        speedups.append(baseline_ms / config_ms)

            if speedups:
                avg_speedup = sum(speedups) / len(speedups)
                min_speedup = min(speedups)
                max_speedup = max(speedups)
                print(f"    {config_desc:<28s} {avg_speedup:>7.3f}x {min_speedup:>7.3f}x {max_speedup:>7.3f}x")

    print()

    # Export to CSV
    csv_path = export_to_csv(config_results)

    return 0 if csv_path else 1


def print_results(analysis_exit_code):
    """Print final results and status."""
    if analysis_exit_code == 0:
        print()
        print("=" * 40)
        print("Analysis Complete!")
        print("=" * 40)
        print()
        print("Results:")
        print(f"  CSV File:  {RESULTS_DIR / CSV_FILENAME}")
        print(f"  Log files: {KERNEL_TIME_DIR}/*/")
        print()
    else:
        print()
        print(f"Warning: Analysis failed, but test logs are still available in {KERNEL_TIME_DIR}/")
        print()

    print("=" * 40)


def main():
    """Main entry point."""
    print_header()

    if not check_python():
        print("Error: Python3 is not installed or not in PATH")
        sys.exit(1)

    if not check_triton_sanitizer():
        print("Warning: triton-sanitizer not found in PATH")
        print("Make sure triton-sanitizer is installed and available in PATH")
        if not prompt_continue():
            print("Aborted.")
            sys.exit(1)

    # Create output directories
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    KERNEL_TIME_DIR.mkdir(parents=True, exist_ok=True)

    check_whitelists()
    print_configuration_info()

    # Run tests
    test_exit_code = run_tests()

    print()
    print("=" * 40)
    print("Test Runs Complete")
    print("=" * 40)
    print()
    print(f"Results saved in: {KERNEL_TIME_DIR}/")
    print()

    # Run analysis and generate CSV
    analysis_exit_code = run_analysis()

    print_results(analysis_exit_code)

    sys.exit(analysis_exit_code)


if __name__ == "__main__":
    main()
