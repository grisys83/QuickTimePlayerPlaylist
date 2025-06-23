#!/usr/bin/env python3
"""
Relative AirPlay detector that finds positions relative to QuickTime window
"""

import subprocess
import time
import json
from pathlib import Path

class RelativeAirPlayDetector:
    def __init__(self):
        self.quicktime_window = None
        
    def find_quicktime_window(self):
        """Find QuickTime window position and size"""
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
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            self.quicktime_window = {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
            return self.quicktime_window
        return None
    
    def get_relative_airplay_position(self):
        """Get AirPlay position relative to QuickTime window"""
        if not self.find_quicktime_window():
            return None
            
        # Common relative positions for AirPlay icon
        # Usually in bottom-right area of the window
        relative_positions = {
            'standard': {
                # Standard position (from bottom-right corner)
                'airplay_offset_x': -150,  # 150 pixels from right edge
                'airplay_offset_y': -50,   # 50 pixels from bottom
                'appletv_offset_x': 50,    # 50 pixels right of airplay
                'appletv_offset_y': 70     # 70 pixels below airplay
            },
            'fullscreen': {
                # Fullscreen position
                'airplay_offset_x': -200,
                'airplay_offset_y': -60,
                'appletv_offset_x': 50,
                'appletv_offset_y': 70
            }
        }
        
        # Determine if fullscreen
        import Quartz
        screen_width = Quartz.CGDisplayPixelsWide(0)
        is_fullscreen = self.quicktime_window['width'] >= screen_width * 0.95
        
        mode = 'fullscreen' if is_fullscreen else 'standard'
        offsets = relative_positions[mode]
        
        # Calculate absolute positions
        airplay_x = self.quicktime_window['x'] + self.quicktime_window['width'] + offsets['airplay_offset_x']
        airplay_y = self.quicktime_window['y'] + self.quicktime_window['height'] + offsets['airplay_offset_y']
        
        appletv_x = airplay_x + offsets['appletv_offset_x']
        appletv_y = airplay_y + offsets['appletv_offset_y']
        
        return {
            'airplay_icon_coords': {'x': airplay_x, 'y': airplay_y},
            'apple_tv_coords': {'x': appletv_x, 'y': appletv_y},
            'window_info': self.quicktime_window,
            'mode': mode
        }
    
    def show_controls_and_get_position(self):
        """Move mouse to show controls and get positions"""
        if not self.find_quicktime_window():
            return None
            
        # Move mouse to bottom center to show controls
        center_x = self.quicktime_window['x'] + self.quicktime_window['width'] // 2
        bottom_y = self.quicktime_window['y'] + self.quicktime_window['height'] - 20
        
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        time.sleep(0.8)  # Wait for controls to appear
        
        return self.get_relative_airplay_position()
    
    def enable_airplay_relative(self):
        """Enable AirPlay using relative positioning"""
        coords = self.show_controls_and_get_position()
        if not coords:
            print("Could not find QuickTime window")
            return False
            
        print(f"QuickTime window: {coords['window_info']}")
        print(f"Mode: {coords['mode']}")
        print(f"AirPlay position: {coords['airplay_icon_coords']}")
        
        # Click AirPlay
        x = coords['airplay_icon_coords']['x']
        y = coords['airplay_icon_coords']['y']
        subprocess.run(['cliclick', f'c:{x},{y}'])
        time.sleep(0.5)
        
        # Click Apple TV
        x = coords['apple_tv_coords']['x']
        y = coords['apple_tv_coords']['y']
        subprocess.run(['cliclick', f'c:{x},{y}'])
        
        return True


def update_apps_with_relative_positioning():
    """Update all apps to use relative positioning"""
    detector = RelativeAirPlayDetector()
    
    print("Testing relative positioning...")
    coords = detector.show_controls_and_get_position()
    
    if coords:
        print("\nDetected positions:")
        print(f"Window: {coords['window_info']['x']}, {coords['window_info']['y']} "
              f"({coords['window_info']['width']}x{coords['window_info']['height']})")
        print(f"AirPlay: {coords['airplay_icon_coords']}")
        print(f"Apple TV: {coords['apple_tv_coords']}")
        
        # Save as default coordinates
        save = input("\nSave these as default coordinates? (y/n): ")
        if save.lower() == 'y':
            # Update QuickDrop settings
            settings = {
                'airplay_icon_coords': coords['airplay_icon_coords'],
                'apple_tv_coords': coords['apple_tv_coords'],
                'airplay_configured': True,
                'use_relative_positioning': True
            }
            
            settings_file = Path.home() / '.quickdrop_settings.json'
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"Settings saved to {settings_file}")
            
            # Also update converter settings
            converter_settings = Path.home() / '.quicktime_converter_settings.json'
            with open(converter_settings, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"Settings saved to {converter_settings}")
    else:
        print("Could not detect QuickTime window")


if __name__ == "__main__":
    update_apps_with_relative_positioning()