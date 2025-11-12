#!/bin/bash
# Run compute-sanitizer experiments for all repositories

echo "========================================"
echo "Running Compute-Sanitizer Experiments"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if compute-sanitizer is available
if ! command -v compute-sanitizer &> /dev/null; then
    echo "Warning: compute-sanitizer not found in PATH"
    echo "Make sure NVIDIA CUDA Toolkit is installed and compute-sanitizer is available"
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

# Run compute-sanitizer tests for all repositories
echo "Starting compute-sanitizer tests..."
echo "Tool: NVIDIA Compute Sanitizer for memory error detection"
echo "Configuration: 4 compute-sanitizer configurations with TRITON_ALWAYS_COMPILE and PYTORCH_NO_CUDA_MEMORY_CACHING variations"
echo "Repositories: liger_kernel, flag_gems, tritonbench"
echo ""

python3 runner.py \
    --repos all \
    --config-groups compute_sanitizer \
    --output-dir test_outputs_compute_sanitizer_${TIMESTAMP}

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Compute-sanitizer experiments completed successfully!"
    echo "Results saved in: test_outputs_compute_sanitizer_${TIMESTAMP}/"
    echo "CSV results: test_outputs_compute_sanitizer_${TIMESTAMP}/results_*.csv"
    echo ""
    echo "To check for memory errors:"
    echo "  grep -i 'error\|violation' test_outputs_compute_sanitizer_${TIMESTAMP}/compute_sanitizer/*/*.log"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "Compute-sanitizer experiments failed or were interrupted"
    echo "Partial results may be in: test_outputs_compute_sanitizer_${TIMESTAMP}/"
    echo "========================================"
    exit 1
fi