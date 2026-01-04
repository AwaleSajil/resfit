import re
from pathlib import Path

def sync_flowchart():
    mmd_path = Path("docs/flowchart.mmd")
    readme_path = Path("README.md")

    if not mmd_path.exists():
        print(f"Error: {mmd_path} not found")
        return

    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return

    with open(mmd_path, "r") as f:
        mmd_content = f.read().strip()

    with open(readme_path, "r") as f:
        readme_content = f.read()

    # Regex to find the mermaid block in README.md
    # It looks for ```mermaid ... ```
    pattern = r"```mermaid\n(.*?)\n```"
    
    new_mermaid_block = f"```mermaid\n{mmd_content}\n```"
    
    if re.search(pattern, readme_content, re.DOTALL):
        new_readme_content = re.sub(pattern, new_mermaid_block, readme_content, flags=re.DOTALL)
        
        with open(readme_path, "w") as f:
            f.write(new_readme_content)
        print("Successfully synced flowchart to README.md")
    else:
        print("Could not find mermaid block in README.md")

if __name__ == "__main__":
    sync_flowchart()
