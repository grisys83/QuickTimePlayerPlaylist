#!/usr/bin/env python3
"""
Audio AirPlay Detector - Detect AirPlay button for audio files in QuickTime
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import time
import json
from pathlib import Path


class AudioAirPlayDetector:
    def __init__(self):
        self.scale_factor = self._get_scale_factor()
        
    def _get_scale_factor(self):
        """Get display scale factor"""
        try:
            logical_width, _ = pyautogui.size()
            screenshot = pyautogui.screenshot()
            physical_width = screenshot.width
            return physical_width / logical_width
        except:
            return 2.0
    
    def detect_audio_airplay(self):
        """Detect AirPlay button for audio playback"""
        print("\n🎵 Audio AirPlay Detection")
        print("=" * 50)
        print("\nPlease make sure:")
        print("1. QuickTime Player is open with an audio file")
        print("2. The audio player window is visible")
        print("3. You can see the playback controls")
        
        input("\nPress Enter when ready...")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Find QuickTime window
        qt_window = self._find_quicktime_audio_window()
        if not qt_window:
            print("❌ Could not find QuickTime audio window")
            return None
            
        print(f"\n✅ Found QuickTime audio window at: {qt_window}")
        
        # AirPlay button is typically on the right side of the control bar
        # For audio, it's at a fixed position relative to the window
        airplay_x = qt_window['x'] + qt_window['width'] - 45  # 45 pixels from right
        airplay_y = qt_window['y'] + qt_window['height'] - 35  # 35 pixels from bottom
        
        print(f"\n🎯 Estimated AirPlay position: ({airplay_x}, {airplay_y})")
        
        # Highlight the area
        self._highlight_area(screenshot_cv2, airplay_x, airplay_y)
        
        # Confirm with user
        response = input("\nIs this the correct AirPlay button location? (y/n): ")
        if response.lower() != 'y':
            print("\n👆 Please click on the AirPlay button...")
            airplay_x, airplay_y = self._manual_select(screenshot_cv2)
        
        if airplay_x and airplay_y:
            # Test clicking AirPlay
            print("\n🖱️ Testing AirPlay click...")
            pyautogui.click(airplay_x, airplay_y)
            time.sleep(1.5)
            
            # Take screenshot of menu
            menu_screenshot = pyautogui.screenshot()
            menu_np = np.array(menu_screenshot)
            menu_cv2 = cv2.cvtColor(menu_np, cv2.COLOR_RGB2BGR)
            
            # Find Apple TV checkbox
            print("\n📺 Looking for Apple TV option...")
            apple_tv_x = airplay_x + 50  # Usually to the right
            apple_tv_y = airplay_y + 70  # Usually below
            
            print(f"Estimated Apple TV checkbox: ({apple_tv_x}, {apple_tv_y})")
            
            # Save results
            results = {
                'airplay_icon_coords': {'x': airplay_x, 'y': airplay_y},
                'apple_tv_coords': {'x': apple_tv_x, 'y': apple_tv_y},
                'window_type': 'audio'
            }
            
            self._save_results(results)
            return results
            
        return None
    
    def _find_quicktime_audio_window(self):
        """Find QuickTime audio player window"""
        # Use AppleScript to get window info
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
    
    def _highlight_area(self, screenshot, x, y, radius=30):
        """Highlight an area on screenshot"""
        # Convert to physical coordinates for drawing
        phys_x = int(x * self.scale_factor)
        phys_y = int(y * self.scale_factor)
        
        # Draw circle and crosshair
        cv2.circle(screenshot, (phys_x, phys_y), radius, (0, 255, 0), 3)
        cv2.drawMarker(screenshot, (phys_x, phys_y), (255, 0, 0), 
                      cv2.MARKER_CROSS, radius * 2, 2)
        
        # Save debug image
        debug_dir = Path("audio_airplay_debug")
        debug_dir.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_dir / "airplay_location.png"), screenshot)
        print(f"📸 Debug image saved to: {debug_dir / 'airplay_location.png'}")
    
    def _manual_select(self, screenshot):
        """Manual selection of AirPlay button"""
        # Create window for selection
        cv2.namedWindow('Select AirPlay Button', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Select AirPlay Button', 1200, 800)
        
        clicked_pos = None
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal clicked_pos
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_pos = (x, y)
                cv2.destroyAllWindows()
        
        cv2.setMouseCallback('Select AirPlay Button', mouse_callback)
        
        # Add instructions
        inst_img = screenshot.copy()
        cv2.putText(inst_img, "Click on the AirPlay button", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(inst_img, "Press ESC to cancel", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        cv2.imshow('Select AirPlay Button', inst_img)
        
        while clicked_pos is None:
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                cv2.destroyAllWindows()
                return None, None
        
        if clicked_pos:
            phys_x, phys_y = clicked_pos
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            return logical_x, logical_y
            
        return None, None
    
    def _save_results(self, results):
        """Save results to file"""
        # Save to audio-specific settings
        audio_settings = Path.home() / '.audio_airplay_settings.json'
        with open(audio_settings, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Audio AirPlay settings saved to: {audio_settings}")
        
        # Also update the main templates file
        templates_file = Path.home() / '.airplay_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        # Add audio-specific coordinates
        templates['audio_airplay'] = {
            'airplay_button': {'captured_at': results['airplay_icon_coords']},
            'apple_tv_checkbox': {'captured_at': results['apple_tv_coords']}
        }
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        print(f"💾 Updated templates: {templates_file}")


def main():
    print("🎵 Audio AirPlay Detector")
    print("This tool detects AirPlay button location for audio files")
    print("\nNote: Audio files have different UI than video files in QuickTime")
    
    detector = AudioAirPlayDetector()
    result = detector.detect_audio_airplay()
    
    if result:
        print("\n✅ Detection complete!")
        print(f"AirPlay button: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"Apple TV checkbox: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        
        # Test the coordinates
        test = input("\n🧪 Test these coordinates? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting in 3 seconds...")
            time.sleep(3)
            
            # Click AirPlay
            pyautogui.click(result['airplay_icon_coords']['x'], 
                          result['airplay_icon_coords']['y'])
            time.sleep(1.5)
            
            # Click Apple TV
            pyautogui.click(result['apple_tv_coords']['x'], 
                          result['apple_tv_coords']['y'])
            
            print("✅ Test complete!")
    else:
        print("\n❌ Detection failed")


if __name__ == "__main__":
    main()