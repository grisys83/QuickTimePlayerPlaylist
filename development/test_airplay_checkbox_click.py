#!/usr/bin/env python3
"""
Test clicking checkbox area in AirPlay menu
"""

import subprocess
import time
import pyautogui


def test_checkbox_click():
    """Test clicking checkbox area in AirPlay menu"""
    print("\n☑️ Testing AirPlay Menu Checkbox Click")
    print("=" * 40)
    
    # Activate QuickTime
    print("1️⃣ Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Get AirPlay button position
    print("\n2️⃣ Getting AirPlay button position...")
    
    get_airplay_pos = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btn to button "외장 재생 메뉴 보기" of window 1
            set btnPos to position of btn
            set btnSize to size of btn
            return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & "," & ¬
                   (item 1 of btnSize as string) & "," & (item 2 of btnSize as string)
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', get_airplay_pos], 
                          capture_output=True, text=True)
    
    parts = result.stdout.strip().split(',')
    airplay_x = int(parts[0])
    airplay_y = int(parts[1])
    airplay_width = int(parts[2]) if len(parts) > 2 else 30
    airplay_height = int(parts[3]) if len(parts) > 3 else 30
    
    print(f"   AirPlay button at: ({airplay_x}, {airplay_y})")
    print(f"   Size: {airplay_width}x{airplay_height}")
    
    # Click AirPlay button
    print("\n3️⃣ Clicking AirPlay button...")
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    # Calculate checkbox positions
    print("\n4️⃣ Calculating checkbox positions...")
    
    # Based on the screenshot, the menu appears below the AirPlay button
    # and checkboxes are on the right side of each menu item
    
    # Menu starts about 10-20 pixels below the button
    menu_start_y = airplay_y + airplay_height + 10
    
    # Each menu item is about 30 pixels tall
    item_height = 30
    
    # Checkboxes are on the right side of the menu
    # The menu width looks about 200 pixels, checkbox is near the right edge
    checkbox_x = airplay_x + 150  # Adjust this based on menu width
    
    # Calculate Y positions for each item
    macbook_y = menu_start_y + (item_height // 2)
    living_y = menu_start_y + item_height + (item_height // 2)
    tv_y = menu_start_y + (item_height * 2) + (item_height // 2)
    
    print(f"   Menu items:")
    print(f"   - MacBook Air checkbox at: ({checkbox_x}, {macbook_y})")
    print(f"   - living checkbox at: ({checkbox_x}, {living_y})")
    print(f"   - TV checkbox at: ({checkbox_x}, {tv_y})")
    
    # Click TV checkbox
    print("\n5️⃣ Clicking TV checkbox...")
    pyautogui.click(checkbox_x, tv_y)
    
    print("\n✅ Clicked TV checkbox!")
    
    # Alternative positions to try
    print("\n💡 If this didn't work, try these adjustments:")
    print(f"   1. More to the right: ({checkbox_x + 30}, {tv_y})")
    print(f"   2. More to the left: ({checkbox_x - 30}, {tv_y})")
    print(f"   3. Click living instead: ({checkbox_x}, {living_y})")
    
    # Test alternative - click with offset
    print("\n6️⃣ Alternative - Trying different X offset...")
    time.sleep(2)
    
    # Click AirPlay again
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    # Try clicking more to the right
    alternative_x = airplay_x + 180
    print(f"   Clicking at: ({alternative_x}, {tv_y})")
    pyautogui.click(alternative_x, tv_y)


if __name__ == "__main__":
    test_checkbox_click()