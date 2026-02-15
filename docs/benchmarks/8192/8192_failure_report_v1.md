# Experiment Report: Failure of 8192 Context Expansion

- **Date**: 2026-02-15 06:09 AM (Crash Time)
- **Target**: Qwen2.5-72B-Instruct-GPTQ-Int8
- **Context Length**: 8192
- **Hardware**: 16GB RAM, 128GB Swap, 8x RTX 3060 (96GB VRAM)

## ❌ Symptom: Out of Memory (OOM)
The server successfully loaded the model shards but failed during the **Graph Capture / Compilation** phase.

### Log Evidence:
- **05:12 AM**: Model weights successfully loaded (took 9.0 GiB of system RAM).
- **05:34 AM**: Torch compilation of initial graphs completed.
- **06:09 AM**: The process was **Killed** by the system.
- **Error**: `vllm.exceptions.VLLMValidationError` or kernel OOM killer.
- **Log Snippet**: `./start_vllm.sh: line 30: 3578 Killed systemd-run ...`

## 🔍 Root Cause Analysis
1. **System RAM Overhead**: The 72B model requires approximately 9GB of system RAM just for metadata and weights during loading.
2. **Graph Capture Intensity**: Compiling CUDA graphs for 8192 context across 8 GPUs creates a massive memory overhead for descriptors and temporary buffers.
3. **16GB Hard Limit**: On this specific hardware (2-core Pentium, 16GB RAM), the overhead for 8192 tokens + the model loader exceeds the available physical and virtual memory stability threshold during the build phase.

## 🏁 Conclusion & Recommendations
- **Golden Setting**: **4096 context length** is the stable maximum for a 72B model on 16GB RAM hardware.
- **Constraint**: Do not attempt 8192 context unless system RAM is upgraded to at least 32GB or 64GB.
- **Next Step**: Roll back to the `main` branch (4096 context) to maintain a functional server.
