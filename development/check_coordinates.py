#!/usr/bin/env python3
"""
Check and fix coordinate issues
"""

import json
from pathlib import Path
import pyautogui

def check_coordinates():
    print("🔍 Coordinate Check Tool")
    print("=" * 50)
    
    # Get screen info
    logical_width, logical_height = pyautogui.size()
    screenshot = pyautogui.screenshot()
    physical_width = screenshot.width
    physical_height = screenshot.height
    scale_factor = physical_width / logical_width
    
    print(f"\n📐 Screen Info:")
    print(f"  Logical size: {logical_width}x{logical_height}")
    print(f"  Physical size: {physical_width}x{physical_height}")
    print(f"  Scale factor: {scale_factor}")
    
    # Check templates file
    templates_file = Path.home() / '.airplay_templates.json'
    if templates_file.exists():
        print(f"\n📄 Checking {templates_file}")
        with open(templates_file, 'r') as f:
            templates = json.load(f)
        
        if 'airplay_button' in templates:
            pos = templates['airplay_button']['captured_at']
            print(f"\n  AirPlay button: ({pos['x']}, {pos['y']})")
            if pos['x'] > logical_width or pos['y'] > logical_height:
                print(f"    ⚠️ Seems to be physical pixels!")
                print(f"    → Logical: ({pos['x']/scale_factor:.0f}, {pos['y']/scale_factor:.0f})")
            else:
                print(f"    ✅ Already in logical pixels")
                
        if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
            if 'checkbox' in templates['apple_tv_icon']['offsets']:
                pos = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                print(f"\n  Checkbox: ({pos['x']}, {pos['y']})")
                if pos['x'] > logical_width or pos['y'] > logical_height:
                    print(f"    ⚠️ Seems to be physical pixels!")
                    print(f"    → Logical: ({pos['x']/scale_factor:.0f}, {pos['y']/scale_factor:.0f})")
                else:
                    print(f"    ✅ Already in logical pixels")
    
    # Check QuickDrop settings
    quickdrop_file = Path.home() / '.quickdrop_settings.json'
    if quickdrop_file.exists():
        print(f"\n📄 Checking {quickdrop_file}")
        with open(quickdrop_file, 'r') as f:
            settings = json.load(f)
            
        for key in ['airplay_icon_coords', 'apple_tv_coords']:
            if key in settings:
                pos = settings[key]
                print(f"\n  {key}: ({pos['x']}, {pos['y']})")
                if pos['x'] > logical_width or pos['y'] > logical_height:
                    print(f"    ⚠️ Seems to be physical pixels!")
                    print(f"    → Logical: ({pos['x']/scale_factor:.0f}, {pos['y']/scale_factor:.0f})")
                else:
                    print(f"    ✅ Already in logical pixels")

def fix_coordinates():
    """Fix coordinate issues in saved files"""
    print("\n\n🔧 Fixing Coordinates")
    print("=" * 50)
    
    logical_width, logical_height = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale_factor = screenshot.width / logical_width
    
    # Fix templates file
    templates_file = Path.home() / '.airplay_templates.json'
    if templates_file.exists():
        with open(templates_file, 'r') as f:
            templates = json.load(f)
        
        fixed = False
        
        if 'airplay_button' in templates:
            pos = templates['airplay_button']['captured_at']
            if pos['x'] > logical_width or pos['y'] > logical_height:
                pos['x'] = int(pos['x'] / scale_factor)
                pos['y'] = int(pos['y'] / scale_factor)
                fixed = True
                print(f"✅ Fixed airplay_button: ({pos['x']}, {pos['y']})")
                
        if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
            if 'checkbox' in templates['apple_tv_icon']['offsets']:
                pos = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                if pos['x'] > logical_width or pos['y'] > logical_height:
                    pos['x'] = int(pos['x'] / scale_factor)
                    pos['y'] = int(pos['y'] / scale_factor)
                    fixed = True
                    print(f"✅ Fixed checkbox: ({pos['x']}, {pos['y']})")
        
        if fixed:
            # Backup original
            backup_path = templates_file.with_suffix('.json.bak')
            with open(backup_path, 'w') as f:
                with open(templates_file, 'r') as orig:
                    f.write(orig.read())
            
            # Save fixed version
            with open(templates_file, 'w') as f:
                json.dump(templates, f, indent=2)
            print(f"\n💾 Saved fixed coordinates")
            print(f"   Backup: {backup_path}")

def main():
    check_coordinates()
    
    # Ask to fix
    print("\n\nFix coordinate issues? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        fix_coordinates()
        print("\n✅ Done! Try running QuickDrop again.")

if __name__ == "__main__":
    main()