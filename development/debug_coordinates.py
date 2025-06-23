#!/usr/bin/env python3
"""
Debug coordinate conversion issues in QuickTimeConverterQt
"""

import subprocess
import time
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class CoordinateDebugger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coordinate Debugger")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Info label
        self.info_label = QLabel("Click buttons to test coordinate systems")
        layout.addWidget(self.info_label)
        
        # Test buttons
        btn1 = QPushButton("Test CV2 Coordinates")
        btn1.clicked.connect(self.test_cv2_coordinates)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("Test Fixed Template Detector")
        btn2.clicked.connect(self.test_fixed_detector)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("Debug QuickTime Window")
        btn3.clicked.connect(self.debug_quicktime_window)
        layout.addWidget(btn3)
        
        btn4 = QPushButton("Test Click Positions")
        btn4.clicked.connect(self.test_click_positions)
        layout.addWidget(btn4)
        
        # Results area
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)
        
    def log(self, message):
        """Add message to results"""
        self.results.append(message)
        QApplication.processEvents()
        
    def test_cv2_coordinates(self):
        """Test CV2 coordinate system"""
        self.log("\n=== Testing CV2 Coordinates ===")
        
        try:
            import cv2
            from coordinate_converter import CoordinateConverter
            
            converter = CoordinateConverter()
            self.log(f"Scale factor: {converter.scale_factor}")
            
            # Take screenshot
            screenshot_path = "/tmp/debug_cv2.png"
            subprocess.run(["screencapture", "-x", screenshot_path])
            screenshot = cv2.imread(screenshot_path)
            
            self.log(f"Screenshot size (CV2): {screenshot.shape[1]}x{screenshot.shape[0]}")
            
            # Test conversions
            test_points = [
                (100, 100),
                (500, 500),
                (screenshot.shape[1]-100, screenshot.shape[0]-100)
            ]
            
            for cv2_x, cv2_y in test_points:
                screen_x, screen_y = converter.cv2_to_screen(cv2_x, cv2_y)
                self.log(f"\nCV2: ({cv2_x}, {cv2_y}) -> Screen: ({screen_x}, {screen_y})")
                
                # Move mouse to show position
                subprocess.run(['cliclick', f'm:{screen_x},{screen_y}'])
                time.sleep(0.5)
                
            subprocess.run(["rm", screenshot_path])
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            
    def test_fixed_detector(self):
        """Test the fixed template detector"""
        self.log("\n=== Testing Fixed Template Detector ===")
        
        try:
            from fixed_template_detector import FixedTemplateDetector
            
            detector = FixedTemplateDetector()
            self.log(f"Converter scale factor: {detector.converter.scale_factor}")
            
            # Check if template exists
            template = detector.template_dir / "airplay_icon.png"
            if not template.exists():
                self.log(f"Template not found: {template}")
                return
                
            # Get QuickTime window
            window = detector.get_quicktime_window()
            if not window:
                self.log("QuickTime window not found")
                return
                
            self.log(f"QuickTime window: {window}")
            
            # Show controls
            detector.show_controls(window)
            
            # Capture and find
            screenshot = detector.capture_screen()
            result = detector.find_with_correct_coordinates(template, screenshot)
            
            if result:
                self.log(f"\nFound AirPlay icon!")
                self.log(f"CV2 coords: {result['cv2_coords']}")
                self.log(f"Screen coords: {result['screen_coords']}")
                self.log(f"Confidence: {result['confidence']:.1%}")
                self.log(f"Scale: {result['scale']}")
                
                # Move mouse
                self.log("\nMoving mouse to icon...")
                subprocess.run(['cliclick', f"m:{result['screen_coords']['x']},{result['screen_coords']['y']}"])
            else:
                self.log("Could not find AirPlay icon")
                
        except Exception as e:
            self.log(f"Error: {str(e)}")
            
    def debug_quicktime_window(self):
        """Debug QuickTime window coordinates"""
        self.log("\n=== Debugging QuickTime Window ===")
        
        try:
            # Get window from AppleScript
            script = '''
            tell application "System Events"
                tell process "QuickTime Player"
                    if exists window 1 then
                        set windowPos to position of window 1
                        set windowSize to size of window 1
                        return (item 1 of windowPos as string) & "," & ¬
                               (item 2 of windowPos as string) & "," & ¬
                               (item 1 of windowSize as string) & "," & ¬
                               (item 2 of windowSize as string)
                    end if
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if not result.stdout.strip():
                self.log("QuickTime not found")
                return
                
            coords = result.stdout.strip().split(',')
            window = {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
            
            self.log(f"Window position: ({window['x']}, {window['y']})")
            self.log(f"Window size: {window['width']}x{window['height']}")
            
            # Move mouse to corners
            corners = [
                (window['x'], window['y'], "Top-left"),
                (window['x'] + window['width'], window['y'], "Top-right"),
                (window['x'] + window['width'], window['y'] + window['height'], "Bottom-right"),
                (window['x'], window['y'] + window['height'], "Bottom-left"),
            ]
            
            for x, y, name in corners:
                self.log(f"\nMoving to {name}: ({x}, {y})")
                subprocess.run(['cliclick', f'm:{x},{y}'])
                time.sleep(0.5)
                
        except Exception as e:
            self.log(f"Error: {str(e)}")
            
    def test_click_positions(self):
        """Test actual click positions"""
        self.log("\n=== Testing Click Positions ===")
        
        try:
            # Load saved settings
            settings_file = Path.home() / '.quicktime_converter_settings.json'
            if settings_file.exists():
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    
                airplay = settings.get('airplay_icon_coords', {})
                appletv = settings.get('apple_tv_coords', {})
                
                self.log(f"Saved AirPlay coords: {airplay}")
                self.log(f"Saved Apple TV coords: {appletv}")
                
                if airplay:
                    self.log(f"\nMoving to saved AirPlay position...")
                    subprocess.run(['cliclick', f"m:{airplay['x']},{airplay['y']}"])
                    time.sleep(1)
                    
                if appletv:
                    self.log(f"\nMoving to saved Apple TV position...")
                    subprocess.run(['cliclick', f"m:{appletv['x']},{appletv['y']}"])
            else:
                self.log("No saved settings found")
                
        except Exception as e:
            self.log(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    debugger = CoordinateDebugger()
    debugger.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()