"""UI utility functions for styling and presentation."""
from pathlib import Path


def load_css(css_file: str = "styles.css") -> str:
    """
    Load CSS from the ui/styles directory and return as HTML style tag.
    
    Args:
        css_file: Name of the CSS file to load (default: "styles.css")
        
    Returns:
        HTML string containing the CSS wrapped in <style> tags
    """
    # Get the path to ui/styles directory relative to this file
    css_path = Path(__file__).parent.parent / "styles" / css_file
    
    with open(css_path, "r") as f:
        css = f.read()
    
    return f"<style>{css}</style>"

