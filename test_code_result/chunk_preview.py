import os

def split_text_into_chunks(text, chunk_size=4000, overlap=500):
    """
    แบ่งข้อความออกเป็นส่วนๆ (Chunks) โดยมีการซ้อนทับกัน (Overlap)
    เพื่อให้ AI เห็นบริบทที่ต่อเนื่องกัน
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # คำนวณจุดสิ้นสุดของ Chunk
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # เลื่อนจุดเริ่มต้นกลับไปตามระยะ Overlap เพื่อให้ Chunk ถัดไปมีเนื้อหาเดิมติดไปด้วย
        start += (chunk_size - overlap)
        
        # ป้องกัน Infinite Loop ถ้า overlap >= chunk_size
        if overlap >= chunk_size:
            break
            
    return chunks

def preview_chunks():
    source_file = "test_code_result/cat_novel_final.txt"
    if not os.path.exists(source_file):
        print("❌ ไม่พบไฟล์ต้นฉบับ")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # ตั้งค่าทดสอบ: Chunk ละ 1000 ตัวอักษร ซ้อนทับ 200 ตัวอักษร
    chunks = split_text_into_chunks(content, chunk_size=1000, overlap=200)
    
    print(f"📊 ต้นฉบับยาว: {len(content)} ตัวอักษร")
    print(f"📦 แบ่งได้ทั้งหมด: {len(chunks)} Chunks\n")
    
    for i, chunk in enumerate(chunks):
        print(f"--- [Chunk {i+1}] (ยาว {len(chunk)} ตัวอักษร) ---")
        # แสดงเฉพาะต้นและท้ายของ Chunk ให้ดูรอยต่อ
        print(f"เริ่ม: {chunk[:50]}...")
        print(f"จบ  : ...{chunk[-50:]}\n")

if __name__ == "__main__":
    preview_chunks()
