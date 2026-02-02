# Research Paper Translator v2.0

## Overview

Research Paper Translator is a local, privacy-focused pipeline designed to convert and translate academic PDF documents. It utilizes deep learning-based OCR (Optical Character Recognition) to extract structure, equations, and code blocks from PDFs, and subsequently uses local Large Language Models (LLMs) via Ollama to perform high-fidelity translations.

This tool is optimized for high-performance GPUs (e.g., NVIDIA RTX 4090/5090) and handles memory management dynamically to prevent OOM (Out of Memory) errors during heavy workloads.

### Key Features

* **Local Processing:** All data remains on your machine. No data is sent to external APIs.
* **High-Fidelity OCR:** Uses `marker-pdf` to convert PDFs to Markdown, preserving mathematical notation ($LaTeX$), code blocks, and images.
* **Smart Chunking:** Splits text based on semantic boundaries (paragraphs) rather than arbitrary character limits to ensure context retention.
* **Artifact Cleaning:** Automatically removes web scraping artifacts (headers, footers, navigation links) before translation.
* **Dynamic Resource Management:** Automatically loads and unloads LLM models from GPU memory to allow OCR and Inference phases to run without conflict.

---

## Prerequisites

* **OS:** Linux (Ubuntu 22.04+ recommended) or Windows via WSL2.
* **Python:** Version 3.10 or higher.
* **GPU:** NVIDIA GPU with at least 12GB VRAM recommended (24GB+ for larger models like `nemotron-3-nano:30b` or `gemma2:27b`).
* **Ollama:** Must be installed and running locally. [Download Ollama](https://ollama.com).

---

## Installation

1.  **Clone the repository**
    ```bash
    git clone <your-repo-url>
    cd research-paper-translator
    ```

2.  **Create a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    *(Ensure you have PyTorch installed with CUDA support before installing other requirements)*
    ```bash
    pip install marker-pdf ollama
    ```

4.  **Pull required LLM models**
    ```bash
    ollama pull nemotron-3-nano:30b
    # Optional: Pull lighter models for testing
    ollama pull llama3
    ```

---

## Usage

### Basic Usage

Place your PDF files in the `input/` directory.

To process the first found PDF using default settings (Finnish translation, Nemotron 30B model):

```bash
python main.py
```

### Advanced Usage via CLI

You can control the target language, model selection, and chunking parameters using command-line arguments.

**Syntax:**
```bash
python main.py [filename] [options]
```

**Examples:**

1.  **Translate a specific file to English:**
    ```bash
    python main.py paper.pdf --lang English
    ```

2.  **Use a specific model and force re-running OCR:**
    ```bash
    python main.py paper.pdf --model llama3 --force-ocr
    ```

3.  **Optimize for high-end GPUs (Larger chunk size):**
    If you have 24GB+ VRAM, you can increase the chunk size to process text faster.
    ```bash
    python main.py --chunk-size 6000
    ```

### Command Line Arguments

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `filename` | string | (Auto) | Specific PDF filename in `input/`. If omitted, picks first available PDF. |
| `--lang` | string | Finnish | Target language for translation. |
| `--model` | string | nemotron-3-nano:30b | The Ollama model tag to use. |
| `--chunk-size` | int | 5000 | Character limit per translation chunk. Higher values use more VRAM context. |
| `--force-ocr` | flag | False | Forces the pipeline to re-run the PDF-to-Markdown conversion phase. |

---

## Project Structure

```text
research-paper-translator/
├── input/                  # Place source PDF files here
├── output/
│   ├── 1_converted/        # Intermediate Markdown files (OCR output)
│   └── 2_translated/       # Final translated Markdown files
├── src/
│   ├── converter.py        # Wrapper for marker_single OCR tool
│   └── translator.py       # LLM interaction, cleaning logic, and chunking
├── main.py                 # Entry point and argument parsing
├── .gitignore              # Git exclusion rules
└── README.md               # Documentation
```

---

## Troubleshooting

**Ollama Out of Memory:**
If you encounter errors related to CUDA memory during the OCR phase, ensure the `unload_model` function is working correctly. The script attempts to unload the LLM before running Marker. You can manually restart Ollama if it holds onto memory:
```bash
sudo systemctl restart ollama
```

**OCR Quality Issues:**
If equations are malformed, ensure the source PDF is high resolution. `marker-pdf` relies on visual layout analysis and works best with born-digital PDFs, though it supports scanned documents.

**Translation Loops or Hallucinations:**
If the model repeats text or hallucinates, try reducing the `--chunk-size` (e.g., to 2500) or switching to a different model family (e.g., `llama3` instead of `nemotron`).

---

## License

MIT License
