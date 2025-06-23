#!/usr/bin/env python3
"""
Audio AirPlay Detector V2 - ROI-based detection for audio playback
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import time
import json
from pathlib import Path


class AudioAirPlayDetectorV2:
    def __init__(self):
        self.scale_factor = self._get_scale_factor()
        self.debug_dir = Path("audio_airplay_debug_v2")
        self.debug_dir.mkdir(exist_ok=True)
        
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
        """Detect AirPlay button and Apple TV checkbox using ROI approach"""
        print("\n🎵 Audio AirPlay Detection V2 (ROI-based)")
        print("=" * 50)
        print("\nPlease make sure:")
        print("1. QuickTime Player is open with an audio file")
        print("2. The audio player window is visible")
        
        input("\nPress Enter when ready...")
        
        # Step 1: Find QuickTime window
        qt_window = self._find_quicktime_window()
        if not qt_window:
            print("❌ Could not find QuickTime window")
            return None
            
        print(f"✅ Found QuickTime window: {qt_window}")
        
        # Step 2: Detect AirPlay button in the control bar
        airplay_coords = self._detect_airplay_button(qt_window)
        if not airplay_coords:
            print("❌ Could not detect AirPlay button")
            return None
            
        print(f"✅ Found AirPlay button at: ({airplay_coords['x']}, {airplay_coords['y']})")
        
        # Step 3: Click AirPlay and detect Apple TV in popup
        apple_tv_coords = self._detect_apple_tv_checkbox(airplay_coords)
        if not apple_tv_coords:
            print("❌ Could not detect Apple TV checkbox")
            return None
            
        print(f"✅ Found Apple TV checkbox at: ({apple_tv_coords['x']}, {apple_tv_coords['y']})")
        
        # Save results
        results = {
            'airplay_icon_coords': airplay_coords,
            'apple_tv_coords': apple_tv_coords,
            'window_type': 'audio',
            'detection_method': 'roi_v2'
        }
        
        self._save_results(results)
        return results
    
    def _find_quicktime_window(self):
        """Find QuickTime window bounds"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    set windowName to name of window 1
                    return (item 1 of windowPos as string) & "," & ¬
                           (item 2 of windowPos as string) & "," & ¬
                           (item 1 of windowSize as string) & "," & ¬
                           (item 2 of windowSize as string) & "," & ¬
                           windowName
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.stdout.strip():
            parts = result.stdout.strip().split(',', 4)
            return {
                'x': int(parts[0]),
                'y': int(parts[1]),
                'width': int(parts[2]),
                'height': int(parts[3]),
                'name': parts[4] if len(parts) > 4 else "QuickTime Player"
            }
        return None
    
    def _detect_airplay_button(self, qt_window):
        """Detect AirPlay button in the control bar"""
        print("\n🔍 Detecting AirPlay button...")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Define control bar ROI (bottom part of window)
        control_bar_roi = {
            'x': qt_window['x'],
            'y': qt_window['y'] + qt_window['height'] - 60,  # Bottom 60 pixels
            'width': qt_window['width'],
            'height': 60
        }
        
        # Convert to physical coordinates for cropping
        phys_x = int(control_bar_roi['x'] * self.scale_factor)
        phys_y = int(control_bar_roi['y'] * self.scale_factor)
        phys_w = int(control_bar_roi['width'] * self.scale_factor)
        phys_h = int(control_bar_roi['height'] * self.scale_factor)
        
        # Crop control bar
        control_bar = screenshot_cv2[phys_y:phys_y+phys_h, phys_x:phys_x+phys_w]
        
        # Save debug image
        cv2.imwrite(str(self.debug_dir / "01_control_bar.png"), control_bar)
        
        # AirPlay button is typically in the right portion
        # For audio, it's around 45 pixels from the right edge
        airplay_x = qt_window['x'] + qt_window['width'] - 45
        airplay_y = qt_window['y'] + qt_window['height'] - 35
        
        # Verify with user
        self._highlight_and_save(screenshot_cv2, airplay_x, airplay_y, "02_airplay_button_location.png")
        
        response = input("\nIs the green circle on the AirPlay button? (y/n): ")
        if response.lower() != 'y':
            print("\n👆 Please click on the AirPlay button...")
            airplay_x, airplay_y = self._manual_select(screenshot_cv2, "Select AirPlay Button")
            if not airplay_x:
                return None
        
        return {'x': airplay_x, 'y': airplay_y}
    
    def _detect_apple_tv_checkbox(self, airplay_coords):
        """Click AirPlay and detect Apple TV checkbox in the popup"""
        print("\n🖱️ Clicking AirPlay button...")
        pyautogui.click(airplay_coords['x'], airplay_coords['y'])
        time.sleep(1.5)  # Wait for popup
        
        # Take screenshot of popup
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Define ROI for popup (600x600 centered on AirPlay button)
        roi_size = 600
        roi = {
            'x': airplay_coords['x'] - roi_size // 2,
            'y': airplay_coords['y'] - roi_size // 2,
            'width': roi_size,
            'height': roi_size
        }
        
        # Ensure ROI is within screen bounds
        screen_width, screen_height = pyautogui.size()
        roi['x'] = max(0, min(roi['x'], screen_width - roi_size))
        roi['y'] = max(0, min(roi['y'], screen_height - roi_size))
        
        # Convert to physical coordinates
        phys_x = int(roi['x'] * self.scale_factor)
        phys_y = int(roi['y'] * self.scale_factor)
        phys_w = int(roi['width'] * self.scale_factor)
        phys_h = int(roi['height'] * self.scale_factor)
        
        # Crop ROI
        roi_img = screenshot_cv2[phys_y:phys_y+phys_h, phys_x:phys_x+phys_w]
        cv2.imwrite(str(self.debug_dir / "03_airplay_popup_roi.png"), roi_img)
        
        # Look for Apple TV icon and checkboxes
        print("\n🔍 Looking for Apple TV option...")
        
        # Try template matching for Apple TV icon
        apple_tv_template = Path("templates") / "apple_tv_icon.png"
        if apple_tv_template.exists():
            template = cv2.imread(str(apple_tv_template))
            result = cv2.matchTemplate(roi_img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.7:
                # Found Apple TV icon
                icon_center_x = max_loc[0] + template.shape[1] // 2
                icon_center_y = max_loc[1] + template.shape[0] // 2
                
                # Convert back to logical screen coordinates
                icon_screen_x = roi['x'] + icon_center_x / self.scale_factor
                icon_screen_y = roi['y'] + icon_center_y / self.scale_factor
                
                print(f"   Found Apple TV icon at ({icon_screen_x:.0f}, {icon_screen_y:.0f})")
                
                # Checkbox should be on same Y axis, to the right
                checkbox_x = icon_screen_x + 200  # Adjust based on UI
                checkbox_y = icon_screen_y
                
                # Highlight both icon and checkbox
                annotated = screenshot_cv2.copy()
                self._draw_marker(annotated, icon_screen_x, icon_screen_y, (0, 255, 0), "Icon")
                self._draw_marker(annotated, checkbox_x, checkbox_y, (0, 0, 255), "Checkbox")
                cv2.imwrite(str(self.debug_dir / "04_detected_positions.png"), annotated)
                
                response = input("\nIs the red circle on the correct checkbox? (y/n): ")
                if response.lower() == 'y':
                    return {'x': int(checkbox_x), 'y': int(checkbox_y)}
        
        # Manual selection fallback
        print("\n👆 Please click on the Apple TV checkbox...")
        # First close the popup
        pyautogui.click(100, 100)  # Click away
        time.sleep(0.5)
        
        # Reopen popup
        pyautogui.click(airplay_coords['x'], airplay_coords['y'])
        time.sleep(1.5)
        
        # Take new screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        checkbox_x, checkbox_y = self._manual_select(screenshot_cv2, "Select Apple TV Checkbox")
        
        # Close popup
        pyautogui.click(100, 100)
        
        if checkbox_x:
            return {'x': checkbox_x, 'y': checkbox_y}
        
        return None
    
    def _highlight_and_save(self, image, x, y, filename, radius=30):
        """Highlight a position and save image"""
        annotated = image.copy()
        self._draw_marker(annotated, x, y, (0, 255, 0))
        cv2.imwrite(str(self.debug_dir / filename), annotated)
        print(f"📸 Saved debug image: {filename}")
    
    def _draw_marker(self, image, x, y, color, label=None):
        """Draw a marker at the specified position"""
        phys_x = int(x * self.scale_factor)
        phys_y = int(y * self.scale_factor)
        
        cv2.circle(image, (phys_x, phys_y), 30, color, 3)
        cv2.drawMarker(image, (phys_x, phys_y), color, cv2.MARKER_CROSS, 60, 2)
        
        if label:
            cv2.putText(image, label, (phys_x - 30, phys_y - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    def _countdown(self, seconds, action):
        """Show countdown timer like a camera"""
        print(f"\n⏱️  {action} in:")
        for i in range(seconds, 0, -1):
            if i <= 3:
                print(f"\r🔴 {i}...", end='', flush=True)
            elif i <= 5:
                print(f"\r🟡 {i}...", end='', flush=True)  
            else:
                print(f"\r🟢 {i}...", end='', flush=True)
            time.sleep(1)
        print("\r📸 Capturing NOW!                    ")
        
    def _manual_select(self, screenshot, window_title):
        """Manual selection of a position"""
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_title, 1200, 800)
        
        clicked_pos = None
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal clicked_pos
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_pos = (x, y)
                cv2.destroyAllWindows()
        
        cv2.setMouseCallback(window_title, mouse_callback)
        
        # Add instructions
        inst_img = screenshot.copy()
        cv2.putText(inst_img, "Click on the target", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(inst_img, "Press ESC to cancel", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        cv2.imshow(window_title, inst_img)
        
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
        """Save detection results"""
        # Save to audio-specific settings
        audio_settings = Path.home() / '.audio_airplay_settings.json'
        with open(audio_settings, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Audio AirPlay settings saved to: {audio_settings}")
        
        # Update templates file
        templates_file = Path.home() / '.airplay_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        templates['audio_airplay_v2'] = results
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        print(f"💾 Updated templates: {templates_file}")


def main():
    print("🎵 Audio AirPlay Detector V2")
    print("ROI-based detection for accurate results")
    
    detector = AudioAirPlayDetectorV2()
    result = detector.detect_audio_airplay()
    
    if result:
        print("\n✅ Detection complete!")
        print(f"AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        print(f"\nDebug images saved in: {detector.debug_dir}")
        
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
        print(f"Check debug images in: {detector.debug_dir}")


if __name__ == "__main__":
    main()