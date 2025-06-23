#!/usr/bin/env python3
"""
Reset and reconfigure AirPlay coordinates with proper conversion
"""

import subprocess
import time
import json
from pathlib import Path

def reset_and_configure():
    """Reset coordinates and configure new ones"""
    print("🔧 AirPlay Coordinate Reset & Configuration")
    print("=" * 50)
    
    # Import necessary modules
    try:
        from fixed_template_detector import FixedTemplateDetector
        from coordinate_converter import CoordinateConverter
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Create detector
    detector = FixedTemplateDetector()
    converter = CoordinateConverter()
    
    print(f"\n📊 System Information:")
    print(f"   Scale factor: {converter.scale_factor}")
    print(f"   Screen info: {converter.screen_info}")
    
    # Check QuickTime
    print("\n📺 Please ensure:")
    print("1. QuickTime Player is open")
    print("2. A video is loaded")
    print("3. The QuickTime window is visible")
    
    input("\nPress Enter when ready...")
    
    # Activate QuickTime
    print("\n🎬 Activating QuickTime...")
    detector.activate_quicktime()
    
    # Get window
    window = detector.get_quicktime_window()
    if not window:
        print("❌ QuickTime window not found!")
        return
        
    print(f"✅ QuickTime window found: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
    
    # Show controls
    print("\n🎮 Showing controls...")
    detector.show_controls(window)
    
    # Manual coordinate input
    print("\n🎯 Manual Coordinate Configuration")
    print("I'll help you find the correct positions.")
    
    # Find AirPlay icon
    print("\n1️⃣ Finding AirPlay Icon")
    print("Move your mouse to the AirPlay icon and tell me when you're there.")
    input("Press Enter when your mouse is on the AirPlay icon...")
    
    # Get current mouse position
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        airplay_x, airplay_y = int(coords[0]), int(coords[1])
        print(f"✅ AirPlay position recorded: ({airplay_x}, {airplay_y})")
    else:
        print("❌ Could not get mouse position")
        return
    
    # Click to open menu
    print("\n🖱️ Clicking AirPlay to open menu...")
    subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
    time.sleep(1)
    
    # Find Apple TV checkbox
    print("\n2️⃣ Finding Apple TV Checkbox")
    print("Move your mouse to the Apple TV checkbox in the menu.")
    input("Press Enter when your mouse is on the Apple TV checkbox...")
    
    # Get current mouse position
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        appletv_x, appletv_y = int(coords[0]), int(coords[1])
        print(f"✅ Apple TV position recorded: ({appletv_x}, {appletv_y})")
    else:
        print("❌ Could not get mouse position")
        return
    
    # Close menu
    subprocess.run(['cliclick', 'c:100,100'])
    
    # Test the positions
    print("\n🧪 Testing recorded positions...")
    
    # Show controls again
    detector.show_controls(window)
    time.sleep(1)
    
    # Move to AirPlay
    print(f"Moving to AirPlay ({airplay_x}, {airplay_y})...")
    subprocess.run(['cliclick', f'm:{airplay_x},{airplay_y}'])
    
    confirm = input("Is the mouse on the AirPlay icon? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Position verification failed")
        return
    
    # Save settings
    settings = {
        'airplay_icon_coords': {'x': airplay_x, 'y': airplay_y},
        'apple_tv_coords': {'x': appletv_x, 'y': appletv_y},
        'airplay_enabled': True,
        'use_relative_positioning': False,
        'manually_configured': True,
        'scale_factor': converter.scale_factor
    }
    
    # Save to both settings files
    for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
        settings_file = Path.home() / filename
        print(f"\n💾 Saving to {filename}...")
        
        # Load existing settings if any
        existing = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    existing = json.load(f)
            except:
                pass
        
        # Update with new coordinates
        existing.update(settings)
        
        # Save
        with open(settings_file, 'w') as f:
            json.dump(existing, f, indent=2)
            
        print(f"✅ Saved to {settings_file}")
    
    print("\n✅ Configuration complete!")
    print(f"   AirPlay: ({airplay_x}, {airplay_y})")
    print(f"   Apple TV: ({appletv_x}, {appletv_y})")
    
    # Final test
    test = input("\n🎬 Test complete AirPlay sequence? (y/n): ")
    if test.lower() == 'y':
        print("\n Running AirPlay sequence...")
        
        # Show controls
        detector.show_controls(window)
        time.sleep(1)
        
        # Click AirPlay
        print("1️⃣ Clicking AirPlay...")
        subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
        time.sleep(1)
        
        # Click Apple TV
        print("2️⃣ Clicking Apple TV...")
        subprocess.run(['cliclick', f'c:{appletv_x},{appletv_y}'])
        
        print("\n✅ Sequence complete! AirPlay should now be active.")

if __name__ == "__main__":
    reset_and_configure()