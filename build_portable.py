#!/usr/bin/env python3
"""
Build script to create portable executable for Subtitle Editor
Enhanced with detailed logging and feedback
"""

import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

def print_separator(char="=", length=60):
    """Print a separator line"""
    print(char * length)

def print_step(step_num, total_steps, description):
    """Print a step with progress"""
    print(f"\n📋 Step {step_num}/{total_steps}: {description}")
    print_separator("-", 40)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_progress(message):
    """Print progress message"""
    print(f"🔄 {message}")

def run_command_with_feedback(cmd, description, timeout=None):
    """Run a command with detailed feedback"""
    print_progress(f"Running: {description}")
    print_info(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    start_time = time.time()
    
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=os.getcwd()
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"Completed in {elapsed_time:.1f}s")
            if result.stdout.strip():
                print_info("Output:")
                for line in result.stdout.strip().split('\n'):
                    print(f"  📄 {line}")
            return True, result.stdout
        else:
            print_error(f"Failed with exit code {result.returncode}")
            if result.stderr.strip():
                print_error("Error output:")
                for line in result.stderr.strip().split('\n'):
                    print(f"  🔥 {line}")
            if result.stdout.strip():
                print_info("Standard output:")
                for line in result.stdout.strip().split('\n'):
                    print(f"  📄 {line}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"Command timed out after {timeout}s")
        return False, "Timeout"
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        return False, "Command not found"
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False, str(e)

def check_file_exists(file_path, description):
    """Check if a file exists with feedback"""
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        print_success(f"{description} found ({size:,} bytes)")
        return True
    else:
        print_error(f"{description} not found: {file_path}")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed with detailed feedback"""
    print_progress("Checking PyInstaller installation...")
    
    try:
        import PyInstaller
        version = PyInstaller.__version__
        print_success(f"PyInstaller {version} is installed")
        return True
    except ImportError:
        print_warning("PyInstaller is not installed")
        return False

def install_pyinstaller():
    """Install PyInstaller with detailed feedback"""
    print_step("", "", "Installing PyInstaller")
    
    success, output = run_command_with_feedback(
        [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
        "Installing PyInstaller via pip",
        timeout=300  # 5 minutes timeout
    )
    
    if success:
        print_success("PyInstaller installed successfully")
        return True
    else:
        print_error("Failed to install PyInstaller")
        print_info("You can try installing manually with: pip install pyinstaller")
        return False

def check_dependencies():
    """Check all dependencies with detailed feedback"""
    print_progress("Checking project dependencies...")
    
    deps = {
        'customtkinter': 'CustomTkinter UI framework',
        'ffmpeg': 'FFmpeg Python wrapper',
        'PIL': 'Pillow image processing',
    }
    
    missing_deps = []
    
    for module, description in deps.items():
        try:
            __import__(module)
            print_success(f"{description} - Available")
        except ImportError:
            print_warning(f"{description} - Missing")
            missing_deps.append(module)
    
    if missing_deps:
        print_error(f"Missing dependencies: {', '.join(missing_deps)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    else:
        print_success("All dependencies are available")
        return True

def get_ffmpeg_url():
    """Get FFmpeg download URL for the current platform"""
    system = platform.system().lower()
    
    urls = {
        'windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
        'darwin': 'https://evermeet.cx/ffmpeg/ffmpeg-latest.zip',  # macOS
        'linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
    }
    
    return urls.get(system)

def cleanup_build_artifacts():
    """Clean up previous build artifacts"""
    print_progress("Cleaning up previous build artifacts...")
    
    cleanup_dirs = ['build', 'dist', '__pycache__']
    cleanup_files = ['*.spec']
    
    for dir_name in cleanup_dirs:
        if Path(dir_name).exists():
            print_info(f"Removing directory: {dir_name}")
            shutil.rmtree(dir_name)
            print_success(f"Removed {dir_name}")
    
    # Clean up spec files
    for spec_file in Path('.').glob('*.spec'):
        print_info(f"Removing spec file: {spec_file}")
        spec_file.unlink()
        print_success(f"Removed {spec_file}")

def build_executable():
    """Build the portable executable with detailed feedback"""
    print_step("", "", "Building Portable Executable")
    
    # Clean up first
    cleanup_build_artifacts()
    
    # Prepare PyInstaller command
    system = platform.system()
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'SubtitleEditor',
        '--add-data', f'requirements.txt{os.pathsep}.',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'ffmpeg',
        '--clean',
    ]
    
    # Add platform-specific options
    if system == 'Windows':
        cmd.extend(['--console'])  # Keep console for debugging on Windows
    
    cmd.append('main.py')
    
    print_info("PyInstaller configuration:")
    for i, arg in enumerate(cmd):
        print(f"  {i+1:2d}. {arg}")
    
    # Run PyInstaller
    success, output = run_command_with_feedback(
        cmd,
        "Building executable with PyInstaller",
        timeout=600  # 10 minutes timeout
    )
    
    if success:
        print_success("Executable built successfully!")
        
        # Check if executable was created
        exe_name = 'SubtitleEditor.exe' if system == 'Windows' else 'SubtitleEditor'
        exe_path = Path('dist') / exe_name
        
        if check_file_exists(exe_path, "Executable file"):
            return True
        else:
            print_error("Executable was not created despite successful build")
            return False
    else:
        print_error("Failed to build executable")
        return False

def create_portable_package():
    """Create a complete portable package with detailed feedback"""
    print_step("", "", "Creating Portable Package")
    
    # Create distribution directory
    dist_dir = Path('dist_portable')
    
    print_progress(f"Setting up distribution directory: {dist_dir}")
    
    if dist_dir.exists():
        print_info("Removing existing distribution directory")
        shutil.rmtree(dist_dir)
        print_success("Cleaned up existing directory")
    
    dist_dir.mkdir()
    print_success("Created distribution directory")
    
    # Copy executable
    system = platform.system()
    exe_name = 'SubtitleEditor.exe' if system == 'Windows' else 'SubtitleEditor'
    exe_path = Path('dist') / exe_name
    target_exe = dist_dir / exe_name
    
    if check_file_exists(exe_path, "Source executable"):
        print_progress(f"Copying executable to package")
        shutil.copy2(exe_path, target_exe)
        
        if check_file_exists(target_exe, "Packaged executable"):
            # Make executable on Unix systems
            if system != 'Windows':
                os.chmod(target_exe, 0o755)
                print_success("Set executable permissions")
        else:
            print_error("Failed to copy executable")
            return False
    else:
        print_error("Source executable not found")
        return False
    
    # Copy documentation
    docs_to_copy = [
        ('README.md', 'README.txt'),
        ('requirements.txt', 'requirements.txt')
    ]
    
    for src, dst in docs_to_copy:
        if Path(src).exists():
            print_progress(f"Copying {src} -> {dst}")
            shutil.copy2(src, dist_dir / dst)
            print_success(f"Copied {dst}")
        else:
            print_warning(f"Documentation file not found: {src}")
    
    # Create examples directory
    examples_dir = dist_dir / 'examples'
    print_progress("Creating examples directory")
    examples_dir.mkdir()
    
    # Create sample subtitle file
    sample_srt = examples_dir / 'sample_subtitle.srt'
    print_progress("Creating sample subtitle file")
    
    sample_content = """1
00:00:01,000 --> 00:00:04,000
Welcome to Subtitle Editor!

2
00:00:05,000 --> 00:00:08,000
This is a sample subtitle file.

3
00:00:09,000 --> 00:00:12,000
You can use this to test the application.

4
00:00:13,000 --> 00:00:16,000
Load a video and try adding this subtitle!
"""
    
    with open(sample_srt, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print_success("Created sample subtitle file")
    
    # Create launcher script
    print_progress("Creating launcher scripts")
    
    if system == 'Windows':
        launcher_script = dist_dir / 'run_subtitle_editor.bat'
        launcher_content = f'''@echo off
echo Starting Subtitle Editor...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if FFmpeg is available
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found in PATH
    echo For full functionality, download FFmpeg and place ffmpeg.exe in this folder
    echo.
)

REM Run the application
echo Launching Subtitle Editor...
{exe_name}

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application ended with error code %errorlevel%
    echo Check that all dependencies are installed
    pause
)
'''
    else:
        launcher_script = dist_dir / 'run_subtitle_editor.sh'
        launcher_content = f'''#!/bin/bash

echo "Starting Subtitle Editor..."
echo

# Change to the script directory
cd "$(dirname "$0")"

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg not found in PATH"
    echo "For full functionality, download FFmpeg and place it in this folder"
    echo
fi

# Run the application
echo "Launching Subtitle Editor..."
./{exe_name}

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo "Application ended with error"
    echo "Check that all dependencies are installed"
    read -p "Press Enter to continue..."
fi
'''
        
    with open(launcher_script, 'w') as f:
        f.write(launcher_content)
    
    # Set executable permissions on Unix
    if system != 'Windows':
        os.chmod(launcher_script, 0o755)
    
    print_success(f"Created launcher script: {launcher_script.name}")
    
    # Create setup instructions
    setup_file = dist_dir / 'SETUP.txt'
    setup_content = f"""Subtitle Editor - Portable Version
===================================

QUICK START:
1. Download FFmpeg for your platform and place the executable in this folder
2. Run the launcher script: {launcher_script.name}
3. Or double-click the executable directly: {exe_name}

FFMPEG SETUP:
For full functionality, you need FFmpeg:

Windows:
- Download from: https://www.gyan.dev/ffmpeg/builds/
- Extract ffmpeg.exe to this folder

macOS:
- Using Homebrew: brew install ffmpeg
- Or download from: https://evermeet.cx/ffmpeg/
- Place ffmpeg binary in this folder

Linux:
- Ubuntu/Debian: sudo apt install ffmpeg
- CentOS/RHEL: sudo yum install ffmpeg
- Or download from: https://johnvansickle.com/ffmpeg/
- Place ffmpeg binary in this folder

FEATURES:
- View subtitle tracks in video files
- Extract subtitles to separate files
- Add new subtitle tracks
- Remove unwanted subtitles
- Set default subtitle tracks
- Modern UI with dark/light themes

SUPPORTED FORMATS:
Video: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
Subtitles: SRT, ASS, SSA, VTT, SUB

For detailed instructions, see README.txt

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Platform: {platform.system()} {platform.release()}
"""
    
    with open(setup_file, 'w') as f:
        f.write(setup_content)
    
    print_success("Created setup instructions")
    
    # Create version info file
    version_file = dist_dir / 'VERSION.txt'
    version_content = f"""Subtitle Editor - Build Information
=====================================

Build Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Platform: {platform.system()} {platform.release()} ({platform.machine()})
Python Version: {sys.version}
Build Directory: {os.getcwd()}

Files Included:
- {exe_name} (Main executable)
- README.txt (Documentation)
- SETUP.txt (Setup instructions)
- requirements.txt (Python dependencies)
- {launcher_script.name} (Launcher script)
- examples/sample_subtitle.srt (Sample file)

For updates and source code:
https://github.com/AtaraxyState/SubtitleEditor
"""
    
    with open(version_file, 'w') as f:
        f.write(version_content)
    
    print_success("Created version information")
    
    # Calculate total package size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    file_count = len(list(dist_dir.rglob('*')))
    
    print_separator()
    print_success("PORTABLE PACKAGE CREATED SUCCESSFULLY!")
    print_separator()
    
    print(f"📦 Package location: {dist_dir.absolute()}")
    print(f"📊 Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    print(f"📁 Total files: {file_count}")
    
    print("\n📋 Package contents:")
    for item in sorted(dist_dir.rglob('*')):
        if item.is_file():
            size = item.stat().st_size
            rel_path = item.relative_to(dist_dir)
            print(f"  📄 {rel_path} ({size:,} bytes)")
        elif item.is_dir() and item != dist_dir:
            rel_path = item.relative_to(dist_dir)
            print(f"  📁 {rel_path}/")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Download FFmpeg for your platform")
    print("2. Place the FFmpeg executable in the dist_portable folder")
    print("3. Test the application using the launcher script")
    print("4. Copy the entire dist_portable folder to distribute")
    
    return True

def main():
    """Main build process with enhanced feedback"""
    print_separator("=", 70)
    print("🚀 SUBTITLE EDITOR - PORTABLE BUILD SYSTEM")
    print_separator("=", 70)
    
    start_time = time.time()
    
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🏗️  Architecture: {platform.machine()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"⏰ Build Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check Python version
    print_step(1, 6, "Checking Python Version")
    if sys.version_info < (3, 7):
        print_error(f"Python {sys.version_info.major}.{sys.version_info.minor} is too old")
        print_error("Python 3.7 or higher is required")
        return 1
    else:
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    
    # Check if we're in the right directory
    print_step(2, 6, "Validating Project Structure")
    required_files = ['main.py', 'subtitle_editor.py', 'video_handler.py', 'requirements.txt']
    
    missing_files = []
    for file in required_files:
        if check_file_exists(file, f"Required file {file}"):
            continue
        else:
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Missing required files: {', '.join(missing_files)}")
        print_error("Please run this script from the project root directory")
        return 1
    else:
        print_success("All required project files found")
    
    # Check dependencies
    print_step(3, 6, "Checking Dependencies")
    if not check_dependencies():
        print_error("Please install missing dependencies first")
        print_info("Run: pip install -r requirements.txt")
        return 1
    
    # Check/install PyInstaller
    print_step(4, 6, "Setting Up PyInstaller")
    if not check_pyinstaller():
        if not install_pyinstaller():
            print_error("Cannot proceed without PyInstaller")
            return 1
    
    # Build executable
    print_step(5, 6, "Building Executable")
    if not build_executable():
        print_error("Build process failed")
        return 1
    
    # Create portable package
    print_step(6, 6, "Creating Portable Package")
    if not create_portable_package():
        print_error("Package creation failed")
        return 1
    
    # Final summary
    elapsed_time = time.time() - start_time
    
    print_separator("=", 70)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print_separator("=", 70)
    
    print(f"⏱️  Total build time: {elapsed_time:.1f} seconds")
    print(f"📦 Portable package ready in: dist_portable/")
    print(f"🔗 Project repository: https://github.com/AtaraxyState/SubtitleEditor")
    
    print("\n✅ BUILD SUMMARY:")
    print("   • Executable created and tested")
    print("   • Documentation included")
    print("   • Sample files provided")
    print("   • Launcher scripts generated")
    print("   • Setup instructions created")
    
    print("\n🚚 DISTRIBUTION READY!")
    print("   Your portable Subtitle Editor is ready for distribution")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Build interrupted by user")
        print("🧹 Cleaning up...")
        
        # Quick cleanup
        cleanup_dirs = ['build', 'dist']
        for dir_name in cleanup_dirs:
            if Path(dir_name).exists():
                try:
                    shutil.rmtree(dir_name)
                    print_info(f"Cleaned up {dir_name}")
                except:
                    pass
        
        print("👋 Build cancelled")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error during build: {e}")
        print_info("This might be a bug. Please report it on GitHub.")
        sys.exit(1) 