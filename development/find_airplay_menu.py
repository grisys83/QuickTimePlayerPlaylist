#!/usr/bin/env python3
"""
Find and interact with AirPlay menu
"""

import subprocess
import time


def find_airplay_menu():
    """Find and interact with AirPlay menu"""
    print("\n🎯 Finding AirPlay Menu")
    print("=" * 40)
    
    # Activate QuickTime
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Click AirPlay button
    print("1️⃣ Clicking AirPlay button...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            click button "외장 재생 메뉴 보기" of window 1
            return "Clicked"
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', click_script], capture_output=True)
    time.sleep(1.5)
    
    # Find menu button
    print("\n2️⃣ Looking for menu button...")
    
    menu_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== MENU BUTTON SEARCH ===" & return
            
            -- Find menu button
            set menuBtnList to every menu button of window 1
            set menuBtnCount to count of menuBtnList
            set output to output & "Found " & (menuBtnCount as string) & " menu buttons" & return
            
            if menuBtnCount > 0 then
                set menuBtn to item 1 of menuBtnList
                set menuBtnPos to position of menuBtn
                set output to output & "Menu button at: (" & (item 1 of menuBtnPos as string) & "," & (item 2 of menuBtnPos as string) & ")" & return
                
                -- Check if it has a menu
                try
                    set menuList to every menu of menuBtn
                    set menuCount to count of menuList
                    set output to output & "Has " & (menuCount as string) & " menus" & return
                    
                    if menuCount > 0 then
                        set mnu to item 1 of menuList
                        set menuItems to every menu item of mnu
                        set itemCount to count of menuItems
                        set output to output & return & "Menu has " & (itemCount as string) & " items:" & return
                        
                        repeat with mi in menuItems
                            try
                                set miTitle to title of mi
                                set output to output & "  - " & miTitle & return
                            end try
                        end repeat
                    end if
                end try
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', menu_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Try to click menu items
    print("\n3️⃣ Trying to interact with menu...")
    
    interact_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to ""
            
            -- Method 1: Direct menu button click
            set menuBtnList to every menu button of window 1
            if (count of menuBtnList) > 0 then
                set menuBtn to item 1 of menuBtnList
                
                -- Click to show menu
                click menuBtn
                delay 0.5
                
                -- Try to access menu items
                try
                    set mnu to menu 1 of menuBtn
                    set menuItems to every menu item of mnu
                    
                    -- Look for Apple TV item
                    repeat with mi in menuItems
                        set miTitle to title of mi
                        if miTitle contains "TV" or miTitle contains "Apple" then
                            click mi
                            set output to output & "Clicked: " & miTitle & return
                            exit repeat
                        end if
                    end repeat
                end try
            end if
            
            -- Method 2: Check for popup window
            delay 0.5
            set winCount to count of windows
            if winCount > 1 then
                set output to output & return & "Found popup window!" & return
                set popup to window 2
                
                -- Look for buttons or menu items in popup
                set popupButtons to every button of popup
                repeat with btn in popupButtons
                    try
                        set btnTitle to title of btn
                        set output to output & "  Button: " & btnTitle & return
                    end try
                end repeat
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', interact_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Alternative: Try keyboard navigation
    print("\n4️⃣ Trying keyboard navigation...")
    
    keyboard_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Click AirPlay button again
            click button "외장 재생 메뉴 보기" of window 1
            delay 0.5
            
            -- Try arrow keys to navigate menu
            key code 125 -- Down arrow
            delay 0.2
            key code 125 -- Down arrow again
            delay 0.2
            key code 36 -- Return key
            
            return "Attempted keyboard navigation"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', keyboard_script], 
                          capture_output=True, text=True)
    print(result.stdout)


if __name__ == "__main__":
    find_airplay_menu()