#!/usr/bin/env python3
"""
Debug checkbox clicking - find exact position
"""

import subprocess
import time
import cv2
from pathlib import Path
from coordinate_converter import CoordinateConverter

class CheckboxDebugger:
    def __init__(self):
        self.converter = CoordinateConverter()
        
    def test_click_positions(self):
        """Test different click positions around the target"""
        print("🎯 Checkbox Click Debugger")
        print("=" * 50)
        
        print("\n📋 Instructions:")
        print("1. Open QuickTime with a video")
        print("2. Manually click AirPlay to open the menu")
        print("3. Keep the menu open")
        
        input("\nPress Enter when AirPlay menu is open...")
        
        # Capture current state
        self.capture_menu_state()
        
        # The attempted position was (759, 639)
        base_x = 759
        base_y = 639
        
        print(f"\n🎯 Base position: ({base_x}, {base_y})")
        print("Testing positions around this point...")
        
        # Test grid around the base position
        offsets = [
            (-20, 0), (-10, 0), (0, 0), (10, 0), (20, 0),  # Horizontal
            (0, -10), (0, -5), (0, 5), (0, 10),            # Vertical
            (-30, 0), (-40, 0), (-50, 0),                  # Further left
        ]
        
        for i, (dx, dy) in enumerate(offsets):
            x = base_x + dx
            y = base_y + dy
            
            print(f"\n🔍 Test {i+1}: Position ({x}, {y}) [offset: {dx:+d}, {dy:+d}]")
            
            # Keep QuickTime active
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(0.2)
            
            # Move mouse to position
            subprocess.run(['cliclick', f'm:{x},{y}'])
            
            response = input("Is the mouse on the checkbox? (y/n/skip): ")
            if response.lower() == 'y':
                print("✅ Found checkbox position!")
                
                # Test click
                test = input("Test click at this position? (y/n): ")
                if test.lower() == 'y':
                    subprocess.run(['cliclick', f'c:{x},{y}'])
                    time.sleep(0.5)
                    
                    worked = input("Did it check/uncheck? (y/n): ")
                    if worked.lower() == 'y':
                        print(f"\n✅ SUCCESS! Working position: ({x}, {y})")
                        print(f"   Offset from base: ({dx:+d}, {dy:+d})")
                        self.save_working_position(x, y)
                        return
            elif response.lower() == 'skip':
                break
        
        # Manual position test
        print("\n🎯 Manual position test")
        print("Move your mouse to the exact checkbox position")
        input("Press Enter when mouse is on checkbox...")
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            manual_x, manual_y = int(coords[0]), int(coords[1])
            print(f"✅ Manual position: ({manual_x}, {manual_y})")
            
            # Calculate offset from base
            offset_x = manual_x - base_x
            offset_y = manual_y - base_y
            print(f"   Offset from base: ({offset_x:+d}, {offset_y:+d})")
            
            # Test click
            test = input("\nTest click at this position? (y/n): ")
            if test.lower() == 'y':
                subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
                time.sleep(0.2)
                subprocess.run(['cliclick', f'c:{manual_x},{manual_y}'])
                
                worked = input("Did it work? (y/n): ")
                if worked.lower() == 'y':
                    self.save_working_position(manual_x, manual_y)
    
    def capture_menu_state(self):
        """Capture menu for analysis"""
        screenshot_path = "/tmp/menu_debug.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        
        if screenshot is not None:
            debug_dir = Path.home() / "checkbox_debug"
            debug_dir.mkdir(exist_ok=True)
            cv2.imwrite(str(debug_dir / "menu_state.png"), screenshot)
            
            # Mark the attempted position
            cv2_x, cv2_y = self.converter.screen_to_cv2(759, 639)
            vis = screenshot.copy()
            cv2.circle(vis, (int(cv2_x), int(cv2_y)), 10, (0, 0, 255), -1)
            cv2.putText(vis, "Attempted", (int(cv2_x - 40), int(cv2_y - 15)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imwrite(str(debug_dir / "attempted_position.png"), vis)
            
            print(f"📸 Debug images saved to: {debug_dir}")
    
    def save_working_position(self, x, y):
        """Save the working position"""
        import json
        
        # Calculate AirPlay position (assuming standard offset)
        airplay_x = x + 80
        airplay_y = y + 160
        
        settings = {
            'airplay_icon_coords': {'x': airplay_x, 'y': airplay_y},
            'apple_tv_coords': {'x': x, 'y': y},
            'checkbox_exact_position': {'x': x, 'y': y},
            'verified_working': True
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
        
        print("\n✅ Working position saved!")


class AlternativeClicker:
    """Try different click methods"""
    
    @staticmethod
    def double_click(x, y):
        """Try double-click"""
        subprocess.run(['cliclick', f'dc:{x},{y}'])
    
    @staticmethod
    def click_and_hold(x, y):
        """Click and hold briefly"""
        subprocess.run(['cliclick', f'dd:{x},{y}'])
        time.sleep(0.1)
        subprocess.run(['cliclick', f'du:{x},{y}'])
    
    @staticmethod
    def move_and_click(x, y):
        """Move to position, wait, then click"""
        subprocess.run(['cliclick', f'm:{x},{y}'])
        time.sleep(0.3)
        subprocess.run(['cliclick', f'c:{x},{y}'])
    
    @staticmethod
    def test_all_methods(x, y):
        """Test different click methods"""
        print(f"\n🧪 Testing click methods at ({x}, {y})")
        
        methods = [
            ("Regular click", lambda: subprocess.run(['cliclick', f'c:{x},{y}'])),
            ("Double click", lambda: AlternativeClicker.double_click(x, y)),
            ("Click and hold", lambda: AlternativeClicker.click_and_hold(x, y)),
            ("Move then click", lambda: AlternativeClicker.move_and_click(x, y))
        ]
        
        for name, method in methods:
            print(f"\n🔍 Testing: {name}")
            input("Press Enter to test...")
            
            # Ensure QuickTime is active
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(0.2)
            
            method()
            
            worked = input("Did it work? (y/n): ")
            if worked.lower() == 'y':
                print(f"✅ Success with: {name}")
                return True
        
        return False


def main():
    print("🔍 Checkbox Click Debugger")
    print("\nOptions:")
    print("1. Test positions around (759, 639)")
    print("2. Test different click methods")
    print("3. Manual position finding")
    
    choice = input("\nSelect (1-3): ")
    
    if choice == '1':
        debugger = CheckboxDebugger()
        debugger.test_click_positions()
    
    elif choice == '2':
        print("\nOpen QuickTime and show AirPlay menu")
        input("Press Enter when ready...")
        
        # Test at the attempted position
        AlternativeClicker.test_all_methods(759, 639)
    
    elif choice == '3':
        print("\nManual position finding")
        print("1. Open QuickTime and show AirPlay menu")
        print("2. Position mouse on the checkbox")
        input("\nPress Enter when mouse is on checkbox...")
        
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            x, y = int(coords[0]), int(coords[1])
            print(f"\n📍 Checkbox position: ({x}, {y})")
            
            # Test it
            test = input("Test click? (y/n): ")
            if test.lower() == 'y':
                subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
                time.sleep(0.2)
                subprocess.run(['cliclick', f'c:{x},{y}'])


if __name__ == "__main__":
    main()