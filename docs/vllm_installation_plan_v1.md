# vLLM Installation Plan (Safety First Edition) - Version 1.0

**Objective**: Safely install and run Qwen2.5-72B-Instruct-GPTQ-Int8 on a resource-constrained machine without freezing the OS.

## 1. System Context & Risk Assessment

| Component | Specification | Bottleneck / Risk | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **CPU** | Intel Pentium G4400 (2 Cores) | Very Slow | Patience; reduce `max-num-seqs`. |
| **RAM** | 16 GB DDR4 | **CRITICAL** (Too low for 72B) | **128GB Native Swap** on HDD/Root. |
| **GPU** | 8x RTX 3060 (12GB) | Riser PCI-E 1x Latency | Disable P2P/IB; Increase timeouts. |
| **Storage** | 240GB SSD (Win), 2TB HDD (Linux) | I/O Speed | Use **Native Ext4 Swap** on Root Partition. |

## 2. Implementation Strategy

### Step 1: Memory Safety (The "Airbag")
We rejected using NTFS Swap due to deadlock risks. We chose **Native Ext4 Swap** on the Root Partition (`/`).

- **Action**: Create `/swapfile` (128GB).
- **Reason**: Ext4 is handled by the Kernel directly. It will not deadlock when RAM is full, unlike FUSE-based NTFS.

### Step 2: Process Safety (The "Emergency Brake")
To prevent the "Infinite Loading Loop" or System Hang:

1.  **EarlyOOM**:
    - **Trigger**: RAM < 5% AND Swap < 5%.
    - **Action**: `SIGTERM` / `SIGKILL` to vLLM process.
    - **Benefit**: Saves SSH and OS from freezing.
2.  **Systemd Cgroups** (Scope):
    - **MemoryMax=90%**: Hard limit. If vLLM exceeds this, it is killed instantly.
    - **OOMScoreAdjust=1000**: Tells Linux Kernel "If you need to kill someone, kill vLLM first, do not kill SSH".
    - **Zombie Process Prevention**: When the systemd scope is stopped/killed, it cleans up ALL child processes, preventing zombies.

### Step 3: PCIe Riser Safety (The "Speed Limiter")
To prevent hangs due to slow PCIe 1x connection:

1.  **Disable P2P**: `NCCL_P2P_DISABLE=1` prevents cards from trying to talk directly (which crashes on risers).
2.  **Disable IB**: `NCCL_IB_DISABLE=1` forces usage of system RAM/Network for communication.
3.  **Async Error Handling**: `NCCL_ASYNC_ERROR_HANDLING=1` ensures if a GPU times out, the process DIES instead of hanging forever.
4.  **Reduce Concurrency**: `max-num-seqs=64` reduces the load to prevent traffic jams on the PCIe bus.

### Step 4: Installation Method (The "Clean Room")
We chose **`uv`** over Anacoda/Pip.

- **Reason**:
    - **Speed**: `uv` is extremely fast.
    - **Isolation**: Creates a standalone venv independent of the system's Conda (avoiding conflicts).
    - **No Bloat**: Does not require installing heavyweight Conda packages.

## 3. Execution Commands (Copy-Paste Ready)

### 3.1 Setup Swap & Safety
```bash
# 1. Create 128GB Swap
sudo fallocate -l 128G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 2. Install EarlyOOM
sudo apt update && sudo apt install -y earlyoom
sudo sed -i 's/^EARLYOOM_ARGS=.*/EARLYOOM_ARGS="-r 5 -m 5 --avoid \x27(^| )(ssh|sshd|bash)( |$)\x27 --prefer \x27(^| )(python3|vllm)( |$)\x27"/' /etc/default/earlyoom
sudo systemctl restart earlyoom
```

### 3.2 Install vLLM via `uv`
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Setup Environment
uv venv vllm-env --python 3.10
source vllm-env/bin/activate
uv pip install vllm
```

### 3.3 Launch vLLM (Safe Mode)
```bash
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_ASYNC_ERROR_HANDLING=1

# Run with Systemd Limits
systemd-run --user --scope \
    -p MemoryMax=90% \
    -p MemorySwapMax=90% \
    -p OOMScoreAdjust=1000 \
    python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192 \
    --max-num-seqs 64 \
    --trust-remote-code \
    --port 8000
```

## 4. Verification Checklist
- [ ] `free -h` shows ~144GB Total Memory (RAM+Swap).
- [ ] `systemctl status earlyoom` is active.
- [ ] `curl http://localhost:8000/v1/models` returns model list.
