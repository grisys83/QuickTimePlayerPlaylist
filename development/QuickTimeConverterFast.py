#!/usr/bin/env python3
"""
QuickTime Converter & Player - Fast Version
Optimized for macOS performance issues
"""

import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
# Force software rendering to avoid macOS GPU issues
os.environ['PYTHONASYNCIODEBUG'] = '0'

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import threading
import time
from pathlib import Path
import shutil

class QuickTimeConverterFast:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Converter & Player - Fast")
        
        # Optimize window
        self.root.geometry("1200x700")
        
        # Force update to ensure proper initialization
        self.root.update()
        
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
            'airplay_icon_coords': {'x': 844, 'y': 714},
            'apple_tv_coords': {'x': 970, 'y': 784}
        }
        
        # Simple UI
        self.setup_simple_ui()
        
    def setup_simple_ui(self):
        """Simplified UI for better performance"""
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(control_frame, text="Select Folder", 
                 command=self.select_folder,
                 bg='#007AFF', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Convert Selected", 
                 command=self.convert_selected,
                 bg='#34C759', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Add to Playlist →", 
                 command=self.add_to_playlist,
                 bg='#FF9500', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Lists frame
        lists_frame = tk.Frame(main_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Audio files
        left_frame = tk.Frame(lists_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="Audio Files", font=('Arial', 14, 'bold')).pack()
        
        # Simple listbox without scrollbar for performance
        self.audio_listbox = tk.Listbox(left_frame, 
                                       selectmode=tk.EXTENDED,
                                       bg='white', 
                                       fg='black',
                                       font=('Arial', 11),
                                       relief=tk.FLAT,
                                       highlightthickness=0)
        self.audio_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Middle: Converted
        middle_frame = tk.Frame(lists_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(middle_frame, text="Converted Videos", font=('Arial', 14, 'bold')).pack()
        
        self.converted_listbox = tk.Listbox(middle_frame,
                                           selectmode=tk.EXTENDED,
                                           bg='white',
                                           fg='black',
                                           font=('Arial', 11),
                                           relief=tk.FLAT,
                                           highlightthickness=0)
        self.converted_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Right: Playlist
        right_frame = tk.Frame(lists_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="Playlist", font=('Arial', 14, 'bold')).pack()
        
        self.playlist_listbox = tk.Listbox(right_frame,
                                          selectmode=tk.EXTENDED,
                                          bg='white',
                                          fg='black',
                                          font=('Arial', 11),
                                          relief=tk.FLAT,
                                          highlightthickness=0)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Playback controls
        playback_frame = tk.Frame(main_frame)
        playback_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(playback_frame, text="▶ Play Selected", 
                 command=self.play_selected,
                 bg='#007AFF', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(playback_frame, text="▶ Play All", 
                 command=self.play_all,
                 bg='#34C759', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(playback_frame, text="⏹ Stop", 
                 command=self.stop_playback,
                 bg='#FF3B30', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(playback_frame, text="Remove from Playlist", 
                 command=self.remove_from_playlist,
                 bg='#8E8E93', fg='white').pack(side=tk.RIGHT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.root, textvariable=self.status_var, 
                         bg='#F2F2F7', relief=tk.SUNKEN)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
    def select_folder(self):
        """Select folder - optimized"""
        folder = filedialog.askdirectory(title="Select Audio Folder")
        if not folder:
            return
            
        self.current_folder = folder
        self.refresh_file_lists()
        
    def refresh_file_lists(self):
        """Refresh lists - optimized"""
        if not self.current_folder:
            return
            
        # Clear
        self.audio_listbox.delete(0, tk.END)
        self.converted_listbox.delete(0, tk.END)
        self.audio_files = []
        self.converted_files = []
        
        # Get files
        folder_path = Path(self.current_folder)
        
        # Audio files
        for ext in ['.mp3', '.m4a', '.aac', '.wav', '.flac']:
            for file in folder_path.glob(f'*{ext}'):
                self.audio_files.append(str(file))
                self.audio_listbox.insert(tk.END, file.name)
                
        # Converted files
        for file in folder_path.glob('*_converted.mp4'):
            self.converted_files.append(str(file))
            self.converted_listbox.insert(tk.END, file.name)
            
        self.status_var.set(f"Found {len(self.audio_files)} audio, {len(self.converted_files)} converted")
        
    def convert_selected(self):
        """Convert selected"""
        selected = self.audio_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select audio files to convert")
            return
            
        files = [self.audio_files[i] for i in selected]
        self.status_var.set(f"Converting {len(files)} files...")
        
        # Convert in thread
        threading.Thread(target=self._convert_files, args=(files,), daemon=True).start()
        
    def _convert_files(self, files):
        """Convert files in thread"""
        try:
            from audio_to_video_minimal import MinimalAudioToVideoConverter
            converter = MinimalAudioToVideoConverter()
            
            for i, audio_file in enumerate(files, 1):
                self.status_var.set(f"Converting {i}/{len(files)}: {os.path.basename(audio_file)}")
                converter.convert_to_video(audio_file)
                
            self.root.after(0, self.refresh_file_lists)
            self.status_var.set(f"Converted {len(files)} files")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            
    def add_to_playlist(self):
        """Add to playlist"""
        selected = self.converted_listbox.curselection()
        if not selected:
            return
            
        for index in selected:
            file_path = self.converted_files[index]
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                self.playlist_listbox.insert(tk.END, os.path.basename(file_path))
                
    def remove_from_playlist(self):
        """Remove from playlist"""
        selected = list(self.playlist_listbox.curselection())
        for index in reversed(selected):
            del self.playlist[index]
            self.playlist_listbox.delete(index)
            
    def play_selected(self):
        """Play selected"""
        selected = self.playlist_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a video to play")
            return
            
        video_path = self.playlist[selected[0]]
        threading.Thread(target=self._play_single, args=(video_path,), daemon=True).start()
        
    def play_all(self):
        """Play all"""
        if not self.playlist:
            messagebox.showinfo("Empty", "Playlist is empty")
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
        ], capture_output=True)
        self.status_var.set("Stopped")
        
    def _play_single(self, video_path):
        """Play single video"""
        self.status_var.set(f"Playing: {os.path.basename(video_path)}")
        self._play_video(video_path)
        self.status_var.set("Ready")
        
    def _play_playlist(self):
        """Play playlist"""
        while self.is_playing and self.current_index < len(self.playlist):
            video_path = self.playlist[self.current_index]
            self.status_var.set(f"Playing {self.current_index + 1}/{len(self.playlist)}")
            self._play_video(video_path)
            self.current_index += 1
            
        self.is_playing = False
        self.status_var.set("Playlist finished")
        
    def _play_video(self, video_path):
        """Play video"""
        # Close existing
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        
        time.sleep(0.3)
        
        # Open new
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(0.8)
        
        # Play
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], capture_output=True)
        
        # Wait
        time.sleep(1)
        while self.is_playing:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to playing of front document'
            ], capture_output=True, text=True)
            
            if result.stdout.strip() != "true":
                break
            time.sleep(1)

def main():
    root = tk.Tk()
    
    # Try to improve performance
    root.tk.call('tk', 'useinputmethods', '0')
    
    app = QuickTimeConverterFast(root)
    root.mainloop()

if __name__ == "__main__":
    main()