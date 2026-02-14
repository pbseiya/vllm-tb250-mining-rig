# Benchmark Results: 4096 Context Baseline

- **Date**: 2026-02-15 04:13 (Local Time)
- **Model**: Qwen2.5-72B-Instruct-GPTQ-Int8
- **Engine**: vLLM V1
- **Hardware**: 8x RTX 3060 (PCIe 1x), 16GB RAM, 128GB Swap

## 📊 Performance Summary

| Test Category | TTFT (s) | Throughput (Tokens/s) | Total Time (s) | Total Tokens |
| :--- | :--- | :--- | :--- | :--- |
| **Short** | 1.28 | 12.70 | 5.29 | 51 |
| **Medium** | 1.36 | 12.19 | 22.53 | 258 |
| **Thai-Test** | 1.54 | 11.93 | 44.39 | 511 |
| **Extreme-Fiction** | 2.69 | 11.22 | 350.05 | 3899 |

## ⚙️ System Metrics (Idle during Start)
- **RAM Used**: ~13GB (Including Swap usage)
- **CPU Load**: High (Busy-waiting is active)

## 📝 Observations
- The **V1 Engine** delivers exceptionally high throughput (~12 TPS) even on PCIe 1x risers once generation begins.
- **Latency (TTFT)** is very manageable at under 1.6s.
- This serves as the stable baseline before testing the **8192 context** expansion.

## 📁 Files
- **Story**: [cat_domination_story_4096.txt](file:///home/seiya/projects/vllm/docs/benchmarks/4096/cat_domination_story_4096.txt)
