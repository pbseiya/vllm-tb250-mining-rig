# Benchmark Results: 8192 Context Performance

- **Date**: 2026-02-15 07:41 (Local Time)
- **Model**: Qwen2.5-72B-Instruct-GPTQ-Int8
- **Engine**: vLLM V1
- **Hardware**: 8x RTX 3060 (PCIe 1x), 16GB RAM, 128GB Swap
- **Configuration**: `--gpu-memory-utilization 0.90` (Optimized for Context)

## 📊 Performance Summary

| Test Category | TTFT (s) | Throughput (Tokens/s) | Total Time (s) | Total Tokens |
| :--- | :--- | :--- | :--- | :--- |
| **Short** | 89.27* | 5.33 | 99.02 | 52 |
| **Medium** | 5.21 | 9.83 | 34.21 | 285 |
| **Thai-Test** | 3.55 | 9.29 | 56.31 | 490 |
| **Extreme-Fiction** | 13.23 | 9.57 | 415.97 | 3856 |

*\*Short TTFT includes initial compilation/warm-up time after server startup.*

## ⏱️ Startup & Preparation Time
- **Start Time**: 06:33 (Initial Command)
- **Ready Time**: 07:32 (Application Startup Complete)
- **Total Startup Duration**: **59 นาที**
    - *Model Shard Loading*: 26 นาที
    - *Graph Capture & Memory Allocation*: 33 นาที

*\*แนะนำให้เตรียมระบบล่วงหน้าอย่างน้อย 1 ชั่วโมงหากต้องการใช้ 8192 Context*

## ⚙️ System Metrics (During Inference)
- **VRAM Utilization**: ~95% across all 8 GPUs (Intentional)
- **RAM Used**: ~14.2GB (High utilization, but stable)
- **Swap Used**: ~9.3GB
- **CPU Load**: ~12.6 (Stable inference)

## 📝 Observations
- **Success Over 4096**: Successfully doubled the context window to 8192 tokens on the same 16GB RAM hardware.
- **Throughput Consistency**: Maintains a high 9.5 - 10.5 TPS, comparable to the 4096 baseline (~11-12 TPS).
- **Latency**: TTFT remains under 14s for long sequences, which is excellent for a 72B model.
- **Stability**: The 90% utilization safety net prevented OOM during the Graph Capture phase.

## 📁 Files
- **Story**: [cat_domination_story_8192.txt](file:///home/seiya/projects/vllm/docs/benchmarks/8192/cat_domination_story_8192.txt)
