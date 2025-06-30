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
        if not self.current_video_path or not os.path.exists(subtitle_file_path):
            return False
        
        try:
            video_input = ffmpeg.input(self.current_video_path)
            subtitle_input = ffmpeg.input(subtitle_file_path)
            
            # Prepare metadata
            metadata = {}
            if language != "unknown":
                metadata[f'metadata:s:s:{len(self.subtitle_tracks)}'] = f'language={language}'
            if title:
                metadata[f'metadata:s:s:{len(self.subtitle_tracks)}'] = f'title={title}'
            
            # Set disposition
            disposition = {}
            if is_default:
                disposition[f'disposition:s:s:{len(self.subtitle_tracks)}'] = 'default'
            
            # Combine video and subtitle
            output_args = {
                'c:v': 'copy',
                'c:a': 'copy',
                'c:s': 'copy',
                **metadata,
                **disposition
            }
            
            (
                ffmpeg
                .output(video_input, subtitle_input, output_path, **output_args)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except Exception as e:
            print(f"Error adding subtitle track: {e}")
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