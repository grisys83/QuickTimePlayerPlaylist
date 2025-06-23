#!/usr/bin/env python3
"""
Smart AirPlay detector that works step by step
"""

import cv2
import numpy as np
import subprocess
import time
from pathlib import Path
import json

class SmartAirPlayDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_mode = True
        
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_quicktime_window(self):
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
    
    def step1_find_airplay_icon(self):
        """Step 1: Find AirPlay icon in QuickTime controls"""
        print("\n=== Step 1: Finding AirPlay Icon ===")
        
        # Get QuickTime window
        qt_window = self.find_quicktime_window()
        if not qt_window:
            print("❌ QuickTime window not found")
            return None
            
        print(f"✓ QuickTime window found at ({qt_window['x']}, {qt_window['y']})")
        
        # Show controls by moving mouse to bottom
        center_x = qt_window['x'] + qt_window['width'] // 2
        bottom_y = qt_window['y'] + qt_window['height'] - 340
        print(f"✓ Moving mouse to show controls at ({center_x}, {bottom_y})")
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        time.sleep(1)
        
        # Capture screen
        screenshot = self.capture_screen()
        
        # Try template matching if available
        airplay_template = self.template_dir / "airplay_icon.png"
        if airplay_template.exists():
            print("✓ Using template matching")
            from template_based_detector import TemplateBasedDetector
            detector = TemplateBasedDetector()
            result = detector.find_with_multiple_scales(airplay_template, screenshot)
            
            if result and result['confidence'] > 0.5:
                print(f"✓ Found AirPlay icon with {result['confidence']:.1%} confidence")
                return {'x': result['x'], 'y': result['y']}
        
        # Fallback: Use relative positioning
        print("⚠️  Using relative positioning (template not found)")
        # AirPlay is typically 150px from right, 50px from bottom
        airplay_x = qt_window['x'] + qt_window['width'] - 150
        airplay_y = qt_window['y'] + qt_window['height'] - 50
        
        return {'x': airplay_x, 'y': airplay_y}
    
    def step2_click_airplay_and_wait(self, airplay_pos):
        """Step 2: Click AirPlay and wait for menu"""
        print("\n=== Step 2: Opening AirPlay Menu ===")
        
        print(f"✓ Clicking AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        
        print("✓ Waiting for menu to appear...")
        time.sleep(0.8)
        
        # Capture screen with menu
        screenshot = self.capture_screen()
        
        if self.debug_mode:
            cv2.imwrite("debug_airplay_menu.png", screenshot)
            print("✓ Saved menu screenshot to debug_airplay_menu.png")
            
        return screenshot
    
    def step3_find_apple_tv_in_menu(self, menu_screenshot, airplay_pos):
        """Step 3: Find Apple TV in the menu"""
        print("\n=== Step 3: Finding Apple TV in Menu ===")
        
        # Define search area around where menu should appear
        search_x = max(0, airplay_pos['x'] - 200)
        search_y = airplay_pos['y'] + 10
        search_width = 400
        search_height = 300
        
        # Extract menu area
        menu_area = menu_screenshot[
            search_y:min(search_y + search_height, menu_screenshot.shape[0]),
            search_x:min(search_x + search_width, menu_screenshot.shape[1])
        ]
        
        if self.debug_mode:
            cv2.imwrite("debug_menu_area.png", menu_area)
            print(f"✓ Extracted menu area: {menu_area.shape}")
        
        # Method 1: Template matching for Apple TV
        appletv_template = self.template_dir / "apple_tv_checkbox.png"
        if appletv_template.exists():
            print("✓ Using Apple TV template")
            from template_based_detector import TemplateBasedDetector
            detector = TemplateBasedDetector()
            
            # Try to find the template in the menu area
            template = cv2.imread(str(appletv_template))
            result = detector.find_with_multiple_scales(appletv_template, menu_screenshot)
            
            if result and result['confidence'] > 0.5:
                print(f"✓ Found Apple TV with {result['confidence']:.1%} confidence")
                return {'x': result['x'], 'y': result['y']}
        
        # Method 2: Look for checkbox patterns
        print("⚠️  Looking for checkbox patterns")
        checkbox_pos = self._find_checkboxes_in_menu(menu_area, search_x, search_y)
        if checkbox_pos:
            print("✓ Found checkbox pattern")
            return checkbox_pos
            
        # Method 3: Use offset from AirPlay icon
        print("⚠️  Using estimated position")
        # Typically: right 50px, down 70px from AirPlay
        return {
            'x': airplay_pos['x'] + 50,
            'y': airplay_pos['y'] + 70
        }
    
    def _find_checkboxes_in_menu(self, menu_area, offset_x, offset_y):
        """Find checkbox patterns in menu"""
        # Convert to grayscale
        gray = cv2.cvtColor(menu_area, cv2.COLOR_BGR2GRAY)
        
        # Look for square shapes (checkboxes)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        checkboxes = []
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Checkbox characteristics
            if 12 < w < 25 and 12 < h < 25:  # Size
                aspect_ratio = w / h
                if 0.8 < aspect_ratio < 1.2:  # Square-ish
                    checkboxes.append({
                        'x': offset_x + x + w // 2,
                        'y': offset_y + y + h // 2
                    })
        
        # Return the first checkbox found (usually Apple TV)
        if checkboxes:
            return checkboxes[0]
        return None
    
    def detect_complete_sequence(self):
        """Run complete detection sequence"""
        print("🚀 Starting Smart AirPlay Detection")
        print("=" * 50)
        
        # Step 1: Find AirPlay icon
        airplay_pos = self.step1_find_airplay_icon()
        if not airplay_pos:
            print("❌ Failed to find AirPlay icon")
            return None
            
        # Step 2: Click and wait for menu
        menu_screenshot = self.step2_click_airplay_and_wait(airplay_pos)
        
        # Step 3: Find Apple TV in menu
        appletv_pos = self.step3_find_apple_tv_in_menu(menu_screenshot, airplay_pos)
        
        # Close menu
        print("\n✓ Closing menu")
        subprocess.run(['cliclick', 'c:100,100'])
        
        result = {
            'airplay_icon_coords': {'x': airplay_pos['x'], 'y': airplay_pos['y']},
            'apple_tv_coords': {'x': appletv_pos['x'], 'y': appletv_pos['y']}
        }
        
        print("\n✅ Detection Complete!")
        print(f"AirPlay Icon: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        
        return result
    
    def test_detection(self):
        """Test the detected positions"""
        coords = self.detect_complete_sequence()
        if not coords:
            return
            
        print("\n🧪 Testing detected positions...")
        test = input("Test by clicking the positions? (y/n): ")
        
        if test.lower() == 'y':
            # First, get QuickTime window and show controls
            qt_window = self.find_quicktime_window()
            if qt_window:
                print("Showing QuickTime controls...")
                center_x = qt_window['x'] + qt_window['width'] // 2
                bottom_y = qt_window['y'] + qt_window['height'] - 20
                subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
                time.sleep(1.5)  # Wait for controls to appear
                
            print("Clicking AirPlay...")
            subprocess.run(['cliclick', f"c:{coords['airplay_icon_coords']['x']},{coords['airplay_icon_coords']['y']}"])
            time.sleep(1.5)  # Wait for menu to appear
            
            print("Clicking Apple TV...")
            subprocess.run(['cliclick', f"c:{coords['apple_tv_coords']['x']},{coords['apple_tv_coords']['y']}"])
            time.sleep(0.5)
            
            print("✓ Test complete!")
        
        # Save settings
        save = input("\nSave these settings? (y/n): ")
        if save.lower() == 'y':
            settings = coords.copy()
            settings['airplay_configured'] = True
            settings['detection_method'] = 'smart'
            
            # Save to both apps
            for filename in ['.quickdrop_settings.json', '.quicktime_converter_settings.json']:
                settings_file = Path.home() / filename
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                print(f"✓ Saved to {settings_file}")


def main():
    detector = SmartAirPlayDetector()
    
    print("Smart AirPlay Detector")
    print("This will detect AirPlay positions step by step")
    print("\nMake sure:")
    print("1. QuickTime Player is open")
    print("2. A video is loaded")
    print("3. You can see the video playing")
    
    input("\nPress Enter to start...")
    
    detector.test_detection()


if __name__ == "__main__":
    main()