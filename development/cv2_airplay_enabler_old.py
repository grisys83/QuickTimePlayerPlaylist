#!/usr/bin/env python3
"""
CV2-based AirPlay enabler for fast, reliable automation
Can be used by any app that needs AirPlay functionality
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

class CV2AirPlayEnabler:
    def __init__(self, settings=None):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.settings = settings or {}
        
        # Check if templates exist
        self.templates_available = self._check_templates()
        
    def _check_templates(self):
        """Check if required templates exist"""
        required = ['airplay_icon.png']
        optional = ['apple_tv.png', 'checkbox_unchecked.png', 'checkbox_checked.png']
        
        for template in required:
            if not (self.template_dir / template).exists():
                return False
                
        return True
    
    def capture_screen(self):
        """Quick screen capture"""
        screenshot_path = "/tmp/cv2_airplay_screen.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_template(self, screenshot, template_name, threshold=0.7):
        """Find template with proper coordinate conversion"""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path))
        if template is None:
            return None
            
        # Try multiple scales
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        
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
                
                return {
                    'x': screen_x,
                    'y': screen_y,
                    'confidence': max_val
                }
        
        return None
    
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
    
    def show_controls(self, window=None):
        """Show QuickTime controls"""
        if not window:
            window = self.get_quicktime_window()
            if not window:
                return False
                
        # Move to bottom 1/4 of window
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + int(window['height'] * 0.75)
        
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.5)  # Reduced from 0.8
        
        # Small movement to keep visible
        subprocess.run(['cliclick', f'm:{center_x + 5},{control_y}'])
        time.sleep(0.2)  # Reduced from 0.3
        
        return True
    
    def enable_airplay_cv2(self):
        """Enable AirPlay using CV2 detection - FAST version"""
        try:
            # Use templates if available
            if self.templates_available:
                return self._enable_with_templates()
            else:
                # Fall back to saved coordinates
                return self._enable_with_saved_coords()
                
        except Exception as e:
            print(f"CV2 AirPlay error: {e}")
            return False
    
    def _enable_with_templates(self):
        """Enable using template matching"""
        # Ensure QuickTime is active
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.2)  # Reduced from 0.3
        
        # Get window and show controls
        window = self.get_quicktime_window()
        if not window:
            return False
            
        self.show_controls(window)
        
        # Capture screen
        screenshot = self.capture_screen()
        
        # Find AirPlay icon
        airplay = self.find_template(screenshot, 'airplay_icon.png')
        if not airplay:
            # Try showing controls again
            self.show_controls(window)
            screenshot = self.capture_screen()
            airplay = self.find_template(screenshot, 'airplay_icon.png')
            
        if not airplay:
            print("Could not find AirPlay icon with CV2")
            return self._enable_with_saved_coords()
            
        # Click AirPlay
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(0.5)  # Reduced from 0.8
        
        # Find and click checkbox/Apple TV
        menu_screenshot = self.capture_screen()
        
        # Try to find checkbox
        checkbox = self.find_template(menu_screenshot, 'checkbox_unchecked.png', threshold=0.6)
        if checkbox:
            print(f"Found checkbox at ({checkbox['x']}, {checkbox['y']})")
            subprocess.run(['cliclick', f"c:{checkbox['x']},{checkbox['y']}"])
        else:
            # If we have saved Apple TV coordinates, use them
            if self.settings and 'apple_tv_coords' in self.settings:
                appletv = self.settings['apple_tv_coords']
                print(f"Using saved Apple TV coords: ({appletv['x']}, {appletv['y']})")
                subprocess.run(['cliclick', f"c:{appletv['x']},{appletv['y']}"])
            else:
                # Use offset from AirPlay
                print("Using offset from AirPlay position")
                subprocess.run(['cliclick', f"c:{airplay['x'] + 50},{airplay['y'] + 70}"])
            
        time.sleep(0.3)  # Reduced from 0.5
        return True
    
    def _enable_with_saved_coords(self):
        """Enable using saved coordinates"""
        if not self.settings or 'airplay_icon_coords' not in self.settings:
            return False
            
        airplay = self.settings['airplay_icon_coords']
        appletv = self.settings['apple_tv_coords']
        
        # Ensure QuickTime is active
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.2)  # Reduced from 0.3
        
        # Show controls
        window = self.get_quicktime_window()
        if window:
            self.show_controls(window)
        else:
            # Move to AirPlay position to trigger controls
            subprocess.run(['cliclick', f"m:{airplay['x']},{airplay['y']}"])
            time.sleep(0.3)  # Reduced from 0.5
        
        # Click sequence
        print(f"Clicking AirPlay at ({airplay['x']}, {airplay['y']})")
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(0.5)  # Reduced from 0.8
        
        print(f"Clicking Apple TV at ({appletv['x']}, {appletv['y']})")
        subprocess.run(['cliclick', f"c:{appletv['x']},{appletv['y']}"])
        time.sleep(0.3)  # Reduced from 0.5
        
        return True
    
    def enable_airplay_fast(self):
        """Fastest possible AirPlay enable - ALWAYS use CV2 detection for accuracy"""
        try:
            # Always use CV2 detection for real-time accuracy
            return self.enable_airplay_cv2()
                
        except Exception as e:
            print(f"Fast AirPlay error: {e}")
            # Fallback to saved coordinates only if CV2 fails
            if self.settings and 'airplay_icon_coords' in self.settings:
                print("Falling back to saved coordinates...")
                return self._enable_with_saved_coords()
            return False


# Convenience function for drop-in replacement
def enable_airplay_fast(settings=None):
    """Quick function to enable AirPlay"""
    enabler = CV2AirPlayEnabler(settings)
    return enabler.enable_airplay_fast()


# Test function
def test_cv2_enabler():
    """Test the CV2 enabler"""
    print("🚀 Testing CV2 AirPlay Enabler")
    
    # Load settings
    import json
    from pathlib import Path
    
    settings_file = Path.home() / '.quicktime_converter_settings.json'
    settings = {}
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    
    enabler = CV2AirPlayEnabler(settings)
    
    print(f"Templates available: {enabler.templates_available}")
    print(f"Has saved coordinates: {'airplay_icon_coords' in settings}")
    
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to test...")
    
    start_time = time.time()
    success = enabler.enable_airplay_fast()
    elapsed = time.time() - start_time
    
    if success:
        print(f"✅ AirPlay enabled in {elapsed:.2f} seconds!")
    else:
        print(f"❌ Failed to enable AirPlay")


if __name__ == "__main__":
    test_cv2_enabler()