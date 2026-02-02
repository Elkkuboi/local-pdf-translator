import os
import subprocess

def convert_pdf_to_markdown(input_path, output_base_dir):
    """
    Käyttää 'marker_single' komentoa PDF:n muuntamiseen Markdowniksi.
    """
    print(f"🔄 Aloitetaan konversio: {input_path}")
    
    # KORJAUS: Lisätty "--output_dir" lippu, koska uusin marker ei hyväksy
    # positiota ilman sitä.
    cmd = [
        "marker_single",
        input_path,
        "--output_dir", output_base_dir
    ]
    
    try:
        print(f"Suoritetaan komento: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"✅ Konversio valmis (Marker).")
        
        # Selvitetään markkerin luoma polku
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # Etsitään tiedostoa, koska marker voi luoda alikansion tai olla luomatta
        # riippuen versiosta.
        expected_subdir = os.path.join(output_base_dir, base_name)
        possible_paths = [
            os.path.join(output_base_dir, f"{base_name}.md"),           # Suoraan outputissa
            os.path.join(expected_subdir, f"{base_name}.md"),           # Alikansiossa
            os.path.join(expected_subdir, base_name, f"{base_name}.md") # Tupla-alikansiossa
        ]

        for p in possible_paths:
            if os.path.exists(p):
                return p
        
        # Jos ei löydy, tehdään haku
        print(f"⚠️ Tiedostoa ei löytynyt vakiopaikoista. Etsitään {output_base_dir}...")
        for root, dirs, files in os.walk(output_base_dir):
            for file in files:
                if file.endswith(".md") and base_name in file:
                    return os.path.join(root, file)
        
        return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Virhe konversiossa (Marker). Exit code: {e.returncode}")
        # Tulostetaan markerin help, jotta nähdään oikeat liput jos tämäkin hajoaa
        if e.returncode == 2:
            print("--- DEBUG: Markerin sallitut komennot: ---")
            subprocess.run(["marker_single", "--help"])
        return None