#!/usr/bin/env python3
"""
Helper to capture AirPlay templates from full screenshots
"""

import cv2
import numpy as np
import subprocess
import time
from pathlib import Path

class TemplateCapturer:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def capture_and_select(self, name):
        """Capture screen and let user select region"""
        print(f"\nCapturing {name}...")
        print("Instructions:")
        print("1. A window will open with your screenshot")
        print("2. Click and drag to select the area")
        print("3. Press 'c' to confirm, 'r' to retry, 'q' to quit")
        
        # Capture screen
        screenshot_path = "/tmp/fullscreen.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        
        # Load image
        img = cv2.imread(screenshot_path)
        clone = img.copy()
        
        # Variables for selection
        selecting = False
        x1, y1, x2, y2 = -1, -1, -1, -1
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal selecting, x1, y1, x2, y2, img
            
            if event == cv2.EVENT_LBUTTONDOWN:
                selecting = True
                x1, y1 = x, y
                
            elif event == cv2.EVENT_MOUSEMOVE:
                if selecting:
                    img = clone.copy()
                    cv2.rectangle(img, (x1, y1), (x, y), (0, 255, 0), 2)
                    
            elif event == cv2.EVENT_LBUTTONUP:
                selecting = False
                x2, y2 = x, y
                img = clone.copy()
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Create window
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(name, mouse_callback)
        
        while True:
            cv2.imshow(name, img)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c') and x1 >= 0:  # Confirm
                # Extract selected region
                x_min = min(x1, x2)
                x_max = max(x1, x2)
                y_min = min(y1, y2)
                y_max = max(y1, y2)
                
                if x_max - x_min > 5 and y_max - y_min > 5:  # Minimum size
                    selected = clone[y_min:y_max, x_min:x_max]
                    
                    # Save template
                    template_path = self.template_dir / f"{name}.png"
                    cv2.imwrite(str(template_path), selected)
                    print(f"✓ Saved to: {template_path}")
                    
                    cv2.destroyAllWindows()
                    return template_path
                else:
                    print("Selection too small, try again")
                    
            elif key == ord('r'):  # Retry
                img = clone.copy()
                x1, y1, x2, y2 = -1, -1, -1, -1
                
            elif key == ord('q'):  # Quit
                cv2.destroyAllWindows()
                return None
        
    def capture_airplay_templates(self):
        """Guide through capturing both templates"""
        print("QuickTime AirPlay Template Capture Tool")
        print("=" * 50)
        
        # Step 1: AirPlay icon
        print("\nStep 1: Capture AirPlay Icon")
        print("1. Open QuickTime Player with a video")
        print("2. Move mouse to bottom to show control bar")
        print("3. Press Enter when ready...")
        input()
        
        airplay_path = self.capture_and_select("airplay_icon")
        if not airplay_path:
            print("Cancelled")
            return
        
        # Step 2: Apple TV checkbox
        print("\nStep 2: Capture Apple TV Checkbox")
        print("1. Click the AirPlay icon to show the menu")
        print("2. Make sure Apple TV/HomePod option is visible")
        print("3. Press Enter when ready...")
        input()
        
        apple_tv_path = self.capture_and_select("apple_tv_checkbox")
        if not apple_tv_path:
            print("Cancelled")
            return
        
        print("\n✓ Templates captured successfully!")
        print(f"Location: {self.template_dir}")
        
        # Test detection
        print("\nWould you like to test detection now? (y/n)")
        if input().lower() == 'y':
            from template_based_detector import TemplateBasedDetector
            detector = TemplateBasedDetector()
            result = detector.detect_airplay_setup()
            
            if result:
                print("\n✓ Detection successful!")
                print(f"AirPlay: {result.get('airplay_icon_coords', 'Not found')}")
                print(f"Apple TV: {result.get('apple_tv_coords', 'Not found')}")
            else:
                print("\n✗ Detection failed")

def main():
    capturer = TemplateCapturer()
    capturer.capture_airplay_templates()

if __name__ == "__main__":
    main()