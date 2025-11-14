#!/bin/bash
# Run TritonBench tests with kernel timing configuration
# This script uses runner.py with the kernel_time_tritonbench config group
# which runs baseline, compute-sanitizer, and triton-sanitizer with:
# TRITON_ALWAYS_COMPILE=0 and PYTORCH_NO_CUDA_MEMORY_CACHING=0
#
# Profiling is enabled for baseline and compute-sanitizer,
# but disabled for triton-sanitizer (triton-viz has its own profiling).
# triton-sanitizer also sets ENABLE_TIMING=1 for timing measurements.

echo "========================================"
echo "Running TritonBench Kernel Time Tests"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Create timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Check for TritonBench whitelist
echo "Checking for TritonBench whitelist..."
if [ -f "tritonbench_whitelist.txt" ]; then
    echo "  ✓ TritonBench whitelist detected"
    echo "    Will run only whitelisted tests"
else
    echo "  ⚠ No TritonBench whitelist found, will run all tests"
fi
echo ""

# Configuration
echo "Configuration:"
echo "  Config Group: kernel_time_tritonbench"
echo "  Repository: tritonbench"
echo "  Environment Variables:"
echo "    TRITON_ALWAYS_COMPILE=0"
echo "    PYTORCH_NO_CUDA_MEMORY_CACHING=0"
echo "  Sanitizers:"
echo "    - baseline (profiling enabled)"
echo "    - compute-sanitizer (profiling enabled)"
echo "    - triton-sanitizer (profiling disabled, uses triton-viz, ENABLE_TIMING=1)"
echo ""

# Base output directory
OUTPUT_BASE="test_outputs_kernel_time_${TIMESTAMP}"

# Run tests using runner.py
echo "========================================"
echo "Starting Tests"
echo "========================================"
echo ""

python3 runner.py \
    --repos tritonbench \
    --config-groups kernel_time_tritonbench \
    --output-dir "${OUTPUT_BASE}"

TEST_EXIT_CODE=$?

echo ""
echo "========================================"
echo "Test Runs Complete"
echo "========================================"
echo ""
echo "Test execution completed. Check the summary below for individual test results."
echo ""
echo "Results saved in: ${OUTPUT_BASE}/"
echo ""

# Run analysis script and generate CSV
echo "========================================"
echo "Analyzing Results and Generating CSV"
echo "========================================"
echo ""

python3 analyze_kernel_time.py "${OUTPUT_BASE}" --csv "kernel_timing_results.csv"

ANALYSIS_EXIT_CODE=$?

if [ ${ANALYSIS_EXIT_CODE} -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Analysis Complete!"
    echo "========================================"
    echo ""
    echo "Results:"
    echo "  CSV File:  ${OUTPUT_BASE}/kernel_timing_results.csv (ordered by test number)"
    echo "  Log files: ${OUTPUT_BASE}/kernel_time_tritonbench/*/"
    echo ""
    echo "To view CSV:"
    echo "  cat ${OUTPUT_BASE}/kernel_timing_results.csv"
    echo "  or"
    echo "  column -t -s, ${OUTPUT_BASE}/kernel_timing_results.csv | less -S"
    echo ""
else
    echo ""
    echo "⚠ Analysis script failed, but test logs are still available in ${OUTPUT_BASE}/"
    echo ""
fi

echo "========================================"

# Exit with analysis status (tests always succeed in runner.py)
exit ${ANALYSIS_EXIT_CODE}
