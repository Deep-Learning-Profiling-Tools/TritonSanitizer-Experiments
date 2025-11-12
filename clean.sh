#!/bin/bash
# Clean all generated test output directories

echo "========================================"
echo "Cleaning Test Output Directories"
echo "========================================"
echo ""

# Default pattern
PATTERN="test_outputs*"

# Check if custom pattern provided
if [ "$1" != "" ]; then
    PATTERN="$1"
    echo "Using custom pattern: $PATTERN"
else
    echo "Using default pattern: $PATTERN"
fi

echo ""

# Run the cleanup
python3 runner.py --clean --clean-pattern "$PATTERN"

echo ""
echo "Cleanup process completed!"