#!/usr/bin/env python3
"""
Find the exact offset from Apple TV icon to checkbox
"""

import subprocess
import time

def find_checkbox_offset():
    print("🎯 Finding Checkbox Offset")
    print("=" * 50)
    
    print("\n📋 Instructions:")
    print("1. Open QuickTime with a video")
    print("2. Click AirPlay to open the menu")
    print("3. Make sure 'living' (Apple TV) is visible")
    
    input("\nPress Enter when AirPlay menu is open...")
    
    # Get Apple TV text position
    print("\n🎯 Step 1: Position mouse on 'living' text")
    input("Move your mouse to the 'living' text and press Enter...")
    
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        text_x, text_y = int(coords[0]), int(coords[1])
        print(f"✅ 'living' text position: ({text_x}, {text_y})")
    else:
        print("❌ Could not get position")
        return
    
    # Get checkbox position
    print("\n🎯 Step 2: Position mouse on the checkbox")
    input("Move your mouse to the checkbox for 'living' and press Enter...")
    
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        checkbox_x, checkbox_y = int(coords[0]), int(coords[1])
        print(f"✅ Checkbox position: ({checkbox_x}, {checkbox_y})")
    else:
        print("❌ Could not get position")
        return
    
    # Calculate offset
    offset_x = checkbox_x - text_x
    offset_y = checkbox_y - text_y
    
    print("\n📊 Results:")
    print(f"   Text position: ({text_x}, {text_y})")
    print(f"   Checkbox position: ({checkbox_x}, {checkbox_y})")
    print(f"   Offset: X={offset_x}, Y={offset_y}")
    
    print("\n💡 To use this offset:")
    print(f"   checkbox_x = appletv_x + {offset_x}")
    print(f"   checkbox_y = appletv_y + {offset_y}")
    
    # Test click
    test = input("\n🧪 Test click at calculated position? (y/n): ")
    if test.lower() == 'y':
        print(f"Clicking at ({checkbox_x}, {checkbox_y})...")
        subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])


if __name__ == "__main__":
    find_checkbox_offset()