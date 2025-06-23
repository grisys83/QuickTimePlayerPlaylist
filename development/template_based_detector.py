#!/usr/bin/env python3
"""
Template-based AirPlay detection using captured images
"""

import cv2
import numpy as np
import subprocess
import os
import time
from pathlib import Path

class TemplateBasedDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def capture_screen(self):
        """Capture current screen"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        os.remove(screenshot_path)
        return screenshot
    
    def find_template(self, template_path, screenshot=None, threshold=0.8):
        """Find template in screenshot using template matching"""
        if screenshot is None:
            screenshot = self.capture_screen()
            
        # Load template
        template = cv2.imread(str(template_path))
        if template is None:
            print(f"Could not load template: {template_path}")
            return None
            
        # Convert to grayscale for better matching
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Get template dimensions
        h, w = template_gray.shape
        
        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # Return center coordinates
            x = max_loc[0] + w // 2
            y = max_loc[1] + h // 2
            return {
                'x': x,
                'y': y,
                'confidence': max_val,
                'top_left': max_loc,
                'bottom_right': (max_loc[0] + w, max_loc[1] + h)
            }
        
        return None
    
    def find_with_multiple_scales(self, template_path, screenshot=None, scales=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]):
        """Try finding template at different scales"""
        if screenshot is None:
            screenshot = self.capture_screen()
            
        template = cv2.imread(str(template_path))
        if template is None:
            print(f"Could not load template: {template_path}")
            return None
            
        best_match = None
        best_confidence = 0
        
        for scale in scales:
            # Resize template
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = {
                    'x': max_loc[0] + width // 2,
                    'y': max_loc[1] + height // 2,
                    'confidence': max_val,
                    'scale': scale,
                    'top_left': max_loc,
                    'bottom_right': (max_loc[0] + width, max_loc[1] + height)
                }
        
        if best_match and best_match['confidence'] >= 0.5:  # Lower threshold
            return best_match
        
        return None
    
    def detect_airplay_setup(self):
        """Detect both AirPlay icon and Apple TV checkbox using templates"""
        results = {}
        
        # Check if templates exist
        airplay_template = self.template_dir / "airplay_icon.png"
        apple_tv_template = self.template_dir / "apple_tv_checkbox.png"
        
        if not airplay_template.exists():
            print(f"Please save AirPlay icon screenshot as: {airplay_template}")
            return None
            
        # Step 1: Find AirPlay icon
        print("Looking for AirPlay icon...")
        screenshot = self.capture_screen()
        airplay = self.find_with_multiple_scales(airplay_template, screenshot)
        
        if airplay:
            print(f"Found AirPlay icon at ({airplay['x']}, {airplay['y']}) with {airplay['confidence']:.1%} confidence")
            results['airplay_icon_coords'] = {'x': airplay['x'], 'y': airplay['y']}
            
            # Step 2: Click AirPlay to show menu
            subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
            time.sleep(0.8)  # Wait for menu
            
            # Step 3: Find Apple TV checkbox
            if apple_tv_template.exists():
                print("Looking for Apple TV checkbox...")
                menu_screenshot = self.capture_screen()
                apple_tv = self.find_with_multiple_scales(apple_tv_template, menu_screenshot)
                
                if apple_tv:
                    print(f"Found Apple TV at ({apple_tv['x']}, {apple_tv['y']}) with {apple_tv['confidence']:.1%} confidence")
                    results['apple_tv_coords'] = {'x': apple_tv['x'], 'y': apple_tv['y']}
                else:
                    print("Could not find Apple TV checkbox")
                    # Estimate position
                    results['apple_tv_coords'] = {
                        'x': airplay['x'] + 50,
                        'y': airplay['y'] + 70
                    }
            else:
                print(f"Please save Apple TV checkbox screenshot as: {apple_tv_template}")
                
            # Close menu
            subprocess.run(['cliclick', 'c:100,100'])
        else:
            print("Could not find AirPlay icon")
            
        return results
    
    def visualize_detection(self, output_path="detection_visual.png"):
        """Show detection results visually"""
        screenshot = self.capture_screen()
        
        # Try to find both templates
        airplay_template = self.template_dir / "airplay_icon.png"
        apple_tv_template = self.template_dir / "apple_tv_checkbox.png"
        
        if airplay_template.exists():
            airplay = self.find_with_multiple_scales(airplay_template, screenshot)
            if airplay:
                # Draw rectangle around AirPlay icon
                cv2.rectangle(screenshot, airplay['top_left'], airplay['bottom_right'], (0, 255, 0), 2)
                cv2.putText(screenshot, f"AirPlay {airplay['confidence']:.1%}", 
                           (airplay['top_left'][0], airplay['top_left'][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Click to show menu
                subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
                time.sleep(0.8)
                
                # Capture with menu
                menu_screenshot = self.capture_screen()
                
                if apple_tv_template.exists():
                    apple_tv = self.find_with_multiple_scales(apple_tv_template, menu_screenshot)
                    if apple_tv:
                        # Draw rectangle around Apple TV
                        cv2.rectangle(menu_screenshot, apple_tv['top_left'], apple_tv['bottom_right'], (255, 0, 0), 2)
                        cv2.putText(menu_screenshot, f"Apple TV {apple_tv['confidence']:.1%}", 
                                   (apple_tv['top_left'][0], apple_tv['top_left'][1] - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        
                        screenshot = menu_screenshot
                
                # Close menu
                subprocess.run(['cliclick', 'c:100,100'])
        
        cv2.imwrite(output_path, screenshot)
        print(f"Visualization saved to: {output_path}")
        return output_path


def main():
    detector = TemplateBasedDetector()
    
    print("Template-based AirPlay Detector")
    print("=" * 50)
    print(f"Template directory: {detector.template_dir}")
    print("\nPlease ensure you have saved:")
    print("1. airplay_icon.png - Screenshot of the AirPlay icon")
    print("2. apple_tv_checkbox.png - Screenshot of the Apple TV checkbox")
    print("\nOptions:")
    print("1. Detect coordinates")
    print("2. Visualize detection")
    print("3. Test detection accuracy")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        result = detector.detect_airplay_setup()
        if result:
            print("\nDetection successful!")
            print(f"AirPlay: {result.get('airplay_icon_coords', 'Not found')}")
            print(f"Apple TV: {result.get('apple_tv_coords', 'Not found')}")
    
    elif choice == "2":
        detector.visualize_detection()
        
    elif choice == "3":
        print("\nTesting detection accuracy...")
        for i in range(3):
            print(f"\nTest {i+1}/3:")
            result = detector.detect_airplay_setup()
            if result:
                print("✓ Success")
            else:
                print("✗ Failed")
            time.sleep(2)

if __name__ == "__main__":
    main()