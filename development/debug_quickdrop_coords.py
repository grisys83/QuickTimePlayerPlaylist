#!/usr/bin/env python3
"""
Debug QuickDrop coordinates
"""

import json
from pathlib import Path
import pyautogui
import subprocess
import time

def debug_coordinates():
    print("🔍 QuickDrop Coordinate Debug")
    print("=" * 50)
    
    # Get scale factor
    logical_width, logical_height = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale_factor = screenshot.width / logical_width
    
    print(f"\n📐 Display info:")
    print(f"   Logical size: {logical_width}x{logical_height}")
    print(f"   Physical size: {screenshot.width}x{screenshot.height}")
    print(f"   Scale factor: {scale_factor}")
    
    # Check saved coordinates
    templates_file = Path.home() / '.airplay_templates.json'
    if templates_file.exists():
        print(f"\n📄 Loading coordinates from {templates_file.name}")
        with open(templates_file, 'r') as f:
            templates = json.load(f)
        
        airplay_coords = None
        checkbox_coords = None
        
        if 'airplay_button' in templates:
            airplay_coords = templates['airplay_button']['captured_at']
            print(f"\n🎯 AirPlay button:")
            print(f"   Saved: ({airplay_coords['x']}, {airplay_coords['y']})")
            
        if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
            if 'checkbox' in templates['apple_tv_icon']['offsets']:
                checkbox_coords = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                print(f"\n☑️  Checkbox:")
                print(f"   Saved: ({checkbox_coords['x']}, {checkbox_coords['y']})")
        
        # Test the coordinates
        if airplay_coords and checkbox_coords:
            print("\n\n🧪 Testing coordinates...")
            print("Watch where the mouse moves!")
            
            # Activate QuickTime
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(1)
            
            # Test 1: Move to AirPlay position as saved
            print(f"\n1. Moving to saved AirPlay position ({airplay_coords['x']}, {airplay_coords['y']})...")
            pyautogui.moveTo(airplay_coords['x'], airplay_coords['y'], duration=1)
            time.sleep(2)
            
            # Test 2: Click AirPlay
            print("   Clicking AirPlay...")
            pyautogui.click()
            time.sleep(2)
            
            # Test 3: Move to checkbox as saved
            print(f"\n2. Moving to saved checkbox position ({checkbox_coords['x']}, {checkbox_coords['y']})...")
            pyautogui.moveTo(checkbox_coords['x'], checkbox_coords['y'], duration=1)
            time.sleep(2)
            
            # Test 4: If coordinates are wrong, try dividing by scale factor
            if checkbox_coords['x'] > logical_width or checkbox_coords['y'] > logical_height:
                print("\n⚠️  Coordinates seem to be physical pixels!")
                logical_x = int(checkbox_coords['x'] / scale_factor)
                logical_y = int(checkbox_coords['y'] / scale_factor)
                print(f"\n3. Moving to logical position ({logical_x}, {logical_y})...")
                pyautogui.moveTo(logical_x, logical_y, duration=1)
                time.sleep(2)

def fix_quickdrop_settings():
    """Fix QuickDrop settings if needed"""
    print("\n\n🔧 Fixing QuickDrop Settings")
    print("=" * 50)
    
    # Create correct settings from templates
    templates_file = Path.home() / '.airplay_templates.json'
    if not templates_file.exists():
        print("❌ No templates found")
        return
        
    with open(templates_file, 'r') as f:
        templates = json.load(f)
    
    # Get scale factor
    logical_width, _ = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale_factor = screenshot.width / logical_width
    
    # Build QuickDrop settings
    quickdrop_settings = {'airplay_configured': True}
    
    if 'airplay_button' in templates:
        coords = templates['airplay_button']['captured_at'].copy()
        # Ensure logical coordinates
        if coords['x'] > logical_width:
            coords['x'] = int(coords['x'] / scale_factor)
            coords['y'] = int(coords['y'] / scale_factor)
        quickdrop_settings['airplay_icon_coords'] = coords
        
    if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
        if 'checkbox' in templates['apple_tv_icon']['offsets']:
            coords = templates['apple_tv_icon']['offsets']['checkbox']['absolute'].copy()
            # Ensure logical coordinates
            if coords['x'] > logical_width:
                coords['x'] = int(coords['x'] / scale_factor)
                coords['y'] = int(coords['y'] / scale_factor)
            quickdrop_settings['apple_tv_coords'] = coords
    
    # Save fixed settings
    settings_file = Path.home() / '.quickdrop_settings.json'
    with open(settings_file, 'w') as f:
        json.dump(quickdrop_settings, f, indent=2)
    
    print(f"\n💾 Saved fixed settings to {settings_file}")
    print(json.dumps(quickdrop_settings, indent=2))

def main():
    debug_coordinates()
    
    print("\n\nFix coordinates? (y/n): ", end='')
    if input().strip().lower() == 'y':
        fix_quickdrop_settings()
        print("\n✅ Done! Try QuickDrop again.")

if __name__ == "__main__":
    main()