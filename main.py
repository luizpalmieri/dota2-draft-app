#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dota 2 Draft Analyzer - Main Entry Point
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main() -> None:
    """Main entry point for the application."""
    try:
        from app.ui.draft_analyzer_ui import MainApplication
        import tkinter as tk
        
        root = tk.Tk()
        app = MainApplication(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
