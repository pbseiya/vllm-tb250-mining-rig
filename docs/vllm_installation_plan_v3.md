# vLLM Installation Plan (Stable Engine Edition) - Version 3.0

**Objective**: Run Qwen2.5-72B on a mining rig (Pentium G4400, 16GB RAM, PCIe 1x) with maximum stability by bypassing JIT compilation.

## 1. Evolution Log (v2 → v3)

In Version 2.0, we optimized for memory safety (EarlyOOM). However, during the initial run, we encountered a **JIT Compilation Failure** with vLLM's new V1 Engine. The weak CPU and complex driver environment caused the runtime compilation of CUDA kernels to fail.

**Improvements in v3.0**:
- **Force V0 Engine**: We explicitly set `VLLM_USE_V1=0` to use the legacy, pre-compiled engine.
- **Reasoning**: The V0 engine is purely Python/C++ based and does not require runtime JIT compilation of kernels, making it far more robust for "non-standard" hardware like mining rigs.
- **Library Paths**: Added explicit `LIBRARY_PATH` exports to ensure `libcuda.so` is always found.

## 2. Finalized Safety Architecture

| Layer | Tool | Action | Purpose |
| :--- | :--- | :--- | :--- |
| **Engine** | **V0 (Legacy)** | **Disable JIT (`VLLM_USE_V1=0`)** | **Prevent compilation crashes on startup.** |
| **Memory** | **128GB Swap** | Absorbs ~80GB of model weights. | Prevent OOM on 16GB RAM. |
| **Watchdog** | **EarlyOOM** | Kills vLLM if RAM < 5%. | Prevent system lockups. |
| **Interconnect** | **NCCL Flags** | Disables P2P/IB. | Stability on PCIe 1x Risers. |

## 3. Implementation Steps

### 3.1 Swap & Safety (Unchanged)
```bash
# ... (Same as v2) ...
sudo fallocate -l 128G /swapfile
# ...
```

### 3.2 Optimized Startup Script (v3.0 Final)
The critical changes are the export variables at the top.

```bash
#!/bin/bash

# 1. Engine & Library Fixes (New in v3)
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_USE_V1=0   # Critical: Force V0 engine to bypass JIT compilation
export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 2. PCIe 1x Riser Safety
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_ASYNC_ERROR_HANDLING=1

# 3. Environment
source /home/seiya/projects/vllm/vllm-env/bin/activate

# 4. Launch (Systemd Scope)
echo "Starting vLLM (V0 Engine) with Systemd Scope Safety..."
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

## 4. Why V0 Engine?
The V1 engine attempts to optimize performance by compiling custom kernels at runtime. On a machine with:
1.  Pentium G4400 (Slow compilation)
2.  Complex library paths (Conda vs System)
3.  PCIe 1x Latency

This compilation is a point of failure. **V0 relies on pre-compiled binaries**, ensuring that if the driver is loaded, the model *will* load.

## 5. Verification
- **Check Engine**: Logs should NOT show "Initializing V1 Engine".
- **Check Progress**: `vmstat 1` should show heavy disk reads (`bi`) during loading.
