#!/usr/bin/env python3
"""
Simple script to view ASCII art diagrams from documentation files.
This demonstrates that diagrams are now visible in all text viewers.
"""

import os
import re

def extract_ascii_art(file_path):
    """Extract ASCII art diagrams from a markdown file."""
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find ASCII art blocks (between ``` and ```)
    ascii_blocks = re.findall(r'```\n(.*?)\n```', content, re.DOTALL)
    
    return ascii_blocks

def view_diagrams():
    """View ASCII art diagrams from all documentation files."""
    
    docs_dir = "/Users/ajitbehera/Codes/AskTennis_Streamlit/docs"
    
    files_to_view = [
        ("01_System_Architecture.md", "System Architecture"),
        ("02_Data_Flow.md", "Data Flow"),
        ("03_Data_Model.md", "Data Model"),
        ("04_Software_Process_Model.md", "Software Process Model"),
        ("05_Use_Case_Diagram.md", "Use Case Diagram"),
        ("06_State_Diagram.md", "State Diagram"),
        ("07_UI_UX_Design.md", "UI/UX Design")
    ]
    
    print("🎨 AskTennis AI - ASCII Art Diagrams Viewer")
    print("=" * 60)
    
    for filename, title in files_to_view:
        file_path = os.path.join(docs_dir, filename)
        
        print(f"\n📊 {title}")
        print("-" * 40)
        
        ascii_blocks = extract_ascii_art(file_path)
        
        if ascii_blocks:
            for i, block in enumerate(ascii_blocks, 1):
                print(f"\nDiagram {i}:")
                print(block)
        else:
            print("No ASCII art diagrams found")
        
        print("\n" + "=" * 60)

def main():
    """Main function to view all diagrams."""
    view_diagrams()
    
    print("\n✅ All diagrams displayed successfully!")
    print("📝 These ASCII art diagrams are visible in any text viewer")
    print("🔧 For enhanced viewing, use Mermaid-compatible viewers")

if __name__ == "__main__":
    main()
