# ASPLOS-26-AE

## Setup

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone submodules

```bash
git submodule init && git submodule update
```

### AMD Docker Environment

Start the Docker container:

```bash
./start_docker_rocm_asan.sh
docker attach rocm_asan
```

Install dependencies (triton, triton-viz, and project):

```bash
cd setup_amd
./install_envs.sh
```

Activate the environment:

```bash
source /opt/venv/bin/activate
```

### Test Address Sanitizer

To verify the address sanitizer is correctly installed, run:

```bash
./run_asan_test.sh
```

This test intentionally triggers an out-of-bounds access. If ASAN is working correctly, it will detect and report the memory violation.

### CUDA Environment

```bash
uv venv .venv
uv sync --extra cuda
source .venv/bin/activate
```
