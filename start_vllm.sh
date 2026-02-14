#!/bin/bash

# Configuration for PCIe 1x Risers
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_ASYNC_ERROR_HANDLING=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn
# export VLLM_USE_V1=0
export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Activate Environment
source /home/seiya/projects/vllm/vllm-env/bin/activate

# Launch Safety Information
echo "Starting vLLM with Systemd Scope Safety..."
echo "- MemoryMax: 90%"
echo "- PCIe P2P: Disabled"

# Run with Systemd Scope (Priority and Grouping only)
systemd-run --user --scope \
    python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096 \
    --max-num-seqs 32 \
    --swap-space 1 \
    --trust-remote-code \
    --port 8000
