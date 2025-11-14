#!/bin/bash
# Run ablation study experiments for all repositories

echo "========================================"
echo "Running Ablation Study Experiments"
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

# Run ablation study tests for all repositories
echo "Starting ablation study tests..."
echo "Tool: Triton Sanitizer with cache ablation configurations"
echo "Configuration: 5 cache configurations testing different cache combinations"
echo "  - no_cache: All caches disabled (0,0,0,0)"
echo "  - symbol_only: Only symbol cache enabled (1,0,0,0)"
echo "  - symbol_loop: Symbol and loop cache enabled (1,1,0,0)"
echo "  - symbol_loop_grid: Symbol, loop and grid cache enabled (1,1,1,0)"
echo "  - all_cache: All caches enabled (1,1,1,1)"
echo "Repositories: liger_kernel, flag_gems, tritonbench"
echo ""

python3 runner.py \
    --repos all \
    --config-groups ablation_studies \
    --output-dir test_outputs_ablation_${TIMESTAMP}

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Ablation study experiments completed successfully!"
    echo "Results saved in: test_outputs_ablation_${TIMESTAMP}/"
    echo "CSV results: test_outputs_ablation_${TIMESTAMP}/results_*.csv"
    echo ""
    echo "To analyze the timing results:"
    echo "  Check the CSV file for execution time comparison across different cache configurations"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "Ablation study experiments failed or were interrupted"
    echo "Partial results may be in: test_outputs_ablation_${TIMESTAMP}/"
    echo "========================================"
    exit 1
fi
