#!/usr/bin/env python3
"""
QuickTime Playlist Manager with GUI
Play multiple video files in custom order with reordering capability
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import time

class QuickTimePlaylistManager:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Playlist Manager")
        self.root.geometry("600x500")
        
        # Playlist data
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # Top frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_playlist).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Play All", command=self.play_all).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Play Selected", command=self.play_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Stop", command=self.stop_playback).pack(side=tk.LEFT, padx=5)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Reorder buttons
        reorder_frame = tk.Frame(self.root)
        reorder_frame.pack(pady=5)
        
        tk.Button(reorder_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=5)
        tk.Button(reorder_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=5)
        tk.Button(reorder_frame, text="Remove", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        
        # Playback control buttons
        tk.Label(reorder_frame, text="  |  ").pack(side=tk.LEFT)
        tk.Button(reorder_frame, text="◀ Previous", command=self.play_previous).pack(side=tk.LEFT, padx=5)
        tk.Button(reorder_frame, text="Next ▶", command=self.play_next).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Bind drag and drop (only if tkinterdnd2 is available)
        try:
            self.root.drop_target_register(tk.DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop_files)
        except AttributeError:
            # tkinterdnd2 not available, continue without drag and drop
            pass
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[("Video files", "*.mp4 *.mov *.m4v *.avi"), ("All files", "*.*")]
        )
        
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                self.listbox.insert(tk.END, os.path.basename(file))
                
    def clear_playlist(self):
        self.playlist.clear()
        self.listbox.delete(0, tk.END)
        self.status_label.config(text="Playlist cleared")
        
    def move_up(self):
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        index = selection[0]
        self.playlist[index], self.playlist[index-1] = self.playlist[index-1], self.playlist[index]
        
        value = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index-1, value)
        self.listbox.selection_set(index-1)
        
    def move_down(self):
        selection = self.listbox.curselection()
        if not selection or selection[0] == len(self.playlist)-1:
            return
            
        index = selection[0]
        self.playlist[index], self.playlist[index+1] = self.playlist[index+1], self.playlist[index]
        
        value = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index+1, value)
        self.listbox.selection_set(index+1)
        
    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        del self.playlist[index]
        self.listbox.delete(index)
        
    def play_all(self):
        if not self.playlist:
            messagebox.showwarning("No Files", "Please add video files to the playlist first")
            return
            
        self.is_playing = True
        self.current_index = 0
        threading.Thread(target=self._play_thread, daemon=True).start()
        
    def play_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a video to play")
            return
            
        self.is_playing = True
        self.current_index = selection[0]
        threading.Thread(target=self._play_single, args=(self.current_index,), daemon=True).start()
        
    def play_next(self):
        if not self.playlist:
            return
            
        if self.current_index < len(self.playlist) - 1:
            self.stop_playback()
            self.current_index += 1
            self.is_playing = True
            threading.Thread(target=self._play_single, args=(self.current_index,), daemon=True).start()
        else:
            messagebox.showinfo("End of Playlist", "This is the last video")
            
    def play_previous(self):
        if not self.playlist:
            return
            
        if self.current_index > 0:
            self.stop_playback()
            self.current_index -= 1
            self.is_playing = True
            threading.Thread(target=self._play_single, args=(self.current_index,), daemon=True).start()
        else:
            messagebox.showinfo("Start of Playlist", "This is the first video")
        
    def _play_thread(self):
        for i in range(self.current_index, len(self.playlist)):
            if not self.is_playing:
                break
                
            self.current_index = i
            self._play_video(self.playlist[i])
                
        self.root.after(0, self._update_status, "Playback completed")
        self.root.after(0, self._highlight_current, -1)
        self.is_playing = False
        
    def _play_single(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self._play_video(self.playlist[index])
            self.is_playing = False
            
    def _play_video(self, video_path):
        self.root.after(0, self._update_status, f"Playing: {os.path.basename(video_path)}")
        self.root.after(0, self._highlight_current, self.current_index)
        
        # Play video using AppleScript
        applescript = f'''
        tell application "QuickTime Player"
            activate
            set videoDoc to open POSIX file "{video_path}"
            play videoDoc
            repeat while (playing of videoDoc)
                delay 0.5
            end repeat
            close videoDoc saving no
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
        except subprocess.CalledProcessError:
            self.root.after(0, self._update_status, f"Error playing: {os.path.basename(video_path)}")
        
    def _update_status(self, text):
        self.status_label.config(text=text)
        
    def _highlight_current(self, index):
        self.listbox.selection_clear(0, tk.END)
        if index >= 0:
            self.listbox.selection_set(index)
            
    def stop_playback(self):
        self.is_playing = False
        # Stop QuickTime Player
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to close every document saving no'], check=False)
        self.status_label.config(text="Playback stopped")
        
    def drop_files(self, event):
        # Note: This requires tkinterdnd2 package
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.m4v', '.avi')):
                if file not in self.playlist:
                    self.playlist.append(file)
                    self.listbox.insert(tk.END, os.path.basename(file))

def main():
    # Try to import tkinterdnd2 for drag and drop support
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        # Continue without drag and drop support
        root = tk.Tk()
        
    app = QuickTimePlaylistManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()