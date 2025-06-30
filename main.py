#!/usr/bin/env python3
"""
Subtitle Editor - A portable video subtitle management tool
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    try:
        import ffmpeg
    except ImportError:
        missing_deps.append("ffmpeg-python")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    return missing_deps

def check_ffmpeg():
    """Check if FFmpeg is available in the system"""
    import shutil
    return shutil.which("ffmpeg") is not None

def main():
    """Main entry point"""
    # Check Python version
    if sys.version_info < (3, 7):
        messagebox.showerror("Error", "Python 3.7 or higher is required")
        return
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        messagebox.showerror(
            "Missing Dependencies", 
            f"The following dependencies are missing:\n{', '.join(missing_deps)}\n\n"
            "Please install them using:\npip install -r requirements.txt"
        )
        return
    
    # Check FFmpeg
    if not check_ffmpeg():
        messagebox.showwarning(
            "FFmpeg Not Found",
            "FFmpeg is not found in your system PATH.\n\n"
            "Please install FFmpeg and add it to your PATH, or place the FFmpeg executable "
            "in the same directory as this application.\n\n"
            "Download from: https://ffmpeg.org/download.html"
        )
        # Continue anyway - user might have portable FFmpeg
    
    try:
        # Import and run the application
        from subtitle_editor import SubtitleEditor
        
        app = SubtitleEditor()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 