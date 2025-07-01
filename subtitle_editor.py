import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import threading
from pathlib import Path
from video_handler import VideoHandler

# Set appearance mode and theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SubtitleEditor:
    def __init__(self):
        self.video_handler = VideoHandler()
        self.current_video_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the main UI"""
        self.root = ctk.CTk()
        self.root.title("Subtitle Editor")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure grid weight
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Header frame
        header_frame = ctk.CTkFrame(self.root, height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(header_frame, text="Subtitle Editor", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Sidebar
        sidebar_frame = ctk.CTkFrame(self.root, width=200)
        sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        sidebar_frame.grid_propagate(False)
        
        # Video controls
        self.video_button = ctk.CTkButton(sidebar_frame, text="Select Video", 
                                         command=self.select_video, height=40)
        self.video_button.pack(pady=20, padx=20, fill="x")
        
        # Video info frame
        self.video_info_frame = ctk.CTkFrame(sidebar_frame)
        self.video_info_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        self.video_info_label = ctk.CTkLabel(self.video_info_frame, text="No video selected", 
                                           wraplength=160, justify="left")
        self.video_info_label.pack(pady=10, padx=10)
        
        # Action buttons
        self.add_subtitle_button = ctk.CTkButton(sidebar_frame, text="Add Subtitle", 
                                               command=self.add_subtitle, height=35, state="disabled")
        self.add_subtitle_button.pack(pady=(0, 10), padx=20, fill="x")
        
        self.export_button = ctk.CTkButton(sidebar_frame, text="Export Video", 
                                         command=self.export_video, height=35, state="disabled")
        self.export_button.pack(pady=(0, 10), padx=20, fill="x")
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(sidebar_frame, text="Toggle Theme", 
                                        command=self.toggle_theme, height=30)
        self.theme_button.pack(side="bottom", pady=20, padx=20, fill="x")
        
        # Main content area
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Content header
        content_header = ctk.CTkLabel(main_frame, text="Subtitle Tracks", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
        content_header.grid(row=0, column=0, pady=20, padx=20, sticky="w")
        
        # Scrollable frame for subtitle tracks
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, label_text="")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Initial message
        self.empty_message = ctk.CTkLabel(self.scroll_frame, 
                                        text="Select a video file to view subtitle tracks",
                                        font=ctk.CTkFont(size=14),
                                        text_color="gray")
        self.empty_message.grid(row=0, column=0, pady=50)
    
    def select_video(self):
        """Open file dialog to select video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )
        
        if file_path:
            self.load_video(file_path)
    
    def load_video(self, video_path):
        """Load video and update UI"""
        # Show loading state
        self.video_button.configure(text="Loading...", state="disabled")
        
        def load_in_thread():
            success = self.video_handler.load_video(video_path)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.on_video_loaded(success, video_path))
        
        # Run in separate thread to prevent UI freezing
        thread = threading.Thread(target=load_in_thread)
        thread.daemon = True
        thread.start()
    
    def on_video_loaded(self, success, video_path):
        """Handle video loading completion"""
        self.video_button.configure(text="Select Video", state="normal")
        
        if success:
            self.current_video_path = video_path
            self.update_video_info()
            self.update_subtitle_tracks()
            self.add_subtitle_button.configure(state="normal")
            self.export_button.configure(state="normal")
        else:
            messagebox.showerror("Error", "Failed to load video file. Please check if the file is valid and FFmpeg is installed.")
    
    def update_video_info(self):
        """Update video information display"""
        video_info = self.video_handler.get_video_info()
        if video_info:
            duration = int(video_info.get('duration', 0))
            size_mb = video_info.get('size', 0) / (1024 * 1024)
            
            info_text = f"File: {video_info.get('filename', 'Unknown')}\n"
            info_text += f"Duration: {duration // 60}:{duration % 60:02d}\n"
            info_text += f"Size: {size_mb:.1f} MB\n"
            info_text += f"Format: {video_info.get('format', 'Unknown')}"
            
            self.video_info_label.configure(text=info_text)
    
    def update_subtitle_tracks(self):
        """Update subtitle tracks display"""
        # Clear existing tracks
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        tracks = self.video_handler.subtitle_tracks
        
        if not tracks:
            empty_label = ctk.CTkLabel(self.scroll_frame, 
                                     text="No subtitle tracks found in this video",
                                     font=ctk.CTkFont(size=14),
                                     text_color="gray")
            empty_label.grid(row=0, column=0, pady=50)
            return
        
        # Create track widgets
        for i, track in enumerate(tracks):
            self.create_track_widget(i, track)
    
    def create_track_widget(self, index, track):
        """Create a widget for a subtitle track"""
        # Track frame
        track_frame = ctk.CTkFrame(self.scroll_frame)
        track_frame.grid(row=index, column=0, sticky="ew", pady=5, padx=5)
        track_frame.grid_columnconfigure(1, weight=1)
        
        # Track info
        title = track.get('title', f'Track {index + 1}')
        language = track.get('language', 'unknown')
        codec = track.get('codec_name', 'unknown')
        is_default = track.get('is_default', False)
        
        info_text = f"{title}\nLanguage: {language} | Codec: {codec}"
        if is_default:
            info_text += " | DEFAULT"
        
        info_label = ctk.CTkLabel(track_frame, text=info_text, justify="left")
        info_label.grid(row=0, column=0, columnspan=2, pady=10, padx=15, sticky="w")
        
        # Button frame
        button_frame = ctk.CTkFrame(track_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        # Extract button
        extract_btn = ctk.CTkButton(button_frame, text="Extract", width=80, height=30,
                                  command=lambda idx=index: self.extract_subtitle(idx))
        extract_btn.pack(side="left", padx=5, pady=5)
        
        # Set default button
        default_btn = ctk.CTkButton(button_frame, text="Set Default", width=90, height=30,
                                  command=lambda idx=index: self.set_default_subtitle(idx))
        default_btn.pack(side="left", padx=5, pady=5)
        
        # Remove button
        remove_btn = ctk.CTkButton(button_frame, text="Remove", width=80, height=30,
                                 fg_color="red", hover_color="darkred",
                                 command=lambda idx=index: self.remove_subtitle(idx))
        remove_btn.pack(side="right", padx=5, pady=5)
    
    def extract_subtitle(self, track_index):
        """Extract subtitle track to file"""
        track = self.video_handler.subtitle_tracks[track_index]
        default_name = f"subtitle_{track_index + 1}_{track.get('language', 'unknown')}.srt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Subtitle File",
            defaultextension=".srt",
            initialfile=default_name,
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        
        if file_path:
            success = self.video_handler.extract_subtitle(track_index, file_path)
            if success:
                messagebox.showinfo("Success", f"Subtitle extracted to:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to extract subtitle")
    
    def add_subtitle(self):
        """Add new subtitle track"""
        print("🔄 DEBUG: Starting add_subtitle()")
        
        # Check if video is loaded
        if not self.current_video_path:
            print("❌ DEBUG: No video loaded")
            messagebox.showerror("Error", "Please load a video first")
            return
        
        print(f"✅ DEBUG: Current video: {self.current_video_path}")
        
        file_path = filedialog.askopenfilename(
            title="Select Subtitle File",
            filetypes=[
                ("Subtitle files", "*.srt *.ass *.ssa *.vtt *.sub"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            print("❌ DEBUG: No subtitle file selected")
            return
        
        print(f"✅ DEBUG: Selected subtitle file: {file_path}")
        
        # Check if subtitle file exists
        if not os.path.exists(file_path):
            print(f"❌ DEBUG: Subtitle file doesn't exist: {file_path}")
            messagebox.showerror("Error", f"Subtitle file not found: {file_path}")
            return
        
        print("🔄 DEBUG: Opening subtitle properties dialog")
        
        # Get subtitle properties from user
        dialog = SubtitlePropertiesDialog(self.root)
        self.root.wait_window(dialog.dialog)  # Wait for dialog to close
        print(f"🔄 DEBUG: Dialog closed, checking result: {dialog.result}")
        
        if dialog.result:
            language, title, is_default = dialog.result
            print(f"✅ DEBUG: Dialog result - Language: {language}, Title: {title}, Default: {is_default}")
            
            # Add subtitle to current video in-place (create temporary file)
            print("🔄 DEBUG: Adding subtitle in-place...")
            
            # Create a temporary output file
            import tempfile
            temp_dir = tempfile.gettempdir()
            video_name = Path(self.current_video_path).stem
            temp_output = os.path.join(temp_dir, f"{video_name}_temp_with_subtitle{Path(self.current_video_path).suffix}")
            
            print(f"📁 DEBUG: Temporary output path: {temp_output}")
            
            self.process_video_operation(
                lambda: self.video_handler.add_subtitle_track_inplace(file_path, temp_output, language, title, is_default),
                "Adding subtitle track...",
                "Subtitle added to video!",
                temp_output
            )
        else:
            print("❌ DEBUG: Dialog cancelled or no result")
    
    def remove_subtitle(self, track_index):
        """Remove subtitle track"""
        track = self.video_handler.subtitle_tracks[track_index]
        title = track.get('title', f'Track {track_index + 1}')
        
        if messagebox.askyesno("Confirm", f"Remove subtitle track '{title}'?"):
            video_name = Path(self.current_video_path).stem
            output_path = filedialog.asksaveasfilename(
                title="Save Video without Subtitle",
                defaultextension=Path(self.current_video_path).suffix,
                initialfile=f"{video_name}_removed_subtitle{Path(self.current_video_path).suffix}",
                filetypes=[("Video files", "*.mp4 *.avi *.mkv"), ("All files", "*.*")]
            )
            
            if output_path:
                self.process_video_operation(
                    lambda: self.video_handler.remove_subtitle_track(track_index, output_path),
                    "Removing subtitle track...",
                    "Subtitle removed successfully!",
                    output_path
                )
    
    def set_default_subtitle(self, track_index):
        """Set subtitle track as default"""
        track = self.video_handler.subtitle_tracks[track_index]
        title = track.get('title', f'Track {track_index + 1}')
        
        if messagebox.askyesno("Confirm", f"Set '{title}' as default subtitle?"):
            video_name = Path(self.current_video_path).stem
            output_path = filedialog.asksaveasfilename(
                title="Save Video with Default Subtitle",
                defaultextension=Path(self.current_video_path).suffix,
                initialfile=f"{video_name}_default_subtitle{Path(self.current_video_path).suffix}",
                filetypes=[("Video files", "*.mp4 *.avi *.mkv"), ("All files", "*.*")]
            )
            
            if output_path:
                self.process_video_operation(
                    lambda: self.video_handler.set_default_subtitle(track_index, output_path),
                    "Setting default subtitle...",
                    "Default subtitle set successfully!",
                    output_path
                )
    
    def export_video(self):
        """Export current video"""
        if not self.current_video_path:
            return
        
        output_path = filedialog.asksaveasfilename(
            title="Export Video",
            defaultextension=Path(self.current_video_path).suffix,
            initialfile=f"exported_{Path(self.current_video_path).name}",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv"), ("All files", "*.*")]
        )
        
        if output_path:
            # Simple copy for now
            try:
                import shutil
                shutil.copy2(self.current_video_path, output_path)
                messagebox.showinfo("Success", f"Video exported to:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def process_video_operation(self, operation, loading_text, success_text, output_path):
        """Process video operation with loading UI"""
        print(f"🔄 DEBUG: Starting process_video_operation")
        print(f"   💬 Loading text: {loading_text}")
        print(f"   ✅ Success text: {success_text}")
        print(f"   📤 Output path: {output_path}")
        
        # Create progress dialog
        progress_window = ctk.CTkToplevel(self.root)
        progress_window.title("Processing")
        progress_window.geometry("300x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = ctk.CTkLabel(progress_window, text=loading_text)
        progress_label.pack(pady=30)
        
        progress_bar = ctk.CTkProgressBar(progress_window, mode="indeterminate")
        progress_bar.pack(pady=20)
        progress_bar.start()
        
        def run_operation():
            print("🔄 DEBUG: run_operation thread started")
            try:
                print("🔄 DEBUG: Calling operation function...")
                success = operation()
                print(f"✅ DEBUG: Operation completed with result: {success}")
                self.root.after(0, lambda: self.on_operation_complete(progress_window, success, success_text, output_path))
            except Exception as e:
                print(f"❌ DEBUG: Exception in run_operation: {e}")
                import traceback
                print(f"   📋 Traceback: {traceback.format_exc()}")
                self.root.after(0, lambda: self.on_operation_error(progress_window, str(e)))
        
        print("🔄 DEBUG: Starting operation thread...")
        thread = threading.Thread(target=run_operation)
        thread.daemon = True
        thread.start()
        print("🔄 DEBUG: Thread started successfully")
    
    def on_operation_complete(self, progress_window, success, success_text, output_path):
        """Handle operation completion"""
        print(f"🔄 DEBUG: on_operation_complete called")
        print(f"   ✅ Success: {success}")
        print(f"   💬 Success text: {success_text}")
        print(f"   📤 Output path: {output_path}")
        
        progress_window.destroy()
        
        if success:
            print("✅ DEBUG: Operation was successful")
            
            # Check if this is an in-place operation (temp file)
            if "temp_with_subtitle" in output_path:
                print("🔄 DEBUG: In-place operation detected, refreshing UI")
                messagebox.showinfo("Success", success_text)
                # Refresh the UI to show the new subtitle track
                self.update_subtitle_tracks()
                self.update_video_info()
            else:
                print("✅ DEBUG: Export operation, showing success dialog")
                messagebox.showinfo("Success", f"{success_text}\nSaved to: {output_path}")
                # Optionally reload the new video
                if messagebox.askyesno("Load New Video", "Would you like to load the newly created video?"):
                    print("🔄 DEBUG: User chose to load new video")
                    self.load_video(output_path)
                else:
                    print("🔄 DEBUG: User chose not to load new video")
        else:
            print("❌ DEBUG: Operation failed, showing error dialog")
            messagebox.showerror("Error", "Operation failed")
    
    def on_operation_error(self, progress_window, error_message):
        """Handle operation error"""
        print(f"❌ DEBUG: on_operation_error called")
        print(f"   💬 Error message: {error_message}")
        
        progress_window.destroy()
        messagebox.showerror("Error", f"Operation failed: {error_message}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class SubtitlePropertiesDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Subtitle Properties")
        self.dialog.geometry("350x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Language entry
        ctk.CTkLabel(self.dialog, text="Language Code:").pack(pady=10)
        self.language_var = ctk.StringVar(value="en")
        self.language_entry = ctk.CTkEntry(self.dialog, textvariable=self.language_var)
        self.language_entry.pack(pady=5, padx=20, fill="x")
        
        # Title entry
        ctk.CTkLabel(self.dialog, text="Title:").pack(pady=(20, 10))
        self.title_var = ctk.StringVar()
        self.title_entry = ctk.CTkEntry(self.dialog, textvariable=self.title_var)
        self.title_entry.pack(pady=5, padx=20, fill="x")
        
        # Default checkbox
        self.default_var = ctk.BooleanVar()
        self.default_checkbox = ctk.CTkCheckBox(self.dialog, text="Set as default", 
                                              variable=self.default_var)
        self.default_checkbox.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=20, fill="x", padx=20)
        
        ok_button = ctk.CTkButton(button_frame, text="OK", command=self.ok_clicked)
        ok_button.pack(side="right", padx=5)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_clicked)
        cancel_button.pack(side="right", padx=5)
    
    def ok_clicked(self):
        result = (
            self.language_var.get(),
            self.title_var.get(),
            self.default_var.get()
        )
        print(f"🔄 DEBUG Dialog: OK clicked with result: {result}")
        self.result = result
        self.dialog.destroy()
    
    def cancel_clicked(self):
        print("❌ DEBUG Dialog: Cancel clicked")
        self.dialog.destroy() 