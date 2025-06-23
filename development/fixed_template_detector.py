#!/usr/bin/env python3
"""
Fixed template detector with correct coordinate conversion
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

class FixedTemplateDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.converter = CoordinateConverter()
        
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_with_correct_coordinates(self, template_path, screenshot=None):
        """Find template and return CORRECT screen coordinates"""
        if screenshot is None:
            screenshot = self.capture_screen()
            
        template = cv2.imread(str(template_path))
        if template is None:
            print(f"Could not load template: {template_path}")
            return None
            
        # Try multiple scales
        best_match = None
        best_confidence = 0
        
        scales = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]
        
        for scale in scales:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                # Calculate center in CV2 coordinates
                cv2_x = max_loc[0] + width // 2
                cv2_y = max_loc[1] + height // 2
                
                # Convert to screen coordinates
                screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
                
                best_match = {
                    'cv2_coords': {'x': cv2_x, 'y': cv2_y},
                    'screen_coords': {'x': screen_x, 'y': screen_y},
                    'confidence': max_val,
                    'scale': scale
                }
        
        if best_match and best_confidence > 0.5:
            return best_match
        
        return None
    
    def activate_quicktime(self):
        """Activate QuickTime Player"""
        print("🎬 Activating QuickTime Player...")
        script = '''
        tell application "QuickTime Player"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        time.sleep(0.5)
        
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
        
    def move_mouse_slowly(self, target_x, target_y, steps=20):
        """Move mouse slowly so user can see"""
        # Get current position
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            current = result.stdout.strip().split(',')
            current_x, current_y = int(current[0]), int(current[1])
        else:
            current_x, current_y = 0, 0
            
        print(f"🖱️  Moving mouse from ({current_x}, {current_y}) to ({target_x}, {target_y})...")
        
        for i in range(steps + 1):
            progress = i / steps
            x = int(current_x + (target_x - current_x) * progress)
            y = int(current_y + (target_y - current_y) * progress)
            subprocess.run(['cliclick', f'm:{x},{y}'])
            time.sleep(0.03)
            
    def show_controls(self, window):
        """Show QuickTime controls"""
        print("\n🎮 Showing QuickTime controls...")
        
        # Move to bottom center of window to show controls
        center_x = window['x'] + window['width'] // 2
        bottom_y = window['y'] + window['height'] - 340  # Using the offset you measured
        
        print(f"   Moving to control area...")
        self.move_mouse_slowly(center_x, bottom_y, steps=30)
        
        print("   Waiting for controls to appear...")
        time.sleep(1.5)
        
        # Small movement to keep controls visible
        self.move_mouse_slowly(center_x + 10, bottom_y, steps=5)
        time.sleep(0.5)
        
        print("✅ Controls should be visible now")
        
    def test_airplay_detection(self):
        """Test AirPlay detection with correct coordinates"""
        print("\n🎯 Testing AirPlay Detection with Fixed Coordinates")
        
        # Step 1: Activate QuickTime
        self.activate_quicktime()
        
        # Step 2: Get window info
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime window not found")
            return None
            
        print(f"✅ QuickTime window: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
        
        # Step 3: Show controls
        self.show_controls(window)
        
        # Step 4: Check for template
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            print(f"❌ No template at: {airplay_template}")
            return
            
        # Step 5: Capture and find
        print("\n📸 Capturing screen with controls visible...")
        screenshot = self.capture_screen()
        
        print("🔍 Looking for AirPlay icon...")
        result = self.find_with_correct_coordinates(airplay_template, screenshot)
        
        if result:
            print(f"\n✅ Found AirPlay icon!")
            print(f"   CV2 coordinates: ({result['cv2_coords']['x']}, {result['cv2_coords']['y']})")
            print(f"   Screen coordinates: ({result['screen_coords']['x']}, {result['screen_coords']['y']})")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"   Scale: {result['scale']}")
            print(f"   Conversion factor: {self.converter.scale_factor}")
            
            # Move mouse to show the position
            print("\n🖱️  Moving mouse to AirPlay icon...")
            subprocess.run(['cliclick', f"m:{result['screen_coords']['x']},{result['screen_coords']['y']}"])
            
            confirm = input("Is the mouse on the AirPlay icon? (y/n): ")
            if confirm.lower() == 'y':
                print("✅ Coordinate conversion is working correctly!")
                return result['screen_coords']
            else:
                print("❌ Coordinate conversion still needs adjustment")
        else:
            print("❌ Could not find AirPlay icon")
        
        return None


    def test_apple_tv_detection(self, airplay_coords):
        """Find and click Apple TV checkbox after AirPlay menu is open"""
        print("\n📺 Looking for Apple TV checkbox...")
        
        # Wait for menu to fully appear
        time.sleep(0.8)
        
        # Capture screen with menu
        print("📸 Capturing menu...")
        menu_screenshot = self.capture_screen()
        
        # Try template first
        appletv_template = self.template_dir / "apple_tv_checkbox.png"
        if appletv_template.exists():
            print("🔍 Looking for Apple TV using template...")
            result = self.find_with_correct_coordinates(appletv_template, menu_screenshot)
            
            if result:
                print(f"\n✅ Found Apple TV checkbox!")
                print(f"   Screen coordinates: ({result['screen_coords']['x']}, {result['screen_coords']['y']})")
                print(f"   Confidence: {result['confidence']:.1%}")
                
                # Move mouse to show position
                print("🖱️  Moving to Apple TV checkbox...")
                self.move_mouse_slowly(result['screen_coords']['x'], result['screen_coords']['y'])
                
                confirm = input("Is the mouse on the Apple TV checkbox? (y/n): ")
                if confirm.lower() == 'y':
                    return result['screen_coords']
        
        # If template not found, use offset
        print("\n⚠️  Template not found, using offset method...")
        # Apple TV is typically 50px right, 70px down from AirPlay
        appletv_x = airplay_coords['x'] + 50
        appletv_y = airplay_coords['y'] + 70
        
        print(f"   Estimated position: ({appletv_x}, {appletv_y})")
        self.move_mouse_slowly(appletv_x, appletv_y)
        
        confirm = input("Is this close to the Apple TV checkbox? (y/n): ")
        if confirm.lower() == 'y':
            return {'x': appletv_x, 'y': appletv_y}
            
        # Manual adjustment
        print("\n🎯 Manual adjustment mode")
        print("Use w/a/s/d to move, c to confirm")
        
        x, y = appletv_x, appletv_y
        step = 10
        
        while True:
            cmd = input(f"Position ({x}, {y}): ").lower()
            if cmd == 'c':
                return {'x': x, 'y': y}
            elif cmd == 'w':
                y -= step
            elif cmd == 's':
                y += step
            elif cmd == 'a':
                x -= step
            elif cmd == 'd':
                x += step
            elif cmd == 'q':
                return None
                
            subprocess.run(['cliclick', f'm:{x},{y}'])


def quick_test():
    """Quick test of the fixed detector"""
    print("🔧 Fixed Template Detector Test")
    print(f"This should correctly handle Retina displays")
    
    detector = FixedTemplateDetector()
    
    # Make sure QuickTime is ready
    print("\nMake sure:")
    print("1. QuickTime Player is open")
    print("2. A video is loaded")
    
    input("\nPress Enter when ready...")
    
    airplay_coords = detector.test_airplay_detection()
    
    if airplay_coords:
        print(f"\n🎉 Success! AirPlay coordinates:")
        print(f"   X: {airplay_coords['x']}")
        print(f"   Y: {airplay_coords['y']}")
        
        # Test clicking
        test_click = input("\nTest click on AirPlay? (y/n): ")
        if test_click.lower() == 'y':
            print("Clicking AirPlay...")
            subprocess.run(['cliclick', f"c:{airplay_coords['x']},{airplay_coords['y']}"])
            
            # Now find Apple TV
            appletv_coords = detector.test_apple_tv_detection(airplay_coords)
            
            if appletv_coords:
                print(f"\n🎉 Apple TV coordinates:")
                print(f"   X: {appletv_coords['x']}")
                print(f"   Y: {appletv_coords['y']}")
                
                # Test complete sequence
                test_complete = input("\nTest complete AirPlay sequence? (y/n): ")
                if test_complete.lower() == 'y':
                    print("\n🎬 Running complete sequence...")
                    
                    # Show controls
                    window = detector.get_quicktime_window()
                    if window:
                        detector.show_controls(window)
                    
                    # Click AirPlay
                    print("1️⃣ Clicking AirPlay...")
                    subprocess.run(['cliclick', f"c:{airplay_coords['x']},{airplay_coords['y']}"])
                    time.sleep(1)
                    
                    # Click Apple TV
                    print("2️⃣ Clicking Apple TV...")
                    subprocess.run(['cliclick', f"c:{appletv_coords['x']},{appletv_coords['y']}"])
                    
                    print("\n✅ Complete! AirPlay should now be active.")


if __name__ == "__main__":
    quick_test()