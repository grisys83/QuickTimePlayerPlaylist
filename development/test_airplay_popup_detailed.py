#!/usr/bin/env python3
"""
Detailed test for AirPlay popup structure
"""

import subprocess
import time


def test_airplay_popup():
    """Test AirPlay popup with more detailed inspection"""
    print("\n🔍 Detailed AirPlay Popup Test")
    print("=" * 50)
    
    # Click AirPlay button
    print("\n1️⃣ Clicking AirPlay button...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- Find and click AirPlay button
            set airplayButton to first button of window 1 whose description contains "외장"
            click airplayButton
            
            return "Clicked AirPlay button"
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', click_script], capture_output=True)
    print("✅ AirPlay button clicked")
    
    # Wait for popup
    print("\n⏳ Waiting for popup...")
    time.sleep(2)
    
    # Detailed inspection
    print("\n2️⃣ Inspecting all UI elements...")
    
    inspect_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== ALL UI ELEMENTS ===" & return
            
            -- Check every UI element of window 1
            set allElements to every UI element of window 1
            set elemCount to count of allElements
            set output to output & "Total UI elements in window 1: " & (elemCount as string) & return & return
            
            repeat with i from 1 to elemCount
                set elem to item i of allElements
                set elemClass to class of elem as string
                set output to output & "Element " & i & ": " & elemClass
                
                -- Get more details based on type
                if elemClass contains "group" then
                    set groupElements to every UI element of elem
                    set groupCount to count of groupElements
                    set output to output & " (contains " & (groupCount as string) & " elements)"
                    
                    -- Check for menus in groups
                    try
                        set menuList to every menu of elem
                        if (count of menuList) > 0 then
                            set output to output & " [HAS MENU!]"
                        end if
                    end try
                else if elemClass contains "checkbox" then
                    try
                        set cbTitle to title of elem
                        set cbValue to value of elem
                        set cbPos to position of elem
                        set output to output & " '" & cbTitle & "' at (" & (item 1 of cbPos as string) & "," & (item 2 of cbPos as string) & ") checked=" & (cbValue as string)
                    end try
                else if elemClass contains "static text" then
                    try
                        set txtValue to value of elem
                        set output to output & " '" & txtValue & "'"
                    end try
                end if
                
                set output to output & return
            end repeat
            
            -- Check for popup or sheet
            set output to output & return & "=== SHEETS/POPUPS ===" & return
            try
                set sheetList to every sheet of window 1
                set sheetCount to count of sheetList
                set output to output & "Sheets: " & (sheetCount as string) & return
            end try
            
            -- Check all windows
            set output to output & return & "=== ALL WINDOWS ===" & return
            set allWindows to every window
            repeat with win in allWindows
                try
                    set winName to name of win
                    set winRole to role of win
                    set winSubrole to subrole of win
                    set output to output & "Window: " & winName & " (role=" & winRole & ", subrole=" & winSubrole & ")" & return
                end try
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', inspect_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Try to interact with checkboxes
    print("\n3️⃣ Trying to interact with checkboxes...")
    
    checkbox_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== CHECKBOX INTERACTION ===" & return
            
            -- Get all checkboxes
            set cbList to every checkbox of window 1
            set cbCount to count of cbList
            set output to output & "Found " & (cbCount as string) & " checkboxes" & return
            
            -- Try to click the second checkbox (usually Apple TV)
            if cbCount >= 2 then
                set targetCB to item 2 of cbList
                set cbPos to position of targetCB
                set output to output & "Clicking checkbox 2 at (" & (item 1 of cbPos as string) & "," & (item 2 of cbPos as string) & ")" & return
                
                click targetCB
                set output to output & "Clicked!" & return
            else
                set output to output & "Not enough checkboxes found" & return
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', checkbox_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_airplay_popup()