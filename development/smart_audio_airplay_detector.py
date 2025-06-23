#!/usr/bin/env python3
"""
Smart Audio AirPlay Detector - Automatic detection with visual features
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import time
import json
from pathlib import Path


class SmartAudioAirPlayDetector:
    def __init__(self):
        self.scale_factor = self._get_scale_factor()
        self.debug_dir = Path("smart_airplay_debug")
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
        """Smart detection using visual features"""
        print("\n🧠 Smart Audio AirPlay Detection")
        print("=" * 50)
        print("\nThis detector automatically finds AirPlay controls")
        print("regardless of window position")
        
        input("\nMake sure QuickTime is playing audio, then press Enter...")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Step 1: Find QuickTime window by visual features
        qt_window = self._find_quicktime_window_smart(screenshot_cv2)
        if not qt_window:
            print("❌ Could not find QuickTime window")
            return None
            
        print(f"✅ Found QuickTime window at ({qt_window['x']}, {qt_window['y']})")
        
        # Step 2: Find AirPlay button in control bar
        airplay_coords = self._find_airplay_button_smart(screenshot_cv2, qt_window)
        if not airplay_coords:
            print("❌ Could not find AirPlay button")
            return None
            
        print(f"✅ Found AirPlay button at ({airplay_coords['x']}, {airplay_coords['y']})")
        
        # Step 3: Click and find Apple TV
        apple_tv_coords = self._find_apple_tv_smart(airplay_coords)
        if not apple_tv_coords:
            print("❌ Could not find Apple TV option")
            return None
            
        print(f"✅ Found Apple TV at ({apple_tv_coords['x']}, {apple_tv_coords['y']})")
        
        # Save results
        results = {
            'airplay_icon_coords': airplay_coords,
            'apple_tv_coords': apple_tv_coords,
            'window_type': 'audio',
            'detection_method': 'smart_visual'
        }
        
        self._save_results(results)
        return results
    
    def _find_quicktime_window_smart(self, screenshot):
        """Find QuickTime window using visual features"""
        print("\n🔍 Finding QuickTime window...")
        
        # Method 1: Look for QuickTime's dark player interface
        # Audio player has a distinct dark gray color scheme
        
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Look for large dark rectangular regions
        _, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter for window-sized rectangles
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # QuickTime audio window characteristics:
            # - Width: 300-800 pixels (logical)
            # - Height: 100-300 pixels (logical)
            # - Dark background
            logical_w = w / self.scale_factor
            logical_h = h / self.scale_factor
            
            if (300 <= logical_w <= 800 and 
                100 <= logical_h <= 300 and
                logical_w > logical_h * 1.5):  # Wider than tall
                
                # Check if it's dark enough
                roi = gray[y:y+h, x:x+w]
                mean_brightness = np.mean(roi)
                
                if mean_brightness < 80:  # Dark interface
                    candidates.append({
                        'x': int(x / self.scale_factor),
                        'y': int(y / self.scale_factor),
                        'width': int(logical_w),
                        'height': int(logical_h),
                        'brightness': mean_brightness
                    })
        
        # Debug: save detection result
        debug_img = screenshot.copy()
        for i, cand in enumerate(candidates):
            phys_x = int(cand['x'] * self.scale_factor)
            phys_y = int(cand['y'] * self.scale_factor)
            phys_w = int(cand['width'] * self.scale_factor)
            phys_h = int(cand['height'] * self.scale_factor)
            
            cv2.rectangle(debug_img, (phys_x, phys_y), 
                         (phys_x + phys_w, phys_y + phys_h), 
                         (0, 255, 0), 2)
            cv2.putText(debug_img, f"Candidate {i+1}", 
                       (phys_x, phys_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imwrite(str(self.debug_dir / "01_window_candidates.png"), debug_img)
        
        if candidates:
            # Return the darkest candidate (most likely QuickTime)
            best = min(candidates, key=lambda c: c['brightness'])
            return best
        
        # Fallback: Use AppleScript
        return self._get_window_from_applescript()
    
    def _find_airplay_button_smart(self, screenshot, qt_window):
        """Find AirPlay button using visual features"""
        print("\n🔍 Finding AirPlay button...")
        
        # Crop to control bar area (bottom portion of window)
        x = int(qt_window['x'] * self.scale_factor)
        y = int((qt_window['y'] + qt_window['height'] - 60) * self.scale_factor)
        w = int(qt_window['width'] * self.scale_factor)
        h = int(60 * self.scale_factor)
        
        control_bar = screenshot[y:y+h, x:x+w]
        
        # Method 1: Look for blue-ish pixels (AirPlay icon is blue)
        hsv = cv2.cvtColor(control_bar, cv2.COLOR_BGR2HSV)
        
        # Blue color range
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Also look for light gray (inactive state)
        gray_low = np.array([0, 0, 150])
        gray_high = np.array([180, 30, 200])
        gray_mask = cv2.inRange(hsv, gray_low, gray_high)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(blue_mask, gray_mask)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for AirPlay-shaped objects (small, rightmost)
        candidates = []
        for contour in contours:
            cx, cy, cw, ch = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # AirPlay icon characteristics:
            # - Small (10-30 pixels)
            # - In the right portion of control bar
            # - Roughly square aspect ratio
            if (100 < area < 2000 and 
                cx > w * 0.6 and  # Right side
                0.5 < cw/ch < 2.0):  # Aspect ratio
                
                # Calculate center in logical coordinates
                center_x = qt_window['x'] + (cx + cw//2) / self.scale_factor
                center_y = qt_window['y'] + qt_window['height'] - 60 + (cy + ch//2) / self.scale_factor
                
                candidates.append({
                    'x': int(center_x),
                    'y': int(center_y),
                    'area': area,
                    'position': cx  # For sorting by rightmost
                })
        
        # Debug: save mask and candidates
        debug_img = control_bar.copy()
        for cand in candidates:
            local_x = int((cand['x'] - qt_window['x']) * self.scale_factor)
            local_y = int((cand['y'] - (qt_window['y'] + qt_window['height'] - 60)) * self.scale_factor)
            cv2.circle(debug_img, (local_x, local_y), 15, (0, 255, 0), 2)
        
        cv2.imwrite(str(self.debug_dir / "02_airplay_candidates.png"), debug_img)
        cv2.imwrite(str(self.debug_dir / "03_color_mask.png"), combined_mask)
        
        if candidates:
            # Return the rightmost candidate
            best = max(candidates, key=lambda c: c['position'])
            return {'x': best['x'], 'y': best['y']}
        
        # Fallback: Use fixed offset
        print("   Using fallback position...")
        return {
            'x': qt_window['x'] + qt_window['width'] - 45,
            'y': qt_window['y'] + qt_window['height'] - 35
        }
    
    def _find_apple_tv_smart(self, airplay_coords):
        """Find Apple TV in popup using smart detection"""
        print("\n🔍 Finding Apple TV option...")
        
        # Click AirPlay
        print("   Clicking AirPlay button...")
        pyautogui.click(airplay_coords['x'], airplay_coords['y'])
        time.sleep(1.5)
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Define search region
        search_size = 400
        search_x = max(0, airplay_coords['x'] - search_size // 2)
        search_y = max(0, airplay_coords['y'] - search_size // 2)
        
        # Look for text "TV" or Apple logo
        # For now, use OCR or pattern matching would be ideal
        # Simplified: look for checkbox patterns
        
        phys_x = int(search_x * self.scale_factor)
        phys_y = int(search_y * self.scale_factor)
        phys_size = int(search_size * self.scale_factor)
        
        search_region = screenshot_cv2[phys_y:phys_y+phys_size, phys_x:phys_x+phys_size]
        
        # Convert to grayscale
        gray = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
        
        # Look for circular shapes (checkboxes)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=8,
            maxRadius=20
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            
            # Debug: save detected circles
            debug_img = search_region.copy()
            for i, (x, y, r) in enumerate(circles[0]):
                cv2.circle(debug_img, (x, y), r, (0, 255, 0), 2)
                cv2.putText(debug_img, str(i+1), (x-10, y-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imwrite(str(self.debug_dir / "04_checkboxes_found.png"), debug_img)
            
            # Return the most likely checkbox (usually 2nd or 3rd from top)
            if len(circles[0]) >= 2:
                # Sort by Y position
                sorted_circles = sorted(circles[0], key=lambda c: c[1])
                
                # Take the 2nd one (first is usually "This Computer")
                best = sorted_circles[1] if len(sorted_circles) > 1 else sorted_circles[0]
                
                logical_x = search_x + best[0] / self.scale_factor
                logical_y = search_y + best[1] / self.scale_factor
                
                # Close popup
                pyautogui.click(100, 100)
                
                return {'x': int(logical_x), 'y': int(logical_y)}
        
        # Fallback
        print("   Using fallback position...")
        pyautogui.click(100, 100)  # Close popup
        
        return {
            'x': airplay_coords['x'] + 50,
            'y': airplay_coords['y'] + 70
        }
    
    def _get_window_from_applescript(self):
        """Fallback: Get window position from AppleScript"""
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
    
    def _save_results(self, results):
        """Save detection results"""
        settings_file = Path.home() / '.smart_audio_airplay_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Settings saved to: {settings_file}")
        
        # Also update main templates
        templates_file = Path.home() / '.airplay_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        templates['smart_audio_airplay'] = results
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)


def main():
    print("🧠 Smart Audio AirPlay Detector")
    print("Automatic detection that adapts to window position")
    
    detector = SmartAudioAirPlayDetector()
    result = detector.detect_audio_airplay()
    
    if result:
        print("\n✅ Detection complete!")
        print("\n📊 Results:")
        print(f"   AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"   Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        print(f"\n📁 Debug images: {detector.debug_dir}")
        
        # Test
        test = input("\n🧪 Test detection? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting...")
            time.sleep(2)
            
            # Click AirPlay
            pyautogui.click(result['airplay_icon_coords']['x'], 
                          result['airplay_icon_coords']['y'])
            time.sleep(1.5)
            
            # Click Apple TV
            pyautogui.click(result['apple_tv_coords']['x'], 
                          result['apple_tv_coords']['y'])
            
            print("✅ Test complete!")
            
            # Ask if it worked
            worked = input("\nDid it work correctly? (y/n): ")
            if worked.lower() != 'y':
                print("\n💡 Tip: Check the debug images to see what was detected")
                print("You may need to use the timer-based detector for more control")
    else:
        print("\n❌ Detection failed")
        print("Try the timer-based detector for manual control")


if __name__ == "__main__":
    main()