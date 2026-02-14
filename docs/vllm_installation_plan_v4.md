# vLLM Installation Plan (The Golden Edition) - Version 4.0

**Objective**: Run Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8 on a low-RAM mining rig (Pentium G4400, 16GB RAM, 8x GPUs on PCIe 1x) with 100% stability using the vLLM V1 Engine.

## 1. Final Evolution Log (v3 → v4)

In Version 3.0, we were considering the V0 engine for stability. However, after fixing the system toolchain and optimizing memory, we successfully stabilized the **V1 Engine**, which provides better performance and future-proofing.

### Critical Discoveries & Fixes:
1.  **Toolchain Gap**: The "JIT failed" errors were caused by missing development headers. Solution: Installed `python3-dev` and `libnuma-dev`.
2.  **The "Silent OOM"**: Even with huge swap, the V1 engine crashed at 100% loading because it tried to allocate a massive KV Cache (utilization 0.90). Solution: Reduced `gpu-memory-utilization` to **0.85**.
3.  **PCIe Bottleneck**: With PCIe 1x lanes with HHD Swap, the "Graph Capture" and initialization phases are silent and take **~15-20 minutes**. Patience is required.

---

## 2. System Optimization (One-time Setup)

### Linux Swap Configuration
For 80GB models on 16GB RAM, a fast and large swap is non-negotiable.
```bash
# We created a 128GB native swap file on the root partition
sudo fallocate -l 128G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Compiler Toolchain
Ensures vLLM can compile specialized kernels at runtime.
```bash
sudo apt update
sudo apt install -y build-essential python3-dev libnuma-dev pkg-config
```

---

## 3. Final Stable Configuration

### [start_vllm.sh](file:///home/seiya/projects/vllm/start_vllm.sh)
The "Magic Numbers" that stopped the crashes:
```bash
#!/bin/bash
export VLLM_USE_V1=1 # V1 is now stable!
export LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LIBRARY_PATH

nohup systemd-run --scope -p MemoryMax=90% \
    python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096 \
    --max-num-seqs 32 \
    --swap-space 1 \
    --trust-remote-code \
    --port 8000 > vllm.log 2>&1 &
```

---

## 4. Operational Expectations
- **Model Loading**: ~28 minutes.
- **Initialization (Silent Phase)**: ~15-20 minutes.
- **Prompt Throughput**: ~4.0 tokens/s.
- **Generation Throughput**: ~4-5 tokens/s.
- **Memory Profile**:
    - **Physical RAM**: Used ~7.5GB - 13GB (Fluctuates during init).
    - **Swap**: Used ~11-15GB.
    - **GPU VRAM**: Used ~9GB per card.

## 5. Troubleshooting
- **If JIT fails again**: Reboot the system to clear memory fragmentation.
- **If Connection Refused**: Wait longer. The "Application startup complete" log is the only signal of readiness.

**Status**: Verified Stable & Tested.
