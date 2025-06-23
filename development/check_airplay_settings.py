#!/usr/bin/env python3
"""
Check and debug AirPlay settings
"""

import json
from pathlib import Path
import subprocess

def check_settings():
    """Check current AirPlay settings"""
    print("🔍 Checking AirPlay Settings")
    print("=" * 50)
    
    # Check both settings files
    files = [
        '.quicktime_converter_settings.json',
        '.quickdrop_settings.json'
    ]
    
    for filename in files:
        settings_file = Path.home() / filename
        print(f"\n📄 {filename}:")
        
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                
            if 'airplay_icon_coords' in settings:
                airplay = settings['airplay_icon_coords']
                print(f"   AirPlay icon: ({airplay['x']}, {airplay['y']})")
            else:
                print("   ❌ No AirPlay icon coordinates")
                
            if 'apple_tv_coords' in settings:
                appletv = settings['apple_tv_coords']
                print(f"   Apple TV: ({appletv['x']}, {appletv['y']})")
            else:
                print("   ❌ No Apple TV coordinates")
                
            if 'airplay_enabled' in settings:
                print(f"   AirPlay enabled: {settings['airplay_enabled']}")
                
            if 'manually_configured' in settings:
                print(f"   Manually configured: {settings['manually_configured']}")
        else:
            print("   ❌ File not found")
    
    # Check templates
    print("\n📁 Templates:")
    template_dir = Path(__file__).parent / "templates"
    if template_dir.exists():
        templates = [
            'airplay_icon.png',
            'apple_tv.png',
            'checkbox_unchecked.png',
            'checkbox_checked.png'
        ]
        
        for template in templates:
            path = template_dir / template
            if path.exists():
                print(f"   ✅ {template}")
            else:
                print(f"   ❌ {template}")
    else:
        print("   ❌ Templates directory not found")
    
    # Test coordinates
    print("\n🧪 Test current coordinates?")
    print("1. Test AirPlay icon position")
    print("2. Test Apple TV position")
    print("3. Test both")
    print("4. Skip")
    
    choice = input("\nSelect (1-4): ")
    
    if choice in ['1', '2', '3']:
        # Load settings
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                
            print("\nMake sure QuickTime is open with a video")
            input("Press Enter to continue...")
            
            if choice in ['1', '3'] and 'airplay_icon_coords' in settings:
                airplay = settings['airplay_icon_coords']
                print(f"\n🎯 Moving to AirPlay icon ({airplay['x']}, {airplay['y']})...")
                subprocess.run(['cliclick', f"m:{airplay['x']},{airplay['y']}"])
                response = input("Is the cursor on the AirPlay icon? (y/n): ")
                if response.lower() != 'y':
                    print("❌ AirPlay coordinates need to be updated")
                    print("Run: python3 reset_airplay_coordinates.py")
                
            if choice in ['2', '3'] and 'apple_tv_coords' in settings:
                appletv = settings['apple_tv_coords']
                print(f"\n🎯 Moving to Apple TV ({appletv['x']}, {appletv['y']})...")
                subprocess.run(['cliclick', f"m:{appletv['x']},{appletv['y']}"])
                response = input("Is the cursor on the Apple TV checkbox? (y/n): ")
                if response.lower() != 'y':
                    print("❌ Apple TV coordinates need to be updated")
                    print("Run: python3 reset_airplay_coordinates.py")

if __name__ == "__main__":
    check_settings()