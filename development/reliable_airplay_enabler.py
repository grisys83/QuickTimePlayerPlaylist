#!/usr/bin/env python3
"""
Reliable AirPlay enabler that handles UI delays
"""

import subprocess
import time
import json
from pathlib import Path

class ReliableAirPlayEnabler:
    def __init__(self, settings=None):
        self.settings = settings or self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {
            'airplay_icon_coords': {'x': 844, 'y': 714},
            'apple_tv_coords': {'x': 970, 'y': 784}
        }
    
    def find_quicktime_window(self):
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
    
    def show_controls(self):
        """Show QuickTime controls by moving mouse"""
        qt_window = self.find_quicktime_window()
        if not qt_window:
            print("QuickTime window not found")
            return False
            
        # Move mouse to bottom center
        center_x = qt_window['x'] + qt_window['width'] // 2
        bottom_y = qt_window['y'] + qt_window['height'] - 340
        
        print(f"Moving mouse to show controls...")
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        
        # Wait for controls to appear with animation
        time.sleep(1.0)
        
        # Small mouse movement to ensure controls stay visible
        subprocess.run(['cliclick', f'm:{center_x + 5},{bottom_y}'])
        time.sleep(0.3)
        
        return True
    
    def enable_airplay(self, use_smart_detection=True):
        """Enable AirPlay with proper timing"""
        print("Enabling AirPlay...")
        
        # Step 1: Show controls
        if not self.show_controls():
            return False
            
        # Step 2: Get coordinates
        if use_smart_detection and self.settings.get('detection_method') == 'smart':
            # Use smart detection to update coordinates
            from smart_airplay_detector import SmartAirPlayDetector
            detector = SmartAirPlayDetector()
            detector.debug_mode = False
            
            airplay_pos = detector.step1_find_airplay_icon()
            if airplay_pos:
                airplay_x = airplay_pos['x']
                airplay_y = airplay_pos['y']
            else:
                airplay_x = self.settings['airplay_icon_coords']['x']
                airplay_y = self.settings['airplay_icon_coords']['y']
        else:
            airplay_x = self.settings['airplay_icon_coords']['x']
            airplay_y = self.settings['airplay_icon_coords']['y']
            
        # Step 3: Click AirPlay icon
        print(f"Clicking AirPlay icon at ({airplay_x}, {airplay_y})")
        subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
        
        # Wait for menu to appear
        time.sleep(1.2)
        
        # Step 4: Click Apple TV
        appletv_x = self.settings['apple_tv_coords']['x']
        appletv_y = self.settings['apple_tv_coords']['y']
        
        print(f"Clicking Apple TV at ({appletv_x}, {appletv_y})")
        subprocess.run(['cliclick', f'c:{appletv_x},{appletv_y}'])
        
        # Wait for connection
        time.sleep(0.8)
        
        print("✓ AirPlay enabled")
        return True


# Patch for all apps to use this reliable method
def create_airplay_patch():
    """Create a patch file for apps to use reliable AirPlay"""
    patch_content = '''
# Add this to your app's _enable_airplay method:
from reliable_airplay_enabler import ReliableAirPlayEnabler
enabler = ReliableAirPlayEnabler(self.settings)
enabler.enable_airplay()
'''
    
    print("To use reliable AirPlay in your apps, replace _enable_airplay with:")
    print(patch_content)


if __name__ == "__main__":
    print("Testing Reliable AirPlay Enabler")
    print("=" * 50)
    
    enabler = ReliableAirPlayEnabler()
    
    print("Make sure QuickTime Player is open with a video")
    input("Press Enter to test...")
    
    if enabler.enable_airplay():
        print("\n✅ Success! AirPlay should now be active")
    else:
        print("\n❌ Failed to enable AirPlay")