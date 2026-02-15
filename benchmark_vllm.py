import requests
import time
import json
import csv
import os
from datetime import datetime

# --- Configuration ---
API_URL = "http://localhost:8000/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8"
RESULTS_FILE = "docs/benchmarks/benchmark_results.csv"

# Prompts for testing
TEST_PROMPTS = [
    {"name": "Short", "text": "Explain quantum entanglement in 2 sentences."},
    {"name": "Medium", "text": "Write a short story about a robot learning to paint (approx 200 words)."},
    {"name": "Thai-Test", "text": "ช่วยอธิบายวิธีต้มมาม่าให้อร่อยที่สุดเป็นภาษาไทยหน่อย"},
    {"name": "Extreme-Fiction", "text": "เขียนนิยายแนว Fiction เรื่อง 'แมวจะครองโลก' โดยเน้นเนื้อหาที่เข้มข้นและจินตนาการล้ำเลิศ ขอความยาวที่สุดเท่าที่คุณจะทำได้ (เป้าหมายคือ 10,000 คำ)"},
]

def get_system_metrics():
    """Simple wrapper to get RAM and CPU load via shell."""
    try:
        with os.popen("free -m | grep Mem") as f:
            ram = f.read().split()[2] # Used RAM in MB
        with os.popen("uptime | awk '{print $(NF-2)}'") as f:
            load = f.read().strip().replace(",", "") # 1-min Load Avg
        return ram, load
    except:
        return "N/A", "N/A"

def run_benchmark(prompt_name, prompt_text, max_tokens=512):
    print(f"\n[Benchmarking] Category: {prompt_name}")
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": True,
        "max_tokens": max_tokens,
        "temperature": 0.8
    }

    start_time = time.time()
    ttft = 0
    total_tokens = 0
    full_response = ""
    
    ram_start, load_start = get_system_metrics()

    try:
        response = requests.post(API_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                if ttft == 0:
                    ttft = time.time() - start_time
                    print(f"  > Time to First Token (TTFT): {ttft:.2f}s")
                
                decoded_line = line.decode('utf-8').replace('data: ', '')
                if decoded_line == '[DONE]':
                    break
                
                try:
                    data = json.loads(decoded_line)
                    content = data['choices'][0]['delta'].get('content', '')
                    full_response += content
                    if content:
                        total_tokens += 1
                except:
                    continue

        end_time = time.time()
        total_time = end_time - start_time
        tps = total_tokens / (total_time - ttft) if (total_time - ttft) > 0 else 0
        
        print(f"  > Total Time: {total_time:.2f}s")
        print(f"  > Throughput (TPS): {tps:.2f} tokens/s")
        print(f"  > Total Tokens: {total_tokens}")

        # Save to CSV
        file_exists = os.path.isfile(RESULTS_FILE)
        with open(RESULTS_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Category", "TTFT", "TPS", "Total_Time", "Tokens", "RAM_Used_MB", "CPU_Load"])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                prompt_name,
                f"{ttft:.2f}",
                f"{tps:.2f}",
                f"{total_time:.2f}",
                total_tokens,
                ram_start,
                load_start
            ])
        
        # Save content for extreme fiction
        if prompt_name == "Extreme-Fiction":
            # Try to detect context length from payload
            ctx_len = payload.get("max_tokens", "unknown")
            content_file = f"docs/benchmarks/cat_domination_story_{ctx_len}.txt"
            with open(content_file, "w", encoding="utf-8") as f:
                f.write(full_response)
            print(f"  > Story saved to: {content_file}")

    except Exception as e:
        print(f"  [ERROR] {e}")

if __name__ == "__main__":
    print("=== vLLM Performance Benchmark Utility ===")
    print(f"Targeting: {MODEL}")
    for p in TEST_PROMPTS:
        m_tokens = 3900 if p["name"] == "Extreme-Fiction" else 512
        run_benchmark(p["name"], p["text"], max_tokens=m_tokens)
    print("\nBenchmark Complete! Results saved to docs/benchmarks/benchmark_results.csv")
