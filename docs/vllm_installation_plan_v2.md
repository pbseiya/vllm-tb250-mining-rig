# vLLM Installation Plan (High-Capacity Safety Edition) - Version 2.0

**Objective**: Safely install and run Qwen2.5-72B-Instruct-GPTQ-Int8 on a 16GB RAM machine using a 128GB Swap file and specialized safety layers.

## 1. System Evolution & Learning (v1 → v2)

In Version 1.0, we used a restrictive `MemoryMax=90%` cgroup limit. During the loading of the 72B model, we discovered that this limit was too aggressive for the "Model Mapping" phase, causing an immediate crash. 

**Improvements in v2.0**:
- **Removed Restrictive Cgroups**: We removed `-p MemoryMax=90%` from `systemd-run`.
- **Reasoning**: The 72B model requires significant virtual memory mapping upfront. By removing the process-level cap, we allow the model to utilize the **128GB Swap File** freely.
- **Safety Guarantee**: We now rely on **EarlyOOM** as the primary "System Watchdog." If total system RAM falls below 5%, EarlyOOM will kill the vLLM process *before* the OS freezes, ensuring the machine remains reachable via SSH.

## 2. Updated Safety Architecture

| Layer | Tool | Action | Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Memory** | **128GB Native Swap** | Absorbs ~80GB of model weights. | Prevent OOM on 16GB physical RAM. |
| **System Watchdog** | **EarlyOOM** | Kills vLLM if RAM < 5%. | Prevent total system freeze/lockout. |
| **Process Manager** | **Systemd Scope** | Groups processes & sets OOM priority. | Easy management and clean cleanup. |
| **Interconnect** | **NCCL Flags** | Disables P2P and IB. | Stability on PCIe 1x Risers. |

## 3. Implementation Steps

### 3.1 Swap & Safety Configuration
```bash
# 1. Create 128GB Swap (Permanent)
sudo fallocate -l 128G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 2. Configure EarlyOOM (Watchdog)
sudo apt update && sudo apt install -y earlyoom
# Set to prefer killing vLLM and avoid killing SSH
sudo sed -i 's/^EARLYOOM_ARGS=.*/EARLYOOM_ARGS="-r 5 -m 5 --avoid \x27(^| )(ssh|sshd|bash|zsh)( |$)\x27 --prefer \x27(^| )(python3|vllm)( |$)\x27"/' /etc/default/earlyoom
sudo systemctl restart earlyoom
```

### 3.2 vLLM Installation (via uv)
```bash
# Install uv (Fastest Python Package Manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Setup Isolated Environment
uv venv vllm-env --python 3.10
source vllm-env/bin/activate
uv pip install vllm
```

### 3.3 Optimized Startup Script (`start_vllm.sh`)
```bash
#!/bin/bash
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_ASYNC_ERROR_HANDLING=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn

source /home/seiya/projects/vllm/vllm-env/bin/activate

# Launch via Systemd Scope (No restrictive MemoryMax, relying on EarlyOOM)
systemd-run --user --scope \
    python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192 \
    --max-num-seqs 64 \
    --swap-space 1 \
    --trust-remote-code \
    --port 8000
```

## 4. Verification & Monitoring
- **Check Progress**: `tail -f vllm.log`
- **Check Disk Usage**: `du -shL ~/.cache/huggingface/hub/`
- **Check Memory**: `free -h` and `swapon --show`
- **Final Test**: `curl http://localhost:8000/v1/models`
