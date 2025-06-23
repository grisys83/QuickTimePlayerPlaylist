#!/usr/bin/env python3
"""
Apple TV icon detector
1. Click AirPlay to open menu
2. Find Apple TV icon in the menu
3. Click checkbox relative to the icon
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import json
import numpy as np

class AppleTVIconDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path.home() / "appletv_detection_debug"
        self.debug_dir.mkdir(exist_ok=True)
        
    def detect_and_enable(self):
        """Main detection flow"""
        print("🎯 Apple TV Icon Detection")
        print("=" * 50)
        
        # Step 1: Get QuickTime window
        print("\n📍 Step 1: Finding QuickTime window...")
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime not found")
            return False
            
        # Step 2: Show controls and find AirPlay
        print("\n📍 Step 2: Finding AirPlay icon...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        self.show_controls(window)
        screenshot = self.capture_screen("controls")
        
        airplay_pos = self.find_airplay_icon(screenshot, window)
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            return False
            
        print(f"✅ Found AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})")
        
        # Step 3: Click AirPlay to open menu
        print("\n📍 Step 3: Opening AirPlay menu...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1.5)  # Wait for menu animation
        
        # Step 4: Find Apple TV icon in menu
        print("\n📍 Step 4: Finding Apple TV icon in menu...")
        menu_screenshot = self.capture_screen("menu")
        
        appletv_pos = self.find_appletv_icon(menu_screenshot, airplay_pos)
        if not appletv_pos:
            print("❌ Could not find Apple TV icon")
            print("📸 Check debug images in:", self.debug_dir)
            return False
            
        print(f"✅ Found Apple TV icon at ({appletv_pos['x']}, {appletv_pos['y']})")
        
        # Step 5: Click checkbox (to the RIGHT of icon)
        checkbox_x = appletv_pos['x'] + 246  # Checkbox is 246px to the right
        checkbox_y = appletv_pos['y']
        
        print(f"\n📍 Step 5: Clicking checkbox at ({checkbox_x}, {checkbox_y})...")
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
        
        # Save successful positions
        self.save_positions(airplay_pos, appletv_pos, checkbox_x, checkbox_y)
        
        print("\n✅ AirPlay should now be enabled!")
        return True
    
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
        
        # Save ROI for debug
        cv2.imwrite(str(self.debug_dir / "control_bar_roi.png"), roi)
        
        # Find AirPlay template
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            print(f"❌ Template not found: {airplay_template}")
            return None
            
        template = cv2.imread(str(airplay_template))
        
        # Try multiple scales
        best_match = None
        best_val = 0
        
        for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            result = cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_match = {
                    'loc': max_loc,
                    'size': (width, height),
                    'scale': scale
                }
        
        if best_match and best_val > 0.5:
            cv2_x = win_cv2_x1 + best_match['loc'][0] + best_match['size'][0] // 2
            cv2_y = roi_top + best_match['loc'][1] + best_match['size'][1] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            print(f"   AirPlay confidence: {best_val:.1%}")
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
    def find_appletv_icon(self, menu_screenshot, airplay_pos):
        """Find Apple TV icon in the menu"""
        # Define search area around where menu appears
        height, width = menu_screenshot.shape[:2]
        airplay_cv2_x, airplay_cv2_y = self.converter.screen_to_cv2(airplay_pos['x'], airplay_pos['y'])
        
        # Menu appears above/around AirPlay icon
        search_left = max(0, int(airplay_cv2_x - 400))
        search_right = min(width, int(airplay_cv2_x + 400))
        search_top = max(0, int(airplay_cv2_y - 800))
        search_bottom = int(airplay_cv2_y)
        
        search_roi = menu_screenshot[search_top:search_bottom, search_left:search_right]
        
        # Save search area
        cv2.imwrite(str(self.debug_dir / "menu_search_area.png"), search_roi)
        
        # Try different Apple TV icon templates
        possible_templates = [
            "apple_tv_icon.png",      # TV icon
            "appletv_device.png",      # Device icon
            "tv_icon.png",             # Generic TV
            "apple_tv_menu_icon.png"   # Menu specific
        ]
        
        best_match = None
        best_confidence = 0
        best_template_name = None
        
        for template_name in possible_templates:
            template_path = self.template_dir / template_name
            if not template_path.exists():
                continue
                
            template = cv2.imread(str(template_path))
            if template is None:
                continue
            
            # Try template matching
            result = cv2.matchTemplate(search_roi, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"   {template_name}: {max_val:.1%}")
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = {
                    'loc': max_loc,
                    'size': (template.shape[1], template.shape[0])
                }
                best_template_name = template_name
        
        if best_match and best_confidence > 0.5:
            # Convert to full image coordinates
            cv2_x = search_left + best_match['loc'][0] + best_match['size'][0] // 2
            cv2_y = search_top + best_match['loc'][1] + best_match['size'][1] // 2
            
            # Visualize found position
            vis = menu_screenshot.copy()
            cv2.rectangle(vis, 
                         (int(cv2_x - best_match['size'][0]//2), int(cv2_y - best_match['size'][1]//2)),
                         (int(cv2_x + best_match['size'][0]//2), int(cv2_y + best_match['size'][1]//2)),
                         (0, 255, 0), 2)
            cv2.putText(vis, f"Apple TV {best_confidence:.0%}", 
                       (int(cv2_x - 40), int(cv2_y - 20)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw checkbox target (246 pixels to the RIGHT)
            checkbox_cv2_x = cv2_x + 246 * self.converter.scale_factor  # Adjust for retina
            cv2.circle(vis, (int(checkbox_cv2_x), int(cv2_y)), 8, (255, 0, 0), -1)
            cv2.putText(vis, "Checkbox", 
                       (int(checkbox_cv2_x - 35), int(cv2_y + 25)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            cv2.imwrite(str(self.debug_dir / "appletv_found.png"), vis)
            
            # Convert to screen coordinates
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            print(f"✅ Found with {best_template_name}")
            return {'x': screen_x, 'y': screen_y}
        
        print("❌ No Apple TV icon found")
        print("💡 You may need to create a template of your Apple TV icon")
        return None
    
    def create_appletv_template(self):
        """Helper to create Apple TV icon template"""
        print("\n📸 Apple TV Icon Template Creator")
        print("1. Open QuickTime and click AirPlay to show menu")
        print("2. Take a screenshot of just the Apple TV icon")
        print("3. Save it as 'apple_tv_icon.png' in templates/")
        
        print("\n⏰ Opening AirPlay menu in 3 seconds...")
        time.sleep(3)
        
        # Find and click AirPlay
        window = self.get_quicktime_window()
        if window:
            self.show_controls(window)
            screenshot = self.capture_screen("template_controls")
            airplay_pos = self.find_airplay_icon(screenshot, window)
            
            if airplay_pos:
                subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
                time.sleep(1.5)
                
                # Capture menu
                menu_screenshot = self.capture_screen("template_menu")
                cv2.imwrite(str(self.debug_dir / "menu_for_template.png"), menu_screenshot)
                
                print(f"\n📸 Menu screenshot saved to: {self.debug_dir / 'menu_for_template.png'}")
                print("Crop the Apple TV icon and save as templates/apple_tv_icon.png")
    
    def show_controls(self, window):
        """Show QuickTime controls"""
        center_x = window['x'] + window['width'] // 2
        if window['height'] < 400:
            control_y = window['y'] + int(window['height'] * 0.65)
        else:
            control_y = window['y'] + window['height'] - 250
        
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.8)
    
    def capture_screen(self, name):
        """Capture screen"""
        screenshot_path = f"/tmp/{name}.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        # Save copy for debug
        if screenshot is not None:
            cv2.imwrite(str(self.debug_dir / f"{name}.png"), screenshot)
        
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
    
    def save_positions(self, airplay_pos, appletv_pos, checkbox_x, checkbox_y):
        """Save successful positions"""
        settings = {
            'airplay_icon_coords': airplay_pos,
            'apple_tv_icon_coords': appletv_pos,
            'apple_tv_checkbox_coords': {'x': checkbox_x, 'y': checkbox_y},
            'icon_to_checkbox_offset': {
                'x': checkbox_x - appletv_pos['x'],
                'y': checkbox_y - appletv_pos['y']
            },
            'detection_method': 'appletv_icon',
            'last_detection': time.strftime('%Y-%m-%d %H:%M:%S')
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
        
        print("\n💾 Positions saved successfully!")


def main():
    detector = AppleTVIconDetector()
    
    print("🍎 Apple TV Icon Detector")
    print("\nOptions:")
    print("1. Detect and enable AirPlay")
    print("2. Create Apple TV icon template")
    
    choice = input("\nSelect (1-2): ")
    
    if choice == '1':
        print("\nMake sure QuickTime is open with a video")
        input("Press Enter to start...")
        
        detector.detect_and_enable()
        
    elif choice == '2':
        detector.create_appletv_template()


if __name__ == "__main__":
    main()