#!/usr/bin/env python3
"""
Pytest plugin to enable Triton kernel timing profiler.

This plugin automatically enables the Triton profiler when ENABLE_TRITON_PROFILER=1
is set in the environment.

Usage:
    pytest -p pytest_triton_profiler test_file.py
    or
    ENABLE_TRITON_PROFILER=1 pytest -p pytest_triton_profiler test_file.py
"""
import os
import sys
import pytest


def pytest_configure(config):
    """
    Called after command line options have been parsed and all plugins
    and initial conftest files been loaded.
    """
    # Check if profiling should be enabled
    if os.getenv("ENABLE_TRITON_PROFILER", "0") == "1":
        # Add the project root directory to Python path (parent of utils)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)

        # Import and enable the profiler
        try:
            from utils.triton_profiler import enable_triton_kernel_timing
            enable_triton_kernel_timing()
            print("[pytest-triton-profiler] Triton kernel timing enabled via pytest plugin")
        except ImportError as e:
            print(f"[pytest-triton-profiler] Warning: Could not import triton_profiler: {e}", file=sys.stderr)


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    """
    # Optionally disable profiling on exit
    if os.getenv("ENABLE_TRITON_PROFILER", "0") == "1":
        try:
            from utils.triton_profiler import disable_triton_kernel_timing
            disable_triton_kernel_timing()
        except ImportError:
            pass
