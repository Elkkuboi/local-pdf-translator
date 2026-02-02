import os
import subprocess
import shutil

def generate_pdf_from_markdown(md_file_path, output_pdf_path):
    """
    Converts a Markdown file to PDF using Pandoc.
    It handles image path resolution (copying images to a temp folder if needed).
    
    Args:
        md_file_path (str): Path to the source Markdown file (e.g. output/2_translated/paper_FI.md).
        output_pdf_path (str): Where to save the PDF.
    """
    print(f"[INFO] Starting PDF generation: {md_file_path} -> {output_pdf_path}")
    
    # 1. Resolve working directory (where images are relative to the MD file)
    work_dir = os.path.dirname(md_file_path)
    md_filename = os.path.basename(md_file_path)
    
    # 2. Check if we need to locate images from the 'converted' folder
    # Often images are in output/1_converted/paper/images but the MD is in output/2_translated/
    # We might need to copy images to make Pandoc find them.
    
    # Construct command
    # We use xelatex engine because it supports UTF-8 (Scandinavian chars) and math well.
    cmd = [
        "pandoc",
        md_filename,
        "-o", os.path.basename(output_pdf_path),
        "--pdf-engine=xelatex",
        "-V", "geometry:margin=1in",
        "-V", "mainfont=DejaVu Serif", # Ensure we have a font with good unicode support
        "-V", "monofont=DejaVu Sans Mono",
        "--highlight-style=tango"
    ]
    
    try:
        # We run pandoc INSIDE the directory of the MD file so relative image links work.
        print(f"[DEBUG] Running Pandoc in {work_dir}")
        subprocess.run(cmd, cwd=work_dir, check=True)
        print(f"[SUCCESS] PDF created successfully at: {output_pdf_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pandoc failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("[ERROR] Pandoc not found. Please install it: sudo apt install pandoc texlive-xetex")
        return False

def copy_images_for_pdf(original_md_path, translated_md_path):
    """
    Helper to copy images from the source folder (converted) to the destination (translated)
    so Pandoc can find them.
    """
    # Logic:
    # 1_converted/paper/paper.md  <-- Images are here (e.g. 1_converted/paper/figures/)
    # 2_translated/paper_FI.md    <-- We are here
    
    # Find the source directory of images
    # This is a bit heuristic, assuming standard folder structure
    source_dir = os.path.dirname(original_md_path)
    dest_dir = os.path.dirname(translated_md_path)
    
    # Common marker image folders
    possible_img_folders = ["figures", "images", "img"]
    
    for folder in possible_img_folders:
        src_img_path = os.path.join(source_dir, folder)
        if os.path.exists(src_img_path):
            dest_img_path = os.path.join(dest_dir, folder)
            if not os.path.exists(dest_img_path):
                print(f"[INFO] Copying images from {src_img_path} to {dest_img_path}")
                shutil.copytree(src_img_path, dest_img_path)
            return