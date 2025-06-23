#!/usr/bin/env python3
"""
QuickDrop - The simplest AirPlay music player
Just drop music files and they play on your HomePod/Apple TV
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

class DropZone(QLabel):
    filesDropped = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #aaa;
                border-radius: 20px;
                background-color: #f0f0f0;
                color: #666;
                font-size: 24px;
                padding: 50px;
            }
            QLabel:hover {
                border-color: #007AFF;
                background-color: #e8f4ff;
            }
        """)
        self.setText("Drop Music Here\n\n🎵")
        self.setMinimumSize(400, 300)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #007AFF;
                    border-radius: 20px;
                    background-color: #e8f4ff;
                    color: #007AFF;
                    font-size: 24px;
                    padding: 50px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #aaa;
                border-radius: 20px;
                background-color: #f0f0f0;
                color: #666;
                font-size: 24px;
                padding: 50px;
            }
        """)
        
    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).suffix.lower() in ['.mp3', '.m4a', '.aac', '.flac', '.wav']:
                files.append(file_path)
        
        if files:
            self.filesDropped.emit(files)
            
        self.dragLeaveEvent(event)


class QuickDrop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_process = None
        self._scale_factor = None  # Initialize scale factor
        self.settings = self.load_settings()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("QuickDrop")
        self.setFixedSize(450, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.filesDropped.connect(self.handle_drop)
        layout.addWidget(self.drop_zone)
        
        # Status label
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status)
        
        # Progress bar (hidden initially)
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 5px;
            }
        """)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Auto-detect AirPlay coordinates on first run
        if not self.settings.get('airplay_configured'):
            QTimer.singleShot(1000, self.auto_configure)
            
    def load_settings(self):
        settings_file = Path.home() / '.quickdrop_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Check if coordinates need scale adjustment
                self._ensure_logical_coordinates(settings)
                return settings
        
        # Try to load from new AirPlay templates
        airplay_templates = Path.home() / '.airplay_templates.json'
        if airplay_templates.exists():
            try:
                with open(airplay_templates, 'r') as f:
                    templates = json.load(f)
                    # Convert template format to QuickDrop format
                    settings = {'airplay_configured': True}
                    
                    if 'airplay_button' in templates:
                        settings['airplay_icon_coords'] = templates['airplay_button']['captured_at']
                    
                    if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
                        if 'checkbox' in templates['apple_tv_icon']['offsets']:
                            settings['apple_tv_coords'] = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                    
                    # Ensure coordinates are in logical pixels
                    self._ensure_logical_coordinates(settings)
                    return settings
            except:
                pass
        
        # Try to load from QuickTimeConverter settings as fallback
        qt_settings_file = Path.home() / '.quicktime_converter_settings.json'
        if qt_settings_file.exists():
            try:
                with open(qt_settings_file, 'r') as f:
                    qt_settings = json.load(f)
                    if 'airplay_icon_coords' in qt_settings:
                        return {
                            'airplay_icon_coords': qt_settings['airplay_icon_coords'],
                            'apple_tv_coords': qt_settings['apple_tv_coords']
                        }
            except:
                pass
                
        # Default fallback
        return {
            'airplay_icon_coords': {'x': 844, 'y': 714},
            'apple_tv_coords': {'x': 970, 'y': 784}
        }
        
    def _ensure_logical_coordinates(self, settings):
        """Ensure coordinates are in logical pixels for cliclick"""
        # Check if we need to detect scale factor
        if not hasattr(self, '_scale_factor'):
            try:
                # Get scale factor using PyAutoGUI
                import pyautogui
                logical_width, _ = pyautogui.size()
                screenshot = pyautogui.screenshot()
                physical_width = screenshot.width
                self._scale_factor = physical_width / logical_width
            except:
                # Default to 2.0 for Retina displays
                self._scale_factor = 2.0
        
        # If coordinates seem to be in physical pixels (too large), convert them
        screen_width, screen_height = self._get_screen_size()
        
        for coord_key in ['airplay_icon_coords', 'apple_tv_coords']:
            if coord_key in settings:
                coords = settings[coord_key]
                # If coordinates are beyond logical screen bounds, they're likely physical
                if coords['x'] > screen_width or coords['y'] > screen_height:
                    print(f"Converting {coord_key} from physical to logical pixels")
                    coords['x'] = int(coords['x'] / self._scale_factor)
                    coords['y'] = int(coords['y'] / self._scale_factor)
                    
    def _get_screen_size(self):
        """Get logical screen size"""
        try:
            import pyautogui
            return pyautogui.size()
        except:
            # Fallback
            return (1440, 900)
            
    def save_settings(self):
        settings_file = Path.home() / '.quickdrop_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f)
            
    def auto_configure(self):
        """Auto-configure AirPlay coordinates on first run"""
        # Check if new templates already exist
        airplay_templates = Path.home() / '.airplay_templates.json'
        if airplay_templates.exists():
            # Templates already configured, just reload settings
            self.settings = self.load_settings()
            if self.settings.get('airplay_configured'):
                return
        
        reply = QMessageBox.question(self, "Setup AirPlay", 
            "Would you like to configure AirPlay settings?\n\n"
            "Make sure QuickTime Player is open with any video.",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.run_template_creator()
            
    def run_template_creator(self):
        """Run the template creator in a separate process"""
        try:
            self.status.setText("Running template configuration...")
            QApplication.processEvents()
            
            # Run template creator
            result = subprocess.run([sys.executable, 'template_creator_slow.py'], 
                                  capture_output=True, text=True)
            
            # Reload settings
            self.settings = self.load_settings()
            
            if self.settings.get('airplay_configured'):
                self.status.setText("AirPlay configured ✓")
                QTimer.singleShot(2000, lambda: self.status.setText("Ready"))
            else:
                self.status.setText("Configuration incomplete")
                
        except Exception as e:
            print(f"Template creator error: {e}")
            self.status.setText("Configuration failed")
            
    def detect_airplay_coordinates(self):
        """Legacy method - redirects to template creator"""
        self.run_template_creator()
            
    def handle_drop(self, files):
        """Handle dropped files"""
        if files:
            # Take only the first file for simplicity
            print(f"Dropped file: {files[0]}")
            self.play_file(files[0])
            
    def play_file(self, file_path):
        """Convert and play a single file"""
        self.drop_zone.setText("Converting...\n\n⚡")
        self.status.setText(f"Processing: {Path(file_path).name}")
        self.progress.show()
        self.progress.setRange(0, 0)  # Indeterminate
        
        # Create worker thread
        self.worker = ConvertAndPlayWorker(file_path, self.settings)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.on_playback_finished)
        self.worker.start()
        
    def update_status(self, message):
        self.status.setText(message)
        
    def on_playback_finished(self):
        self.drop_zone.setText("Drop Music Here\n\n🎵")
        self.status.setText("Ready")
        self.progress.hide()
        
    def closeEvent(self, event):
        # Kill QuickTime if running
        subprocess.run(['osascript', '-e', 
            'tell application "QuickTime Player" to close every document'])
        event.accept()


class ConvertAndPlayWorker(QThread):
    status_update = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, file_path, settings):
        super().__init__()
        self.file_path = file_path
        self.settings = settings
        
    def run(self):
        try:
            # Convert to video
            self.status_update.emit("Converting to video...")
            print(f"Converting: {self.file_path}")
            
            from audio_to_video_minimal import MinimalAudioToVideoConverter
            converter = MinimalAudioToVideoConverter()
            
            # Note: converter creates file with _converted.mp4 suffix
            converter.convert_to_video(self.file_path)
            output_path = Path(self.file_path).parent / f"{Path(self.file_path).stem}_converted.mp4"
            print(f"Looking for converted file: {output_path}")
            
            if not output_path.exists():
                self.status_update.emit("Conversion failed")
                return
                
            # Close any existing QuickTime windows
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to close every document'
            ], capture_output=True)
            
            time.sleep(0.5)
            
            # Open in QuickTime
            self.status_update.emit("Opening QuickTime...")
            subprocess.run(['open', '-a', 'QuickTime Player', str(output_path)])
            time.sleep(1.5)
            
            # Enable AirPlay
            self.status_update.emit("Connecting to AirPlay...")
            self._enable_airplay()
            
            # Start playback
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to play front document'
            ], capture_output=True)
            
            self.status_update.emit(f"Playing: {Path(self.file_path).name}")
            
            # Monitor playback
            while True:
                result = subprocess.run([
                    'osascript', '-e',
                    'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
                ], capture_output=True, text=True)
                
                if result.stdout.strip() != "true":
                    break
                time.sleep(2)
                
            # Clean up
            if output_path.exists():
                output_path.unlink()
                
        except Exception as e:
            print(f"Error in worker thread: {e}")
            import traceback
            traceback.print_exc()
            self.status_update.emit(f"Error: {str(e)}")
            
        finally:
            self.finished.emit()
            
    def _enable_airplay(self):
        """Enable AirPlay using saved coordinates"""
        print("DEBUG: Starting AirPlay enable process...")
        
        try:
            # Check if we have saved coordinates
            if 'airplay_icon_coords' in self.settings and 'apple_tv_coords' in self.settings:
                airplay_coords = self.settings['airplay_icon_coords']
                checkbox_coords = self.settings['apple_tv_coords']
                
                print(f"DEBUG: Using coordinates:")
                print(f"  AirPlay: ({airplay_coords['x']}, {airplay_coords['y']})")
                print(f"  Checkbox: ({checkbox_coords['x']}, {checkbox_coords['y']})")
                
                # Activate QuickTime
                subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
                time.sleep(1)
                
                # Use PyAutoGUI for consistent coordinate handling
                try:
                    import pyautogui
                    
                    # Show controls
                    print("DEBUG: Showing controls...")
                    pyautogui.moveTo(airplay_coords['x'], airplay_coords['y'] - 50, duration=0.5)
                    time.sleep(0.5)
                    
                    # Click AirPlay
                    print(f"DEBUG: Clicking AirPlay at ({airplay_coords['x']}, {airplay_coords['y']})")
                    pyautogui.click(airplay_coords['x'], airplay_coords['y'])
                    time.sleep(1.5)
                    
                    # Click checkbox
                    print(f"DEBUG: Clicking checkbox at ({checkbox_coords['x']}, {checkbox_coords['y']})")
                    pyautogui.click(checkbox_coords['x'], checkbox_coords['y'])
                    time.sleep(0.5)
                    
                    print("DEBUG: AirPlay enabled successfully")
                    return True
                    
                except Exception as e:
                    print(f"DEBUG: PyAutoGUI error: {e}")
                    # Fallback to cliclick
                    import shutil
                    if shutil.which('cliclick'):
                        subprocess.run(['cliclick', f'm:{airplay_coords["x"]},{airplay_coords["y"] - 50}'])
                        time.sleep(0.5)
                        subprocess.run(['cliclick', f'c:{airplay_coords["x"]},{airplay_coords["y"]}'])
                        time.sleep(1.5)
                        subprocess.run(['cliclick', f'c:{checkbox_coords["x"]},{checkbox_coords["y"]}'])
                        return True
            else:
                print("DEBUG: No saved coordinates found")
                
        except Exception as e:
            print(f"DEBUG: AirPlay enable error: {e}")
            import traceback
            traceback.print_exc()
            
        return False


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set app icon
    app.setWindowIcon(QIcon())
    
    window = QuickDrop()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()