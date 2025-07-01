import ffmpeg
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class VideoHandler:
    def __init__(self):
        self.current_video_path = None
        self.subtitle_tracks = []
    
    def load_video(self, video_path: str) -> bool:
        """Load a video file and extract subtitle information"""
        try:
            if not os.path.exists(video_path):
                return False
            
            self.current_video_path = video_path
            self.subtitle_tracks = self._get_subtitle_tracks()
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False
    
    def _get_subtitle_tracks(self) -> List[Dict]:
        """Extract subtitle track information from the video"""
        if not self.current_video_path:
            return []
        
        try:
            # Get video information using ffprobe
            probe = ffmpeg.probe(self.current_video_path)
            
            subtitle_tracks = []
            for i, stream in enumerate(probe['streams']):
                if stream['codec_type'] == 'subtitle':
                    track_info = {
                        'index': i,
                        'stream_index': stream['index'],
                        'codec_name': stream.get('codec_name', 'unknown'),
                        'language': stream.get('tags', {}).get('language', 'unknown'),
                        'title': stream.get('tags', {}).get('title', f'Subtitle Track {len(subtitle_tracks) + 1}'),
                        'disposition': stream.get('disposition', {}),
                        'is_default': stream.get('disposition', {}).get('default', 0) == 1
                    }
                    subtitle_tracks.append(track_info)
            
            return subtitle_tracks
        except Exception as e:
            print(f"Error getting subtitle tracks: {e}")
            return []
    
    def extract_subtitle(self, track_index: int, output_path: str) -> bool:
        """Extract a subtitle track to a file"""
        if not self.current_video_path or track_index >= len(self.subtitle_tracks):
            return False
        
        try:
            track = self.subtitle_tracks[track_index]
            stream_index = track['stream_index']
            
            # Extract subtitle using ffmpeg
            (
                ffmpeg
                .input(self.current_video_path)
                .output(output_path, map=f'0:s:{track_index}')
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except Exception as e:
            print(f"Error extracting subtitle: {e}")
            return False
    
    def remove_subtitle_track(self, track_index: int, output_path: str) -> bool:
        """Create a new video file without the specified subtitle track"""
        if not self.current_video_path or track_index >= len(self.subtitle_tracks):
            return False
        
        try:
            # Get all streams except the subtitle track to remove
            input_stream = ffmpeg.input(self.current_video_path)
            
            # Map all streams except the subtitle track to remove
            streams_to_map = []
            
            # Add video streams
            probe = ffmpeg.probe(self.current_video_path)
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    streams_to_map.append(f"0:{stream['index']}")
                elif stream['codec_type'] == 'audio':
                    streams_to_map.append(f"0:{stream['index']}")
                elif stream['codec_type'] == 'subtitle' and stream['index'] != self.subtitle_tracks[track_index]['stream_index']:
                    streams_to_map.append(f"0:{stream['index']}")
            
            # Build the ffmpeg command
            cmd = ffmpeg.input(self.current_video_path)
            for map_spec in streams_to_map:
                cmd = cmd.output(output_path, map=map_spec, c='copy')
            
            cmd.overwrite_output().run(quiet=True)
            return True
        except Exception as e:
            print(f"Error removing subtitle track: {e}")
            return False
    
    def add_subtitle_track(self, subtitle_file_path: str, output_path: str, language: str = "unknown", title: str = "", is_default: bool = False) -> bool:
        """Add a new subtitle track to the video"""
        print(f"🔄 DEBUG VideoHandler: Starting add_subtitle_track")
        print(f"   📁 Video: {self.current_video_path}")
        print(f"   📄 Subtitle: {subtitle_file_path}")
        print(f"   📤 Output: {output_path}")
        print(f"   🌐 Language: {language}")
        print(f"   📝 Title: {title}")
        print(f"   ⭐ Default: {is_default}")
        print(f"   📊 Current tracks: {len(self.subtitle_tracks)}")
        
        # Validation checks
        if not self.current_video_path:
            print("❌ DEBUG: No current video path")
            return False
            
        if not os.path.exists(self.current_video_path):
            print(f"❌ DEBUG: Video file doesn't exist: {self.current_video_path}")
            return False
            
        if not os.path.exists(subtitle_file_path):
            print(f"❌ DEBUG: Subtitle file doesn't exist: {subtitle_file_path}")
            return False
        
        print("✅ DEBUG: All file validation passed")
        
        try:
            print("🔄 DEBUG: Using subprocess approach for better control")
            
            # Get current subtitle track count for proper indexing
            current_sub_count = len(self.subtitle_tracks)
            print(f"📊 DEBUG: Current subtitle track count: {current_sub_count}")
            
            # Build FFmpeg command manually for better control
            import subprocess
            
            # Determine subtitle format and codec
            subtitle_ext = Path(subtitle_file_path).suffix.lower()
            subtitle_codec = 'copy'
            
            # For ASS/SSA files, we might need to convert them or handle them specially
            if subtitle_ext in ['.ass', '.ssa']:
                print(f"🎭 DEBUG: Detected ASS/SSA subtitle format")
                # Keep original codec for ASS/SSA
                subtitle_codec = 'copy'
            elif subtitle_ext in ['.srt']:
                print(f"📝 DEBUG: Detected SRT subtitle format")
                subtitle_codec = 'copy'
            
            cmd = [
                'ffmpeg',
                '-i', self.current_video_path,      # Input 0: video file
                '-i', subtitle_file_path,           # Input 1: subtitle file
                '-map', '0',                        # Map all streams from input 0 (video)
                '-map', '1:0',                      # Map stream 0 from input 1 (subtitle)
                '-c:v', 'copy',                     # Copy video without re-encoding
                '-c:a', 'copy',                     # Copy audio without re-encoding
                '-c:s', subtitle_codec,             # Handle subtitle codec
                '-y',                               # Overwrite output file
                output_path
            ]
            
            # Add metadata for the NEW subtitle track (use correct index)
            new_sub_index = current_sub_count
            
            if language and language != "unknown":
                cmd.extend([f'-metadata:s:s:{new_sub_index}', f'language={language}'])
                print(f"🌐 DEBUG: Added language metadata for track s:{new_sub_index}: {language}")
            
            if title and title.strip():
                cmd.extend([f'-metadata:s:s:{new_sub_index}', f'title={title}'])
                print(f"📝 DEBUG: Added title metadata for track s:{new_sub_index}: {title}")
            
            # Set disposition for the NEW subtitle track
            if is_default:
                cmd.extend([f'-disposition:s:s:{new_sub_index}', 'default'])
                print(f"⭐ DEBUG: Set track s:{new_sub_index} as default")
            
            print(f"🔄 DEBUG: FFmpeg command: {' '.join(cmd)}")
            
            print("🔄 DEBUG: Running FFmpeg command via subprocess...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            print(f"📤 DEBUG: FFmpeg return code: {result.returncode}")
            if result.stdout:
                print(f"📤 DEBUG: FFmpeg stdout: {result.stdout}")
            if result.stderr:
                print(f"📤 DEBUG: FFmpeg stderr: {result.stderr}")
            
            if result.returncode == 0:
                print("✅ DEBUG: FFmpeg command completed successfully")
                print(f"📤 DEBUG: Output file created: {os.path.exists(output_path)}")
                if os.path.exists(output_path):
                    output_size = os.path.getsize(output_path)
                    print(f"📏 DEBUG: Output file size: {output_size} bytes")
                return True
            else:
                print(f"❌ DEBUG: FFmpeg failed with return code: {result.returncode}")
                return False
            
            print("✅ DEBUG: FFmpeg command completed successfully")
            print(f"📤 DEBUG: Output file created: {os.path.exists(output_path)}")
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                print(f"📏 DEBUG: Output file size: {output_size} bytes")
            
            return True
            
        except ffmpeg.Error as e:
            print(f"❌ DEBUG: FFmpeg error occurred")
            print(f"   📤 stdout: {e.stdout.decode() if e.stdout else 'None'}")
            print(f"   📤 stderr: {e.stderr.decode() if e.stderr else 'None'}")
            return False
        except Exception as e:
            print(f"❌ DEBUG: General error adding subtitle track: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return False
    
    def add_subtitle_track_inplace(self, subtitle_file_path: str, temp_output_path: str, language: str = "unknown", title: str = "", is_default: bool = False) -> bool:
        """Add subtitle track and replace current video in-place"""
        print(f"🔄 DEBUG VideoHandler: Starting add_subtitle_track_inplace")
        
        # First add the subtitle track to temporary file
        success = self.add_subtitle_track(subtitle_file_path, temp_output_path, language, title, is_default)
        
        if success and os.path.exists(temp_output_path):
            print("✅ DEBUG: Subtitle added to temp file, replacing original...")
            try:
                # Replace the original file with the new one
                import shutil
                shutil.move(temp_output_path, self.current_video_path)
                print("✅ DEBUG: Original file replaced successfully")
                
                # Reload the video to update subtitle tracks
                self.load_video(self.current_video_path)
                print("✅ DEBUG: Video reloaded with new subtitle track")
                
                return True
            except Exception as e:
                print(f"❌ DEBUG: Error replacing original file: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                return False
        else:
            print("❌ DEBUG: Failed to create temp file with subtitle")
            return False
    
    def set_default_subtitle(self, track_index: int, output_path: str) -> bool:
        """Set a subtitle track as default"""
        if not self.current_video_path or track_index >= len(self.subtitle_tracks):
            return False
        
        try:
            input_stream = ffmpeg.input(self.current_video_path)
            
            # Build disposition arguments
            disposition_args = {}
            for i, track in enumerate(self.subtitle_tracks):
                if i == track_index:
                    disposition_args[f'disposition:s:{i}'] = 'default'
                else:
                    disposition_args[f'disposition:s:{i}'] = '0'
            
            output_args = {
                'c': 'copy',
                **disposition_args
            }
            
            (
                ffmpeg
                .output(input_stream, output_path, **output_args)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except Exception as e:
            print(f"Error setting default subtitle: {e}")
            return False
    
    def get_video_info(self) -> Dict:
        """Get basic video information"""
        if not self.current_video_path:
            return {}
        
        try:
            probe = ffmpeg.probe(self.current_video_path)
            format_info = probe.get('format', {})
            
            return {
                'filename': os.path.basename(self.current_video_path),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'format': format_info.get('format_name', 'unknown')
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {} 