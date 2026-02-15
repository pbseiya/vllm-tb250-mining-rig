# vLLM Experiment Plan - Version 5.0 (Extended Context)

**Objective**: Increase `max-model-len` to **8192** for Qwen2.5-72B on 16GB RAM hardware.

## 🛠 Proposed Configuration Changes
To accommodate the larger context (which increases KV Cache size), we must tighten other memory constraints:

| Parameter | Old (Safe) | New (Experiment) | Rationale |
| :--- | :--- | :--- | :--- |
| `max-model-len` | 4096 | **8192** | Double the context for longer conversations. |
| `gpu-memory-utilization` | 0.85 | **0.80** | Reduce GPU reservation to give system more headroom. |
| `max-num-seqs` | 32 | **16** | Reduce parallel requests to save system RAM. |
| `Engine` | V1 (Stable) | **V1 (Experimental)** | Stick with V1 as requested for better performance. |

## 🚀 Execution Steps
1. **Update Script**: `start_vllm.sh` has been updated with the new parameters.
2. **Reboot**: A clean reboot is required to clear RAM fragmentation and ensure a successful Graph Capture.
3. **Patience**: The "Silent Phase" (Graph Capture) may increase from 20 minutes to **~30-40 minutes**.

## ⚠️ Risk Assessment
- **High Risk of OOM**: The larger context might exceed the 16GB RAM limit during the final stage of initialization.
- **Performance Drop**: Swapping may increase due to higher memory pressure.

**Status**: Ready for Reboot.
