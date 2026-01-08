#!/bin/bash
set -e

source /opt/venv/bin/activate

pip uninstall -y triton pytorch-triton-rocm

cd ../submodules/triton/
python -m pip install -r python/requirements.txt
python -m pip install -r python/test-requirements.txt

python -m pip install -e . --no-build-isolation -v

cd ../triton-viz/
python -m pip install -e .

cd ../..
python -m pip install -e .
