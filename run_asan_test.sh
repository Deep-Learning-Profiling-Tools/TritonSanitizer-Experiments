#!/bin/bash

ulimit -s 1024

export PATH=$(find ~/.triton/llvm -name llvm-symbolizer -printf '%h\n'):$PATH

TORCH_PATH=$(find /opt -name libcaffe2_nvrtc.so -printf '%h\n')
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$TORCH_PATH

# Ensure libamdhip64.so is restored on exit/interrupt
cleanup() {
    if [ -f "$TORCH_PATH/libamdhip64_bck.so" ]; then
        mv $TORCH_PATH/libamdhip64_bck.so $TORCH_PATH/libamdhip64.so
    fi
}
trap cleanup EXIT

mv $TORCH_PATH/libamdhip64.so $TORCH_PATH/libamdhip64_bck.so

export LD_LIBRARY_PATH=$(find /opt -name libclang_rt.asan-x86_64.so -printf '%h\n'):$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$(find /opt -type d -wholename *lib/llvm/lib/asan):$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$(find /opt -wholename *lib/asan/libamdhip64.so -printf '%h\n'):$LD_LIBRARY_PATH

export CLANG_ASAN_LIB=$(find /opt -name libclang_rt.asan-x86_64.so)
export HIP_ASAN_LIB=$(find /opt -wholename *lib/asan/libamdhip64.so)

# Environment variables are set in test_asan_wrapper.py (matching CI behavior)
# The wrapper runs test_asan.py in a subprocess

ASAN_OPTIONS=detect_leaks=0,alloc_dealloc_mismatch=0 \
LD_PRELOAD=$CLANG_ASAN_LIB:$HIP_ASAN_LIB python test_asan_wrapper.py
