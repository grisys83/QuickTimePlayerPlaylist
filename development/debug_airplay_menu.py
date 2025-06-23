#!/usr/bin/env python3
"""
Debug AirPlay menu detection - find Apple TV first
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import json

class AirPlayMenuDebugger:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path.home() / "airplay_menu_debug"
        self.debug_dir.mkdir(exist_ok=True)
        
    def debug_menu_detection(self):
        """Debug the menu detection step by step"""
        print("🔍 AirPlay Menu Debugger")
        print("=" * 50)
        
        print("\n📋 Steps:")
        print("1. Open QuickTime with a video")
        print("2. We'll show controls and click AirPlay")
        print("3. Then debug the menu detection")
        
        input("\nPress Enter when ready...")
        
        # Get window
        window = self.get_quicktime_window()
        if not window:
            return
            
        # Activate and show controls
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Show controls
        center_x = window['x'] + window['width'] // 2
        if window['height'] < 400:
            control_y = window['y'] + int(window['height'] * 0.65)
        else:
            control_y = window['y'] + window['height'] - 250
            
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(1)
        
        # Find AirPlay icon first
        print("\n🔍 Step 1: Finding AirPlay icon...")
        screenshot1 = self.capture_screen()
        airplay_pos = self.find_airplay_icon(screenshot1, window)
        
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            return
            
        print(f"✅ Found AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})")
        
        # Click AirPlay
        print("\n🖱️ Clicking AirPlay icon...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1.5)
        
        # Capture menu
        print("\n📸 Capturing menu...")
        menu_screenshot = self.capture_screen()
        cv2.imwrite(str(self.debug_dir / "1_menu_full.png"), menu_screenshot)
        
        # Debug menu detection
        self.debug_menu_roi(menu_screenshot, airplay_pos)
        
    def find_airplay_icon(self, screenshot, window):
        """Find AirPlay icon in control bar"""
        # Convert window to CV2 coords
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Define control bar ROI
        if window['height'] < 400:
            roi_top_offset = int(window['height'] * 0.8)
            roi_bottom_offset = int(window['height'] * 0.05)
        else:
            roi_top_offset = 450
            roi_bottom_offset = 150
            
        roi_top = int(win_cv2_y2 - roi_top_offset)
        roi_bottom = int(win_cv2_y2 - roi_bottom_offset)
        
        # Extract ROI
        control_roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Find AirPlay template
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            print(f"❌ Template not found: {airplay_template}")
            return None
            
        template = cv2.imread(str(airplay_template))
        
        # Try to find
        result = cv2.matchTemplate(control_roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            # Convert to full coords
            cv2_x = win_cv2_x1 + max_loc[0] + template.shape[1] // 2
            cv2_y = roi_top + max_loc[1] + template.shape[0] // 2
            
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            return {'x': screen_x, 'y': screen_y, 'cv2_x': cv2_x, 'cv2_y': cv2_y}
            
        return None
    
    def debug_menu_roi(self, menu_screenshot, airplay_pos):
        """Debug the menu ROI and Apple TV detection"""
        print("\n🔍 Debugging menu detection...")
        
        height, width = menu_screenshot.shape[:2]
        airplay_cv2_x, airplay_cv2_y = airplay_pos['cv2_x'], airplay_pos['cv2_y']
        
        # Define menu ROI - MUCH larger for small windows
        # Menu can be quite large relative to window size
        menu_roi_left = max(0, int(airplay_cv2_x - 400))
        menu_roi_right = min(width, int(airplay_cv2_x + 400))
        menu_roi_top = max(0, int(airplay_cv2_y - 800))  # Much taller
        menu_roi_bottom = int(airplay_cv2_y - 20)
        
        print(f"\n📐 Menu ROI:")
        print(f"   Left: {menu_roi_left}")
        print(f"   Right: {menu_roi_right}")
        print(f"   Top: {menu_roi_top}")
        print(f"   Bottom: {menu_roi_bottom}")
        print(f"   Size: {menu_roi_right - menu_roi_left} x {menu_roi_bottom - menu_roi_top}")
        
        # Visualize ROI
        vis = menu_screenshot.copy()
        cv2.rectangle(vis, (menu_roi_left, menu_roi_top), 
                     (menu_roi_right, menu_roi_bottom), (0, 255, 0), 2)
        cv2.putText(vis, "Menu ROI", (menu_roi_left, menu_roi_top - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mark AirPlay position
        cv2.circle(vis, (int(airplay_cv2_x), int(airplay_cv2_y)), 10, (0, 0, 255), -1)
        cv2.putText(vis, "AirPlay", (int(airplay_cv2_x + 15), int(airplay_cv2_y)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        cv2.imwrite(str(self.debug_dir / "2_menu_roi_vis.png"), vis)
        
        # Extract ROI
        if menu_roi_top < menu_roi_bottom and menu_roi_left < menu_roi_right:
            menu_roi = menu_screenshot[menu_roi_top:menu_roi_bottom, menu_roi_left:menu_roi_right]
            cv2.imwrite(str(self.debug_dir / "3_menu_roi_extracted.png"), menu_roi)
            
            # Try to find Apple TV text
            print("\n🔍 Looking for Apple TV text/icon...")
            self.find_apple_tv_in_roi(menu_roi, menu_roi_left, menu_roi_top)
        else:
            print("❌ Invalid ROI dimensions")
    
    def find_apple_tv_in_roi(self, roi, roi_left, roi_top):
        """Try to find Apple TV in the ROI"""
        # List all possible Apple TV templates
        possible_templates = [
            "apple_tv.png",
            "apple_tv_text.png",
            "appletv_icon.png",
            "apple_tv_checkbox.png"
        ]
        
        found = False
        for template_name in possible_templates:
            template_path = self.template_dir / template_name
            if template_path.exists():
                print(f"\n🔍 Trying template: {template_name}")
                template = cv2.imread(str(template_path))
                if template is None:
                    continue
                
                # Check if template fits in ROI
                if template.shape[0] > roi.shape[0] or template.shape[1] > roi.shape[1]:
                    print(f"   ⚠️  Template too large! Template: {template.shape[1]}x{template.shape[0]}, ROI: {roi.shape[1]}x{roi.shape[0]}")
                    continue
                    
                result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                print(f"   Best match: {max_val:.2%}")
                
                if max_val > 0.5:
                    print(f"   ✅ Found with {template_name}!")
                    
                    # Visualize
                    vis = roi.copy()
                    cv2.rectangle(vis, max_loc, 
                                (max_loc[0] + template.shape[1], max_loc[1] + template.shape[0]),
                                (0, 255, 0), 2)
                    cv2.putText(vis, f"{max_val:.0%}", 
                               (max_loc[0], max_loc[1] - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    cv2.imwrite(str(self.debug_dir / f"4_found_{template_name}"), vis)
                    found = True
                    
                    # Now look for checkbox to the left
                    self.find_checkbox_near_appletv(roi, max_loc, template.shape)
                    break
        
        if not found:
            print("\n❌ Could not find Apple TV with any template")
            print("\n💡 Suggestions:")
            print("1. Make sure Apple TV is visible in the menu")
            print("2. You may need to create a new template")
            print("3. Check the ROI images in:", self.debug_dir)
    
    def find_checkbox_near_appletv(self, roi, appletv_loc, appletv_size):
        """Look for checkbox near Apple TV text"""
        print("\n🔍 Looking for checkbox near Apple TV...")
        
        # Define search area to the left of Apple TV
        search_left = max(0, appletv_loc[0] - 100)
        search_right = appletv_loc[0]
        search_top = max(0, appletv_loc[1] - 20)
        search_bottom = min(roi.shape[0], appletv_loc[1] + appletv_size[1] + 20)
        
        # Visualize search area
        vis = roi.copy()
        cv2.rectangle(vis, (search_left, search_top), 
                     (search_right, search_bottom), (255, 0, 255), 2)
        cv2.putText(vis, "Checkbox search", (search_left, search_top - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        cv2.imwrite(str(self.debug_dir / "5_checkbox_search_area.png"), vis)
        
        # Extract search area
        if search_left < search_right and search_top < search_bottom:
            search_roi = roi[search_top:search_bottom, search_left:search_right]
            cv2.imwrite(str(self.debug_dir / "6_checkbox_search_roi.png"), search_roi)
            
            # Try to find checkbox
            checkbox_template = self.template_dir / "checkbox_unchecked.png"
            if checkbox_template.exists():
                template = cv2.imread(str(checkbox_template))
                if template is not None:
                    result = cv2.matchTemplate(search_roi, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    print(f"   Checkbox match: {max_val:.2%}")
                    
                    if max_val > 0.5:
                        print(f"   ✅ Found checkbox!")
                    else:
                        print(f"   ❌ No checkbox found")
                        print(f"   💡 Try clicking at offset from Apple TV text")
    
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/menu_debug.png"
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
    debugger = AirPlayMenuDebugger()
    debugger.debug_menu_detection()
    
    print(f"\n📁 Debug images saved to: {debugger.debug_dir}")
    print("\nCheck the images to see:")
    print("1. The full menu screenshot")
    print("2. The menu ROI visualization")
    print("3. The extracted ROI")
    print("4. Apple TV detection results")
    print("5. Checkbox search area")


if __name__ == "__main__":
    main()