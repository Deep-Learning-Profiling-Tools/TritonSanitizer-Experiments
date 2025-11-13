#!/bin/bash
# Run Liger-Kernel tests with kernel timing configuration
# This script uses runner.py with the kernel_time_liger_kernel config group
# which runs baseline, compute-sanitizer, and triton-sanitizer with:
# TRITON_ALWAYS_COMPILE=0 and PYTORCH_NO_CUDA_MEMORY_CACHING=0

echo "========================================"
echo "Running Liger-Kernel Kernel Time Tests"
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

# Check for liger_kernel whitelist
echo "Checking for Liger-Kernel whitelist..."
if [ -f "liger_kernel_whitelist.txt" ]; then
    echo "  ✓ Liger-Kernel whitelist detected"
    echo "    Will run only whitelisted tests"
else
    echo "  ⚠ No Liger-Kernel whitelist found, will run all tests"
fi
echo ""

# Configuration
echo "Configuration:"
echo "  Config Group: kernel_time_liger_kernel"
echo "  Repository: liger_kernel"
echo "  Environment Variables:"
echo "    TRITON_ALWAYS_COMPILE=0"
echo "    PYTORCH_NO_CUDA_MEMORY_CACHING=0"
echo "  Sanitizers: baseline, compute-sanitizer, triton-sanitizer"
echo ""

# Base output directory
OUTPUT_BASE="test_outputs_kernel_time_${TIMESTAMP}"

# Run tests using runner.py
echo "========================================"
echo "Starting Tests"
echo "========================================"
echo ""

python3 runner.py \
    --repos liger_kernel \
    --config-groups kernel_time_liger_kernel \
    --output-dir "${OUTPUT_BASE}"

TEST_EXIT_CODE=$?

echo ""
echo "========================================"
echo "Test Runs Complete"
echo "========================================"
echo ""

if [ ${TEST_EXIT_CODE} -eq 0 ]; then
    echo "✓ All tests completed successfully"
else
    echo "⚠ Some tests failed or were interrupted"
fi

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
    echo "Reordering CSV according to whitelist order..."
    python3 reorder_csv.py "${OUTPUT_BASE}/kernel_timing_results.csv" "${OUTPUT_BASE}/kernel_timing_ordered.csv"
    REORDER_EXIT_CODE=$?

    echo ""
    echo "========================================"
    echo "Analysis Complete!"
    echo "========================================"
    echo ""
    echo "Results:"
    echo "  Aggregated CSV: ${OUTPUT_BASE}/kernel_timing_results.csv (alphabetical)"
    echo "  Ordered CSV:    ${OUTPUT_BASE}/kernel_timing_ordered.csv (whitelist order)"
    echo "  Log files:      ${OUTPUT_BASE}/kernel_time_liger_kernel/*/"
    echo ""
    echo "To view ordered CSV:"
    echo "  cat ${OUTPUT_BASE}/kernel_timing_ordered.csv"
    echo "  or"
    echo "  column -t -s, ${OUTPUT_BASE}/kernel_timing_ordered.csv"
    echo ""
else
    echo ""
    echo "⚠ Analysis script failed, but test logs are still available in ${OUTPUT_BASE}/"
    echo ""
fi

echo "========================================"

# Exit with combined error status
if [ ${TEST_EXIT_CODE} -ne 0 ] || [ ${ANALYSIS_EXIT_CODE} -ne 0 ]; then
    exit 1
fi

exit 0
