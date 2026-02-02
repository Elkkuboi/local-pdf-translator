import ollama
import time
import os
import re

MODEL = "nemotron-3-nano:30b" 

def clean_text_garbage(text):
    """
    Kevyempi siivous. Poistaa vain ilmiselvät roskat, mutta säästää kaiken mikä voi olla tekstiä.
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # SÄILYTÄ KUVAT (tämä oli aiemmin jo korjattu, pidetään se)
        if stripped.startswith("![") or stripped.startswith("[!["):
            cleaned_lines.append(line)
            continue
            
        # Poistetaan vain lyhyet roskarivit. 
        # Jos rivi on pitkä (yli 100 merkkiä), se on todennäköisesti oikeaa tekstiä
        # vaikka siinä olisi sana "Subscribe".
        garbage_words = ["Subscribe", "Join", "Like +", "Discuss", "Privacy Policy", "Sign up"]
        if any(x in stripped for x in garbage_words) and len(stripped) < 80:
            continue
            
        # Poistetaan pelkät numerot (esim. sivunumerot), mutta ei jos siinä on tekstiä
        if re.match(r'^[\d\W_]+$', stripped):
            continue
            
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)

def translate_chunk(text, chunk_index, total_chunks):
    # Siivotaan pahimmat, mutta varovasti
    clean_text = clean_text_garbage(text)
    
    if len(clean_text.strip()) < 5:
        return text # Palautetaan alkuperäinen jos siivous meni liian pitkälle

    # --- PÄIVITETTY PROMPTI: VÄHEMMÄN AGGRESSIIVINEN ---
    prompt = f"""
    Käännä oheinen englanninkielinen teksti suomeksi.
    
    OHJEET:
    1. Tärkein tavoite: ÄLÄ HUKKAA LAUSEITA. Käännä kaikki leipäteksti.
    2. Jos et ole varma onko jokin otsikko tai metadataa, KÄÄNNÄ SE SILTI.
    3. Säilytä kuvatagit (![](...)) ja koodilohkot (```) sellaisenaan.
    4. Älä käännä koodin sisällä olevia komentoja.
    5. Suomenna sujuvasti, mutta pysy uskollisena alkutekstille.
    
    Käännettävä teksti:
    {clean_text}
    """
    
    try:
        response = ollama.chat(model=MODEL, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        print(f"\n❌ Virhe lohkossa {chunk_index}: {e}")
        return text

def create_smart_chunks(text, max_chars=2500): 
    # Pienensin chunk-kokoa hieman (3000 -> 2500), jotta malli pysyy tarkempana
    # eikä "unohda" kääntää osia pitkän pätkän alusta tai lopusta.
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

def process_markdown_translation(input_file, output_file):
    print(f"🤖 Aloitetaan käännös mallilla {MODEL} (Sallivampi moodi)...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📦 Optimoidaan lohkoja...")
    chunks = create_smart_chunks(content)
    
    translated_chunks = []
    total = len(chunks)
    
    print(f"📊 Käännettäviä lohkoja: {total}")
    
    start_time = time.time()
    
    for i, chunk in enumerate(chunks):
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1) if i > 0 else 0
        remaining = (total - (i + 1)) * avg_time
        remaining_min = int(remaining // 60)
        
        print(f"⏳ Käännetään {i+1}/{total} | Arvio jäljellä: {remaining_min} min...", end='\r')
        
        translated = translate_chunk(chunk, i, total)
        if translated:
            translated_chunks.append(translated)
        
        if i % 5 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_chunks))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated_chunks))
    
    print(f"\n✅ Käännös valmis! Tallennettu: {output_file}")


def unload_model():
    """
    Pakottaa Ollaman vapauttamaan GPU-muistin heti.
    """
    print("🧹 Vapautetaan GPU-muisti...")
    try:
        # Lähetetään tyhjä pyyntö, jossa keep_alive on 0. 
        # Tämä kertoo Ollamalle: "Unohda malli heti".
        ollama.generate(model=MODEL, prompt="", keep_alive=0)
        print("✅ GPU-muisti vapautettu.")
    except Exception as e:
        print(f"⚠️ Muistin vapautus ei onnistunut (Ollama ehkä jo kiinni): {e}")