# Local PDF Translator (RTX 5090 Edition)

Tämä työkalu kääntää PDF:t suomeksi kahdessa vaiheessa:
1. **Marker** muuntaa PDF:n siistiksi Markdowniksi (säilyttää kaavat).
2. **Ollama** kääntää tekstin suomeksi (säilyttää LaTeXin).

## Asennus
1. Luo venv: `python3 -m venv venv`
2. Aktivoi: `source venv/bin/activate`
3. Asenna: `pip install -r requirements.txt`
4. Lataa malli: `ollama pull gemma2:27b`

## Käyttö
1. Laita PDF kansioon `input/`.
2. Aja: `python main.py`
