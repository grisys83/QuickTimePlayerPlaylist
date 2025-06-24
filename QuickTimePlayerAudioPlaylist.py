#!/usr/bin/env python3
"""
Audio Playlist Pro - Enhanced audio playlist with AirPlay support
Features: Repeat One/All, Shuffle, Save/Load playlist, Drag reorder, Delete items
"""

import sys
import os
import json
import random
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import time


class SettingsDialog(QDialog):
    """Settings dialog for AirPlay offset configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 350)
        
        # Get current settings
        self.settings = parent.settings if parent else {}
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # AirPlay Settings Group
        airplay_group = QGroupBox("AirPlay Settings")
        airplay_layout = QGridLayout()
        
        # Instructions
        instructions = QLabel(
            "Adjust the offset values to position the AirPlay device click correctly.\n"
            "Default values work for 'living' device in most cases."
        )
        instructions.setWordWrap(True)
        airplay_layout.addWidget(instructions, 0, 0, 1, 3)
        
        # X Offset
        airplay_layout.addWidget(QLabel("X Offset:"), 1, 0)
        self.x_offset_spin = QSpinBox()
        self.x_offset_spin.setRange(-500, 500)
        self.x_offset_spin.setValue(self.settings.get('airplay_offset_x', 135))
        self.x_offset_spin.setSuffix(" pixels")
        airplay_layout.addWidget(self.x_offset_spin, 1, 1)
        
        # Y Offset
        airplay_layout.addWidget(QLabel("Y Offset:"), 2, 0)
        self.y_offset_spin = QSpinBox()
        self.y_offset_spin.setRange(-500, 500)
        self.y_offset_spin.setValue(self.settings.get('airplay_offset_y', 80))
        self.y_offset_spin.setSuffix(" pixels")
        airplay_layout.addWidget(self.y_offset_spin, 2, 1)
        
        # Reset button
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_defaults)
        airplay_layout.addWidget(reset_btn, 1, 2, 2, 1)
        
        airplay_group.setLayout(airplay_layout)
        layout.addWidget(airplay_group)
        
        # AirPlay Timing Group
        timing_group = QGroupBox("AirPlay Timing")
        timing_layout = QGridLayout()
        
        timing_layout.addWidget(QLabel("AirPlay Delay:"), 0, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(100, 10000)
        self.delay_spin.setValue(self.settings.get('airplay_delay', 100))
        self.delay_spin.setSuffix(" ms")
        self.delay_spin.setSingleStep(100)
        timing_layout.addWidget(self.delay_spin, 0, 1)
        
        timing_layout.addWidget(QLabel("Menu Wait Time:"), 1, 0)
        self.menu_wait_spin = QSpinBox()
        self.menu_wait_spin.setRange(100, 5000)
        self.menu_wait_spin.setValue(self.settings.get('airplay_menu_wait', 1000))
        self.menu_wait_spin.setSuffix(" ms")
        self.menu_wait_spin.setSingleStep(100)
        timing_layout.addWidget(self.menu_wait_spin, 1, 1)
        
        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)
        
        # Playback Settings Group
        playback_group = QGroupBox("Playback Settings")
        playback_layout = QVBoxLayout()
        
        # Auto minimize checkbox
        self.auto_minimize_check = QCheckBox("Auto-minimize window when AirPlay is active")
        self.auto_minimize_check.setChecked(self.settings.get('auto_minimize_on_airplay', True))
        self.auto_minimize_check.setToolTip(
            "Automatically minimize QuickTime window when playing through AirPlay"
        )
        playback_layout.addWidget(self.auto_minimize_check)
        
        playback_group.setLayout(playback_layout)
        layout.addWidget(playback_group)
        
        # Help text
        help_text = QLabel(
            "Tip: If AirPlay is not clicking the right device, adjust the X and Y offsets.\n"
            "Positive X = right, Negative X = left\n"
            "Positive Y = down, Negative Y = up"
        )
        help_text.setStyleSheet("color: #666; font-size: 11px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def reset_defaults(self):
        """Reset to default values"""
        self.x_offset_spin.setValue(135)
        self.y_offset_spin.setValue(80)
        self.delay_spin.setValue(100)
        self.menu_wait_spin.setValue(1000)
    
    def get_settings(self):
        """Get the configured settings"""
        return {
            'airplay_offset_x': self.x_offset_spin.value(),
            'airplay_offset_y': self.y_offset_spin.value(),
            'airplay_delay': self.delay_spin.value(),
            'airplay_menu_wait': self.menu_wait_spin.value(),
            'auto_minimize_on_airplay': self.auto_minimize_check.isChecked()
        }


class PlaylistWidget(QListWidget):
    """Custom QListWidget with drag and drop reordering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(True)
        
        # Enable selection
        self.setSelectionMode(QListWidget.ExtendedSelection)
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        """Show context menu for playlist items"""
        if self.count() == 0:
            return
            
        menu = QMenu(self)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        # Play action
        if self.currentItem():
            play_action = QAction("Play", self)
            play_action.triggered.connect(lambda: self.parent().play_selected_item())
            menu.addAction(play_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def delete_selected(self):
        """Delete selected items"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        reply = QMessageBox.question(
            self, 
            "Delete Items", 
            f"Delete {len(selected_items)} selected item(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove items in reverse order to maintain indices
            for item in reversed(selected_items):
                row = self.row(item)
                self.takeItem(row)
                # Also remove from parent's playlist
                if hasattr(self.parent(), 'playlist'):
                    del self.parent().playlist[row]
            
            # Update parent
            if hasattr(self.parent(), 'update_status'):
                self.parent().update_status()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
        else:
            super().keyPressEvent(event)


class AudioPlaylistPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.airplay_enabled = False
        self.repeat_mode = "none"  # none, one, all
        self.shuffle_enabled = False
        self.play_history = []  # Track played songs
        self.shuffle_queue = []  # Shuffle order
        self.single_track_mode = False  # For play one feature
        
        self.settings_file = Path.home() / '.audio_playlist_pro_settings.json'
        self.settings = {}
        self.load_settings()
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("QuickTime Player Audio Playlist")
        self.setGeometry(100, 100, 700, 500)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #ffffff;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #007AFF;
                color: white;
                border: none;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Current track display
        self.current_track_label = QLabel("No track playing")
        self.current_track_label.setAlignment(Qt.AlignCenter)
        self.current_track_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        layout.addWidget(self.current_track_label)
        
        # Top controls
        top_controls = QHBoxLayout()
        
        # File controls
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        top_controls.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        top_controls.addWidget(add_folder_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_playlist)
        top_controls.addWidget(clear_btn)
        
        top_controls.addSpacing(20)
        
        # Save/Load
        save_btn = QPushButton("Save Playlist")
        save_btn.clicked.connect(self.save_playlist)
        top_controls.addWidget(save_btn)
        
        load_btn = QPushButton("Load Playlist")
        load_btn.clicked.connect(self.load_playlist)
        top_controls.addWidget(load_btn)
        
        top_controls.addStretch()
        
        # AirPlay button
        self.airplay_btn = QPushButton("AirPlay")
        self.airplay_btn.setCheckable(True)
        self.airplay_btn.clicked.connect(self.toggle_airplay)
        top_controls.addWidget(self.airplay_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("Settings")
        settings_btn.setFixedWidth(40)
        settings_btn.clicked.connect(self.open_settings)
        top_controls.addWidget(settings_btn)
        
        # Exit button
        exit_btn = QPushButton("✕")
        exit_btn.setToolTip("Exit")
        exit_btn.setFixedWidth(40)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
        """)
        exit_btn.clicked.connect(self.close)
        top_controls.addWidget(exit_btn)
        
        layout.addLayout(top_controls)
        
        # Playlist widget
        self.playlist_widget = PlaylistWidget(self)
        self.playlist_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.playlist_widget)
        
        # Playback controls
        controls_widget = QWidget()
        controls_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_widget)
        
        # Shuffle button
        self.shuffle_btn = QPushButton("🔀 Shuffle")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        controls_layout.addWidget(self.shuffle_btn)
        
        controls_layout.addSpacing(20)
        
        # Main playback controls
        self.prev_btn = QPushButton("⏮ Previous")
        self.prev_btn.clicked.connect(self.play_previous)
        controls_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.play_pause)
        self.play_btn.setMinimumWidth(100)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        controls_layout.addWidget(self.stop_btn)
        
        self.play_one_btn = QPushButton("▶¹ Play One")
        self.play_one_btn.clicked.connect(self.play_one)
        self.play_one_btn.setToolTip("Play selected track only")
        controls_layout.addWidget(self.play_one_btn)
        
        self.next_btn = QPushButton("⏭ Next")
        self.next_btn.clicked.connect(self.play_next)
        controls_layout.addWidget(self.next_btn)
        
        controls_layout.addSpacing(20)
        
        # Repeat button
        self.repeat_btn = QPushButton("🔁 Repeat")
        self.repeat_btn.clicked.connect(self.cycle_repeat_mode)
        controls_layout.addWidget(self.repeat_btn)
        
        layout.addWidget(controls_widget)
        
        # Status bar
        self.status_label = QLabel("0 tracks")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 5px; color: #666;")
        layout.addWidget(self.status_label)
        
        # Timer for checking playback
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_playback)
        self.check_timer.setInterval(2000)
        
        # Update repeat button appearance
        self.update_repeat_button()
        
        # Update shuffle button state and appearance
        self.shuffle_btn.setChecked(self.shuffle_enabled)
        if self.shuffle_enabled:
            self.shuffle_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; }")
        else:
            self.shuffle_btn.setStyleSheet("")
        
        # Update AirPlay button state
        self.airplay_btn.setChecked(self.airplay_enabled)
        
    def add_files(self):
        """Add audio files to playlist"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.m4a *.aac *.wav *.aiff *.flac);;All Files (*.*)"
        )
        
        if files:
            for file in files:
                self.playlist.append(file)
                self.playlist_widget.addItem(Path(file).name)
            self.update_status()
            self.generate_shuffle_queue()
    
    def add_folder(self):
        """Add all audio files from folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder:
            audio_extensions = ['.mp3', '.m4a', '.aac', '.wav', '.aiff', '.flac']
            folder_path = Path(folder)
            
            files_added = 0
            for file_path in sorted(folder_path.iterdir()):
                if file_path.suffix.lower() in audio_extensions:
                    self.playlist.append(str(file_path))
                    self.playlist_widget.addItem(file_path.name)
                    files_added += 1
            
            if files_added > 0:
                self.update_status()
                self.generate_shuffle_queue()
                QMessageBox.information(self, "Success", f"Added {files_added} audio files")
            else:
                QMessageBox.warning(self, "No Files", "No audio files found in the selected folder")
    
    def clear_playlist(self):
        """Clear the entire playlist"""
        if self.playlist:
            reply = QMessageBox.question(
                self,
                "Clear Playlist",
                "Are you sure you want to clear the entire playlist?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_playback()
                self.playlist.clear()
                self.playlist_widget.clear()
                self.current_index = -1
                self.play_history.clear()
                self.shuffle_queue.clear()
                self.update_status()
                self.current_track_label.setText("No track playing")
    
    def save_playlist(self):
        """Save playlist to file"""
        if not self.playlist:
            QMessageBox.warning(self, "Empty Playlist", "No tracks to save")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Playlist",
            "",
            "Playlist Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                playlist_data = {
                    'tracks': self.playlist,
                    'shuffle': self.shuffle_enabled,
                    'repeat': self.repeat_mode
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(playlist_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Success", "Playlist saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save playlist: {str(e)}")
    
    def load_playlist(self):
        """Load playlist from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Playlist",
            "",
            "Playlist Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    playlist_data = json.load(f)
                
                # Clear current playlist
                self.playlist.clear()
                self.playlist_widget.clear()
                
                # Load tracks
                for track in playlist_data.get('tracks', []):
                    if Path(track).exists():
                        self.playlist.append(track)
                        self.playlist_widget.addItem(Path(track).name)
                
                # Load settings
                self.shuffle_enabled = playlist_data.get('shuffle', False)
                self.shuffle_btn.setChecked(self.shuffle_enabled)
                
                self.repeat_mode = playlist_data.get('repeat', 'none')
                self.update_repeat_button()
                
                self.update_status()
                self.generate_shuffle_queue()
                
                QMessageBox.information(self, "Success", f"Loaded {len(self.playlist)} tracks")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def on_item_double_clicked(self, item):
        """Play the double-clicked item"""
        self.play_selected_item()
    
    def play_selected_item(self):
        """Play the currently selected item"""
        current_item = self.playlist_widget.currentItem()
        if current_item:
            row = self.playlist_widget.row(current_item)
            if 0 <= row < len(self.playlist):
                self.current_index = row
                self.play_current()
    
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_enabled = self.shuffle_btn.isChecked()
        self.generate_shuffle_queue()
        
        # Update button appearance
        if self.shuffle_enabled:
            self.shuffle_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; }")
        else:
            self.shuffle_btn.setStyleSheet("")
        
        status = "enabled" if self.shuffle_enabled else "disabled"
        self.status_label.setText(f"Shuffle {status}")
        QTimer.singleShot(2000, self.update_status)
    
    def generate_shuffle_queue(self):
        """Generate a shuffled play order"""
        if self.shuffle_enabled and self.playlist:
            self.shuffle_queue = list(range(len(self.playlist)))
            random.shuffle(self.shuffle_queue)
    
    def cycle_repeat_mode(self):
        """Cycle through repeat modes: none -> one -> all -> none"""
        modes = ["none", "one", "all"]
        current_idx = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_idx + 1) % len(modes)]
        self.update_repeat_button()
        
        # Show status
        mode_text = {
            "none": "Repeat Off",
            "one": "Repeat One",
            "all": "Repeat All"
        }
        self.status_label.setText(mode_text[self.repeat_mode])
        QTimer.singleShot(2000, self.update_status)
    
    def update_repeat_button(self):
        """Update repeat button appearance based on mode"""
        if self.repeat_mode == "none":
            self.repeat_btn.setText("🔁 Repeat")
            self.repeat_btn.setStyleSheet("")
        elif self.repeat_mode == "one":
            self.repeat_btn.setText("🔂 Repeat One")
            self.repeat_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; }")
        else:  # all
            self.repeat_btn.setText("🔁 Repeat All")
            self.repeat_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; }")
    
    def play_pause(self):
        """Play or pause playback"""
        if self.is_playing:
            self.pause()
        else:
            # Check if a specific item is selected
            current_item = self.playlist_widget.currentItem()
            if current_item:
                row = self.playlist_widget.row(current_item)
                if 0 <= row < len(self.playlist):
                    self.current_index = row
                    self.play_history.clear()
            elif self.current_index == -1 and self.playlist:
                self.current_index = 0
                self.play_history.clear()
            self.play_current()
    
    def play_one(self):
        """Play only the selected track without continuing to next"""
        current_item = self.playlist_widget.currentItem()
        if current_item:
            row = self.playlist_widget.row(current_item)
            if 0 <= row < len(self.playlist):
                # Mark as single track playback
                self.single_track_mode = True
                self._in_play_one = True
                
                # Play the selected track
                self.current_index = row
                self.play_history.clear()
                self.play_current()
                
                # Clear the flag
                self._in_play_one = False
    
    def play_current(self):
        """Play current track"""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            
            # Reset single track mode if not explicitly set
            if not hasattr(self, '_in_play_one'):
                self.single_track_mode = False
            
            # Update UI
            self.current_track_label.setText(f"Playing: {Path(file_path).name}")
            self.playlist_widget.setCurrentRow(self.current_index)
            
            # Track play history
            if self.current_index not in self.play_history:
                self.play_history.append(self.current_index)
            
            # Close existing QuickTime documents
            try:
                subprocess.run([
                    'osascript', '-e',
                    'tell application "QuickTime Player" to close every document'
                ], capture_output=True)
                time.sleep(0.5)
            except:
                pass
            
            # Open and play with QuickTime
            try:
                # Different behavior based on AirPlay status
                if self.airplay_btn.isChecked():
                    # AirPlay is on - just load, don't play
                    script = f'''
                    tell application "QuickTime Player"
                        activate
                        open POSIX file "{file_path}"
                        delay 2
                        
                        -- Wait for document to be ready but don't play
                        repeat 10 times
                            if (count documents) > 0 then
                                if exists front document then
                                    return "ready"
                                end if
                            end if
                            delay 0.5
                        end repeat
                        
                        return "failed"
                    end tell
                    '''
                else:
                    # AirPlay is off - load and play normally
                    script = f'''
                    tell application "QuickTime Player"
                        activate
                        open POSIX file "{file_path}"
                        delay 2
                        
                        -- Wait for document to be ready and play
                        repeat 10 times
                            if (count documents) > 0 then
                                if exists front document then
                                    delay 0.5
                                    play front document
                                    return "playing"
                                end if
                            end if
                            delay 0.5
                        end repeat
                        
                        return "failed"
                    end tell
                    '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True)
                
                if result.stderr or "failed" in result.stdout:
                    raise Exception(result.stderr or "Failed to load document")
                
                # Handle based on AirPlay status
                if self.airplay_btn.isChecked():
                    # AirPlay is on - enable AirPlay then start playback
                    delay = self.settings.get('airplay_delay', 100)
                    QTimer.singleShot(delay, self.enable_airplay_and_start)
                else:
                    # AirPlay is off - already playing from the script
                    self.is_playing = True
                    self.play_btn.setText("⏸ Pause")
                
                # Start checking playback
                self.check_timer.start()
                
            except Exception as e:
                print(f"Error playing file: {e}")
                QMessageBox.warning(self, "Playback Error", f"Could not play file: {Path(file_path).name}")
    
    def pause(self):
        """Pause playback"""
        try:
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to pause front document'
            ], capture_output=True)
            
            self.is_playing = False
            self.play_btn.setText("▶ Play")
            self.check_timer.stop()
        except:
            pass
    
    def stop_playback(self):
        """Stop playback completely"""
        self.check_timer.stop()
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        
        # Reset current track display
        if self.current_index >= 0 and self.current_index < len(self.playlist):
            self.current_track_label.setText(f"Stopped: {Path(self.playlist[self.current_index]).name}")
        else:
            self.current_track_label.setText("No track playing")
        
        # Clear current position indicator
        self.playlist_widget.setCurrentRow(-1)
        
        # Force close QuickTime completely
        try:
            script = '''
            tell application "QuickTime Player"
                close every document
                delay 0.5
                quit
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=10)
            print("QuickTime stopped and quit")
        except:
            # Fallback: Kill QuickTime process
            try:
                subprocess.run(['pkill', '-f', 'QuickTime Player'], capture_output=True)
                print("QuickTime force killed")
            except:
                pass
    
    def play_next(self):
        """Play next track"""
        if not self.playlist:
            return
        
        # Stop current playback first
        if self.is_playing:
            self.stop_playback()
            # Wait for QuickTime to close properly
            QTimer.singleShot(500, self._play_next_after_delay)
        else:
            self._play_next_after_delay()
    
    def _play_next_after_delay(self):
        """Actually play next track after delay"""
        if self.shuffle_enabled and self.shuffle_queue:
            # Find current position in shuffle queue
            try:
                current_shuffle_idx = self.shuffle_queue.index(self.current_index)
                next_shuffle_idx = (current_shuffle_idx + 1) % len(self.shuffle_queue)
                self.current_index = self.shuffle_queue[next_shuffle_idx]
            except:
                self.current_index = self.shuffle_queue[0]
        else:
            # Normal sequential playback
            self.current_index = (self.current_index + 1) % len(self.playlist)
        
        self.play_current()
    
    def play_previous(self):
        """Play previous track"""
        if not self.playlist:
            return
        
        # Stop current playback first
        if self.is_playing:
            self.stop_playback()
            # Wait for QuickTime to close properly
            QTimer.singleShot(500, self._play_previous_after_delay)
        else:
            self._play_previous_after_delay()
    
    def _play_previous_after_delay(self):
        """Actually play previous track after delay"""
        if self.shuffle_enabled and self.shuffle_queue:
            # Find current position in shuffle queue
            try:
                current_shuffle_idx = self.shuffle_queue.index(self.current_index)
                prev_shuffle_idx = (current_shuffle_idx - 1) % len(self.shuffle_queue)
                self.current_index = self.shuffle_queue[prev_shuffle_idx]
            except:
                self.current_index = self.shuffle_queue[-1]
        else:
            # Normal sequential playback
            self.current_index = (self.current_index - 1) % len(self.playlist)
        
        self.play_current()
    
    def check_playback(self):
        """Check if current track has finished"""
        if not self.is_playing:
            return
            
        try:
            # Simple check: if QuickTime is running and has documents
            check_script = '''
            tell application "System Events"
                if exists (process "QuickTime Player") then
                    tell application "QuickTime Player"
                        if (count documents) > 0 then
                            try
                                set isPlaying to playing of front document
                                if isPlaying then
                                    return "playing"
                                else
                                    -- Check if finished
                                    try
                                        set currentTime to current time of front document
                                        set duration to duration of front document
                                        if currentTime >= (duration - 1) then
                                            return "finished"
                                        else
                                            return "paused"
                                        end if
                                    on error
                                        return "finished"
                                    end try
                                end if
                            on error
                                return "finished"
                            end try
                        else
                            return "no_document"
                        end if
                    end tell
                else
                    return "not_running"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', check_script], 
                                  capture_output=True, text=True, timeout=5)
            
            status = result.stdout.strip()
            
            if status in ["finished", "no_document", "not_running"]:
                # Track finished, decide what to do next
                print(f"Playback status: {status}")
                self.handle_track_finished()
            elif status == "error":
                # QuickTime might be in a bad state, assume finished
                print("QuickTime error detected, assuming track finished")
                self.handle_track_finished()
                
        except subprocess.TimeoutExpired:
            print("Playback check timeout, assuming track finished")
            self.handle_track_finished()
        except Exception as e:
            print(f"Check playback error: {e}, assuming track finished")
            self.handle_track_finished()
    
    def handle_track_finished(self):
        """Handle when a track finishes playing"""
        # Stop the timer first
        self.check_timer.stop()
        self.is_playing = False
        
        # Close the current document first and wait
        self.close_current_document()
        
        # Wait for document to close completely before deciding next action
        QTimer.singleShot(1000, self._handle_track_finished_after_close)
    
    def _handle_track_finished_after_close(self):
        """Handle track finished after document is closed"""
        # Check if in single track mode FIRST - this takes priority over all other modes
        if self.single_track_mode:
            self.single_track_mode = False
            self.current_track_label.setText(f"Finished: {Path(self.playlist[self.current_index]).name}")
            self.play_btn.setText("▶ Play")  # Reset play button
            return
            
        if self.repeat_mode == "one":
            # Repeat the same track
            self.play_current()
        elif self.repeat_mode == "all":
            # Play next track (will loop to beginning if at end)
            self.play_next()
        else:
            # Check if all tracks have been played
            if len(self.play_history) >= len(self.playlist):
                # All tracks played, stop
                self.current_track_label.setText("Playlist finished")
                self.play_history.clear()
                self.play_btn.setText("▶ Play")  # Reset play button
            else:
                # Play next unplayed track
                if self.shuffle_enabled:
                    # Find next unplayed track in shuffle order
                    for idx in self.shuffle_queue:
                        if idx not in self.play_history:
                            self.current_index = idx
                            self.play_current()
                            return
                else:
                    # Normal sequential - play next
                    self.play_next()
    
    def close_current_document(self):
        """Close the current QuickTime document and quit if no documents remain"""
        try:
            script = '''
            tell application "QuickTime Player"
                if (count documents) > 0 then
                    close front document
                    delay 0.5
                    
                    -- If no documents remain, quit QuickTime
                    if (count documents) = 0 then
                        quit
                    end if
                end if
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            print("Document closed and QuickTime quit if no documents remain")
        except Exception as e:
            print(f"Error closing document: {e}")
            # Fallback: Force quit QuickTime
            try:
                subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'], 
                             capture_output=True)
                print("Fallback: QuickTime force quit")
            except:
                pass
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Update settings
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.save_settings()
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
    
    def toggle_airplay(self):
        """Toggle AirPlay on/off"""
        self.airplay_enabled = self.airplay_btn.isChecked()
        
        if self.airplay_enabled and self.is_playing:
            # Enable AirPlay on current track
            self.enable_airplay()
        
        status = "enabled" if self.airplay_enabled else "disabled"
        self.status_label.setText(f"AirPlay {status}")
        QTimer.singleShot(2000, self.update_status)
    
    def start_playback(self):
        """Start playing the loaded document"""
        try:
            # First, just start playback
            script = '''
            tell application "QuickTime Player"
                if (count documents) > 0 then
                    play front document
                    return "playing"
                else
                    return "no document"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if "playing" in result.stdout:
                self.is_playing = True
                self.play_btn.setText("⏸ Pause")
                
                # Check if auto-minimize is enabled and AirPlay is active
                auto_minimize = self.settings.get('auto_minimize_on_airplay', True)
                if auto_minimize and self.airplay_btn.isChecked():
                    # Delay minimize by 300ms after playback starts
                    QTimer.singleShot(300, self.minimize_window)
        except Exception as e:
            print(f"Error starting playback: {e}")
    
    def minimize_window(self):
        """Minimize QuickTime window"""
        try:
            script = '''
            tell application "QuickTime Player"
                if exists window 1 then
                    set miniaturized of window 1 to true
                end if
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            print("QuickTime window minimized")
        except Exception as e:
            print(f"Error minimizing window: {e}")
    
    def enable_airplay_and_start(self):
        """Enable AirPlay and then start playback"""
        # First enable AirPlay
        self.enable_airplay()
        
        # Then start playback after a short delay
        QTimer.singleShot(500, self.start_playback)
    
    def enable_airplay(self):
        """Enable AirPlay using the successful offset method"""
        try:
            # First click AirPlay button and get its position
            click_script = '''
            tell application "System Events"
                tell process "QuickTime Player"
                    set frontmost to true
                    
                    -- Find AirPlay button
                    set btnList to every button of window 1
                    repeat with i from 1 to count of btnList
                        try
                            set btnDesc to description of button i of window 1
                            if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                                set btnPos to position of button i of window 1
                                click button i of window 1
                                return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                            end if
                        end try
                    end repeat
                    
                    return "not found"
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', click_script], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() != "not found" and ',' in result.stdout:
                x, y = result.stdout.strip().split(',')
                airplay_x = int(x)
                airplay_y = int(y)
                
                # Wait for menu with configurable time
                menu_wait = self.settings.get('airplay_menu_wait', 1000) / 1000.0  # Convert ms to seconds
                time.sleep(menu_wait)
                
                # Click living checkbox using configurable offset
                offset_x = self.settings.get('airplay_offset_x', 135)
                offset_y = self.settings.get('airplay_offset_y', 80)
                checkbox_x = airplay_x + offset_x
                checkbox_y = airplay_y + offset_y
                
                subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
                print(f"AirPlay: Clicked at ({checkbox_x}, {checkbox_y}) with offset ({offset_x}, {offset_y})")
                
        except Exception as e:
            print(f"AirPlay error: {e}")
    
    def update_status(self):
        """Update status label"""
        track_text = f"{len(self.playlist)} track{'s' if len(self.playlist) != 1 else ''}"
        
        # Add mode indicators
        modes = []
        if self.shuffle_enabled:
            modes.append("Shuffle")
        if self.repeat_mode != "none":
            modes.append(f"Repeat {self.repeat_mode.title()}")
        
        if modes:
            track_text += f" • {' • '.join(modes)}"
            
        self.status_label.setText(track_text)
    
    def load_settings(self):
        """Load application settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                    self.airplay_enabled = self.settings.get('airplay_enabled', False)
                    self.shuffle_enabled = self.settings.get('shuffle_enabled', False)
                    self.repeat_mode = self.settings.get('repeat_mode', 'none')
            except:
                pass
        
        # Ensure default values exist
        if 'airplay_offset_x' not in self.settings:
            self.settings['airplay_offset_x'] = 135
        if 'airplay_offset_y' not in self.settings:
            self.settings['airplay_offset_y'] = 80
        if 'airplay_delay' not in self.settings:
            self.settings['airplay_delay'] = 100
        if 'airplay_menu_wait' not in self.settings:
            self.settings['airplay_menu_wait'] = 1000
    
    def save_settings(self):
        """Save application settings"""
        # Update current states
        self.settings['airplay_enabled'] = self.airplay_enabled
        self.settings['shuffle_enabled'] = self.shuffle_enabled
        self.settings['repeat_mode'] = self.repeat_mode
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def closeEvent(self, event):
        """Clean up when closing"""
        self.stop_playback()
        self.save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application icon if available
    app.setApplicationName("QuickTime Player Audio Playlist")
    
    window = AudioPlaylistPro()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()