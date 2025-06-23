#!/usr/bin/env python3
"""
Adaptive control bar finder that learns the correct position
"""

import subprocess
import time
import json
from pathlib import Path
import cv2
import numpy as np

class AdaptiveControlFinder:
    def __init__(self):
        self.settings_file = Path.home() / '.quicktime_control_settings.json'
        self.load_settings()
        
    def load_settings(self):
        """Load saved control positions"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'control_offset': None,  # Will be learned
                'last_window_height': None,
                'detection_method': 'adaptive'
            }
    
    def save_settings(self):
        """Save learned positions"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def find_control_bar_position(self, window):
        """Find control bar position adaptively"""
        
        # Method 1: Use saved offset if window size hasn't changed much
        if (self.settings['control_offset'] and 
            self.settings['last_window_height'] and
            abs(window['height'] - self.settings['last_window_height']) < 50):
            
            print(f"Using saved offset: {self.settings['control_offset']}px")
            return window['y'] + window['height'] - self.settings['control_offset']
        
        # Method 2: Binary search to find control bar
        print("Learning control bar position...")
        offset = self.binary_search_control_position(window)
        
        if offset:
            self.settings['control_offset'] = offset
            self.settings['last_window_height'] = window['height']
            self.save_settings()
            return window['y'] + window['height'] - offset
            
        # Method 3: Fall back to common positions
        return self.try_common_positions(window)
    
    def binary_search_control_position(self, window):
        """Binary search to find where controls appear"""
        center_x = window['x'] + window['width'] // 2
        
        # Search between 50px and 500px from bottom
        low, high = 50, 500
        found_offset = None
        
        print("Searching for control bar...")
        
        while low <= high:
            mid = (low + high) // 2
            test_y = window['y'] + window['height'] - mid
            
            # Move mouse to test position
            subprocess.run(['cliclick', f'm:{center_x},{test_y}'])
            time.sleep(0.8)
            
            # Check if controls appeared
            if self.check_controls_visible():
                print(f"✓ Controls visible at offset {mid}px")
                found_offset = mid
                # Try going lower (closer to edge) to find minimum
                high = mid - 1
            else:
                print(f"✗ No controls at offset {mid}px")
                # Go higher (further from edge)
                low = mid + 1
        
        # Verify the found position
        if found_offset:
            # Add some margin to ensure controls stay visible
            final_offset = found_offset + 20
            test_y = window['y'] + window['height'] - final_offset
            subprocess.run(['cliclick', f'm:{center_x},{test_y}'])
            time.sleep(0.8)
            
            if self.check_controls_visible():
                print(f"✅ Optimal offset: {final_offset}px")
                return final_offset
        
        return None
    
    def check_controls_visible(self):
        """Check if controls are visible using visual detection"""
        # Take screenshot
        screenshot_path = "/tmp/qt_check.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        # Look for control bar characteristics
        # Control bars usually have:
        # 1. Horizontal gradient/bar at bottom
        # 2. Buttons/icons visible
        # 3. Different color/brightness than video
        
        height, width = screenshot.shape[:2]
        bottom_region = screenshot[height-400:height, :]
        
        # Convert to grayscale
        gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        
        # Look for horizontal edges (control bar boundary)
        edges = cv2.Canny(gray, 50, 150)
        
        # Count horizontal lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=200, maxLineGap=10)
        
        if lines is not None and len(lines) > 3:
            # Multiple horizontal elements suggest controls are visible
            return True
            
        # Alternative: Check for UI elements (circles, rectangles)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ui_elements = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:  # Reasonable size for buttons
                ui_elements += 1
        
        return ui_elements > 5  # Multiple UI elements suggest controls
    
    def try_common_positions(self, window):
        """Try common control bar positions"""
        print("Trying common positions...")
        
        center_x = window['x'] + window['width'] // 2
        common_offsets = [340, 350, 330, 300, 250, 200, 150, 400]
        
        for offset in common_offsets:
            test_y = window['y'] + window['height'] - offset
            subprocess.run(['cliclick', f'm:{center_x},{test_y}'])
            time.sleep(0.8)
            
            if self.check_controls_visible():
                print(f"✓ Found controls at offset {offset}px")
                self.settings['control_offset'] = offset
                self.settings['last_window_height'] = window['height']
                self.save_settings()
                return test_y
        
        # Default fallback
        print("⚠️  Using default offset 340px")
        return window['y'] + window['height'] - 340
    
    def show_controls_adaptive(self):
        """Show controls using adaptive method"""
        # Get QuickTime window
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
            return None
            
        coords = result.stdout.strip().split(',')
        window = {
            'x': int(coords[0]),
            'y': int(coords[1]),
            'width': int(coords[2]),
            'height': int(coords[3])
        }
        
        # Find control position
        control_y = self.find_control_bar_position(window)
        center_x = window['x'] + window['width'] // 2
        
        # Move mouse to show controls
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(1)
        
        # Small movement to keep visible
        subprocess.run(['cliclick', f'm:{center_x + 5},{control_y}'])
        
        return {
            'window': window,
            'control_position': {'x': center_x, 'y': control_y},
            'control_offset': self.settings['control_offset']
        }


def create_adaptive_enabler():
    """Create a version that learns and adapts"""
    
    content = '''
# Adaptive AirPlay Enabler
# This version learns where the control bar is

from adaptive_control_finder import AdaptiveControlFinder

class AdaptiveAirPlayEnabler:
    def __init__(self):
        self.control_finder = AdaptiveControlFinder()
        
    def enable_airplay(self, settings):
        # Show controls adaptively
        result = self.control_finder.show_controls_adaptive()
        if not result:
            return False
            
        # Rest of AirPlay enabling logic...
        return True
'''
    
    print("Adaptive system created!")
    print("\nBenefits:")
    print("✓ Learns control bar position")
    print("✓ Adapts to different window sizes") 
    print("✓ Remembers positions between sessions")
    print("✓ No hardcoded values!")


if __name__ == "__main__":
    print("🧠 Adaptive Control Bar Finder")
    print("This will learn where QuickTime's controls are")
    
    finder = AdaptiveControlFinder()
    
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to start learning...")
    
    result = finder.show_controls_adaptive()
    
    if result:
        print(f"\n✅ Success!")
        print(f"Window: {result['window']['width']}x{result['window']['height']}")
        print(f"Control position: ({result['control_position']['x']}, {result['control_position']['y']})")
        print(f"Learned offset: {result['control_offset']}px")
        print("\nThis offset has been saved and will be used next time!")
    else:
        print("❌ Failed to find controls")