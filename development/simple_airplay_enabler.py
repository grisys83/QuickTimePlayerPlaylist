#!/usr/bin/env python3
"""
Simple AirPlay enabler using known offsets
Since the offset-based approach works, let's use it directly
"""

import subprocess
import time
from pathlib import Path
import json

class SimpleAirPlayEnabler:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        
    def enable_airplay_simple(self):
        """Simple enabler using the working offset"""
        print("🚀 Simple AirPlay Enabler")
        print("=" * 50)
        
        # Step 1: Activate QuickTime
        print("\n📍 Activating QuickTime...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Step 2: Get window and show controls
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime not found")
            return False
            
        print("✅ QuickTime window found")
        
        # Step 3: Show controls
        print("\n📍 Showing controls...")
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 250
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.8)
        
        # Step 4: Click AirPlay (typical position)
        # AirPlay is usually on the right side of control bar
        airplay_x = window['x'] + window['width'] - 150
        airplay_y = window['y'] + window['height'] - 50
        
        print(f"\n📍 Clicking AirPlay at ({airplay_x}, {airplay_y})...")
        subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
        time.sleep(1.5)
        
        # Step 5: Click checkbox using the offset that works
        # Based on your testing: checkbox is roughly at these offsets from AirPlay
        checkbox_x = airplay_x - 94   # Adjusted based on your successful click
        checkbox_y = airplay_y - 160  # Above AirPlay
        
        print(f"\n📍 Clicking checkbox at ({checkbox_x}, {checkbox_y})...")
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
        
        print("\n✅ AirPlay should be enabled!")
        
        # Save the positions that worked
        self.save_working_positions(airplay_x, airplay_y, checkbox_x, checkbox_y)
        
        return True
    
    def save_working_positions(self, airplay_x, airplay_y, checkbox_x, checkbox_y):
        """Save positions that worked"""
        settings = {
            'working_positions': {
                'airplay': {'x': airplay_x, 'y': airplay_y},
                'checkbox': {'x': checkbox_x, 'y': checkbox_y}
            },
            'working_offset': {
                'x': checkbox_x - airplay_x,
                'y': checkbox_y - airplay_y
            },
            'method': 'simple_offset'
        }
        
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            
            existing = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    try:
                        existing = json.load(f)
                    except:
                        pass
            
            existing.update(settings)
            
            with open(settings_file, 'w') as f:
                json.dump(existing, f, indent=2)
    
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


def create_apple_tv_template():
    """Create Apple TV icon template from menu"""
    print("📸 Creating Apple TV Icon Template")
    print("=" * 50)
    
    print("\n1. I'll open the AirPlay menu")
    print("2. Take a screenshot")
    print("3. You can crop the Apple TV icon")
    
    input("\nPress Enter to start...")
    
    enabler = SimpleAirPlayEnabler()
    
    # Get window
    window = enabler.get_quicktime_window()
    if not window:
        print("❌ QuickTime not found")
        return
    
    # Show controls and click AirPlay
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    center_x = window['x'] + window['width'] // 2
    control_y = window['y'] + window['height'] - 250
    subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
    time.sleep(0.8)
    
    airplay_x = window['x'] + window['width'] - 150
    airplay_y = window['y'] + window['height'] - 50
    subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
    time.sleep(1.5)
    
    # Capture menu
    screenshot_path = str(Path.home() / "airplay_menu_for_template.png")
    subprocess.run(["screencapture", "-x", screenshot_path])
    
    print(f"\n📸 Menu screenshot saved to: {screenshot_path}")
    print("\n📋 Next steps:")
    print("1. Open the screenshot in Preview")
    print("2. Find the Apple TV device icon")
    print("3. Select and crop just the icon (Cmd+K)")
    print("4. Save as 'apple_tv_icon.png' in:")
    print(f"   {Path(__file__).parent / 'templates'}")
    
    # Also show where the checkbox was clicked
    print(f"\n💡 For reference, the working checkbox position was:")
    print(f"   ({airplay_x - 94}, {airplay_y - 160})")


def main():
    print("🍎 Simple AirPlay Enabler")
    print("\nOptions:")
    print("1. Enable AirPlay (simple method)")
    print("2. Create Apple TV icon template")
    
    choice = input("\nSelect (1-2): ")
    
    if choice == '1':
        enabler = SimpleAirPlayEnabler()
        enabler.enable_airplay_simple()
    elif choice == '2':
        create_apple_tv_template()


if __name__ == "__main__":
    main()