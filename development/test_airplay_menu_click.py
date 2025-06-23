#!/usr/bin/env python3
"""
Test clicking AirPlay menu items directly
"""

import subprocess
import time
import pyautogui


def test_menu_click():
    """Test clicking menu items in AirPlay popup"""
    print("\n🖱️ Testing AirPlay Menu Click")
    print("=" * 40)
    
    # Activate QuickTime
    print("1️⃣ Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Get AirPlay button position and click
    print("\n2️⃣ Getting AirPlay button position...")
    
    get_airplay_pos = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btn to button "외장 재생 메뉴 보기" of window 1
            set btnPos to position of btn
            return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', get_airplay_pos], 
                          capture_output=True, text=True)
    
    airplay_pos = result.stdout.strip().split(',')
    airplay_x = int(airplay_pos[0])
    airplay_y = int(airplay_pos[1])
    print(f"   AirPlay button at: ({airplay_x}, {airplay_y})")
    
    # Click AirPlay button
    print("\n3️⃣ Clicking AirPlay button...")
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    # Method 1: Try to find menu items using Accessibility API
    print("\n4️⃣ Method 1: Looking for menu items...")
    
    find_menu_items = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to ""
            
            -- Check all windows
            set winCount to count of windows
            set output to output & "Windows: " & (winCount as string) & return
            
            if winCount > 1 then
                -- Menu is window 2
                set menuWindow to window 2
                
                -- Try different ways to access menu items
                -- Method A: Direct menu items
                try
                    set menuItems to every menu item of menuWindow
                    set output to output & "Found " & (count of menuItems as string) & " menu items" & return
                    repeat with mi in menuItems
                        set miTitle to title of mi
                        set output to output & "  - " & miTitle & return
                    end repeat
                end try
                
                -- Method B: UI elements
                set allElements to every UI element of menuWindow
                set output to output & return & "All UI elements: " & (count of allElements as string) & return
                
                set elementIndex to 0
                repeat with elem in allElements
                    set elementIndex to elementIndex + 1
                    set elemClass to class of elem as string
                    
                    -- Try to get position for clickable elements
                    if elemClass contains "button" or elemClass contains "menu" then
                        try
                            set elemPos to position of elem
                            set elemSize to size of elem
                            set output to output & elementIndex & ". " & elemClass & " at (" & ¬
                                (item 1 of elemPos as string) & "," & (item 2 of elemPos as string) & ") " & ¬
                                "size: " & (item 1 of elemSize as string) & "x" & (item 2 of elemSize as string)
                            
                            -- Try to get name/title
                            try
                                set elemName to name of elem
                                set output to output & " name: " & elemName
                            end try
                            try
                                set elemTitle to title of elem
                                set output to output & " title: " & elemTitle
                            end try
                            
                            set output to output & return
                        end try
                    end if
                end repeat
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', find_menu_items], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Method 2: Click by relative position
    print("\n5️⃣ Method 2: Clicking by position...")
    print("   Menu items are typically:")
    print("   - 1st: Park의 MacBook Air (current)")
    print("   - 2nd: living (~40 pixels down)")
    print("   - 3rd: TV (~80 pixels down)")
    
    # Calculate positions relative to AirPlay button
    # Menu appears below the button
    menu_x = airplay_x
    living_y = airplay_y + 40  # Approximate position
    tv_y = airplay_y + 80      # Approximate position
    
    print(f"\n   Clicking 'TV' at approximately ({menu_x}, {tv_y})...")
    pyautogui.click(menu_x, tv_y)
    
    print("\n✅ Done!")
    print("\n💡 If this didn't work, we can:")
    print("   1. Adjust the Y offsets (40, 80)")
    print("   2. Try clicking 'living' instead")
    print("   3. Use image recognition to find menu items")


if __name__ == "__main__":
    test_menu_click()