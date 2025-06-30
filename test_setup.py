#!/usr/bin/env python3
"""
Test script to verify the setup of Subtitle Editor
"""

import sys
import os
import platform

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def test_python_version():
    """Test Python version"""
    print("✓ Testing Python version...")
    version = sys.version_info
    if version >= (3, 7):
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n✓ Testing dependencies...")
    
    deps = {
        'customtkinter': 'CustomTkinter',
        'ffmpeg': 'FFmpeg-Python',
        'PIL': 'Pillow',
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"  ✅ {name} - OK")
        except ImportError:
            print(f"  ❌ {name} - NOT FOUND")
            all_ok = False
    
    return all_ok

def test_ffmpeg():
    """Test FFmpeg availability"""
    print("\n✓ Testing FFmpeg...")
    
    import shutil
    ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path:
        print(f"  ✅ FFmpeg found at: {ffmpeg_path}")
        
        # Test FFmpeg functionality
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"  ✅ FFmpeg version: {version}")
                return True
            else:
                print(f"  ⚠️  FFmpeg found but returned error code {result.returncode}")
                return False
        except Exception as e:
            print(f"  ⚠️  FFmpeg found but error testing: {e}")
            return False
    else:
        print("  ❌ FFmpeg not found in PATH")
        print("     Please install FFmpeg or place it in the application directory")
        return False

def test_ui():
    """Test UI components"""
    print("\n✓ Testing UI components...")
    
    try:
        import tkinter as tk
        # Test if we can create a Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("  ✅ Tkinter - OK")
        
        import customtkinter as ctk
        # Test CustomTkinter
        ctk.set_appearance_mode("System")
        print("  ✅ CustomTkinter - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ UI Error: {e}")
        return False

def provide_installation_help():
    """Provide installation instructions"""
    print_header("INSTALLATION HELP")
    
    print("To install missing dependencies, run:")
    print("  pip install -r requirements.txt")
    
    print("\nTo install FFmpeg:")
    system = platform.system()
    if system == "Windows":
        print("  - Download from: https://www.gyan.dev/ffmpeg/builds/")
        print("  - Extract and add to PATH, or place ffmpeg.exe in this directory")
    elif system == "Darwin":  # macOS
        print("  - Using Homebrew: brew install ffmpeg")
        print("  - Or download from: https://evermeet.cx/ffmpeg/")
    else:  # Linux
        print("  - Ubuntu/Debian: sudo apt install ffmpeg")
        print("  - CentOS/RHEL: sudo yum install ffmpeg")
        print("  - Or download from: https://johnvansickle.com/ffmpeg/")

def main():
    """Main test function"""
    print_header("SUBTITLE EDITOR - SETUP TEST")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_python_version()
    all_tests_passed &= test_dependencies()
    all_tests_passed &= test_ffmpeg()
    all_tests_passed &= test_ui()
    
    # Results
    print_header("TEST RESULTS")
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour system is ready to run Subtitle Editor.")
        print("Run the application with: python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the application.")
        provide_installation_help()
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 