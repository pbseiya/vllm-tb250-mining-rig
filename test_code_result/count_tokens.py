import requests
import json

API_URL = "http://localhost:8000/v1/tokenize" # assuming vLLM has this endpoint
MODEL = "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8"

def count_tokens(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # vLLM tokenize endpoint usually takes "prompt"
        payload = {"model": MODEL, "content": text}
        # Note: newer vLLM might use /v1/tokenize with 'content' or 'prompt'
        # Let's try 'content' first
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            return len(response.json().get("tokens", []))
        else:
            # Try 'prompt' if 'content' fails
            payload = {"model": MODEL, "prompt": text}
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                return len(response.json().get("tokens", []))
            
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    files = ["test_code_result/cat_novel_final.txt", "test_code_result/cat_novel_thai_refined.txt"]
    for f in files:
        print(f"Token count for {f}: {count_tokens(f)}")
