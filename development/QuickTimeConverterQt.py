#!/usr/bin/env python3
"""
QuickTime Converter & Player - PyQt5 Version
Fast and responsive UI for macOS
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WorkerThread(QThread):
    """Worker thread for background tasks"""
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)
    finished = pyqtSignal()
    
    def __init__(self, task, *args):
        super().__init__()
        self.task = task
        self.args = args
        
    def run(self):
        self.task(*self.args)
        self.finished.emit()

class QuickTimeConverterQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTime Converter & Player - Qt")
        self.setGeometry(100, 100, 1200, 700)
        
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
        self.load_settings()
        
        # Setup UI
        self.setup_menu()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI with PyQt5"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        
        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.select_folder)
        select_folder_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; padding: 8px; border-radius: 4px; }")
        toolbar.addWidget(select_folder_btn)
        
        convert_btn = QPushButton("Convert Selected")
        convert_btn.clicked.connect(self.convert_selected)
        convert_btn.setStyleSheet("QPushButton { background-color: #34C759; color: white; padding: 8px; border-radius: 4px; }")
        toolbar.addWidget(convert_btn)
        
        convert_all_btn = QPushButton("Convert All →")
        convert_all_btn.clicked.connect(self.convert_all)
        convert_all_btn.setStyleSheet("QPushButton { background-color: #5856D6; color: white; padding: 8px; border-radius: 4px; }")
        toolbar.addWidget(convert_all_btn)
        
        add_playlist_btn = QPushButton("Add to Playlist →")
        add_playlist_btn.clicked.connect(self.add_to_playlist)
        add_playlist_btn.setStyleSheet("QPushButton { background-color: #FF9500; color: white; padding: 8px; border-radius: 4px; }")
        toolbar.addWidget(add_playlist_btn)
        
        toolbar.addStretch()
        main_layout.addLayout(toolbar)
        
        # Lists layout
        lists_layout = QHBoxLayout()
        
        # Audio files list
        audio_group = QGroupBox("Audio Files")
        audio_layout = QVBoxLayout()
        
        self.audio_list = QListWidget()
        self.audio_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.audio_list.setStyleSheet("QListWidget { font-size: 12px; }")
        audio_layout.addWidget(self.audio_list)
        
        audio_group.setLayout(audio_layout)
        lists_layout.addWidget(audio_group)
        
        # Converted files list
        converted_group = QGroupBox("Converted Videos")
        converted_layout = QVBoxLayout()
        
        self.converted_list = QListWidget()
        self.converted_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.converted_list.setStyleSheet("QListWidget { font-size: 12px; }")
        converted_layout.addWidget(self.converted_list)
        
        converted_group.setLayout(converted_layout)
        lists_layout.addWidget(converted_group)
        
        # Playlist
        playlist_group = QGroupBox("Playlist")
        playlist_layout = QVBoxLayout()
        
        self.playlist_list = QListWidget()
        self.playlist_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.playlist_list.setStyleSheet("QListWidget { font-size: 12px; }")
        # Enable drag and drop
        self.playlist_list.setDragDropMode(QAbstractItemView.InternalMove)
        playlist_layout.addWidget(self.playlist_list)
        
        playlist_group.setLayout(playlist_layout)
        lists_layout.addWidget(playlist_group)
        
        main_layout.addLayout(lists_layout)
        
        # Playback controls
        playback_layout = QHBoxLayout()
        
        play_selected_btn = QPushButton("▶ Play Selected")
        play_selected_btn.clicked.connect(self.play_selected)
        play_selected_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; padding: 10px; font-size: 14px; border-radius: 4px; }")
        playback_layout.addWidget(play_selected_btn)
        
        play_all_btn = QPushButton("▶ Play All")
        play_all_btn.clicked.connect(self.play_all)
        play_all_btn.setStyleSheet("QPushButton { background-color: #34C759; color: white; padding: 10px; font-size: 14px; border-radius: 4px; }")
        playback_layout.addWidget(play_all_btn)
        
        stop_btn = QPushButton("⏹ Stop")
        stop_btn.clicked.connect(self.stop_playback)
        stop_btn.setStyleSheet("QPushButton { background-color: #FF3B30; color: white; padding: 10px; font-size: 14px; border-radius: 4px; }")
        playback_layout.addWidget(stop_btn)
        
        playback_layout.addStretch()
        
        remove_btn = QPushButton("Remove from Playlist")
        remove_btn.clicked.connect(self.remove_from_playlist)
        remove_btn.setStyleSheet("QPushButton { background-color: #8E8E93; color: white; padding: 10px; border-radius: 4px; }")
        playback_layout.addWidget(remove_btn)
        
        main_layout.addLayout(playback_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_playlist_action = QAction('Save Playlist', self)
        save_playlist_action.triggered.connect(self.save_playlist)
        file_menu.addAction(save_playlist_action)
        
        load_playlist_action = QAction('Load Playlist', self)
        load_playlist_action.triggered.connect(self.load_playlist)
        file_menu.addAction(load_playlist_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        configure_action = QAction('Configure Coordinates', self)
        configure_action.triggered.connect(self.configure_coordinates)
        settings_menu.addAction(configure_action)
        
        test_action = QAction('Test Click Position', self)
        test_action.triggered.connect(self.test_click_position)
        settings_menu.addAction(test_action)
        
        auto_detect_action = QAction('Auto-detect Coordinates', self)
        auto_detect_action.triggered.connect(self.auto_detect_coordinates)
        settings_menu.addAction(auto_detect_action)
        
    def select_folder(self):
        """Select folder containing audio files"""
        folder = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if not folder:
            return
            
        self.current_folder = folder
        self.refresh_file_lists()
        
    def refresh_file_lists(self):
        """Refresh file lists"""
        if not self.current_folder:
            return
            
        # Clear lists
        self.audio_list.clear()
        self.converted_list.clear()
        self.audio_files = []
        self.converted_files = []
        
        folder_path = Path(self.current_folder)
        
        # Find audio files
        for ext in ['.mp3', '.m4a', '.aac', '.wav', '.flac']:
            for file in folder_path.glob(f'*{ext}'):
                self.audio_files.append(str(file))
                self.audio_list.addItem(file.name)
                
        # Find converted files
        for file in folder_path.glob('*_converted.mp4'):
            self.converted_files.append(str(file))
            self.converted_list.addItem(file.name)
            
        self.status_bar.showMessage(f"Found {len(self.audio_files)} audio files, {len(self.converted_files)} converted videos")
        
    def convert_selected(self):
        """Convert selected audio files"""
        selected_items = self.audio_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select audio files to convert")
            return
            
        selected_indices = [self.audio_list.row(item) for item in selected_items]
        files_to_convert = [self.audio_files[i] for i in selected_indices]
        
        # Create worker thread
        self.convert_thread = WorkerThread(self._convert_files, files_to_convert)
        self.convert_thread.status_update.connect(self.status_bar.showMessage)
        self.convert_thread.finished.connect(self.refresh_file_lists)
        self.convert_thread.start()
        
    def convert_all(self):
        """Convert all audio files and add to playlist"""
        if not self.audio_files:
            QMessageBox.information(self, "No Files", "No audio files to convert")
            return
            
        # Create worker thread for conversion
        self.convert_thread = WorkerThread(self._convert_all_files, self.audio_files)
        self.convert_thread.status_update.connect(self.status_bar.showMessage)
        self.convert_thread.finished.connect(self._add_all_converted)
        self.convert_thread.start()
        
    def _convert_files(self, files):
        """Convert files (runs in thread)"""
        try:
            from audio_to_video_minimal import MinimalAudioToVideoConverter
            converter = MinimalAudioToVideoConverter()
            
            total = len(files)
            for i, audio_file in enumerate(files, 1):
                self.convert_thread.status_update.emit(f"Converting {i}/{total}: {os.path.basename(audio_file)}")
                
                output_path = Path(audio_file).parent / f"{Path(audio_file).stem}_converted.mp4"
                if not output_path.exists():
                    converter.convert_to_video(audio_file)
                    
            self.convert_thread.status_update.emit(f"Conversion complete: {total} files")
        except Exception as e:
            self.convert_thread.status_update.emit(f"Error: {str(e)}")
            
    def _convert_all_files(self, files):
        """Convert all files (runs in thread)"""
        self._convert_files(files)
        
    def _add_all_converted(self):
        """Add all converted files to playlist after conversion"""
        self.refresh_file_lists()
        # Add all converted files to playlist
        for file_path in self.converted_files:
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                self.playlist_list.addItem(os.path.basename(file_path))
            
    def add_to_playlist(self):
        """Add selected converted files to playlist"""
        selected_items = self.converted_list.selectedItems()
        if not selected_items:
            return
            
        selected_indices = [self.converted_list.row(item) for item in selected_items]
        
        for index in selected_indices:
            file_path = self.converted_files[index]
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                self.playlist_list.addItem(os.path.basename(file_path))
                
    def remove_from_playlist(self):
        """Remove selected items from playlist"""
        selected_items = self.playlist_list.selectedItems()
        for item in selected_items:
            index = self.playlist_list.row(item)
            del self.playlist[index]
            self.playlist_list.takeItem(index)
            
    def play_selected(self):
        """Play selected video"""
        selected_items = self.playlist_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a video to play")
            return
            
        index = self.playlist_list.row(selected_items[0])
        video_path = self.playlist[index]
        
        # Play in thread
        threading.Thread(target=self._play_single_video, args=(video_path,), daemon=True).start()
        
    def play_all(self):
        """Play entire playlist"""
        if not self.playlist:
            QMessageBox.information(self, "Empty Playlist", "Playlist is empty")
            return
            
        self.is_playing = True
        self.current_index = 0
        
        # Play in thread
        threading.Thread(target=self._play_playlist, daemon=True).start()
        
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        self.status_bar.showMessage("Playback stopped")
        
    def _play_single_video(self, video_path):
        """Play single video"""
        self.status_bar.showMessage(f"Playing: {os.path.basename(video_path)}")
        self._play_video(video_path)
        self.status_bar.showMessage("Ready")
        
    def _play_playlist(self):
        """Play playlist"""
        while self.is_playing and self.current_index < len(self.playlist):
            video_path = self.playlist[self.current_index]
            QMetaObject.invokeMethod(self.status_bar, "showMessage", 
                                   Qt.QueuedConnection, 
                                   Q_ARG(str, f"Playing {self.current_index + 1}/{len(self.playlist)}"))
            
            self._play_video(video_path)
            self.current_index += 1
            
        self.is_playing = False
        QMetaObject.invokeMethod(self.status_bar, "showMessage", 
                               Qt.QueuedConnection, 
                               Q_ARG(str, "Playlist finished"))
        
    def _play_video(self, video_path):
        """Play video in QuickTime"""
        # Close existing
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        
        time.sleep(0.3)
        
        # Open new
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(0.5)  # Reduced from 0.8
        
        # Enable AirPlay if configured
        if self.settings['airplay_enabled']:
            self._enable_airplay()
        
        # Play
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], capture_output=True)
        
        # Wait for playback
        time.sleep(1)
        while self.is_playing:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
            ], capture_output=True, text=True)
            
            if result.stdout.strip() != "true":
                break
            time.sleep(1)
            
    def _enable_airplay(self):
        """Enable AirPlay using CV2-based fast detection"""
        try:
            # Try CV2-based fast enabler first
            try:
                from cv2_airplay_enabler import CV2AirPlayEnabler
                enabler = CV2AirPlayEnabler(self.settings)
                if enabler.enable_airplay_fast():
                    return
            except ImportError:
                pass
            
            # Fallback to direct cliclick if CV2 not available
            import shutil
            if shutil.which('cliclick') and 'airplay_icon_coords' in self.settings:
                airplay_x = self.settings['airplay_icon_coords']['x']
                airplay_y = self.settings['airplay_icon_coords']['y']
                appletv_x = self.settings['apple_tv_coords']['x']
                appletv_y = self.settings['apple_tv_coords']['y']
                
                # Quick activation and clicks
                subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
                time.sleep(0.3)
                
                # Show controls by moving mouse
                subprocess.run(['cliclick', f'm:{airplay_x},{airplay_y}'])
                time.sleep(0.5)
                
                # Click sequence
                subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
                time.sleep(0.5)
                subprocess.run(['cliclick', f'c:{appletv_x},{appletv_y}'])
                time.sleep(0.5)
        except Exception as e:
            print(f"AirPlay error: {e}")
            
    def configure_coordinates(self):
        """Configure coordinates dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Configure Coordinates")
        dialog.setModal(True)
        
        layout = QFormLayout()
        
        # AirPlay coordinates
        airplay_x = QSpinBox()
        airplay_x.setMaximum(9999)
        airplay_x.setValue(self.settings['airplay_icon_coords']['x'])
        
        airplay_y = QSpinBox()
        airplay_y.setMaximum(9999)
        airplay_y.setValue(self.settings['airplay_icon_coords']['y'])
        
        layout.addRow("AirPlay X:", airplay_x)
        layout.addRow("AirPlay Y:", airplay_y)
        
        # Apple TV coordinates
        appletv_x = QSpinBox()
        appletv_x.setMaximum(9999)
        appletv_x.setValue(self.settings['apple_tv_coords']['x'])
        
        appletv_y = QSpinBox()
        appletv_y.setMaximum(9999)
        appletv_y.setValue(self.settings['apple_tv_coords']['y'])
        
        layout.addRow("Apple TV X:", appletv_x)
        layout.addRow("Apple TV Y:", appletv_y)
        
        # Enable AirPlay
        airplay_enabled = QCheckBox("Enable AirPlay")
        airplay_enabled.setChecked(self.settings['airplay_enabled'])
        layout.addRow(airplay_enabled)
        
        # Test button
        test_btn = QPushButton("Test Position")
        test_btn.clicked.connect(self.test_click_position)
        layout.addRow(test_btn)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_coordinate_settings(
            dialog, airplay_x.value(), airplay_y.value(), 
            appletv_x.value(), appletv_y.value(), airplay_enabled.isChecked()
        ))
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def save_coordinate_settings(self, dialog, airplay_x, airplay_y, appletv_x, appletv_y, airplay_enabled):
        """Save coordinate settings"""
        self.settings['airplay_icon_coords']['x'] = airplay_x
        self.settings['airplay_icon_coords']['y'] = airplay_y
        self.settings['apple_tv_coords']['x'] = appletv_x
        self.settings['apple_tv_coords']['y'] = appletv_y
        self.settings['airplay_enabled'] = airplay_enabled
        self.save_settings()
        dialog.accept()
        
    def save_playlist(self):
        """Save playlist to file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Playlist", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False, indent=2)
            self.status_bar.showMessage(f"Playlist saved: {filename}")
            
    def load_playlist(self):
        """Load playlist from file"""
        filename, _ = QFileDialog.getOpenFileName(self, "Load Playlist", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.playlist = json.load(f)
                
            self.playlist_list.clear()
            for filepath in self.playlist:
                self.playlist_list.addItem(os.path.basename(filepath))
                
            self.status_bar.showMessage(f"Playlist loaded: {filename}")
            
    def save_settings(self):
        """Save settings"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
            
    def load_settings(self):
        """Load settings"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass
                
    def test_click_position(self):
        """Test click positions visually"""
        import shutil
        
        # Create small windows to show positions
        for name, coords, color in [
            ("AirPlay", self.settings['airplay_icon_coords'], "#FF3B30"),
            ("Apple TV", self.settings['apple_tv_coords'], "#007AFF")
        ]:
            # Create a small window
            marker = QWidget()
            marker.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            marker.setAttribute(Qt.WA_TranslucentBackground)
            
            # Create colored circle
            label = QLabel(name, marker)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    border-radius: 20px;
                    padding: 10px;
                    font-weight: bold;
                }}
            """)
            
            # Position window
            marker.move(coords['x'] - 40, coords['y'] - 20)
            marker.resize(80, 40)
            marker.show()
            
            # Auto close after 3 seconds
            QTimer.singleShot(3000, marker.close)
            
        # Move mouse to show positions if cliclick available
        if shutil.which('cliclick'):
            subprocess.run(['cliclick', f"m:{self.settings['airplay_icon_coords']['x']},{self.settings['airplay_icon_coords']['y']}"])
            
        self.status_bar.showMessage("Red = AirPlay, Blue = Apple TV. Markers will disappear in 3 seconds.")
        
    def auto_detect_coordinates(self):
        """Auto-detect AirPlay coordinates using CV2"""
        try:
            # Check if opencv is installed
            import cv2
        except ImportError:
            QMessageBox.warning(self, "OpenCV Not Installed", 
                "Please install opencv-python first:\npip3 install opencv-python")
            return
            
        try:
            # Use the fixed detector with coordinate conversion
            from fixed_template_detector import FixedTemplateDetector
            
            # Check if templates exist
            detector = FixedTemplateDetector()
            airplay_template = detector.template_dir / "airplay_icon.png"
            apple_tv_template = detector.template_dir / "apple_tv_checkbox.png"
            
            if not airplay_template.exists():
                QMessageBox.information(self, "Template Needed", 
                    f"Please save a screenshot of the AirPlay icon as:\n{airplay_template}\n\n"
                    "1. Open QuickTime with a video\n"
                    "2. Move mouse to bottom to show controls\n"
                    "3. Take a screenshot of just the AirPlay icon\n"
                    "4. Save it to the templates folder")
                return
            
            # Show progress dialog
            progress = QProgressDialog("Detecting AirPlay positions...", "Cancel", 0, 4, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Step 1: Ensure QuickTime is open with a video
            reply = QMessageBox.question(self, "Prepare QuickTime", 
                "Please ensure:\n1. QuickTime Player is open\n2. A video is loaded\n\nIs QuickTime ready?",
                QMessageBox.Yes | QMessageBox.No)
                
            if reply != QMessageBox.Yes:
                progress.close()
                return
            
            progress.setValue(1)
            
            # Step 2: Activate QuickTime
            detector.activate_quicktime()
            progress.setValue(2)
            
            # Step 3: Get window and show controls
            window = detector.get_quicktime_window()
            if not window:
                progress.close()
                QMessageBox.warning(self, "Error", "QuickTime window not found")
                return
                
            detector.show_controls(window)
            progress.setValue(3)
            
            # Step 4: Detect AirPlay icon
            screenshot = detector.capture_screen()
            airplay_result = detector.find_with_correct_coordinates(airplay_template, screenshot)
            
            if airplay_result:
                # Extract screen coordinates
                airplay_coords = airplay_result['screen_coords']
                
                # Estimate Apple TV position (typically 50px right, 70px down)
                appletv_coords = {
                    'x': airplay_coords['x'] + 50,
                    'y': airplay_coords['y'] + 70
                }
                
                # Update settings
                self.settings['airplay_icon_coords'] = airplay_coords
                self.settings['apple_tv_coords'] = appletv_coords
                self.save_settings()
                
                progress.setValue(4)
                progress.close()
                
                QMessageBox.information(self, "Success", 
                    f"Found AirPlay icon at:\n"
                    f"X: {airplay_coords['x']}\n"
                    f"Y: {airplay_coords['y']}\n\n"
                    f"Apple TV position estimated at:\n"
                    f"X: {appletv_coords['x']}\n"
                    f"Y: {appletv_coords['y']}")
            else:
                progress.close()
                QMessageBox.warning(self, "Not Found", 
                    "Could not detect AirPlay icon.\n"
                    "Please use manual configuration.")
                
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            QMessageBox.critical(self, "Error", f"Detection failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = QuickTimeConverterQt()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()