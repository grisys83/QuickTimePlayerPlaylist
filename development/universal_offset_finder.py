#!/usr/bin/env python3
"""
Universal offset finder - finds offset from icons, not text
Works regardless of Apple TV name
"""

import subprocess
import time
import cv2
from pathlib import Path
from coordinate_converter import CoordinateConverter
import json

class UniversalOffsetFinder:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        
    def countdown(self, seconds):
        """Show countdown"""
        for i in range(seconds, 0, -1):
            print(f"\r⏱️  {i} seconds remaining...", end='', flush=True)
            time.sleep(1)
        print("\r✅ Capturing position!      ")
    
    def find_universal_offset(self):
        """Find offset from AirPlay icon to checkbox"""
        print("🎯 Universal Offset Finder")
        print("=" * 50)
        print("\n📋 This finds the offset from AirPlay icon to checkbox")
        print("Works regardless of your Apple TV's name!")
        
        # Step 1: Find AirPlay icon position
        print("\n📍 Step 1: Finding AirPlay icon")
        print("1. Open QuickTime with a video")
        print("2. Show controls (move mouse to bottom)")
        print("3. We'll detect the AirPlay icon automatically")
        
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Get window and show controls
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime window not found")
            return
            
        self.show_controls(window)
        
        # Capture and find AirPlay
        print("\n🔍 Detecting AirPlay icon...")
        screenshot = self.capture_screen()
        airplay_pos = self.find_airplay_icon(screenshot, window)
        
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            print("Make sure controls are visible!")
            return
            
        print(f"✅ Found AirPlay icon at: ({airplay_pos['x']}, {airplay_pos['y']})")
        
        # Step 2: Click AirPlay to open menu
        print("\n📍 Step 2: Opening AirPlay menu")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1.5)
        
        # Step 3: Find checkbox position
        print("\n📍 Step 3: Finding YOUR Apple TV's checkbox")
        print("Position your mouse on YOUR Apple TV's checkbox")
        print("(It might be named 'living', '거실', 'Apple TV', etc.)")
        
        print("\n🎯 Position mouse on checkbox NOW!")
        self.countdown(5)
        
        # Capture checkbox position
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if not result.stdout:
            print("❌ Failed to get position")
            return
            
        coords = result.stdout.strip().split(',')
        checkbox_x, checkbox_y = int(coords[0]), int(coords[1])
        
        print(f"\n✅ Checkbox position: ({checkbox_x}, {checkbox_y})")
        
        # Calculate offset
        offset_x = checkbox_x - airplay_pos['x']
        offset_y = checkbox_y - airplay_pos['y']
        
        print(f"\n📐 Universal offset from AirPlay icon:")
        print(f"   X offset: {offset_x:+d} pixels")
        print(f"   Y offset: {offset_y:+d} pixels")
        
        # Visualize
        self.visualize_offset(screenshot, airplay_pos, checkbox_x, checkbox_y)
        
        # Test click
        print("\n🧪 Testing click in 3 seconds...")
        self.countdown(3)
        
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
        
        print("\n❓ Did the checkbox get checked/unchecked? (y/n): ", end='')
        response = input()
        
        if response.lower() == 'y':
            print("\n✅ Success! Saving universal offset...")
            self.save_universal_offset(offset_x, offset_y, airplay_pos, checkbox_x, checkbox_y)
        else:
            print("\n❌ Click didn't work, trying alternative positions...")
            self.try_alternative_positions(airplay_pos, offset_x, offset_y)
    
    def find_offset_from_apple_tv_icon(self):
        """Alternative: Find offset from Apple TV device icon in menu"""
        print("🎯 Offset from Apple TV Icon Method")
        print("=" * 50)
        
        print("\n📋 Instructions:")
        print("1. Open QuickTime and click AirPlay to show menu")
        print("2. You'll position mouse on:")
        print("   - First: The Apple TV/device icon")
        print("   - Then: The checkbox")
        
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        
        # Step 1: Apple TV icon
        print("\n📍 Step 1: Position mouse on Apple TV ICON (not text)")
        print("🎯 Position mouse NOW!")
        self.countdown(5)
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if not result.stdout:
            return
            
        coords = result.stdout.strip().split(',')
        icon_x, icon_y = int(coords[0]), int(coords[1])
        print(f"✅ Apple TV icon: ({icon_x}, {icon_y})")
        
        # Step 2: Checkbox
        print("\n📍 Step 2: Position mouse on the CHECKBOX")
        print("🎯 Position mouse NOW!")
        self.countdown(5)
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if not result.stdout:
            return
            
        coords = result.stdout.strip().split(',')
        checkbox_x, checkbox_y = int(coords[0]), int(coords[1])
        print(f"✅ Checkbox: ({checkbox_x}, {checkbox_y})")
        
        # Calculate offset
        offset_x = checkbox_x - icon_x
        offset_y = checkbox_y - icon_y
        
        print(f"\n📐 Offset from Apple TV icon to checkbox:")
        print(f"   X: {offset_x:+d} pixels")
        print(f"   Y: {offset_y:+d} pixels")
        
        # Test
        print("\n🧪 Testing click...")
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
        
        print("\n❓ Did it work? (y/n): ", end='')
        if input().lower() == 'y':
            self.save_appletv_icon_offset(offset_x, offset_y)
    
    def find_airplay_icon(self, screenshot, window):
        """Find AirPlay icon in control bar"""
        # Convert window to CV2 coords
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Control bar ROI
        if window['height'] < 400:
            roi_top = int(win_cv2_y2 - window['height'] * 0.8)
            roi_bottom = int(win_cv2_y2 - window['height'] * 0.05)
        else:
            roi_top = int(win_cv2_y2 - 450)
            roi_bottom = int(win_cv2_y2 - 150)
        
        roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Find AirPlay template
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            print(f"❌ Template not found: {airplay_template}")
            return None
            
        template = cv2.imread(str(airplay_template))
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            cv2_x = win_cv2_x1 + max_loc[0] + template.shape[1] // 2
            cv2_y = roi_top + max_loc[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
    def visualize_offset(self, screenshot, airplay_pos, checkbox_x, checkbox_y):
        """Visualize the offset"""
        vis = screenshot.copy()
        
        # Convert positions to CV2
        airplay_cv2_x, airplay_cv2_y = self.converter.screen_to_cv2(airplay_pos['x'], airplay_pos['y'])
        checkbox_cv2_x, checkbox_cv2_y = self.converter.screen_to_cv2(checkbox_x, checkbox_y)
        
        # Draw AirPlay position
        cv2.circle(vis, (int(airplay_cv2_x), int(airplay_cv2_y)), 10, (0, 255, 0), -1)
        cv2.putText(vis, "AirPlay", (int(airplay_cv2_x - 30), int(airplay_cv2_y - 15)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw checkbox position
        cv2.circle(vis, (int(checkbox_cv2_x), int(checkbox_cv2_y)), 10, (255, 0, 0), -1)
        cv2.putText(vis, "Checkbox", (int(checkbox_cv2_x - 35), int(checkbox_cv2_y - 15)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Draw line showing offset
        cv2.line(vis, (int(airplay_cv2_x), int(airplay_cv2_y)), 
                (int(checkbox_cv2_x), int(checkbox_cv2_y)), (255, 255, 0), 2)
        
        # Save
        debug_dir = Path.home() / "universal_offset_debug"
        debug_dir.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_dir / "offset_visualization.png"), vis)
        print(f"\n📸 Visualization saved to: {debug_dir}")
    
    def save_universal_offset(self, offset_x, offset_y, airplay_pos, checkbox_x, checkbox_y):
        """Save the universal offset"""
        settings = {
            'airplay_to_checkbox_offset': {
                'x': offset_x,
                'y': offset_y
            },
            'last_known_positions': {
                'airplay': {'x': airplay_pos['x'], 'y': airplay_pos['y']},
                'checkbox': {'x': checkbox_x, 'y': checkbox_y}
            },
            'universal_offset_verified': True
        }
        
        # Save to settings
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
        
        print("✅ Universal offset saved!")
        print(f"\n📋 To use in any script:")
        print(f"   checkbox_x = airplay_x + {offset_x:+d}")
        print(f"   checkbox_y = airplay_y + {offset_y:+d}")
    
    def save_appletv_icon_offset(self, offset_x, offset_y):
        """Save offset from Apple TV icon"""
        settings = {
            'appletv_icon_to_checkbox_offset': {
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
        
        print("✅ Apple TV icon offset saved!")
    
    def try_alternative_positions(self, airplay_pos, base_offset_x, base_offset_y):
        """Try slight variations of the position"""
        print("\n🔍 Trying alternative positions...")
        
        variations = [
            (0, -5), (0, -10), (0, 5), (0, 10),  # Vertical adjustments
            (-5, 0), (-10, 0), (5, 0), (10, 0),  # Horizontal adjustments
        ]
        
        for dx, dy in variations:
            test_x = airplay_pos['x'] + base_offset_x + dx
            test_y = airplay_pos['y'] + base_offset_y + dy
            
            print(f"\n🧪 Testing offset ({base_offset_x + dx:+d}, {base_offset_y + dy:+d})")
            subprocess.run(['cliclick', f'm:{test_x},{test_y}'])
            time.sleep(0.5)
            subprocess.run(['cliclick', f'c:{test_x},{test_y}'])
            
            print("Did it work? (y/n): ", end='')
            if input().lower() == 'y':
                self.save_universal_offset(base_offset_x + dx, base_offset_y + dy, 
                                         airplay_pos, test_x, test_y)
                return
    
    def show_controls(self, window):
        """Show QuickTime controls"""
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 250
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.8)
    
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/universal_offset.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def get_quicktime_window(self):
        """Get QuickTime window info"""
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
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            return {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
        return None


def main():
    finder = UniversalOffsetFinder()
    
    print("🔍 Universal Offset Finder")
    print("\nOptions:")
    print("1. Find offset from AirPlay icon (recommended)")
    print("2. Find offset from Apple TV device icon")
    
    choice = input("\nSelect (1-2): ")
    
    if choice == '1':
        finder.find_universal_offset()
    elif choice == '2':
        finder.find_offset_from_apple_tv_icon()


if __name__ == "__main__":
    main()