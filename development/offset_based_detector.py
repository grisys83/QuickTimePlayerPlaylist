#!/usr/bin/env python3
"""
Offset-based Apple TV detection
Find text, then click at offset for checkbox
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

class OffsetBasedDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        
    def detect_and_click_appletv(self):
        """Main detection using offset approach"""
        print("🎯 Offset-based Apple TV Detection")
        print("=" * 50)
        
        # Get window
        window = self.get_quicktime_window()
        if not window:
            return False
            
        # Show controls
        print("\n🎮 Showing controls...")
        self.show_controls(window)
        
        # Find and click AirPlay
        print("\n🔍 Finding AirPlay icon...")
        screenshot = self.capture_screen()
        airplay_pos = self.find_airplay(screenshot, window)
        
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            return False
            
        print(f"✅ Found AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})")
        print("\n🖱️ Clicking AirPlay...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1.5)
        
        # Capture menu and find Apple TV
        print("\n📺 Looking for Apple TV in menu...")
        menu_screenshot = self.capture_screen()
        
        # Save for debugging
        debug_dir = Path.home() / "offset_debug"
        debug_dir.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_dir / "menu.png"), menu_screenshot)
        
        # Find Apple TV using various methods
        appletv_pos = self.find_appletv_with_offset(menu_screenshot, airplay_pos)
        
        if appletv_pos:
            print(f"\n✅ Clicking Apple TV checkbox at ({appletv_pos['x']}, {appletv_pos['y']})")
            subprocess.run(['cliclick', f"c:{appletv_pos['x']},{appletv_pos['y']}"])
            return True
        else:
            print("\n❌ Could not find Apple TV")
            return False
    
    def find_appletv_with_offset(self, menu_screenshot, airplay_pos):
        """Find Apple TV using multiple strategies"""
        
        # Strategy 1: Look for "living" text
        living_template = self.template_dir / "living_text.png"
        if living_template.exists():
            print("\n📍 Strategy 1: Looking for 'living' text...")
            pos = self.find_template_with_offset(menu_screenshot, living_template, offset_x=-60)
            if pos:
                return pos
        
        # Strategy 2: Look for generic "TV" text
        tv_template = self.template_dir / "tv_text.png"
        if tv_template.exists():
            print("\n📍 Strategy 2: Looking for 'TV' text...")
            pos = self.find_template_with_offset(menu_screenshot, tv_template, offset_x=-60)
            if pos:
                return pos
        
        # Strategy 3: Use fixed offset from AirPlay
        print("\n📍 Strategy 3: Using fixed offset from AirPlay...")
        # Based on your screenshot, Apple TV appears to be roughly:
        # - Same X as AirPlay (maybe slightly left)
        # - About 140-180 pixels above AirPlay
        
        return {
            'x': airplay_pos['x'] - 20,  # Slightly left
            'y': airplay_pos['y'] - 160   # Above AirPlay
        }
    
    def find_template_with_offset(self, screenshot, template_path, offset_x=-60, offset_y=0):
        """Find template and return position with offset"""
        template = cv2.imread(str(template_path))
        if template is None:
            return None
            
        # Convert to grayscale for better matching
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        print(f"   Match confidence: {max_val:.2%}")
        
        if max_val > 0.7:  # High threshold for text
            # Calculate center of found text
            cv2_x = max_loc[0] + template.shape[1] // 2
            cv2_y = max_loc[1] + template.shape[0] // 2
            
            # Apply offset (checkbox is to the left of text)
            cv2_x += offset_x
            cv2_y += offset_y
            
            # Convert to screen coords
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            print(f"   ✅ Found! Checkbox should be at ({screen_x}, {screen_y})")
            
            # Save debug image
            debug_dir = Path.home() / "offset_debug"
            vis = screenshot.copy()
            cv2.rectangle(vis, max_loc, 
                         (max_loc[0] + template.shape[1], max_loc[1] + template.shape[0]),
                         (0, 255, 0), 2)
            cv2.circle(vis, (int(cv2_x), int(cv2_y)), 5, (255, 0, 0), -1)
            cv2.putText(vis, "Click here", (int(cv2_x - 40), int(cv2_y - 10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.imwrite(str(debug_dir / f"found_{template_path.stem}.png"), vis)
            
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
    def find_airplay(self, screenshot, window):
        """Find AirPlay icon"""
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
        
        control_roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Find AirPlay
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            return None
            
        template = cv2.imread(str(airplay_template))
        result = cv2.matchTemplate(control_roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            cv2_x = win_cv2_x1 + max_loc[0] + template.shape[1] // 2
            cv2_y = roi_top + max_loc[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
    def show_controls(self, window):
        """Show controls"""
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        center_x = window['x'] + window['width'] // 2
        if window['height'] < 400:
            control_y = window['y'] + int(window['height'] * 0.65)
        else:
            control_y = window['y'] + window['height'] - 250
            
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(1)
    
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/offset_detect.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def get_quicktime_window(self):
        """Get QuickTime window"""
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
    print("Make sure QuickTime is open with a video")
    input("Press Enter to start...")
    
    detector = OffsetBasedDetector()
    success = detector.detect_and_click_appletv()
    
    if success:
        print("\n✅ Successfully enabled AirPlay!")
    else:
        print("\n❌ Failed to enable AirPlay")
        print("\n💡 Check ~/offset_debug/ for debug images")


if __name__ == "__main__":
    main()