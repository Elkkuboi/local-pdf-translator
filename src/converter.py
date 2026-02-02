import os
import subprocess

def convert_pdf_to_markdown(input_path, output_base_dir):
    """
    Executes the 'marker_single' command line tool to convert a PDF file into Markdown.

    This function handles the subprocess execution and attempts to locate the 
    generated Markdown file, which Marker places in a subdirectory based on the filename.

    Args:
        input_path (str): Full path to the source PDF file.
        output_base_dir (str): Base directory where the output folder should be created.

    Returns:
        str | None: The full path to the generated .md file if successful, otherwise None.
    """
    
    # Extract filename without extension for path resolution later
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    print(f"[INFO] Starting PDF conversion for: {input_path}")
    
    # Construct the command. 
    # Note: '--output_dir' is required by modern versions of Marker.
    cmd = [
        "marker_single",
        input_path,
        "--output_dir", output_base_dir
    ]
    
    try:
        print(f"[DEBUG] Executing command: {' '.join(cmd)}")
        
        # Run the command and wait for it to finish. 
        # check=True raises CalledProcessError if the command fails.
        subprocess.run(cmd, check=True)
        
        print(f"[SUCCESS] Marker conversion process finished.")
        
        # ---------------------------------------------------------
        # Path Resolution Strategy
        # ---------------------------------------------------------
        # Marker usually creates a structure like: output_dir/filename/filename.md
        # However, versions may differ, so we check multiple likely locations.
        
        expected_subdir = os.path.join(output_base_dir, base_name)
        
        possible_paths = [
            # 1. Standard structure: output/filename/filename.md
            os.path.join(expected_subdir, f"{base_name}.md"),
            
            # 2. Flat structure (rare but possible in some configs): output/filename.md
            os.path.join(output_base_dir, f"{base_name}.md"),
            
            # 3. Nested structure: output/filename/filename/filename.md
            os.path.join(expected_subdir, base_name, f"{base_name}.md")
        ]

        # Check standard locations first
        for p in possible_paths:
            if os.path.exists(p):
                print(f"[INFO] Markdown file located at: {p}")
                return p
        
        # Fallback: Recursive search in the output directory
        print(f"[WARN] File not found in standard paths. Searching recursively in {output_base_dir}...")
        
        for root, dirs, files in os.walk(output_base_dir):
            for file in files:
                # Look for the exact markdown file match
                if file == f"{base_name}.md":
                    found_path = os.path.join(root, file)
                    print(f"[INFO] File found via recursive search: {found_path}")
                    return found_path
        
        print(f"[ERROR] Marker finished, but the output .md file could not be found.")
        return None
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Marker conversion failed with exit code: {e.returncode}")
        
        # If exit code is 2, it often implies an argument error. Print help for debugging.
        if e.returncode == 2:
            print("-" * 40)
            print("[DEBUG] Marker help output:")
            subprocess.run(["marker_single", "--help"])
            print("-" * 40)
            
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during conversion: {e}")
        return None