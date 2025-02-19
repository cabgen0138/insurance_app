import os

def generate_directory_structure(base_path, output_file="directory_structure.txt"):
    """Generate a tree-like directory structure and save it to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(base_path):
            # Compute level depth
            level = root.replace(base_path, "").count(os.sep)
            indent = " " * (4 * level)  # 4 spaces per level
            f.write(f"{indent}- {os.path.basename(root)}/\n")

            sub_indent = " " * (4 * (level + 1))
            for file in files:
                f.write(f"{sub_indent}- {file}\n")

    print(f"✅ Directory structure saved to '{output_file}'")

if __name__ == "__main__":
    # Get the root directory of the script
    project_root = os.path.dirname(os.path.abspath(__file__))
    generate_directory_structure(project_root)
