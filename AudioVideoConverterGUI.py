#!/usr/bin/env python3
"""
Audio to Video Converter GUI
Simple drag-and-drop interface for converting audio files to videos
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import shutil

# Import the converter from development folder
try:
    # Try to import from development folder first
    sys.path.append(str(Path(__file__).parent / 'development'))
    from audio_to_video_minimal import MinimalAudioToVideoConverter
except ImportError:
    # If that fails, converter might be in the same directory or embedded
    try:
        from audio_to_video_minimal import MinimalAudioToVideoConverter
    except ImportError:
        # Last resort - define a minimal converter inline
        MinimalAudioToVideoConverter = None


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
                font-size: 18px;
                padding: 40px;
            }
            QLabel:hover {
                border-color: #007AFF;
                background-color: #e8f4ff;
            }
        """)
        self.setText("Drop Audio Files Here\n\n🎵 → 🎬\n\nOr click to browse")
        self.setMinimumSize(400, 250)
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Handle click to open file dialog"""
        if event.button() == Qt.LeftButton:
            # Find the main window
            parent = self.parent()
            while parent and not isinstance(parent, AudioVideoConverterGUI):
                parent = parent.parent()
            if parent:
                parent.browse_files()
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #007AFF;
                    border-radius: 20px;
                    background-color: #e8f4ff;
                    color: #007AFF;
                    font-size: 18px;
                    padding: 40px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #aaa;
                border-radius: 20px;
                background-color: #f0f0f0;
                color: #666;
                font-size: 18px;
                padding: 40px;
            }
        """)
        
    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).suffix.lower() in ['.mp3', '.m4a', '.aac', '.flac', '.wav', '.aiff']:
                files.append(file_path)
        
        if files:
            self.filesDropped.emit(files)
            
        self.dragLeaveEvent(event)


class ConversionWorker(QThread):
    progress_update = pyqtSignal(int, int)  # current, total
    status_update = pyqtSignal(str)
    file_completed = pyqtSignal(str, str)  # input, output
    finished = pyqtSignal()
    
    def __init__(self, files):
        super().__init__()
        self.files = files
        if MinimalAudioToVideoConverter:
            self.converter = MinimalAudioToVideoConverter()
        else:
            self.converter = None
        
    def run(self):
        total = len(self.files)
        
        if not self.converter:
            self.status_update.emit("Error: Converter not available")
            self.finished.emit()
            return
        
        for i, file_path in enumerate(self.files):
            self.progress_update.emit(i, total)
            self.status_update.emit(f"Converting: {Path(file_path).name}")
            
            # Convert with _converted.mp4 suffix
            output_path = Path(file_path).parent / f"{Path(file_path).stem}_converted.mp4"
            
            try:
                result = self.converter.convert_to_video(file_path, output_path)
                if result:
                    self.file_completed.emit(file_path, str(output_path))
            except Exception as e:
                print(f"Error converting {file_path}: {e}")
                self.status_update.emit(f"Error: {Path(file_path).name}")
                
        self.progress_update.emit(total, total)
        self.status_update.emit("Conversion complete!")
        self.finished.emit()


class AudioVideoConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files_to_convert = []
        self.converted_files = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Audio to Video Converter")
        self.setFixedSize(500, 550)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Audio → Video Converter")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.filesDropped.connect(self.add_files)
        layout.addWidget(self.drop_zone)
        
        # File count label
        self.file_count_label = QLabel("No files selected")
        self.file_count_label.setAlignment(Qt.AlignCenter)
        self.file_count_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.file_count_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 5px;
            }
        """)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Status label
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.status.hide()
        layout.addWidget(self.status)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_files)
        self.clear_btn.hide()
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        # Convert button
        self.convert_btn = QPushButton("Convert All")
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.hide()
        button_layout.addWidget(self.convert_btn)
        
        layout.addLayout(button_layout)
        
        # Results list (hidden initially)
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #fafafa;
            }
        """)
        self.results_list.hide()
        layout.addWidget(self.results_list)
        
        # Open folder button
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.open_folder_btn.hide()
        layout.addWidget(self.open_folder_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        # Check dependencies on startup
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import mutagen
            from PIL import Image
        except ImportError:
            QMessageBox.warning(self, "Missing Dependencies",
                "Please install required packages:\n\n"
                "pip3 install mutagen pillow\n\n"
                "Then restart the application.")
            
        # Check ffmpeg
        if not shutil.which('ffmpeg'):
            ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
            if not os.path.exists(ffmpeg_path):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("FFmpeg Not Found")
                msg.setText("FFmpeg is required for audio to video conversion.")
                msg.setInformativeText(
                    "Please install FFmpeg using one of these methods:\n\n"
                    "Option 1 (Recommended):\n"
                    "brew install ffmpeg\n\n"
                    "Option 2:\n"
                    "Download from https://ffmpeg.org/download.html\n\n"
                    "After installation, restart this application."
                )
                msg.setDetailedText(
                    "FFmpeg is a free, open-source multimedia framework.\n"
                    "It's required to convert audio files to video format.\n\n"
                    "If you have Homebrew installed, simply run:\n"
                    "brew install ffmpeg\n\n"
                    "If not, first install Homebrew from https://brew.sh"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                    
    def browse_files(self):
        """Open file dialog for selecting audio files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.m4a *.aac *.wav *.aiff *.flac);;All Files (*.*)"
        )
        
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """Add files to conversion queue"""
        # Filter for audio files
        audio_extensions = ['.mp3', '.m4a', '.aac', '.flac', '.wav', '.aiff']
        new_files = [f for f in files if Path(f).suffix.lower() in audio_extensions]
        
        # Add unique files only
        for file in new_files:
            if file not in self.files_to_convert:
                self.files_to_convert.append(file)
                
        self.update_ui()
        
    def update_ui(self):
        """Update UI based on file selection"""
        count = len(self.files_to_convert)
        
        if count > 0:
            self.file_count_label.setText(f"{count} file{'s' if count > 1 else ''} selected")
            self.convert_btn.show()
            self.clear_btn.show()
            self.drop_zone.setText(f"Drop More Audio Files\n\n🎵 → 🎬\n\n{count} files ready")
        else:
            self.file_count_label.setText("No files selected")
            self.convert_btn.hide()
            self.clear_btn.hide()
            self.drop_zone.setText("Drop Audio Files Here\n\n🎵 → 🎬\n\nOr click to browse")
            self.results_list.hide()
            self.open_folder_btn.hide()
            
    def clear_files(self):
        """Clear file selection"""
        self.files_to_convert.clear()
        self.converted_files.clear()
        self.results_list.clear()
        self.update_ui()
        self.progress.hide()
        self.status.hide()
        
    def start_conversion(self):
        """Start the conversion process"""
        if not self.files_to_convert:
            return
            
        # Disable buttons during conversion
        self.convert_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.drop_zone.setAcceptDrops(False)
        
        # Show progress
        self.progress.show()
        self.progress.setRange(0, len(self.files_to_convert))
        self.progress.setValue(0)
        self.status.show()
        
        # Clear previous results
        self.results_list.clear()
        self.converted_files.clear()
        
        # Start worker thread
        self.worker = ConversionWorker(self.files_to_convert)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)
        self.worker.file_completed.connect(self.on_file_completed)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.start()
        
    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress.setValue(current)
        
    def update_status(self, message):
        """Update status label"""
        self.status.setText(message)
        
    def on_file_completed(self, input_file, output_file):
        """Handle completed file conversion"""
        self.converted_files.append(output_file)
        
        # Add to results list
        item = QListWidgetItem(f"✓ {Path(input_file).name}")
        item.setToolTip(output_file)
        self.results_list.addItem(item)
        
        if not self.results_list.isVisible():
            self.results_list.show()
            
    def on_conversion_finished(self):
        """Handle conversion completion"""
        # Re-enable UI
        self.convert_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.drop_zone.setAcceptDrops(True)
        
        # Update status
        self.status.setText(f"Completed! {len(self.converted_files)} files converted")
        
        # Show open folder button
        if self.converted_files:
            self.open_folder_btn.show()
            
        # Clear the file list for next batch
        self.files_to_convert.clear()
        self.update_ui()
        
        # Show completion message
        QMessageBox.information(self, "Conversion Complete",
            f"Successfully converted {len(self.converted_files)} files!")
            
    def open_output_folder(self):
        """Open the folder containing converted files"""
        if self.converted_files:
            # Get the folder of the first converted file
            folder = Path(self.converted_files[0]).parent
            subprocess.run(['open', str(folder)])
            
    def closeEvent(self, event):
        """Handle window close"""
        # Stop any running conversion
        if hasattr(self, 'worker') and self.worker.isRunning():
            reply = QMessageBox.question(self, "Conversion in Progress",
                "Conversion is still running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No)
                
            if reply == QMessageBox.No:
                event.ignore()
                return
                
            self.worker.terminate()
            
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application name
    app.setApplicationName("Audio to Video Converter")
    
    window = AudioVideoConverterGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()