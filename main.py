import os
import sys
import argparse
from src.converter import convert_pdf_to_markdown
from src.translator import process_markdown_translation, unload_model
from src.pdf_generator import generate_pdf_from_markdown, copy_images_for_pdf

# --- Configuration Constants ---
DEFAULT_INPUT_DIR = "input"
DEFAULT_CONVERTED_DIR = "output/1_converted"
DEFAULT_TRANSLATED_DIR = "output/2_translated"
DEFAULT_MODEL = "nemotron-3-nano:30b"
DEFAULT_LANG = "Finnish"
DEFAULT_CHUNK_SIZE = 5000  # Updated default based on RTX 5090 capabilities

def parse_arguments():
    """
    Parses command line arguments to allow dynamic configuration.
    """
    parser = argparse.ArgumentParser(
        description="Research Paper Translator v2.0 - Local LLM Pipeline"
    )
    
    parser.add_argument(
        "filename", 
        nargs="?", 
        help="Specific PDF filename in the input folder. If omitted, processes the first PDF found."
    )
    
    parser.add_argument(
        "--lang", 
        type=str, 
        default=DEFAULT_LANG, 
        help=f"Target language for translation (default: {DEFAULT_LANG})"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default=DEFAULT_MODEL, 
        help=f"Ollama model to use (default: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=DEFAULT_CHUNK_SIZE, 
        help=f"Character limit per text chunk (default: {DEFAULT_CHUNK_SIZE}). Increase for faster processing on high-end GPUs."
    )
    
    parser.add_argument(
        "--force-ocr", 
        action="store_true", 
        help="Force re-running the OCR phase even if a Markdown file already exists."
    )

    return parser.parse_args()

def main():
    """
    Main execution pipeline.
    """
    args = parse_arguments()
    
    # ---------------------------------------------------------
    # 1. File Resolution
    # ---------------------------------------------------------
    if args.filename:
        pdf_path = os.path.join(DEFAULT_INPUT_DIR, args.filename)
        if not os.path.exists(pdf_path):
            print(f"[ERROR] Specified file not found: {pdf_path}")
            return
    else:
        try:
            files = [f for f in os.listdir(DEFAULT_INPUT_DIR) if f.endswith(".pdf")]
        except FileNotFoundError:
            print(f"[ERROR] Input directory '{DEFAULT_INPUT_DIR}' does not exist.")
            return

        if not files:
            print(f"[ERROR] No PDF files found in '{DEFAULT_INPUT_DIR}'.")
            return
        pdf_path = os.path.join(DEFAULT_INPUT_DIR, files[0])
    
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    print("=" * 60)
    print(f"Processing File:  {os.path.basename(pdf_path)}")
    print(f"Target Language:  {args.lang}")
    print(f"AI Model:         {args.model}")
    print(f"Chunk Size:       {args.chunk_size} chars")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # Phase 1: OCR
        # ---------------------------------------------------------
        expected_md_path = os.path.join(DEFAULT_CONVERTED_DIR, pdf_filename, f"{pdf_filename}.md")
        md_path = None
        
        if os.path.exists(expected_md_path) and not args.force_ocr:
            print(f"[INFO] Found existing Markdown conversion at: {expected_md_path}")
            print("[INFO] Skipping OCR phase.")
            md_path = expected_md_path
        else:
            print("-" * 40)
            print("[PHASE 1] Starting PDF conversion (OCR)...")
            unload_model(args.model) 
            md_path = convert_pdf_to_markdown(pdf_path, DEFAULT_CONVERTED_DIR)
        
        # ---------------------------------------------------------
        # Phase 2: Translation
        # ---------------------------------------------------------
        if md_path and os.path.exists(md_path):
            print("-" * 40)
            print(f"[PHASE 2] Starting AI translation...")
            
            suffix = f"_{args.lang}.md"
            output_filename = os.path.basename(md_path).replace(".md", suffix)
            final_path = os.path.join(DEFAULT_TRANSLATED_DIR, output_filename)
            
            process_markdown_translation(
                input_file=md_path, 
                output_file=final_path, 
                target_language=args.lang, 
                model_name=args.model,
                chunk_size=args.chunk_size # Pass dynamic chunk size
            )
        else:
            print("[ERROR] Conversion failed or file path invalid.")
        
        # ---------------------------------------------------------
        # Phase 3: PDF Generation
        # ---------------------------------------------------------
        if final_path and os.path.exists(final_path):
            print("-" * 40)
            print(f"[PHASE 3] Generating final PDF...")
            
            # 1. Copy images so Pandoc can find them
            copy_images_for_pdf(md_path, final_path)
            
            # 2. Convert MD -> PDF
            pdf_output_filename = os.path.basename(final_path).replace(".md", ".pdf")
            final_pdf_path = os.path.join(DEFAULT_TRANSLATED_DIR, pdf_output_filename)
            
            generate_pdf_from_markdown(final_path, final_pdf_path)
            
    except KeyboardInterrupt:
        print("\n[WARN] Operation cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        print("-" * 40)
        unload_model(args.model)
        print("[INFO] Program execution finished.")

if __name__ == "__main__":
    main()