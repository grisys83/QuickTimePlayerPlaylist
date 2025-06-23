#!/usr/bin/env python3
"""
QuickTime Converter & Player
3-column interface for audio conversion and playlist management
"""

import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import threading
import time
from pathlib import Path
import shutil
import tempfile
from datetime import datetime
import re

class QuickTimeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Converter & Player")
        self.root.geometry("1400x800")
        
        # Performance optimization
        self.root.update_idletasks()
        
        # Data
        self.current_folder = None
        self.audio_files = []
        self.converted_files = []
        self.playlist = []
        self.is_playing = False
        self.current_index = 0
        
        # Settings
        self.settings = {
            'airplay_enabled': True,
            'play_icon_coords': {'x': 0, 'y': 0},
            'airplay_icon_coords': {'x': 844, 'y': 714},
            'apple_tv_coords': {'x': 970, 'y': 784}
        }
        self.load_settings()
        
        # Setup UI
        self.setup_menu()
        self.setup_ui()
        
        # Initial folder - 시작 시 폴더 선택 안 함
        # self.select_folder()
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Folder", command=self.select_folder)
        file_menu.add_command(label="Save Playlist", command=self.save_playlist)
        file_menu.add_command(label="Load Playlist", command=self.load_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Coordinates", command=self.configure_coordinates)
        settings_menu.add_command(label="Test Click Position", command=self.test_click_position)
        
    def setup_ui(self):
        """Setup main UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Column 1: Audio files
        col1_frame = ttk.Frame(main_frame)
        col1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ttk.Label(col1_frame, text="Audio Files", font=('Arial', 12, 'bold')).pack()
        
        # Audio listbox
        audio_scroll = ttk.Scrollbar(col1_frame)
        audio_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.audio_listbox = tk.Listbox(col1_frame, 
                                        yscrollcommand=audio_scroll.set,
                                        selectmode=tk.EXTENDED,
                                        exportselection=False,  # 성능 개선
                                        bg='white', fg='black',
                                        height=25)
        self.audio_listbox.pack(fill=tk.BOTH, expand=True)
        audio_scroll.config(command=self.audio_listbox.yview)
        
        # Convert button
        convert_frame = ttk.Frame(main_frame)
        convert_frame.grid(row=0, column=1, sticky="ns", padx=5)
        
        ttk.Button(convert_frame, text="→\nConvert", 
                  command=self.convert_selected,
                  width=8).pack(pady=(200, 0))
        
        # Column 2: Converted files
        col2_frame = ttk.Frame(main_frame)
        col2_frame.grid(row=0, column=2, sticky="nsew", padx=5)
        
        ttk.Label(col2_frame, text="Converted Videos", font=('Arial', 12, 'bold')).pack()
        
        # Converted listbox
        converted_scroll = ttk.Scrollbar(col2_frame)
        converted_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.converted_listbox = tk.Listbox(col2_frame,
                                           yscrollcommand=converted_scroll.set,
                                           selectmode=tk.EXTENDED,
                                           exportselection=False,  # 성능 개선
                                           bg='white', fg='black',
                                           height=25)
        self.converted_listbox.pack(fill=tk.BOTH, expand=True)
        converted_scroll.config(command=self.converted_listbox.yview)
        
        # Add/Remove buttons
        playlist_control_frame = ttk.Frame(main_frame)
        playlist_control_frame.grid(row=0, column=3, sticky="ns", padx=5)
        
        self.add_button = ttk.Button(playlist_control_frame, text="→", 
                                     command=self.add_to_playlist,
                                     width=5)
        self.add_button.pack(pady=(180, 5))
        ttk.Button(playlist_control_frame, text="←", 
                  command=self.remove_from_playlist,
                  width=5).pack()
        
        # Column 3: Playlist
        col3_frame = ttk.Frame(main_frame)
        col3_frame.grid(row=0, column=4, sticky="nsew", padx=(5, 0))
        
        ttk.Label(col3_frame, text="Playlist", font=('Arial', 12, 'bold')).pack()
        
        # Playlist listbox
        playlist_scroll = ttk.Scrollbar(col3_frame)
        playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_listbox = tk.Listbox(col3_frame,
                                          yscrollcommand=playlist_scroll.set,
                                          selectmode=tk.EXTENDED,
                                          exportselection=False,  # 성능 개선
                                          bg='white', fg='black',
                                          height=20)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        playlist_scroll.config(command=self.playlist_listbox.yview)
        
        # Enable drag and drop for playlist
        self.playlist_listbox.bind('<Button-1>', self.on_drag_start)
        self.playlist_listbox.bind('<B1-Motion>', self.on_drag_motion)
        self.playlist_listbox.bind('<ButtonRelease-1>', self.on_drag_release)
        self.drag_start = None
        
        # Playlist controls
        control_frame = ttk.Frame(col3_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="▶ Play Selected", 
                  command=self.play_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="▶ Play All", 
                  command=self.play_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏹ Stop", 
                  command=self.stop_playback).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_columnconfigure(4, weight=1)
        
    def select_folder(self):
        """Select folder containing audio files"""
        folder = filedialog.askdirectory(title="Select Audio Folder")
        if not folder:
            return
            
        self.current_folder = folder
        self.refresh_file_lists()
        self.status_var.set(f"Folder: {folder}")
        
    def refresh_file_lists(self):
        """Refresh audio and converted file lists"""
        if not self.current_folder:
            return
            
        # Clear lists
        self.audio_listbox.delete(0, tk.END)
        self.converted_listbox.delete(0, tk.END)
        self.audio_files.clear()
        self.converted_files.clear()
        
        # Get files
        folder_path = Path(self.current_folder)
        audio_extensions = ['.mp3', '.m4a', '.aac', '.wav', '.flac']
        
        # Find audio files
        for ext in audio_extensions:
            for file in folder_path.glob(f'*{ext}'):
                self.audio_files.append(str(file))
                self.audio_listbox.insert(tk.END, file.name)
                
        # Find converted files
        for file in folder_path.glob('*_converted.mp4'):
            self.converted_files.append(str(file))
            self.converted_listbox.insert(tk.END, file.name)
            
        # Force update
        self.root.update_idletasks()
            
    def sanitize_filename(self, filename):
        """Sanitize filename for cross-platform compatibility"""
        # Remove path if present
        filename = os.path.basename(filename)
        
        # Replace problematic characters
        # Windows forbidden: < > : " | ? * \
        # Also handle / for all platforms
        forbidden_chars = '<>:"|?*\\/\0'
        for char in forbidden_chars:
            filename = filename.replace(char, '_')
            
        # Remove trailing dots and spaces (Windows issue)
        filename = filename.rstrip('. ')
        
        # Handle Unicode normalization for CJK
        import unicodedata
        filename = unicodedata.normalize('NFC', filename)
        
        # Limit length (255 bytes for most filesystems)
        name, ext = os.path.splitext(filename)
        if len(filename.encode('utf-8')) > 255:
            # Truncate name part while preserving extension
            while len((name + ext).encode('utf-8')) > 255:
                name = name[:-1]
            filename = name + ext
            
        return filename
        
    def convert_selected(self):
        """Convert selected audio files to video"""
        selected = self.audio_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select audio files to convert")
            return
            
        # Get selected files
        files_to_convert = [self.audio_files[i] for i in selected]
        
        # Update status immediately for responsiveness
        self.status_var.set(f"Starting conversion of {len(files_to_convert)} files...")
        self.root.update_idletasks()
        
        # Start conversion in thread
        threading.Thread(target=self._convert_files, args=(files_to_convert,), daemon=True).start()
        
    def _convert_files(self, files):
        """Convert audio files to video (thread)"""
        from audio_to_video_minimal import MinimalAudioToVideoConverter
        
        converter = MinimalAudioToVideoConverter()
        total = len(files)
        
        for i, audio_file in enumerate(files, 1):
            self.status_var.set(f"Converting {i}/{total}: {Path(audio_file).name}")
            
            # Check if already converted
            output_path = Path(audio_file).parent / f"{Path(audio_file).stem}_converted.mp4"
            if not output_path.exists():
                converter.convert_to_video(audio_file)
                
        self.root.after(0, self.refresh_file_lists)
        self.status_var.set(f"Conversion complete: {total} files")
        
    def add_to_playlist(self):
        """Add selected converted files to playlist"""
        print("Add button clicked")  # 디버그
        selected = self.converted_listbox.curselection()
        if not selected:
            print("No selection")
            return
            
        print(f"Adding {len(selected)} items")  # 디버그
        for index in selected:
            file_path = self.converted_files[index]
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                # Path 객체 생성 대신 문자열 처리
                filename = os.path.basename(file_path)
                self.playlist_listbox.insert(tk.END, filename)
                
        self.root.update_idletasks()
        print("Add complete")  # 디버그
                
    def remove_from_playlist(self):
        """Remove selected items from playlist"""
        selected = list(self.playlist_listbox.curselection())
        for index in reversed(selected):
            del self.playlist[index]
            self.playlist_listbox.delete(index)
            
    def on_drag_start(self, event):
        """Start drag operation"""
        self.drag_start = self.playlist_listbox.nearest(event.y)
        
    def on_drag_motion(self, event):
        """Handle drag motion"""
        if self.drag_start is None:
            return
            
        current = self.playlist_listbox.nearest(event.y)
        if current != self.drag_start:
            # Swap items
            self.playlist[self.drag_start], self.playlist[current] = \
                self.playlist[current], self.playlist[self.drag_start]
                
            # Update display
            item1 = self.playlist_listbox.get(self.drag_start)
            item2 = self.playlist_listbox.get(current)
            
            self.playlist_listbox.delete(self.drag_start)
            self.playlist_listbox.insert(self.drag_start, item2)
            
            self.playlist_listbox.delete(current)
            self.playlist_listbox.insert(current, item1)
            
            self.drag_start = current
            
    def on_drag_release(self, event):
        """End drag operation"""
        self.drag_start = None
        
    def play_selected(self):
        """Play selected playlist item"""
        selected = self.playlist_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a video to play")
            return
            
        video_path = self.playlist[selected[0]]
        threading.Thread(target=self._play_single_video, args=(video_path,), daemon=True).start()
        
    def play_all(self):
        """Play entire playlist"""
        if not self.playlist:
            messagebox.showinfo("Empty Playlist", "Playlist is empty")
            return
            
        self.is_playing = True
        self.current_index = 0
        threading.Thread(target=self._play_playlist, daemon=True).start()
        
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.status_var.set("Playback stopped")
        
    def _play_single_video(self, video_path):
        """Play single video"""
        self.status_var.set(f"Playing: {os.path.basename(video_path)}")
        self._play_video(video_path)
        self.status_var.set("Ready")
        
    def _play_playlist(self):
        """Play playlist (thread)"""
        while self.is_playing and self.current_index < len(self.playlist):
            video_path = self.playlist[self.current_index]
            self.status_var.set(f"Playing [{self.current_index + 1}/{len(self.playlist)}]: {os.path.basename(video_path)}")
            
            # Highlight current item
            self.root.after(0, lambda idx=self.current_index: self._highlight_current(idx))
            
            self._play_video(video_path)
            self.current_index += 1
            
        self.is_playing = False
        self.status_var.set("Playlist finished")
        
    def _highlight_current(self, index):
        """Highlight current playing item"""
        self.playlist_listbox.selection_clear(0, tk.END)
        self.playlist_listbox.selection_set(index)
        self.playlist_listbox.see(index)
        
    def _play_video(self, video_path):
        """Play video in QuickTime"""
        # Close any open documents
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(0.5)
        
        # Open video
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(1)
        
        # Enable AirPlay if configured
        if self.settings['airplay_enabled'] and shutil.which('cliclick'):
            self._enable_airplay()
            
        # Start playing
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for playback
        time.sleep(2)
        while self.is_playing and self._is_video_playing():
            time.sleep(1)
            
    def _enable_airplay(self):
        """Enable AirPlay using cliclick"""
        try:
            # Click AirPlay button
            x = self.settings['airplay_icon_coords']['x']
            y = self.settings['airplay_icon_coords']['y']
            subprocess.run(['cliclick', f'c:{x},{y}'])
            time.sleep(0.5)
            
            # Click Apple TV
            x = self.settings['apple_tv_coords']['x']
            y = self.settings['apple_tv_coords']['y']
            subprocess.run(['cliclick', f'c:{x},{y}'])
        except:
            pass
            
    def _is_video_playing(self):
        """Check if video is playing"""
        result = subprocess.run([
            'osascript', '-e',
            '''tell application "QuickTime Player"
                if (count documents) > 0 then
                    return playing of front document
                else
                    return false
                end if
            end tell'''
        ], capture_output=True, text=True)
        
        return result.stdout.strip() == "true"
        
    def configure_coordinates(self):
        """Configure click coordinates"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Coordinates")
        dialog.geometry("400x300")
        
        # AirPlay icon
        ttk.Label(dialog, text="AirPlay Icon Coordinates:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(dialog, text="X:").grid(row=0, column=1)
        airplay_x = ttk.Entry(dialog, width=10)
        airplay_x.insert(0, str(self.settings['airplay_icon_coords']['x']))
        airplay_x.grid(row=0, column=2, padx=5)
        
        ttk.Label(dialog, text="Y:").grid(row=0, column=3)
        airplay_y = ttk.Entry(dialog, width=10)
        airplay_y.insert(0, str(self.settings['airplay_icon_coords']['y']))
        airplay_y.grid(row=0, column=4, padx=5)
        
        # Apple TV checkbox
        ttk.Label(dialog, text="Apple TV Coordinates:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(dialog, text="X:").grid(row=1, column=1)
        appletv_x = ttk.Entry(dialog, width=10)
        appletv_x.insert(0, str(self.settings['apple_tv_coords']['x']))
        appletv_x.grid(row=1, column=2, padx=5)
        
        ttk.Label(dialog, text="Y:").grid(row=1, column=3)
        appletv_y = ttk.Entry(dialog, width=10)
        appletv_y.insert(0, str(self.settings['apple_tv_coords']['y']))
        appletv_y.grid(row=1, column=4, padx=5)
        
        # Enable/Disable AirPlay
        airplay_var = tk.BooleanVar(value=self.settings['airplay_enabled'])
        ttk.Checkbutton(dialog, text="Enable AirPlay", variable=airplay_var).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Instructions
        instructions = ttk.Label(dialog, text="Tip: Use 'cliclick p' in Terminal to get mouse coordinates", 
                                foreground="gray")
        instructions.grid(row=3, column=0, columnspan=5, pady=10)
        
        # Get current position button
        def get_current_position():
            """Get current mouse position using cliclick"""
            if shutil.which('cliclick'):
                result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
                if result.stdout:
                    # Parse "123,456" format
                    coords = result.stdout.strip().split(',')
                    if len(coords) == 2:
                        messagebox.showinfo("Current Mouse Position", 
                                          f"X: {coords[0]}, Y: {coords[1]}")
            else:
                messagebox.showerror("Error", "cliclick not found. Install with: brew install cliclick")
                
        ttk.Button(dialog, text="Get Current Mouse Position", 
                  command=get_current_position).grid(row=4, column=0, columnspan=5, pady=10)
        
        def save_settings():
            try:
                self.settings['airplay_icon_coords']['x'] = int(airplay_x.get())
                self.settings['airplay_icon_coords']['y'] = int(airplay_y.get())
                self.settings['apple_tv_coords']['x'] = int(appletv_x.get())
                self.settings['apple_tv_coords']['y'] = int(appletv_y.get())
                self.settings['airplay_enabled'] = airplay_var.get()
                self.save_settings()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers")
                
        ttk.Button(dialog, text="Save", command=save_settings).grid(row=5, column=0, columnspan=5, pady=20)
        
    def test_click_position(self):
        """Test click position with visual feedback"""
        # Simple approach: show small windows at the coordinates
        for coord_name, coord_data, color in [
            ("AirPlay", self.settings['airplay_icon_coords'], "red"),
            ("Apple TV", self.settings['apple_tv_coords'], "blue")
        ]:
            marker = tk.Toplevel(self.root)
            marker.overrideredirect(True)
            marker.attributes('-topmost', True)
            
            # Create a small colored window
            frame = tk.Frame(marker, bg=color, width=40, height=40)
            frame.pack()
            
            # Add label
            label = tk.Label(frame, text=coord_name, bg=color, fg="white", font=('Arial', 10, 'bold'))
            label.place(x=2, y=10)
            
            # Position the window
            x = coord_data['x'] - 20  # Center the 40x40 window
            y = coord_data['y'] - 20
            marker.geometry(f"40x40+{x}+{y}")
            
            # Auto close after 3 seconds
            marker.after(3000, marker.destroy)
            
        # Also run cliclick to show actual click positions
        if shutil.which('cliclick'):
            # Show where clicks will happen
            subprocess.run(['cliclick', f"m:{self.settings['airplay_icon_coords']['x']},{self.settings['airplay_icon_coords']['y']}"])
            
        self.status_var.set("Red = AirPlay, Blue = Apple TV. Use 'cliclick p' in Terminal for current mouse position.")
        
    def save_playlist(self):
        """Save playlist to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"Playlist saved: {filename}")
            
    def load_playlist(self):
        """Load playlist from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.playlist = json.load(f)
                
            self.playlist_listbox.delete(0, tk.END)
            for filepath in self.playlist:
                self.playlist_listbox.insert(tk.END, Path(filepath).name)
                
            self.status_var.set(f"Playlist loaded: {filename}")
            
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
            
    def load_settings(self):
        """Load settings from file"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass

def main():
    root = tk.Tk()
    app = QuickTimeConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()