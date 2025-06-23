#!/usr/bin/env python3
"""
Auto position finder with 5-second timer
No need to press Enter - just position your mouse
"""

import subprocess
import time
import cv2
from pathlib import Path
from coordinate_converter import CoordinateConverter

class AutoPositionFinder:
    def __init__(self):
        self.converter = CoordinateConverter()
        
    def countdown(self, seconds):
        """Show countdown"""
        for i in range(seconds, 0, -1):
            print(f"\r⏱️  {i} seconds remaining...", end='', flush=True)
            time.sleep(1)
        print("\r✅ Capturing position!      ")
    
    def find_checkbox_auto(self):
        """Find checkbox position with auto timer"""
        print("🎯 Auto Checkbox Position Finder")
        print("=" * 50)
        
        print("\n📋 Instructions:")
        print("1. Open QuickTime with a video")
        print("2. Click AirPlay to open the menu")
        print("3. Position your mouse on the 'living' checkbox")
        print("4. You have 5 seconds to position - no need to press Enter!")
        
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        print("\n🎯 Position your mouse on the checkbox NOW!")
        self.countdown(5)
        
        # Capture position
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if not result.stdout:
            print("❌ Failed to get position")
            return None
            
        coords = result.stdout.strip().split(',')
        checkbox_x, checkbox_y = int(coords[0]), int(coords[1])
        
        print(f"\n📍 Captured checkbox position: ({checkbox_x}, {checkbox_y})")
        
        # Capture screenshot for verification
        self.capture_and_mark(checkbox_x, checkbox_y)
        
        # Test click after short delay
        print("\n🧪 Testing click in 3 seconds...")
        print("Watch if the checkbox changes state!")
        self.countdown(3)
        
        # Click
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
        
        print("\n❓ Did the checkbox get checked/unchecked? (y/n): ", end='')
        response = input()
        
        if response.lower() == 'y':
            print("\n✅ Success! Saving position...")
            self.save_position(checkbox_x, checkbox_y)
            return {'x': checkbox_x, 'y': checkbox_y}
        else:
            print("\n❌ Click didn't work")
            return None
    
    def find_multiple_positions(self):
        """Find multiple UI elements with auto timer"""
        print("🎯 Multi-Position Finder")
        print("=" * 50)
        
        positions = {}
        
        # Step 1: Find Apple TV text
        print("\n📍 Step 1: Finding 'living' text position")
        print("Position your mouse on the 'living' TEXT (not checkbox)")
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        print("\n🎯 Position mouse on 'living' text NOW!")
        self.countdown(5)
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            text_x, text_y = int(coords[0]), int(coords[1])
            positions['text'] = {'x': text_x, 'y': text_y}
            print(f"✅ Text position: ({text_x}, {text_y})")
        
        # Step 2: Find checkbox
        print("\n📍 Step 2: Finding checkbox position")
        print("Now position your mouse on the CHECKBOX for 'living'")
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        print("\n🎯 Position mouse on checkbox NOW!")
        self.countdown(5)
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            checkbox_x, checkbox_y = int(coords[0]), int(coords[1])
            positions['checkbox'] = {'x': checkbox_x, 'y': checkbox_y}
            print(f"✅ Checkbox position: ({checkbox_x}, {checkbox_y})")
        
        # Calculate offset
        if 'text' in positions and 'checkbox' in positions:
            offset_x = positions['checkbox']['x'] - positions['text']['x']
            offset_y = positions['checkbox']['y'] - positions['text']['y']
            print(f"\n📐 Offset from text to checkbox: ({offset_x:+d}, {offset_y:+d})")
            
            # Test click
            print("\n🧪 Testing checkbox click in 3 seconds...")
            self.countdown(3)
            
            subprocess.run(['cliclick', f"c:{positions['checkbox']['x']},{positions['checkbox']['y']}"])
            
            print("\n❓ Did it work? (y/n): ", end='')
            if input().lower() == 'y':
                self.save_position(positions['checkbox']['x'], positions['checkbox']['y'])
                self.save_offset(offset_x, offset_y)
        
        return positions
    
    def capture_and_mark(self, x, y):
        """Capture screen and mark position"""
        screenshot_path = "/tmp/position_check.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        
        if screenshot is not None:
            # Convert to CV2 coords and mark
            cv2_x, cv2_y = self.converter.screen_to_cv2(x, y)
            cv2.circle(screenshot, (int(cv2_x), int(cv2_y)), 10, (0, 255, 0), -1)
            cv2.putText(screenshot, f"({x}, {y})", 
                       (int(cv2_x - 30), int(cv2_y - 15)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Save
            debug_dir = Path.home() / "auto_position_debug"
            debug_dir.mkdir(exist_ok=True)
            cv2.imwrite(str(debug_dir / "marked_position.png"), screenshot)
            print(f"📸 Screenshot saved to: {debug_dir / 'marked_position.png'}")
    
    def save_position(self, x, y):
        """Save working position"""
        import json
        
        settings = {
            'apple_tv_coords': {'x': x, 'y': y},
            'checkbox_verified': True,
            'found_with': 'auto_timer'
        }
        
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            
            existing = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    try:
                        existing = json.load(f)
                    except:
                        pass
            
            existing.update(settings)
            
            with open(settings_file, 'w') as f:
                json.dump(existing, f, indent=2)
        
        print("✅ Position saved to settings!")
    
    def save_offset(self, offset_x, offset_y):
        """Save text to checkbox offset"""
        import json
        
        settings = {
            'text_to_checkbox_offset': {
                'x': offset_x,
                'y': offset_y
            }
        }
        
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            
            existing = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    try:
                        existing = json.load(f)
                    except:
                        pass
            
            existing.update(settings)
            
            with open(settings_file, 'w') as f:
                json.dump(existing, f, indent=2)


def main():
    finder = AutoPositionFinder()
    
    print("🔍 Auto Position Finder")
    print("\nOptions:")
    print("1. Find checkbox only")
    print("2. Find both text and checkbox (calculate offset)")
    
    choice = input("\nSelect (1-2): ")
    
    if choice == '1':
        finder.find_checkbox_auto()
    elif choice == '2':
        finder.find_multiple_positions()


if __name__ == "__main__":
    main()