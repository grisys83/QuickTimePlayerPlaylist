#!/usr/bin/env python3
"""
Debug version of audio playlist to find the issue
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import time
import json


class DebugAudioPlaylist(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Debug Audio Playlist")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Debug output
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        self.debug_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Debug Output:"))
        layout.addWidget(self.debug_text)
        
        # Current track label
        self.current_track_label = QLabel("No track playing")
        self.current_track_label.setAlignment(Qt.AlignCenter)
        self.current_track_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.current_track_label)
        
        # Test buttons
        test_layout = QHBoxLayout()
        
        test1_btn = QPushButton("Test Method 1")
        test1_btn.clicked.connect(lambda: self.test_playback_method(1))
        test_layout.addWidget(test1_btn)
        
        test2_btn = QPushButton("Test Method 2")
        test2_btn.clicked.connect(lambda: self.test_playback_method(2))
        test_layout.addWidget(test2_btn)
        
        test3_btn = QPushButton("Test Method 3")
        test3_btn.clicked.connect(lambda: self.test_playback_method(3))
        test_layout.addWidget(test3_btn)
        
        test4_btn = QPushButton("Test Method 4")
        test4_btn.clicked.connect(lambda: self.test_playback_method(4))
        test_layout.addWidget(test4_btn)
        
        layout.addLayout(test_layout)
        
        # File buttons
        button_layout = QHBoxLayout()
        
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        button_layout.addWidget(add_files_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_playlist)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.playlist_widget)
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("Play Selected")
        self.play_btn.clicked.connect(self.play_selected)
        control_layout.addWidget(self.play_btn)
        
        check_btn = QPushButton("Check QuickTime")
        check_btn.clicked.connect(self.check_quicktime_status)
        control_layout.addWidget(check_btn)
        
        layout.addLayout(control_layout)
        
    def log_debug(self, message):
        """Add debug message"""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        self.debug_text.append(f"[{timestamp}] {message}")
        # Also print to console
        print(f"[{timestamp}] {message}")
        # Force UI update
        QApplication.processEvents()
        
    def add_files(self):
        """Add audio files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.m4a *.aac *.wav *.flac);;All Files (*.*)"
        )
        
        if files:
            for file in files:
                self.playlist.append(file)
                self.playlist_widget.addItem(Path(file).name)
            self.log_debug(f"Added {len(files)} files")
    
    def clear_playlist(self):
        """Clear playlist"""
        self.playlist.clear()
        self.playlist_widget.clear()
        self.current_index = -1
        self.log_debug("Playlist cleared")
    
    def on_item_double_clicked(self, item):
        """Play the double-clicked item"""
        self.log_debug("Double-click detected")
        try:
            row = self.playlist_widget.row(item)
            if 0 <= row < len(self.playlist):
                self.current_index = row
                self.play_current_method_1()  # Use method 1 by default
        except Exception as e:
            self.log_debug(f"Error on double click: {e}")
    
    def play_selected(self):
        """Play selected item"""
        current_item = self.playlist_widget.currentItem()
        if current_item:
            self.on_item_double_clicked(current_item)
        else:
            self.log_debug("No item selected")
    
    def test_playback_method(self, method_num):
        """Test specific playback method"""
        if not self.playlist:
            self.log_debug("No files in playlist")
            return
            
        if self.current_index < 0:
            self.current_index = 0
            
        self.log_debug(f"Testing playback method {method_num}")
        
        if method_num == 1:
            self.play_current_method_1()
        elif method_num == 2:
            self.play_current_method_2()
        elif method_num == 3:
            self.play_current_method_3()
        elif method_num == 4:
            self.play_current_method_4()
    
    def play_current_method_1(self):
        """Method 1: Simple AppleScript"""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.log_debug(f"Method 1: Playing {Path(file_path).name}")
            
            # Update UI
            self.current_track_label.setText(f"Playing: {Path(file_path).name}")
            self.playlist_widget.setCurrentRow(self.current_index)
            
            # Close existing documents
            self.log_debug("Closing existing documents...")
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to close every document'
            ], capture_output=True)
            time.sleep(0.5)
            
            # Open and play
            self.log_debug("Opening file...")
            script = f'''
            tell application "QuickTime Player"
                activate
                open POSIX file "{file_path}"
                delay 1
                play front document
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.stderr:
                self.log_debug(f"Error: {result.stderr}")
            else:
                self.log_debug("Success!")
                
    def play_current_method_2(self):
        """Method 2: With new movie recording"""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.log_debug(f"Method 2: Playing {Path(file_path).name}")
            
            # Create dummy recording
            self.log_debug("Creating dummy recording...")
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to new movie recording'
            ], capture_output=True)
            time.sleep(0.5)
            
            # Open and play
            script = f'''
            tell application "QuickTime Player"
                open POSIX file "{file_path}"
                delay 1
                if (count windows) > 1 then close window 2
                play front document
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.stderr:
                self.log_debug(f"Error: {result.stderr}")
            else:
                self.log_debug("Success!")
                
    def play_current_method_3(self):
        """Method 3: Using QProcess"""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.log_debug(f"Method 3: Playing {Path(file_path).name} with QProcess")
            
            # Use QProcess instead of subprocess
            process = QProcess()
            process.finished.connect(lambda: self.log_debug("QProcess finished"))
            
            script = f'''
            tell application "QuickTime Player"
                activate
                open POSIX file "{file_path}"
                delay 1
                play front document
            end tell
            '''
            
            process.start('osascript', ['-e', script])
            process.waitForFinished(3000)  # Wait up to 3 seconds
            
            output = process.readAllStandardOutput().data().decode()
            error = process.readAllStandardError().data().decode()
            
            if error:
                self.log_debug(f"Error: {error}")
            else:
                self.log_debug("Success!")
                
    def play_current_method_4(self):
        """Method 4: Delayed execution"""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.log_debug(f"Method 4: Playing {Path(file_path).name} with delay")
            
            # Use QTimer to delay execution
            QTimer.singleShot(100, lambda: self._delayed_play(file_path))
            
    def _delayed_play(self, file_path):
        """Execute play command after delay"""
        self.log_debug("Executing delayed play...")
        
        script = f'''
        tell application "QuickTime Player"
            activate
            open POSIX file "{file_path}"
            delay 1
            play front document
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stderr:
            self.log_debug(f"Error: {result.stderr}")
        else:
            self.log_debug("Success!")
    
    def check_quicktime_status(self):
        """Check QuickTime status"""
        self.log_debug("Checking QuickTime status...")
        
        # Count documents
        result = subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to count documents'
        ], capture_output=True, text=True)
        self.log_debug(f"Documents open: {result.stdout.strip()}")
        
        # Check if playing
        result = subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else "no documents"'
        ], capture_output=True, text=True)
        self.log_debug(f"Playing status: {result.stdout.strip()}")
        
        # Check if QuickTime is running
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to (name of processes) contains "QuickTime Player"'
        ], capture_output=True, text=True)
        self.log_debug(f"QuickTime running: {result.stdout.strip()}")


def main():
    app = QApplication(sys.argv)
    window = DebugAudioPlaylist()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()