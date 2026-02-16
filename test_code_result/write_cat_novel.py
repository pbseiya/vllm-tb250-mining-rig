# /// script
# dependencies = [
#   "openai",
# ]
# ///

import os
import sys
import json
import time
from openai import OpenAI

# Configuration
API_BASE = "http://localhost:8000/v1"
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8"
MAX_TOKENS_PER_PASS = 4000  # Leave some room for context/summaries

client = OpenAI(
    api_key="EMPTY",
    base_url=API_BASE,
)

def get_completion(messages, stream=True):
    """Helper to get completion from vLLM."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=stream,
        max_tokens=MAX_TOKENS_PER_PASS,
        temperature=0.8,
        stream_options={"include_usage": True} if stream else None
    )
    
    full_text = ""
    if stream:
        for chunk in response:
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                continue # Usage handled at the end
            if len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_text += content
    else:
        full_text = response.choices[0].message.content
        
    return full_text

def generate_full_novel():
    print(f"--- 🚀 เริ่มต้นการเขียนนิยายแบบ Multi-Pass (เป้าหมาย 10,000+ คำ) ---\n")
    
    # PASS 1: The Beginning
    print(f"--- [PASS 1: ปฐมบทอาณาจักรแมว] ---")
    pass1_prompt = """เริ่มเขียนนิยายมหากาพย์ 'Cats Domination' ตอนที่ 1: การล่มสลายของมนุษย์และการตื่นรู้ของกษัตริย์วิฬาร์ 
เน้นรายละเอียดการสร้างเมืองและเทคโนโลยีของแมว บรรยายให้เห็นภาพความยิ่งใหญ่"""
    
    messages = [
        {"role": "system", "content": "คุณคือนักเขียน Sci-Fi ระดับโลกที่เน้นรายละเอียดสูงมาก คุณต้องเขียนเป็นภาษาไทยที่สละสลวยเท่านั้น ห้ามใช้ภาษาอังกฤษเด็ดขาด"},
        {"role": "user", "content": pass1_prompt}
    ]
    
    part1_text = get_completion(messages)
    
    # PASS 2: Summarization & Connection
    print(f"\n\n--- 🧠 กำลังวิเคราะห์เนื้อหาเพื่อเตรียมเขียนตอนต่อไป... ---")
    summary_prompt = f"จากเนื้อหาบทที่ 1 นี้: \n\n{part1_text[:2000]}...\n\nจงสรุปใจความสำคัญเป็นภาษาไทยสั้นๆ และร่างพล็อตตอนที่ 2 เป็นภาษาไทยเพื่อเขียนต่อให้ตื่นเต้นที่สุด"
    
    summary_messages = [
        {"role": "system", "content": "สรุปเนื้อหาเป็น Synopsis ภาษาไทย และร่างแผนการเขียนบทถัดไปเป็นภาษาไทยเท่านั้น"},
        {"role": "user", "content": summary_prompt}
    ]
    
    summary_data = get_completion(summary_messages, stream=False)
    print(f"\n[Summary Applied]: {summary_data[:200]}...")

    # PASS 3: The Mid-Core
    print(f"\n--- [PASS 2: ศึกชิงบัลลังก์ขนปุย] ---")
    pass2_prompt = f"จากเรื่องที่สรุปมาดังนี้: {summary_data}\n\nจงเขียนตอนที่ 2 ต่อให้จบและเข้มข้นที่สุด โดยใช้ภาษาไทยที่ต่อเนื่องและแนบเนียนที่สุด ห้ามสลับเป็นภาษาอังกฤษ"
    
    messages_pass2 = [
        {"role": "system", "content": "คุณคือนักเขียน Sci-Fi เขียนต่อจากสรุปที่ให้มาอย่างแนบเนียน โดยใช้ภาษาไทย 100%"},
        {"role": "user", "content": pass2_prompt}
    ]
    
    part2_text = get_completion(messages_pass2)

    print(f"\n\n--- ✅ การรวมเล่มเสร็จสิ้น! ---")
    total_length = len(part1_text) + len(part2_text)
    print(f"จำนวนตัวอักษรทั้งหมด: {total_length} (ประมาณ {total_length // 2} tokens)")
    print(f"ระบบได้สร้างไฟล์ 'cat_novel_final.txt' เรียบร้อยแล้ว")

    # Save to file
    with open("cat_novel_final.txt", "w", encoding="utf-8") as f:
        f.write("# Cats Domination\n\n")
        f.write(part1_text)
        f.write("\n\n---\n\n")
        f.write(part2_text)

if __name__ == "__main__":
    generate_full_novel()
