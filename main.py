import os
import sys
from src.converter import convert_pdf_to_markdown
# HUOM: Lisätty unload_model importtiin
from src.translator import process_markdown_translation, unload_model

def main():
    INPUT_DIR = "input"
    OUTPUT_CONVERTED = "output/1_converted"
    OUTPUT_TRANSLATED = "output/2_translated"
    
    # Etsi PDF
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".pdf")]
    if not files:
        print("❌ Ei PDF-tiedostoja input-kansiossa!")
        return
    
    pdf_path = os.path.join(INPUT_DIR, files[0])
    pdf_filename = os.path.splitext(files[0])[0]
    print(f"🚀 Käsitellään: {files[0]}")
    
    # KÄYTETÄÄN TRY-FINALLY RAKENNETTA MUISTIN VAPAUTUKSEEN
    try:
        # --- VAIHE 1: MUUNNOS ---
        expected_md_path = os.path.join(OUTPUT_CONVERTED, pdf_filename, f"{pdf_filename}.md")
        md_path = None
        
        if os.path.exists(expected_md_path):
            print(f"✅ Löydettiin valmis Markdown-muunnos.")
            print("⏩ Hypätään OCR-vaiheen yli.")
            md_path = expected_md_path
        else:
            print("-" * 30)
            print("VAIHE 1: Muunnetaan PDF Markdowniksi (OCR)...")
            # Varmistetaan että GPU on tyhjä ennen raskasta OCR:ää
            unload_model() 
            md_path = convert_pdf_to_markdown(pdf_path, OUTPUT_CONVERTED)
        
        # --- VAIHE 2: KÄÄNNÖS ---
        if md_path and os.path.exists(md_path):
            print("-" * 30)
            print("VAIHE 2: Käännetään tekoälyllä suomeksi...")
            
            output_filename = os.path.basename(md_path).replace(".md", "_FI.md")
            final_path = os.path.join(OUTPUT_TRANSLATED, output_filename)
            
            process_markdown_translation(md_path, final_path)
        else:
            print("❌ Muunto epäonnistui tai tiedostoa ei löydy.")
            
    except KeyboardInterrupt:
        print("\n🛑 Käyttäjä keskeytti toiminnon.")
    except Exception as e:
        print(f"\n❌ Odottamaton virhe: {e}")
    finally:
        # TÄMÄ AJETAAN AINA, ONNISTUI TAI EI
        print("-" * 30)
        unload_model()
        print("🏁 Ohjelma suoritettu.")

if __name__ == "__main__":
    main()