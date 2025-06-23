#!/usr/bin/env python3
"""
AirPlay Icon Detector using OpenCV
Automatically finds AirPlay icon position on screen
"""

import cv2
import numpy as np
import subprocess
import os
from pathlib import Path
import time

class AirPlayDetector:
    def __init__(self):
        # Store template images for AirPlay icons
        self.templates = []
        self.load_templates()
        
    def load_templates(self):
        """Load AirPlay icon templates"""
        # We'll need to capture these templates first
        template_dir = Path(__file__).parent / "templates"
        if template_dir.exists():
            for template_file in template_dir.glob("airplay_*.png"):
                template = cv2.imread(str(template_file), cv2.IMREAD_UNCHANGED)
                if template is not None:
                    self.templates.append(template)
    
    def capture_screen(self):
        """Capture current screen"""
        # Take screenshot using macOS screencapture
        screenshot_path = "/tmp/quicktime_screenshot.png"
        subprocess.run([
            "screencapture", "-x", "-m", screenshot_path
        ], capture_output=True)
        
        # Read screenshot
        screenshot = cv2.imread(screenshot_path)
        os.remove(screenshot_path)
        return screenshot
    
    def find_airplay_icon(self, screenshot=None):
        """Find AirPlay icon in screenshot"""
        if screenshot is None:
            screenshot = self.capture_screen()
            
        # Convert to grayscale for better matching
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        best_match = None
        best_confidence = 0
        
        # Try template matching with different scales
        for scale in [0.5, 0.75, 1.0, 1.25, 1.5]:
            for template in self.templates:
                # Resize template
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                resized_template = cv2.resize(template, (width, height))
                
                # Convert template to grayscale if needed
                if len(resized_template.shape) > 2:
                    gray_template = cv2.cvtColor(resized_template, cv2.COLOR_BGR2GRAY)
                else:
                    gray_template = resized_template
                
                # Template matching
                result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_match = {
                        'confidence': max_val,
                        'location': max_loc,
                        'size': (width, height)
                    }
        
        if best_match and best_match['confidence'] > 0.7:  # 70% confidence threshold
            # Return center of icon
            x = best_match['location'][0] + best_match['size'][0] // 2
            y = best_match['location'][1] + best_match['size'][1] // 2
            return {'x': x, 'y': y, 'confidence': best_match['confidence']}
        
        return None
    
    def find_airplay_icon_with_edges(self):
        """Alternative method using edge detection"""
        screenshot = self.capture_screen()
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours that might be the AirPlay icon
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for triangular shapes (AirPlay icon is triangle + rectangle)
        for contour in contours:
            # Approximate polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it could be AirPlay icon shape
            if len(approx) >= 3 and len(approx) <= 5:
                x, y, w, h = cv2.boundingRect(contour)
                # AirPlay icon has specific aspect ratio
                if 0.7 < w/h < 1.3 and 15 < w < 50:  # Reasonable size for icon
                    return {'x': x + w//2, 'y': y + h//2, 'confidence': 0.6}
        
        return None
    
    def capture_airplay_template(self):
        """Helper to capture AirPlay icon template"""
        print("Please open QuickTime Player with a video loaded")
        print("Make sure the AirPlay icon is visible")
        print("Press Enter when ready...")
        input()
        
        screenshot = self.capture_screen()
        cv2.imwrite("screenshot_for_template.png", screenshot)
        print("Screenshot saved as 'screenshot_for_template.png'")
        print("Please crop the AirPlay icon and save as 'templates/airplay_icon.png'")
        
    def auto_detect_coordinates(self):
        """Auto-detect both AirPlay icon and Apple TV checkbox"""
        results = {}
        
        # Find AirPlay icon
        print("Looking for AirPlay icon...")
        airplay = self.find_airplay_icon()
        if airplay:
            results['airplay_icon_coords'] = {'x': airplay['x'], 'y': airplay['y']}
            print(f"Found AirPlay icon at ({airplay['x']}, {airplay['y']}) with {airplay['confidence']:.1%} confidence")
            
            # After clicking AirPlay, wait and capture menu
            import shutil
            if shutil.which('cliclick'):
                subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
                time.sleep(0.5)
                
                # Capture screen with menu open
                menu_screenshot = self.capture_screen()
                
                # Look for Apple TV text or checkbox
                # This would need OCR or more template matching
                # For now, estimate position (usually below AirPlay icon)
                results['apple_tv_coords'] = {
                    'x': airplay['x'] + 50,  # Offset to the right
                    'y': airplay['y'] + 70   # Offset below
                }
                
                # Click elsewhere to close menu
                subprocess.run(['cliclick', f"c:100,100"])
        else:
            print("Could not find AirPlay icon automatically")
            
        return results


def main():
    """Test the detector"""
    detector = AirPlayDetector()
    
    print("QuickTime AirPlay Icon Detector")
    print("1. Auto-detect coordinates")
    print("2. Capture template for training")
    
    choice = input("Choose option (1 or 2): ")
    
    if choice == "1":
        coords = detector.auto_detect_coordinates()
        if coords:
            print("\nDetected coordinates:")
            print(f"AirPlay Icon: {coords.get('airplay_icon_coords', 'Not found')}")
            print(f"Apple TV: {coords.get('apple_tv_coords', 'Not found')}")
    elif choice == "2":
        detector.capture_airplay_template()

if __name__ == "__main__":
    main()