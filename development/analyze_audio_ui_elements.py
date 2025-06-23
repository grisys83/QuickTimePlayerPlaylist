#!/usr/bin/env python3
"""
Analyze audio player UI elements properly
"""

import subprocess
import time


def analyze_ui_elements():
    """Analyze all UI elements in audio player"""
    print("\n🔍 Analyzing Audio Player UI Elements")
    print("=" * 50)
    
    # Make QuickTime frontmost
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Get ALL UI elements
    print("\n1️⃣ All UI Elements in Window:")
    
    all_elements_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to ""
            set allElements to every UI element of window 1
            set elemCount to count of allElements
            
            repeat with i from 1 to elemCount
                set elem to item i of allElements
                set elemClass to class of elem as string
                set elemPos to position of elem
                set output to output & i & ". " & elemClass & " at (" & (item 1 of elemPos as string) & "," & (item 2 of elemPos as string) & ")"
                
                -- Get additional info based on type
                if elemClass contains "button" then
                    try
                        set btnDesc to description of elem
                        set output to output & " - " & btnDesc
                    end try
                else if elemClass contains "checkbox" then
                    try
                        set cbValue = value of elem
                        set output to output & " - value=" & (cbValue as string)
                    end try
                else if elemClass contains "static text" then
                    try
                        set txtValue to value of elem
                        set output to output & " - '" & txtValue & "'"
                    end try
                end if
                
                set output to output & return
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', all_elements_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Click AirPlay button and check what happens
    print("\n2️⃣ Clicking AirPlay button...")
    
    click_airplay_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    if description of btn contains "외장" then
                        click btn
                        return "Clicked AirPlay button"
                    end if
                end try
            end repeat
            return "AirPlay button not found"
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', click_airplay_script], capture_output=True)
    
    # Wait and check for changes
    print("\n⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # Check for popup or new elements
    print("\n3️⃣ After clicking AirPlay - Looking for popup:")
    
    popup_check_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== WINDOWS ===" & return
            set winCount to count of windows
            set output to output & "Window count: " & (winCount as string) & return
            
            -- Check all windows
            repeat with i from 1 to winCount
                set win to window i
                set winName to name of win
                set winRole to role of win
                set output to output & return & "Window " & i & ": " & winName & " (role=" & winRole & ")" & return
                
                -- Get UI elements in this window
                set winElements to every UI element of win
                set elemCount to count of winElements
                set output to output & "  Elements: " & (elemCount as string) & return
                
                -- Look for menu, list, or other containers
                repeat with elem in winElements
                    set elemClass to class of elem as string
                    if elemClass contains "menu" or elemClass contains "list" or elemClass contains "scroll area" then
                        set output to output & "  Found: " & elemClass & return
                        
                        -- Check children
                        try
                            set childElements to every UI element of elem
                            set childCount to count of childElements
                            set output to output & "    Children: " & (childCount as string) & return
                        end try
                    end if
                end repeat
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', popup_check_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Look for any clickable items
    print("\n4️⃣ Looking for clickable items (buttons, menu items, etc):")
    
    clickable_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== CLICKABLE ITEMS ===" & return
            
            -- Check all windows
            set winList to every window
            repeat with win in winList
                set winName to name of win
                
                -- Buttons
                set btnList to every button of win
                if (count of btnList) > 0 then
                    set output to output & return & "Buttons in " & winName & ":" & return
                    repeat with btn in btnList
                        try
                            set btnDesc to description of btn
                            set btnPos to position of btn
                            set output to output & "  - " & btnDesc & " at (" & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ")" & return
                        end try
                    end repeat
                end if
                
                -- Menu items
                try
                    set menuList to every menu of win
                    repeat with mnu in menuList
                        set menuItems to every menu item of mnu
                        if (count of menuItems) > 0 then
                            set output to output & return & "Menu items:" & return
                            repeat with mi in menuItems
                                try
                                    set miTitle to title of mi
                                    set output to output & "  - " & miTitle & return
                                end try
                            end repeat
                        end if
                    end repeat
                end try
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', clickable_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    print("\n💡 Summary:")
    print("The 'checkboxes' might actually be:")
    print("- Loop/repeat buttons")
    print("- Shuffle button")
    print("- Other playback control buttons")
    print("\nAirPlay devices should appear in a popup menu or list after clicking the AirPlay button")


if __name__ == "__main__":
    analyze_ui_elements()