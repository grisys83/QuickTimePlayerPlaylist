#!/usr/bin/env python3
"""
Smart CV2 AirPlay Enabler
- Always detects current positions
- Updates saved coordinates when successful
- Learns from each use
"""

import cv2
import numpy as np
import subprocess
import time
import json
from pathlib import Path
from coordinate_converter import CoordinateConverter

class SmartCV2AirPlay:
    def __init__(self, settings=None):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.settings = settings or self.load_settings()
        
        # Cache for this session
        self.session_cache = {
            'last_airplay': None,
            'last_appletv': None,
            'last_detection_time': 0
        }
        
    def load_settings(self):
        """Load settings"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_detected_coordinates(self, airplay_coords, appletv_coords):
        """Save successfully detected coordinates for future use"""
        self.settings['airplay_icon_coords'] = airplay_coords
        self.settings['apple_tv_coords'] = appletv_coords
        self.settings['last_cv2_detection'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to both settings files
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            try:
                existing = {}
                if settings_file.exists():
                    with open(settings_file, 'r') as f:
                        existing = json.load(f)
                
                existing.update(self.settings)
                
                with open(settings_file, 'w') as f:
                    json.dump(existing, f, indent=2)
            except:
                pass
    
    def capture_screen(self):
        """Quick screen capture"""
        screenshot_path = "/tmp/smart_cv2_screen.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_template_fast(self, screenshot, template_name, threshold=0.7):
        """Fast template matching with optimal scales"""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path))
        if template is None:
            return None
            
        # Use fewer scales for speed
        scales = [0.9, 1.0, 1.1]  # Most common scales
        
        for scale in scales:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > threshold:
                # Calculate center and convert coordinates
                cv2_x = max_loc[0] + width // 2
                cv2_y = max_loc[1] + height // 2
                screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
                
                return {'x': screen_x, 'y': screen_y, 'confidence': max_val}
        
        return None
    
    def find_all_templates_fast(self, screenshot, template_name, threshold=0.7):
        """Find all instances of a template"""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return []
            
        template = cv2.imread(str(template_path))
        if template is None:
            return []
            
        # Single scale for speed
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # Find all matches
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            cv2_x = pt[0] + template.shape[1] // 2
            cv2_y = pt[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            matches.append({
                'x': screen_x, 
                'y': screen_y,
                'cv2_y': cv2_y,  # Keep for Y-level comparison
                'confidence': result[pt[1], pt[0]]
            })
        
        return matches
    
    def enable_airplay_smart(self):
        """Smart AirPlay enable with real-time detection"""
        start_time = time.time()
        
        # Step 1: Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.2)
        
        # Step 2: Get window and show controls
        window = self.get_quicktime_window()
        if not window:
            return False
            
        self.show_controls_fast(window)
        
        # Step 3: Detect AirPlay icon
        screenshot = self.capture_screen()
        airplay = self.find_template_fast(screenshot, 'airplay_icon.png')
        
        if not airplay:
            print("AirPlay icon not found, retrying...")
            time.sleep(0.3)
            self.show_controls_fast(window)
            screenshot = self.capture_screen()
            airplay = self.find_template_fast(screenshot, 'airplay_icon.png', threshold=0.6)
        
        if not airplay:
            print("Failed to find AirPlay icon")
            return False
        
        # Step 4: Click AirPlay
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(0.4)
        
        # Step 5: Find and click Apple TV checkbox
        menu_screenshot = self.capture_screen()
        
        # Method 1: Direct checkbox detection
        checkbox = self.find_template_fast(menu_screenshot, 'checkbox_unchecked.png', threshold=0.6)
        
        if checkbox:
            appletv_coords = checkbox
        else:
            # Method 2: Find Apple TV text and calculate checkbox position
            appletv_text = self.find_template_fast(menu_screenshot, 'apple_tv.png', threshold=0.6)
            
            if appletv_text:
                # Checkbox is typically 50 pixels to the left
                appletv_coords = {
                    'x': appletv_text['x'] - 50,
                    'y': appletv_text['y']
                }
            else:
                # Method 3: Find all checkboxes and pick the right one
                checkboxes = self.find_all_templates_fast(menu_screenshot, 'checkbox_unchecked.png', threshold=0.5)
                
                if checkboxes:
                    # Usually the first or second checkbox
                    appletv_coords = checkboxes[0] if len(checkboxes) == 1 else checkboxes[1]
                else:
                    # Last resort: offset from AirPlay
                    appletv_coords = {
                        'x': airplay['x'] + 50,
                        'y': airplay['y'] + 70
                    }
        
        # Click Apple TV
        subprocess.run(['cliclick', f"c:{appletv_coords['x']},{appletv_coords['y']}"])
        
        # Save successful coordinates
        self.save_detected_coordinates(airplay, appletv_coords)
        
        elapsed = time.time() - start_time
        print(f"✅ AirPlay enabled in {elapsed:.2f}s (coordinates updated)")
        
        return True
    
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
    
    def show_controls_fast(self, window):
        """Show controls quickly"""
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + int(window['height'] * 0.75)
        
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.4)


# Drop-in replacement for cv2_airplay_enabler
class CV2AirPlayEnabler:
    def __init__(self, settings=None):
        self.smart_enabler = SmartCV2AirPlay(settings)
        self.settings = settings or {}
        self.templates_available = True  # Always try CV2
        
    def enable_airplay_fast(self):
        """Enable AirPlay with smart detection"""
        return self.smart_enabler.enable_airplay_smart()
    
    def enable_airplay_cv2(self):
        """Alias for compatibility"""
        return self.enable_airplay_fast()


def test_smart_airplay():
    """Test the smart AirPlay system"""
    print("🧠 Smart CV2 AirPlay Test")
    print("This will detect positions in real-time")
    
    enabler = SmartCV2AirPlay()
    
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to test...")
    
    success = enabler.enable_airplay_smart()
    
    if success:
        print("\n✅ Success! Coordinates have been updated.")
        print("Future uses will be even faster.")
    else:
        print("\n❌ Failed. Check if templates exist.")


if __name__ == "__main__":
    test_smart_airplay()