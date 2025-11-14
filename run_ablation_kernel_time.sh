#!/bin/bash
# Run ablation study with kernel timing across all repositories
# This script measures kernel execution time with 5 different cache configurations

echo "========================================"
echo "Running Ablation Study with Kernel Timing"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if triton-sanitizer is available
if ! command -v triton-sanitizer &> /dev/null; then
    echo "Warning: triton-sanitizer not found in PATH"
    echo "Make sure triton-sanitizer is installed and available in PATH"
    echo "Continue? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Base output directory
OUTPUT_BASE="test_outputs_ablation_kernel_time_${TIMESTAMP}"

# Create base output directory
mkdir -p "${OUTPUT_BASE}"

# Check for whitelists
echo "Checking for whitelists..."
if [ -f "liger_kernel_whitelist.txt" ]; then
    echo "  ✓ Liger-Kernel whitelist detected (27 tests)"
fi
if [ -f "flag_gems_whitelist.txt" ]; then
    echo "  ✓ FlagGems whitelist detected (20 tests)"
fi
if [ -f "tritonbench_whitelist.txt" ]; then
    echo "  ✓ TritonBench whitelist detected (64 files)"
fi
if [ ! -f "liger_kernel_whitelist.txt" ] && [ ! -f "flag_gems_whitelist.txt" ] && [ ! -f "tritonbench_whitelist.txt" ]; then
    echo "  No whitelists found, will run all tests"
fi
echo ""

# Configuration explanation
echo "Ablation Study Cache Configurations:"
echo "  All using triton-sanitizer with ENABLE_TIMING=1"
echo "  Testing cache configurations (symbol, loop, grid, kernel):"
echo "    1. no_cache:          (0, 0, 0, 0)"
echo "    2. symbol_only:       (1, 0, 0, 0)"
echo "    3. symbol_loop:       (1, 1, 0, 0)"
echo "    4. symbol_loop_grid:  (1, 1, 1, 0)"
echo "    5. all_cache:         (1, 1, 1, 1)"
echo ""
echo "Repositories: Liger-Kernel, FlagGems, TritonBench"
echo ""

# Run all tests
echo "========================================"
echo "Starting Tests"
echo "========================================"
echo ""

python3 runner.py \
    --repos all \
    --config-groups ablation_studies \
    --output-dir "${OUTPUT_BASE}"

TEST_EXIT_CODE=$?

echo ""
echo "========================================"
echo "Test Runs Complete"
echo "========================================"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests completed successfully"
else
    echo "⚠ Some tests failed or were interrupted"
fi

echo ""
echo "Results directory: ${OUTPUT_BASE}/"
echo ""

# Find CSV results
csv_file=$(find "${OUTPUT_BASE}" -name "results_*.csv" | head -1)

if [ -f "$csv_file" ]; then
    echo "CSV Results: ${csv_file}"
    echo ""
    echo "To view the results:"
    echo "  cat ${csv_file}"
    echo "  or"
    echo "  column -t -s, ${csv_file} | less -S"
    echo ""

    # Show column headers
    echo "CSV Columns:"
    head -1 "$csv_file"
    echo ""

    # Count results
    total_tests=$(tail -n +2 "$csv_file" | wc -l)
    echo "Total test results: ${total_tests}"
else
    echo "⚠ No CSV file found"
fi

echo ""
echo "========================================"

exit $TEST_EXIT_CODE
