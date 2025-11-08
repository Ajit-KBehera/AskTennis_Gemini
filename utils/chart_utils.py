"""
Chart display utilities for tennis visualization scripts.

This module provides general utilities for displaying charts and visualizations,
usable across all chart types (serve, return, ranking, tournament, etc.).
"""


def display_chart(fig, html_filename=None):
    """
    Display a Plotly chart in the browser or save to HTML file.
    
    Args:
        fig: Plotly figure object to display
        html_filename: Optional filename for HTML output (default: None, auto-generated)
    """
    try:
        fig.show(renderer='browser')
        print("Plot displayed in browser.")
    except Exception:
        if html_filename is None:
            html_filename = 'chart.html'
        print(f"Error displaying plot in browser. Saving to HTML file.")
        fig.write_html(html_filename)
        print(f"Plot saved to {html_filename}.")

