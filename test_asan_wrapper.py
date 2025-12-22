#!/usr/bin/env python3
"""
Wrapper script to run ASAN test in subprocess, matching CI behavior.
This sets environment variables and spawns the actual test in a subprocess.
"""

import os
import subprocess
import sys

import triton


def is_hip():
    return triton.runtime.driver.active.get_current_target().backend == "hip"


def main():
    if not is_hip():
        print("Not running on HIP backend, skipping ASAN test")
        return

    # Set environment variables (same as test_address_sanitizer.py)
    os.environ["HSA_DISABLE_FRAGMENT_ALLOCATOR"] = "1"
    os.environ["AMD_PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
    os.environ["PYTORCH_NO_HIP_MEMORY_CACHING"] = "1"
    os.environ["TRITON_ENABLE_ASAN"] = "1"
    os.environ["HSA_XNACK"] = "1"
    os.environ["AMDGCN_USE_BUFFER_OPS"] = "0"

    print("Running ASAN test in subprocess...")
    print("=" * 60)

    # Run the actual test in a subprocess (matching CI behavior)
    out = subprocess.Popen(
        ["python", "test_asan.py"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    stdout = out.stdout.read().decode()
    stderr = out.stderr.read().decode()

    print("=== STDOUT ===")
    print(stdout)
    print()
    print("=== STDERR ===")
    print(stderr)
    print()
    print("=" * 60)

    # Check for expected ASAN output
    has_asan_report = "Begin function __asan_report" in stdout
    has_heap_overflow = "heap-buffer-overflow" in stderr

    print("=== ASAN Check ===")
    print(f"Contains '__asan_report' in stdout: {has_asan_report}")
    print(f"Contains 'heap-buffer-overflow' in stderr: {has_heap_overflow}")

    if has_asan_report and has_heap_overflow:
        print("\n✓ ASAN test PASSED")
        sys.exit(0)
    else:
        print("\n✗ ASAN test FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
