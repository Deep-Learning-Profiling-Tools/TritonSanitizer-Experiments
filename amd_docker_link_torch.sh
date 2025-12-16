#!/bin/bash

# Link system torch/triton to uv virtual environment
# Usage: ./link_system_torch.sh [venv_path] [system_packages_path]

VENV_PATH="${1:-.venv}"
SYSTEM_PACKAGES="${2:-/opt/venv/lib/python3.10/site-packages}"

TARGET_DIR="$VENV_PATH/lib/python3.10/site-packages"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR does not exist"
    exit 1
fi

if [ ! -d "$SYSTEM_PACKAGES" ]; then
    echo "Error: $SYSTEM_PACKAGES does not exist"
    exit 1
fi

cd "$TARGET_DIR" || exit 1

# Package directories to link
PACKAGES=(
    "torch"
    "torchgen"
    "triton"
    "torchaudio"
    "torchvision"
    "torchvision.libs"
)

# Link package directories
for pkg in "${PACKAGES[@]}"; do
    if [ -e "$SYSTEM_PACKAGES/$pkg" ]; then
        ln -sf "$SYSTEM_PACKAGES/$pkg" .
        echo "Linked: $pkg"
    fi
done

# Link dist-info directories
for dist_info in "$SYSTEM_PACKAGES"/*torch*.dist-info "$SYSTEM_PACKAGES"/*triton*.dist-info; do
    if [ -e "$dist_info" ]; then
        ln -sf "$dist_info" .
        echo "Linked: $(basename "$dist_info")"
    fi
done

echo "Done!"
