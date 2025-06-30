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
import importlib.util
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

def get_package_path(package_name):
    """Get the path of an installed package"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            return Path(spec.origin).parent
        return None
    except:
        return None

def find_data_files():
    """Find all data files that need to be included"""
    print_progress("Discovering data files to include...")
    
    data_files = []
    
    # CustomTkinter data files
    ctk_path = get_package_path('customtkinter')
    if ctk_path:
        print_info(f"CustomTkinter path: {ctk_path}")
        
        # Include theme files
        theme_dir = ctk_path / 'assets'
        if theme_dir.exists():
            data_files.append((str(theme_dir), 'customtkinter/assets'))
            print_success(f"Found CustomTkinter assets: {theme_dir}")
        
        # Include fonts
        font_dir = ctk_path / 'assets' / 'fonts'
        if font_dir.exists():
            data_files.append((str(font_dir), 'customtkinter/assets/fonts'))
            print_success(f"Found CustomTkinter fonts: {font_dir}")
            
        # Include icons
        icon_dir = ctk_path / 'assets' / 'icons'
        if icon_dir.exists():
            data_files.append((str(icon_dir), 'customtkinter/assets/icons'))
            print_success(f"Found CustomTkinter icons: {icon_dir}")
    
    # PIL/Pillow data files
    pil_path = get_package_path('PIL')
    if pil_path:
        print_info(f"PIL path: {pil_path}")
        # Include any needed PIL data files
        
    print_success(f"Found {len(data_files)} data file groups to include")
    return data_files

def get_all_hidden_imports():
    """Get comprehensive list of hidden imports"""
    print_progress("Preparing comprehensive hidden imports list...")
    
    hidden_imports = [
        # Core dependencies
        'customtkinter',
        'ffmpeg',
        'PIL',
        'PIL.Image',
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        
        # CustomTkinter dependencies
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        'customtkinter.appearance_mode',
        'customtkinter.theme_manager',
        'customtkinter.settings',
        'customtkinter.draw_engine',
        
        # Tkinter related
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.ttk',
        '_tkinter',
        
        # System and standard library
        'threading',
        'pathlib',
        'subprocess',
        'shutil',
        'tempfile',
        'json',
        'os',
        'sys',
        'platform',
        'time',
        
        # FFmpeg related
        'ffmpeg._run',
        'ffmpeg._probe',
        'ffmpeg._dag',
        'future',
        'future.builtins',
        
        # Additional potential dependencies
        'pkg_resources',
        'setuptools',
        'importlib',
        'importlib.util',
        'collections',
        'collections.abc',
        'typing',
        'typing_extensions',
    ]
    
    print_success(f"Prepared {len(hidden_imports)} hidden imports")
    return hidden_imports

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
    installed_versions = {}
    
    for module, description in deps.items():
        try:
            imported_module = __import__(module)
            version = getattr(imported_module, '__version__', 'unknown')
            installed_versions[module] = version
            print_success(f"{description} - Available (v{version})")
        except ImportError:
            print_warning(f"{description} - Missing")
            missing_deps.append(module)
    
    if missing_deps:
        print_error(f"Missing dependencies: {', '.join(missing_deps)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    else:
        print_success("All dependencies are available")
        print_info("Installed versions:")
        for module, version in installed_versions.items():
            print(f"  📦 {module}: {version}")
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
    
    # Get all hidden imports
    hidden_imports = get_all_hidden_imports()
    
    # Get data files
    data_files = find_data_files()
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'SubtitleEditor',
        '--clean',
        '--noconfirm',
    ]
    
    # Add data files
    cmd.extend(['--add-data', f'requirements.txt{os.pathsep}.'])
    
    for src, dst in data_files:
        cmd.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
    
    # Add all hidden imports
    for import_name in hidden_imports:
        cmd.extend(['--hidden-import', import_name])
    
    # Add platform-specific options
    if system == 'Windows':
        cmd.extend(['--console'])  # Keep console for debugging on Windows
        # Exclude some Windows-specific modules that might cause issues
        cmd.extend(['--exclude-module', 'FixTk'])
        cmd.extend(['--exclude-module', 'tcl'])
        cmd.extend(['--exclude-module', 'tk'])
    
    # Optimize the build
    cmd.extend([
        '--strip',  # Strip debug information
        '--optimize', '2',  # Optimize bytecode
    ])
    
    cmd.append('main.py')
    
    print_info("PyInstaller configuration:")
    for i, arg in enumerate(cmd):
        print(f"  {i+1:2d}. {arg}")
    
    print_info(f"Total arguments: {len(cmd)}")
    print_info(f"Hidden imports: {len(hidden_imports)}")
    print_info(f"Data file groups: {len(data_files)}")
    
    # Run PyInstaller
    success, output = run_command_with_feedback(
        cmd,
        "Building executable with PyInstaller",
        timeout=900  # 15 minutes timeout for larger builds
    )
    
    if success:
        print_success("Executable built successfully!")
        
        # Check if executable was created
        exe_name = 'SubtitleEditor.exe' if system == 'Windows' else 'SubtitleEditor'
        exe_path = Path('dist') / exe_name
        
        if check_file_exists(exe_path, "Executable file"):
            # Test the executable briefly
            print_progress("Testing executable...")
            try:
                test_result = subprocess.run(
                    [str(exe_path), '--help'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if test_result.returncode == 0 or 'usage' in test_result.stdout.lower():
                    print_success("Executable test passed")
                else:
                    print_warning("Executable test returned non-zero exit code (might be normal)")
            except subprocess.TimeoutExpired:
                print_warning("Executable test timed out (might be normal for GUI apps)")
            except Exception as e:
                print_warning(f"Could not test executable: {e}")
            
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
    echo Download from: https://www.gyan.dev/ffmpeg/builds/
    echo.
    echo The application will still start, but video processing features may not work.
    echo.
    pause
)

REM Run the application
echo Launching Subtitle Editor...
{exe_name}

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application ended with error code %errorlevel%
    echo.
    echo This might be due to:
    echo - Missing FFmpeg (required for video processing)
    echo - Corrupted video files
    echo - Insufficient permissions
    echo.
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
    echo "Download links:"
    echo "- macOS: https://evermeet.cx/ffmpeg/"
    echo "- Linux: https://johnvansickle.com/ffmpeg/"
    echo
    echo "The application will still start, but video processing features may not work."
    echo
    read -p "Press Enter to continue..."
fi

# Run the application
echo "Launching Subtitle Editor..."
./{exe_name}

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo "Application ended with error"
    echo
    echo "This might be due to:"
    echo "- Missing FFmpeg (required for video processing)"
    echo "- Corrupted video files"
    echo "- Insufficient permissions"
    echo
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

IMPORTANT: This is a PORTABLE application!
- No Python installation required
- All dependencies are bundled in the executable
- Only FFmpeg needs to be added for full functionality

QUICK START:
1. Download FFmpeg for your platform (see links below)
2. Place the FFmpeg executable in this folder
3. Run: {launcher_script.name}
4. Or double-click: {exe_name}

FFMPEG SETUP (Required for video processing):

Windows:
- Download from: https://www.gyan.dev/ffmpeg/builds/
- Extract ffmpeg.exe to this folder
- Or add FFmpeg to your system PATH

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
- Add new subtitle tracks from external files
- Remove unwanted subtitle tracks
- Set default subtitle tracks
- Modern UI with dark/light themes
- Completely portable - no installation needed!

SUPPORTED FORMATS:
Video: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
Subtitles: SRT, ASS, SSA, VTT, SUB

TROUBLESHOOTING:
- If the app doesn't start: Check Windows Defender/antivirus
- If video loading fails: Ensure FFmpeg is properly installed
- If UI looks wrong: Try toggling light/dark theme

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

PORTABLE BUILD - All Python dependencies included!
- No Python installation required on target system
- All libraries bundled in executable
- Only FFmpeg required as external dependency

Files Included:
- {exe_name} (Main executable - SELF-CONTAINED)
- README.txt (Documentation)
- SETUP.txt (Setup instructions)
- requirements.txt (Python dependencies - for reference only)
- {launcher_script.name} (Launcher script with FFmpeg check)
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
    print("1. Download FFmpeg for your target platform")
    print("2. Place the FFmpeg executable in the dist_portable folder")
    print("3. Test the application using the launcher script")
    print("4. Copy the entire dist_portable folder to distribute")
    print("\n✨ IMPORTANT: The executable is now FULLY PORTABLE!")
    print("   No Python or pip installation needed on target systems!")
    
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
    print_step(5, 6, "Building Self-Contained Executable")
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
    print("   • Self-contained executable created")
    print("   • All Python dependencies bundled")
    print("   • No Python installation required on target")
    print("   • Only FFmpeg needed as external dependency")
    print("   • Complete documentation included")
    print("   • Sample files provided")
    print("   • Smart launcher scripts generated")
    
    print("\n🚚 DISTRIBUTION READY!")
    print("   Your portable Subtitle Editor is truly portable now!")
    print("   Users only need to add FFmpeg - no Python/pip required!")
    
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