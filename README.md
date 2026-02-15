# vLLM Safe-Launch: Qwen2.5-72B (8-bit)

This project provides a specialized environment and startup configuration for running the **Qwen2.5-72B-Instruct-GPTQ-Int8** model on a mining rig with specific hardware constraints.

## 🖥️ Hardware Specifications

| Component | Detail | Impact on vLLM |
| :--- | :--- | :--- |
| **CPU** | Intel Pentium G4400 (2 Cores / 2 Threads) | Slow model loading & pre-fill. |
| **System RAM** | 16 GB DDR4 | Insufficient for 72B; requires 128GB Swap. |
| **GPU** | **8x NVIDIA RTX 3060 (12GB each)** | 96GB Total VRAM; fits 8-bit model. |
| **Interconnect** | **PCIe 1x Risers** | High latency; requires `NCCL_P2P_DISABLE=1`. |
| **OS** | Linux (Ubuntu/Zsh) | Native Ext4 Swap support. |

## 🚀 Quick Start

To launch the vLLM server with all safety layers enabled:

```bash
./start_vllm.sh
```

The server will be available at `http://localhost:8000/v1`.

### 🌐 Secure Remote Access (Tailscale)
If you are connecting from outside your home network, use your **Tailscale IP**:
```bash
# Example:
curl http://100.111.46.25:8000/v1/chat/completions
```

## 🛡️ Safety Architecture

Due to the limited System RAM (16GB) and slow interconnects, several safety layers have been implemented:

1.  **128GB Native Swap**: A dedicated swap file on the HDD (ext4) allows the ~80GB model to load safely into vitual memory without deadlocking.
2.  **EarlyOOM Watchdog**: A system-level service that monitors memory usage. It will automatically kill the vLLM process if physical RAM falls below 5%, preventing a total system freeze.
3.  **PCIe 1x Optimization**: Specialized NCCL flags (`NCCL_P2P_DISABLE=1`) are set in the startup script to prevent hangs on hardware using PCIe 1x risers.
4.  **Resource Grouping**: Launched via `systemd-run --scope` to ensure proper process grouping and cleanup.

## ⚠️ Expectations & Critical Information (MUST READ)

Running a 72B model on this hardware is an "extreme" task. Please be aware of the following:

1.  **Long Startup Time (~45-50 Minutes)**:
    *   **Phase 1: Model Loading (~30 mins)**: Shards are loaded from disk. You will see progress bars.
    *   **Phase 2: Graph Capture (~15-20 mins)**: **CRITICAL.** The logs will stop moving. It will look like it has crashed or hung. **DO NOT KILL IT.** It is performing silent GPU optimizations.
2.  **CPU at 100% is NORMAL**:
    *   Even when idle, the CPU will show 100% usage. This is due to vLLM workers actively polling the GPUs for work (Busy-Waiting).
3.  **Memory Management**:
    *   **Total System RAM is only 16GB**. The model weighs 80GB+.
    *   We use **128GB Swap** and `gpu-memory-utilization 0.85`. Do not increase this value, or you will face an instant OOM (Out Of Memory) crash.

## 📂 Project Structure

- `start_vllm.sh`: The main entry point script with optimized parameters.
- `vllm-env/`: Python environment managed by `uv`.
- `docs/`: 
  - `vllm_installation_plan_v4.md`: **Final Stable Plan** (The recommended reference).
- `vllm.log`: Active server logs.

## 🛠️ Monitoring

- **Check Server Logs**: `tail -f vllm.log`
- **Check Memory/Swap**: `free -h` or `swapon --show`
- **Check Hardware**: `gpustat -i 1`

## 🧪 Testing the API

Once the model is loaded (`Application startup complete` appears in logs), you can test it with:

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8",
        "messages": [{"role": "user", "content": "Hello!"}]
    }'
```

### 🌊 Streaming (Real-time)
To see the AI response typing out in real-time (SSE), use the `"stream": true` parameter. 

**Recommended (Clean View):**
```bash
curl -N -s http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8",
        "messages": [{"role": "user", "content": "ขอวิธีทำมาม่าอร่อยสี่เมนู"}],
        "stream": true
    }' | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        data = line[6:].strip()
        if data == '[DONE]': break
        try:
            chunk = json.loads(data)
            content = chunk['choices'][0]['delta'].get('content', '')
            print(content, end='', flush=True)
        except: pass
print()
"
```
