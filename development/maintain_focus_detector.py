#!/usr/bin/env python3
"""
Maintain focus on QuickTime throughout detection
Prevents control bar from disappearing
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import threading

class MaintainFocusDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.keep_focus = True
        
    def focus_keeper_thread(self):
        """Thread to keep QuickTime in focus"""
        while self.keep_focus:
            subprocess.run(['osascript', '-e', 
                          'tell application "QuickTime Player" to activate'], 
                          capture_output=True)
            time.sleep(0.5)
    
    def detect_with_focus(self):
        """Detect while maintaining focus"""
        print("🎯 Focus-Maintained Detection")
        print("=" * 50)
        
        # Start focus keeper thread
        focus_thread = threading.Thread(target=self.focus_keeper_thread)
        focus_thread.start()
        
        try:
            # Get window
            window = self.get_quicktime_window()
            if not window:
                return False
                
            # Quick capture and detection
            print("\n⚡ Rapid detection sequence...")
            
            # Step 1: Show controls and capture
            self.show_controls_quick(window)
            screenshot1 = self.capture_screen_fast()
            
            # Step 2: Find AirPlay immediately
            airplay_pos = self.find_airplay_fast(screenshot1, window)
            if not airplay_pos:
                print("❌ AirPlay not found")
                return False
                
            # Step 3: Click AirPlay
            subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
            time.sleep(0.8)  # Wait for menu
            
            # Step 4: Capture menu and click
            menu_screenshot = self.capture_screen_fast()
            
            # Use simple offset from AirPlay
            # Apple TV is typically:
            # - 20-30 pixels left of AirPlay
            # - 150-180 pixels above AirPlay
            checkbox_x = airplay_pos['x'] - 80  # Further left for checkbox
            checkbox_y = airplay_pos['y'] - 160
            
            print(f"\n🎯 Clicking checkbox at ({checkbox_x}, {checkbox_y})")
            subprocess.run(['cliclick', f"c:{checkbox_x},{checkbox_y}"])
            
            return True
            
        finally:
            # Stop focus keeper
            self.keep_focus = False
            focus_thread.join()
    
    def show_controls_quick(self, window):
        """Show controls quickly"""
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 250
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.3)
    
    def capture_screen_fast(self):
        """Fast screen capture"""
        # Use smaller region if possible
        screenshot_path = "/tmp/qt_fast.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_airplay_fast(self, screenshot, window):
        """Fast AirPlay detection"""
        # Convert window coords
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Control bar ROI
        roi_top = int(win_cv2_y2 - window['height'] * 0.8)
        roi_bottom = int(win_cv2_y2)
        
        roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Find AirPlay
        template_path = self.template_dir / "airplay_icon.png"
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path))
        
        # Single scale for speed
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            cv2_x = win_cv2_x1 + max_loc[0] + template.shape[1] // 2
            cv2_y = roi_top + max_loc[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            return {'x': screen_x, 'y': screen_y}
            
        return None
    
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


class AlternativeFocusMethod:
    """Alternative: Use System Events to maintain focus"""
    
    @staticmethod
    def enable_airplay_with_system_events():
        """Use pure AppleScript to maintain focus"""
        script = '''
        tell application "QuickTime Player"
            activate
        end tell
        
        tell application "System Events"
            tell process "QuickTime Player"
                -- Get window
                set frontWindow to window 1
                set {windowX, windowY} to position of frontWindow
                set {windowWidth, windowHeight} to size of frontWindow
                
                -- Calculate positions (using integer values)
                set controlX to (windowX + (windowWidth div 2)) as integer
                set controlY to (windowY + windowHeight - 100) as integer
                
                -- Show controls by hovering
                do shell script "cliclick m:" & controlX & "," & controlY
                delay 0.5
                
                -- Click AirPlay (adjust position as needed)
                set airplayX to (windowX + windowWidth - 150) as integer
                set airplayY to (windowY + windowHeight - 50) as integer
                do shell script "cliclick c:" & airplayX & "," & airplayY
                delay 1
                
                -- Click Apple TV checkbox (using the successful coordinates)
                -- From the working method: checkbox at (759, 639)
                -- This is roughly airplayX - 80, airplayY - 160
                set checkboxX to (airplayX - 80) as integer
                set checkboxY to (airplayY - 160) as integer
                do shell script "cliclick c:" & checkboxX & "," & checkboxY
            end tell
        end tell
        '''
        
        print("🎯 Using System Events method...")
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Success!")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False


def main():
    print("🔍 Focus-Maintained AirPlay Detection")
    print("\nChoose method:")
    print("1. Thread-based focus keeper")
    print("2. System Events (pure AppleScript)")
    
    choice = input("\nSelect (1-2): ")
    
    if choice == '1':
        print("\nMake sure QuickTime is open with a video")
        input("Press Enter to start...")
        
        detector = MaintainFocusDetector()
        success = detector.detect_with_focus()
        
        if success:
            print("\n✅ AirPlay enabled!")
        else:
            print("\n❌ Failed")
            
    elif choice == '2':
        print("\nMake sure QuickTime is open with a video")
        input("Press Enter to start...")
        
        success = AlternativeFocusMethod.enable_airplay_with_system_events()
        
        if not success:
            print("\n💡 You may need to adjust the coordinates in the script")


if __name__ == "__main__":
    main()