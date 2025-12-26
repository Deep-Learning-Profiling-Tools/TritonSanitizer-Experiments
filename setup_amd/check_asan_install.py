#!/usr/bin/env python3
import os
os.environ['TRITON_ENABLE_ASAN'] = '1'
import triton
import triton.language as tl
import torch

@triton.jit
def test_kernel(x_ptr):
    tl.store(x_ptr, 1.0)

x = torch.zeros(1, device='cuda')
test_kernel[(1,)](x)
print('Kernel compiled successfully with ASAN:', os.environ.get('TRITON_ENABLE_ASAN'))
