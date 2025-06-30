#!/usr/bin/env python3
"""
Build script to create portable executable for Subtitle Editor
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def get_ffmpeg_url():
    """Get FFmpeg download URL for the current platform"""
    system = platform.system().lower()
    
    urls = {
        'windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
        'darwin': 'https://evermeet.cx/ffmpeg/ffmpeg-latest.zip',  # macOS
        'linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
    }
    
    return urls.get(system)

def build_executable():
    """Build the portable executable"""
    print("Building portable executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'SubtitleEditor',
        '--add-data', 'requirements.txt;.',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'PIL._tkinter_finder',
        'main.py'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_portable_package():
    """Create a complete portable package"""
    print("Creating portable package...")
    
    # Create distribution directory
    dist_dir = Path('dist_portable')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy executable
    exe_name = 'SubtitleEditor.exe' if platform.system() == 'Windows' else 'SubtitleEditor'
    exe_path = Path('dist') / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)
        print(f"✅ Copied {exe_name}")
    else:
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Copy README
    if Path('README.md').exists():
        shutil.copy2('README.md', dist_dir / 'README.txt')
        print("✅ Copied README")
    
    # Create examples directory
    examples_dir = dist_dir / 'examples'
    examples_dir.mkdir()
    
    # Create sample subtitle file
    sample_srt = examples_dir / 'sample_subtitle.srt'
    with open(sample_srt, 'w', encoding='utf-8') as f:
        f.write("""1
00:00:01,000 --> 00:00:04,000
Welcome to Subtitle Editor!

2
00:00:05,000 --> 00:00:08,000
This is a sample subtitle file.

3
00:00:09,000 --> 00:00:12,000
You can use this to test the application.
""")
    print("✅ Created sample subtitle file")
    
    # Create batch/shell script for easy launching
    if platform.system() == 'Windows':
        launcher_script = dist_dir / 'run_subtitle_editor.bat'
        with open(launcher_script, 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('SubtitleEditor.exe\n')
            f.write('pause\n')
    else:
        launcher_script = dist_dir / 'run_subtitle_editor.sh'
        with open(launcher_script, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('./SubtitleEditor\n')
        os.chmod(launcher_script, 0o755)
    
    print(f"✅ Created launcher script: {launcher_script.name}")
    
    # Create setup instructions
    setup_file = dist_dir / 'SETUP.txt'
    with open(setup_file, 'w') as f:
        f.write("Subtitle Editor - Portable Version\n")
        f.write("===================================\n\n")
        f.write("QUICK START:\n")
        f.write("1. Download FFmpeg for your platform and place the executable in this folder\n")
        f.write("2. Run the launcher script or double-click the executable\n\n")
        f.write("FFmpeg Download Links:\n")
        f.write("- Windows: https://www.gyan.dev/ffmpeg/builds/\n")
        f.write("- macOS: https://evermeet.cx/ffmpeg/\n")
        f.write("- Linux: https://johnvansickle.com/ffmpeg/\n\n")
        f.write("For detailed instructions, see README.txt\n")
    
    print("✅ Created setup instructions")
    
    print(f"\n🎉 Portable package created in: {dist_dir.absolute()}")
    print("\nTo complete the setup:")
    print("1. Download FFmpeg for your platform")
    print("2. Place the FFmpeg executable in the dist_portable folder")
    print("3. Your portable Subtitle Editor is ready!")
    
    return True

def main():
    """Main build process"""
    print("🚀 Building Portable Subtitle Editor")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return 1
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Check/install PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Create portable package
    if not create_portable_package():
        return 1
    
    print("\n✅ Build completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main()) 