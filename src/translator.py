import ollama
import time
import os
import re
import sys

# Default configuration
DEFAULT_MODEL = "nemotron-3-nano:30b"

def unload_model(model_name=None):
    """
    Forces Ollama to release GPU memory immediately.
    """
    target_model = model_name if model_name else DEFAULT_MODEL
    print(f"[INFO] Unloading model '{target_model}' from GPU memory...")
    
    try:
        ollama.generate(model=target_model, prompt="", keep_alive=0)
        print("[SUCCESS] GPU memory released.")
    except Exception as e:
        print(f"[WARN] Failed to unload model: {e}")

def clean_text_garbage(text):
    """
    Pre-processes text to remove OCR artifacts.
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    garbage_words = ["Subscribe", "Join", "Like +", "Discuss", "Privacy Policy", "Sign up", "Cookies"]
    
    for line in lines:
        stripped = line.strip()
        
        # Keep image tags
        if stripped.startswith("![") or stripped.startswith("[!["):
            cleaned_lines.append(line)
            continue
            
        # Remove web garbage
        if any(x in stripped for x in garbage_words) and len(stripped) < 80:
            continue
            
        # Remove isolated numbers
        if re.match(r'^[\d\W_]+$', stripped):
            continue
            
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)

def translate_chunk(text, target_language, model_name, chunk_index):
    """
    Translates a single chunk.
    """
    clean_text = clean_text_garbage(text)
    
    if len(clean_text.strip()) < 5:
        return text 

    prompt = f"""
    You are an expert academic translator specializing in computer science and mathematics.
    Translate the following text into {target_language}.
    
    STRICT GUIDELINES:
    1. GOAL: Translate all body text fluently. Do not summarize.
    2. AMBIGUITY: If a line looks like metadata, translate it anyway.
    3. PRESERVATION: 
       - DO NOT translate code blocks, variable names, or LaTeX equations (e.g., $x$, \\sum).
       - DO NOT translate Image tags like ![](...). Keep them exactly as is.
    4. TONE: Use professional, academic {target_language}.
    
    TEXT TO TRANSLATE:
    {clean_text}
    """
    
    try:
        response = ollama.chat(model=model_name, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        print(f"\n[ERROR] Translation failed in chunk {chunk_index}: {e}")
        return text

def create_smart_chunks(text, max_chars): 
    """
    Splits text into semantic chunks.
    Now accepts max_chars dynamically.
    """
    paragraphs = text.split('\n\n')
    current_chunk = []
    current_len = 0
    smart_chunks = []
    
    for p in paragraphs:
        if len(p) > max_chars:
            if current_chunk:
                smart_chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            smart_chunks.append(p)
            continue
            
        if current_len + len(p) < max_chars:
            current_chunk.append(p)
            current_len += len(p)
        else:
            smart_chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
            
    if current_chunk:
        smart_chunks.append("\n\n".join(current_chunk))
        
    return smart_chunks

def process_markdown_translation(input_file, output_file, target_language="Finnish", model_name=DEFAULT_MODEL, chunk_size=5000):
    """
    Main orchestration function.
    """
    print(f"[INFO] Starting translation engine using model: {model_name}")
    print(f"[INFO] Target Language: {target_language}")
    print(f"[INFO] Chunk Size: {chunk_size} chars")
    
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"[INFO] Optimizing text chunks (Smart Chunking)...")
    chunks = create_smart_chunks(content, max_chars=chunk_size)
    
    translated_chunks = []
    total = len(chunks)
    
    print(f"[INFO] Total text chunks to process: {total}")
    
    start_time = time.time()
    
    for i, chunk in enumerate(chunks):
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1) if i > 0 else 0
        remaining = (total - (i + 1)) * avg_time
        remaining_min = int(remaining // 60)
        
        print(f"[INFO] Translating chunk {i+1}/{total} | ETA: {remaining_min} min...", end='\r')
        
        translated = translate_chunk(chunk, target_language, model_name, i)
        
        if translated:
            translated_chunks.append(translated)
        
        if i % 5 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_chunks))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated_chunks))
    
    print(f"\n[SUCCESS] Translation complete! Saved to: {output_file}")