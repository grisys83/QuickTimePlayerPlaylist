#!/usr/bin/env python3
"""
Rapid capture before losing focus
Captures all needed screenshots at once
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import os

class RapidCaptureDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        
    def rapid_capture_sequence(self):
        """Capture all needed screenshots rapidly"""
        print("📸 Rapid Capture Sequence")
        print("=" * 50)
        
        captures = {}
        
        # Ensure QuickTime is active
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Get window info
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime window not found")
            return None
            
        print("✅ QuickTime window found")
        
        # Step 1: Show controls and capture
        print("\n📸 Capturing with controls...")
        self.show_controls(window)
        captures['controls'] = self.capture_screen("controls")
        
        # Step 2: Find AirPlay position from first capture
        airplay_pos = self.find_airplay_in_capture(captures['controls'], window)
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            return None
            
        print(f"✅ Found AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})")
        
        # Step 3: Click AirPlay and capture menu
        print("\n📸 Opening AirPlay menu...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(0.8)
        
        captures['menu'] = self.capture_screen("menu")
        
        # Now analyze captures without worrying about focus
        return self.analyze_captures(captures, airplay_pos)
    
    def analyze_captures(self, captures, airplay_pos):
        """Analyze captured screenshots"""
        print("\n🔍 Analyzing captures...")
        
        # Save captures for debugging
        debug_dir = Path.home() / "rapid_capture_debug"
        debug_dir.mkdir(exist_ok=True)
        
        for name, img in captures.items():
            cv2.imwrite(str(debug_dir / f"{name}.png"), img)
        
        # Calculate checkbox position
        # Based on typical layout:
        # - Checkbox is left and above AirPlay icon
        checkbox_x = airplay_pos['x'] - 80
        checkbox_y = airplay_pos['y'] - 160
        
        print(f"\n📍 Calculated checkbox position: ({checkbox_x}, {checkbox_y})")
        
        # Visualize on menu capture
        menu_vis = captures['menu'].copy()
        checkbox_cv2_x, checkbox_cv2_y = self.converter.screen_to_cv2(checkbox_x, checkbox_y)
        cv2.circle(menu_vis, (int(checkbox_cv2_x), int(checkbox_cv2_y)), 10, (0, 255, 0), -1)
        cv2.putText(menu_vis, "Target", 
                   (int(checkbox_cv2_x - 30), int(checkbox_cv2_y - 15)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite(str(debug_dir / "target_position.png"), menu_vis)
        
        return {'checkbox_x': checkbox_x, 'checkbox_y': checkbox_y}
    
    def find_airplay_in_capture(self, screenshot, window):
        """Find AirPlay in captured screenshot"""
        # Convert window coords
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Control bar ROI
        if window['height'] < 400:
            roi_top = int(win_cv2_y2 - window['height'] * 0.8)
        else:
            roi_top = int(win_cv2_y2 - 450)
        roi_bottom = int(win_cv2_y2)
        
        roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Find AirPlay
        template_path = self.template_dir / "airplay_icon.png"
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path))
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            cv2_x = win_cv2_x1 + max_loc[0] + template.shape[1] // 2
            cv2_y = roi_top + max_loc[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
    def show_controls(self, window):
        """Show controls"""
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 250
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.5)
    
    def capture_screen(self, name):
        """Capture screen"""
        screenshot_path = f"/tmp/qt_{name}.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        os.remove(screenshot_path)
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
    
    def enable_airplay(self):
        """Complete AirPlay enable sequence"""
        # First capture everything we need
        result = self.rapid_capture_sequence()
        
        if result:
            # Now click the checkbox
            print("\n🖱️ Clicking checkbox...")
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(0.2)
            subprocess.run(['cliclick', f"c:{result['checkbox_x']},{result['checkbox_y']}"])
            
            print("\n✅ AirPlay should now be enabled!")
            print(f"📁 Debug images saved to: {Path.home() / 'rapid_capture_debug'}")
            return True
        else:
            print("\n❌ Failed to detect positions")
            return False


def main():
    print("🚀 Rapid Capture AirPlay Enabler")
    print("\nThis method captures all screenshots quickly")
    print("before QuickTime loses focus")
    
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to start...")
    
    detector = RapidCaptureDetector()
    detector.enable_airplay()


if __name__ == "__main__":
    main()