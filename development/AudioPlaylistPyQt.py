#!/usr/bin/env python3
"""
Audio Playlist PyQt - Modern audio playlist with AirPlay support
Built with PyQt5 for better file dialog support on macOS
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from PyQt5.QtGui import *
import subprocess
import json
import random
from datetime import datetime

# No conversion needed - QuickTime plays audio files directly


class PlaylistModel(QAbstractListModel):
    """Model for playlist data"""
    def __init__(self):
        super().__init__()
        self.playlist = []
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.playlist)
    
    def data(self, index, role):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            file_path = self.playlist[index.row()]
            return Path(file_path).name
        elif role == Qt.UserRole:
            return self.playlist[index.row()]
            
        return None
    
    def add_files(self, files):
        """Add files to playlist"""
        self.beginInsertRows(QModelIndex(), len(self.playlist), len(self.playlist) + len(files) - 1)
        self.playlist.extend(files)
        self.endInsertRows()
    
    def remove_file(self, index):
        """Remove file from playlist"""
        if 0 <= index < len(self.playlist):
            self.beginRemoveRows(QModelIndex(), index, index)
            self.playlist.pop(index)
            self.endRemoveRows()
    
    def clear(self):
        """Clear playlist"""
        self.beginResetModel()
        self.playlist.clear()
        self.endResetModel()
    
    def move_item(self, from_index, to_index):
        """Move item in playlist"""
        if from_index == to_index:
            return
            
        if 0 <= from_index < len(self.playlist) and 0 <= to_index <= len(self.playlist):
            # Qt's moveRows is complex, so we'll do it manually
            self.beginResetModel()
            item = self.playlist.pop(from_index)
            if to_index > from_index:
                to_index -= 1
            self.playlist.insert(to_index, item)
            self.endResetModel()


class AudioPlaylistPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_index = -1
        self.is_playing = False
        self.shuffle_mode = False
        self.repeat_mode = False
        self.airplay_enabled = False
        # No converter needed
        
        # Load settings
        self.settings = self.load_settings()
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Audio Playlist PyQt")
        self.setGeometry(100, 100, 800, 600)
        
        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QListView {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                font-size: 14px;
            }
            QListView::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListView::item:selected {
                background-color: #0066cc;
            }
            QListView::item:hover {
                background-color: #3a3a3a;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:checked {
                background-color: #0066cc;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Now playing info
        self.now_playing_label = QLabel("No track playing")
        self.now_playing_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background-color: #2b2b2b;
                border-radius: 5px;
            }
        """)
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.now_playing_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3a3a3a;
                border-radius: 3px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Playlist view
        self.playlist_model = PlaylistModel()
        self.playlist_view = QListView()
        self.playlist_view.setModel(self.playlist_model)
        self.playlist_view.setSelectionMode(QListView.SingleSelection)
        self.playlist_view.doubleClicked.connect(self.on_item_double_clicked)
        
        # Enable drag and drop for reordering
        self.playlist_view.setDragDropMode(QListView.InternalMove)
        self.playlist_view.setDefaultDropAction(Qt.MoveAction)
        
        layout.addWidget(self.playlist_view)
        
        # Control buttons
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { color: #999999; }")
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Timer for playback monitoring
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.check_playback_status)
        
        # Enable drag and drop for files
        self.setAcceptDrops(True)
        
    def create_toolbar(self):
        """Create toolbar with file operations"""
        toolbar = QWidget()
        toolbar.setStyleSheet("QWidget { background-color: #2b2b2b; padding: 5px; }")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Add files button
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        layout.addWidget(add_files_btn)
        
        # Add folder button
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        layout.addWidget(add_folder_btn)
        
        # Clear playlist button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_playlist)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        # Shuffle button
        self.shuffle_btn = QPushButton("Shuffle")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        layout.addWidget(self.shuffle_btn)
        
        # Repeat button
        self.repeat_btn = QPushButton("Repeat")
        self.repeat_btn.setCheckable(True)
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        layout.addWidget(self.repeat_btn)
        
        # AirPlay button
        self.airplay_btn = QPushButton("AirPlay")
        self.airplay_btn.setCheckable(True)
        self.airplay_btn.setChecked(self.settings.get('airplay_enabled', False))
        self.airplay_btn.clicked.connect(self.toggle_airplay)
        if self.airplay_btn.isChecked():
            self.airplay_enabled = True
        layout.addWidget(self.airplay_btn)
        
        return toolbar
    
    def create_controls(self):
        """Create playback control buttons"""
        controls = QWidget()
        controls.setStyleSheet("QWidget { background-color: #2b2b2b; padding: 10px; }")
        layout = QHBoxLayout(controls)
        
        # Previous button
        prev_btn = QPushButton("⏮")
        prev_btn.setFixedSize(50, 50)
        prev_btn.clicked.connect(self.play_previous)
        layout.addWidget(prev_btn)
        
        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(60, 60)
        self.play_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #0066cc;
            }
            QPushButton:hover {
                background-color: #0080ff;
            }
        """)
        self.play_btn.clicked.connect(self.play_pause)
        layout.addWidget(self.play_btn)
        
        # Next button
        next_btn = QPushButton("⏭")
        next_btn.setFixedSize(50, 50)
        next_btn.clicked.connect(self.play_next)
        layout.addWidget(next_btn)
        
        # Center the controls
        layout.setAlignment(Qt.AlignCenter)
        
        return controls
    
    def add_files(self):
        """Add audio files to playlist"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.m4a *.aac *.wav *.flac *.ogg *.wma);;All Files (*.*)"
        )
        
        if files:
            self.playlist_model.add_files(files)
            self.update_status()
            self.status_bar.showMessage(f"Added {len(files)} files", 3000)
    
    def add_folder(self):
        """Add all audio files from a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder:
            audio_extensions = ['.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.wma']
            files = []
            
            folder_path = Path(folder)
            for ext in audio_extensions:
                files.extend(str(f) for f in folder_path.glob(f'*{ext}'))
                files.extend(str(f) for f in folder_path.glob(f'*{ext.upper()}'))
            
            if files:
                self.playlist_model.add_files(sorted(files))
                self.update_status()
                self.status_bar.showMessage(f"Added {len(files)} files from folder", 3000)
            else:
                self.status_bar.showMessage("No audio files found in folder", 3000)
    
    def clear_playlist(self):
        """Clear the playlist"""
        reply = QMessageBox.question(
            self, 
            "Clear Playlist", 
            "Are you sure you want to clear the playlist?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_playback()
            self.playlist_model.clear()
            self.current_index = -1
            self.update_status()
            self.now_playing_label.setText("No track playing")
    
    def on_item_double_clicked(self, index):
        """Play item when double-clicked"""
        self.current_index = index.row()
        self.play_current()
    
    def play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.pause_playback()
        else:
            if self.current_index == -1 and self.playlist_model.rowCount() > 0:
                self.current_index = 0
            self.play_current()
    
    def play_current(self):
        """Play current track"""
        if 0 <= self.current_index < self.playlist_model.rowCount():
            file_path = self.playlist_model.playlist[self.current_index]
            
            # Close any existing QuickTime windows
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to close every document'
            ], capture_output=True)
            
            # QuickTime can play audio files directly
            time.sleep(0.5)
            
            # Open in QuickTime
            subprocess.run(['open', '-a', 'QuickTime Player', file_path])
            time.sleep(1.5)
            
            # Enable AirPlay if needed
            if self.airplay_enabled:
                self.enable_airplay()
            
            # Start playback
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to play front document'
            ], capture_output=True)
            
            self.is_playing = True
            self.play_btn.setText("⏸")
            self.now_playing_label.setText(f"Now Playing: {Path(file_path).name}")
            self.status_bar.showMessage("")
            
            # Highlight current item
            index = self.playlist_model.index(self.current_index)
            self.playlist_view.setCurrentIndex(index)
            
            # Start monitoring
            self.playback_timer.start(1000)
            
            # No cleanup needed
    
    def pause_playback(self):
        """Pause playback"""
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to pause front document'
        ], capture_output=True)
        
        self.is_playing = False
        self.play_btn.setText("▶")
    
    def stop_playback(self):
        """Stop playback"""
        self.playback_timer.stop()
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        
        self.is_playing = False
        self.play_btn.setText("▶")
        self.progress_bar.setValue(0)
    
    def play_next(self):
        """Play next track"""
        if self.playlist_model.rowCount() == 0:
            return
            
        if self.shuffle_mode:
            # Random next track
            available_indices = list(range(self.playlist_model.rowCount()))
            if self.current_index in available_indices:
                available_indices.remove(self.current_index)
            if available_indices:
                self.current_index = random.choice(available_indices)
            else:
                self.current_index = 0
        else:
            # Sequential next track
            self.current_index += 1
            if self.current_index >= self.playlist_model.rowCount():
                if self.repeat_mode:
                    self.current_index = 0
                else:
                    self.current_index = self.playlist_model.rowCount() - 1
                    self.stop_playback()
                    return
        
        self.play_current()
    
    def play_previous(self):
        """Play previous track"""
        if self.playlist_model.rowCount() == 0:
            return
            
        self.current_index -= 1
        if self.current_index < 0:
            if self.repeat_mode:
                self.current_index = self.playlist_model.rowCount() - 1
            else:
                self.current_index = 0
        
        self.play_current()
    
    def check_playback_status(self):
        """Check if current track has finished"""
        try:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
            ], capture_output=True, text=True)
            
            if result.stdout.strip() != "true":
                # Track finished, play next
                self.play_next()
            else:
                # Update progress
                self.update_progress()
        except Exception as e:
            print(f"Playback check error: {e}")
    
    def update_progress(self):
        """Update progress bar"""
        try:
            # Get current time
            current_result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to if (count documents) > 0 then current time of front document else 0'
            ], capture_output=True, text=True)
            
            # Get duration
            duration_result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to if (count documents) > 0 then duration of front document else 0'
            ], capture_output=True, text=True)
            
            current = float(current_result.stdout.strip() or 0)
            duration = float(duration_result.stdout.strip() or 0)
            
            if duration > 0:
                progress = int((current / duration) * 100)
                self.progress_bar.setValue(progress)
        except:
            pass
    
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_mode = self.shuffle_btn.isChecked()
        self.status_bar.showMessage(f"Shuffle {'on' if self.shuffle_mode else 'off'}", 2000)
    
    def toggle_repeat(self):
        """Toggle repeat mode"""
        self.repeat_mode = self.repeat_btn.isChecked()
        self.status_bar.showMessage(f"Repeat {'on' if self.repeat_mode else 'off'}", 2000)
    
    def toggle_airplay(self):
        """Toggle AirPlay"""
        self.airplay_enabled = self.airplay_btn.isChecked()
        self.save_settings()
        
        if self.airplay_enabled and self.is_playing:
            self.enable_airplay()
        
        self.status_bar.showMessage(f"AirPlay {'enabled' if self.airplay_enabled else 'disabled'}", 2000)
    
    def enable_airplay(self):
        """Enable AirPlay using saved coordinates"""
        if not self.settings.get('airplay_icon_coords'):
            reply = QMessageBox.question(
                self,
                "Setup AirPlay",
                "AirPlay coordinates not configured. Would you like to configure now?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.configure_airplay()
            return
        
        try:
            coords = self.settings['airplay_icon_coords']
            tv_coords = self.settings.get('apple_tv_coords', {'x': coords['x'] + 50, 'y': coords['y'] + 70})
            
            # Show controls
            subprocess.run(['cliclick', f"m:{coords['x']},{coords['y'] - 50}"])
            time.sleep(0.5)
            
            # Click AirPlay
            subprocess.run(['cliclick', f"c:{coords['x']},{coords['y']}"])
            time.sleep(1)
            
            # Click Apple TV
            subprocess.run(['cliclick', f"c:{tv_coords['x']},{tv_coords['y']}"])
            
        except Exception as e:
            print(f"AirPlay error: {e}")
    
    def configure_airplay(self):
        """Configure AirPlay coordinates"""
        QMessageBox.information(
            self,
            "Configure AirPlay",
            "Please make sure QuickTime Player is open with a video.\n\n"
            "The configuration tool will help you locate the AirPlay button."
        )
        
        # Run configuration tool
        subprocess.run([sys.executable, 'visual_airplay_detector_fixed.py'])
        
        # Reload settings
        self.settings = self.load_settings()
    
    def update_status(self):
        """Update status bar with playlist info"""
        count = self.playlist_model.rowCount()
        self.status_bar.showMessage(f"{count} tracks in playlist")
    
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = Path.home() / '.audio_playlist_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Try to load AirPlay coordinates from other configs
        airplay_templates = Path.home() / '.airplay_templates.json'
        if airplay_templates.exists():
            try:
                with open(airplay_templates, 'r') as f:
                    templates = json.load(f)
                    settings = {}
                    
                    if 'airplay_button' in templates:
                        settings['airplay_icon_coords'] = templates['airplay_button']['captured_at']
                    
                    if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
                        if 'checkbox' in templates['apple_tv_icon']['offsets']:
                            settings['apple_tv_coords'] = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                    
                    return settings
            except:
                pass
        
        return {}
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / '.audio_playlist_settings.json'
        self.settings['airplay_enabled'] = self.airplay_enabled
        
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle file drops"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).is_file():
                # Check if audio file
                if Path(file_path).suffix.lower() in ['.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.wma']:
                    files.append(file_path)
            elif Path(file_path).is_dir():
                # Add all audio files from directory
                self.add_folder_path(file_path)
        
        if files:
            self.playlist_model.add_files(files)
            self.update_status()
            self.status_bar.showMessage(f"Added {len(files)} files", 3000)
    
    def add_folder_path(self, folder_path):
        """Add all audio files from a specific folder path"""
        audio_extensions = ['.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.wma']
        files = []
        
        folder = Path(folder_path)
        for ext in audio_extensions:
            files.extend(str(f) for f in folder.glob(f'*{ext}'))
            files.extend(str(f) for f in folder.glob(f'*{ext.upper()}'))
        
        if files:
            self.playlist_model.add_files(sorted(files))
    
    def closeEvent(self, event):
        """Handle window close"""
        self.stop_playback()
        self.save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(0, 102, 204))
    palette.setColor(QPalette.Highlight, QColor(0, 102, 204))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    # Create and show window
    window = AudioPlaylistPyQt()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()