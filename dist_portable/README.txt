# Subtitle Editor

A portable, modern subtitle management tool for video files. This application allows you to view, extract, add, remove, and manage subtitle tracks in video files without requiring an internet connection or server setup.

## Features

- **Modern UI**: Clean, modern interface with light/dark theme support
- **Portable**: Runs without installation, perfect for USB drives
- **Video Support**: Works with MP4, AVI, MKV, MOV, WMV, FLV, WebM, and M4V files
- **Subtitle Management**:
  - View all subtitle tracks in a video
  - Extract subtitle tracks to separate files
  - Add new subtitle tracks from external files
  - Remove unwanted subtitle tracks
  - Set default subtitle track
- **Multiple Formats**: Supports SRT, ASS, SSA, VTT, and SUB subtitle formats
- **Batch Operations**: Process multiple operations with progress tracking
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7 or higher
- FFmpeg (for video processing)

## Installation

### Method 1: Using Python (Recommended for development)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   - **Windows**: Download from [FFmpeg official website](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

3. **Run the application:**
   ```bash
   python main.py
   ```

### Method 2: Portable Executable (Coming Soon)

We'll provide pre-built portable executables for Windows, macOS, and Linux that include all dependencies.

## Usage

1. **Launch the application** by running `python main.py`

2. **Select a video file** by clicking "Select Video" in the sidebar

3. **View subtitle tracks** - All available subtitle tracks will be displayed in the main area

4. **Manage subtitles:**
   - **Extract**: Save a subtitle track to a separate file
   - **Set Default**: Mark a subtitle track as the default one
   - **Remove**: Create a new video file without the selected subtitle track
   - **Add Subtitle**: Add a new subtitle file to the video

5. **Export** the modified video when you're done

## Creating a Portable Version

To create a portable executable that can run from a USB drive:

### Using PyInstaller

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Create the executable:**
   ```bash
   pyinstaller --onefile --windowed --name "SubtitleEditor" main.py
   ```

3. **For a complete portable package:**
   ```bash
   # Create a more complete package with all dependencies
   pyinstaller --onedir --windowed --name "SubtitleEditor" main.py
   ```

4. **Include FFmpeg:**
   - Download FFmpeg executable for your target platform
   - Place it in the same directory as your executable
   - The application will automatically detect and use it

### Directory Structure for Portable Distribution

```
SubtitleEditor/
├── SubtitleEditor.exe (or SubtitleEditor on macOS/Linux)
├── ffmpeg.exe (or ffmpeg on macOS/Linux)
├── README.txt
└── examples/
    └── sample_subtitle.srt
```

## Technical Details

### Dependencies

- **CustomTkinter**: Modern UI framework for Python
- **FFmpeg-Python**: Python wrapper for FFmpeg
- **Pillow**: Image processing library
- **tkinter-tooltip**: Enhanced tooltips for UI elements

### Video Processing

The application uses FFmpeg for all video and subtitle operations:
- **Probing**: Extracts metadata and stream information
- **Extraction**: Extracts subtitle streams to separate files
- **Muxing**: Combines video with new subtitle tracks
- **Remuxing**: Removes or reorders subtitle tracks

### Supported Formats

**Video Formats:**
- MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V

**Subtitle Formats:**
- SRT (SubRip), ASS/SSA (Advanced SubStation Alpha), VTT (WebVTT), SUB

## Troubleshooting

### Common Issues

1. **"FFmpeg not found" error:**
   - Ensure FFmpeg is installed and added to your system PATH
   - For portable use, place ffmpeg.exe in the same directory as the application

2. **"Failed to load video" error:**
   - Check if the video file is corrupted
   - Ensure the video format is supported
   - Try with a different video file

3. **Subtitle extraction fails:**
   - The video might not contain any subtitle tracks
   - The subtitle format might not be supported
   - Check FFmpeg installation

4. **UI appears too small/large:**
   - The application adapts to your system's DPI settings
   - Try toggling the theme with the "Toggle Theme" button

### Performance Tips

- **Large video files**: Operations may take longer with large files (>1GB)
- **Multiple operations**: Process one operation at a time for best performance
- **Storage space**: Ensure sufficient disk space for output files

## Development

### Project Structure

```
├── main.py              # Application entry point
├── subtitle_editor.py   # Main UI implementation
├── video_handler.py     # Video and subtitle processing
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## Acknowledgments

- **CustomTkinter**: For the modern UI framework
- **FFmpeg**: For powerful video processing capabilities
- **Python Community**: For excellent libraries and tools

---

For issues, feature requests, or contributions, please visit our project repository. 