#!/usr/bin/env python3
"""
Debug AirPlay popup timing and structure
"""

import subprocess
import time


def debug_airplay_popup():
    """Debug AirPlay popup with various timings"""
    print("\n🔍 Debugging AirPlay Popup Timing")
    print("=" * 50)
    
    # Click AirPlay button
    print("\n1️⃣ Clicking AirPlay button...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            set airplayButton to first button of window 1 whose description contains "외장"
            click airplayButton
            
            return "Clicked"
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', click_script], capture_output=True)
    
    # Check for checkboxes at different intervals
    for delay_time in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        print(f"\n⏱️  Checking after {delay_time} seconds...")
        time.sleep(delay_time if delay_time == 0.5 else 0.5)
        
        check_script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set output to "=== After {delay_time}s ===" & return
                
                -- Count windows
                set winCount to count of windows
                set output to output & "Windows: " & (winCount as string) & return
                
                -- Check main window
                set cbList to every checkbox of window 1
                set cbCount to count of cbList
                set output to output & "Checkboxes in window 1: " & (cbCount as string) & return
                
                -- Check if there's a popup window
                if winCount > 1 then
                    repeat with i from 2 to winCount
                        try
                            set popupCBs to every checkbox of window i
                            set popupCBCount to count of popupCBs
                            set output to output & "Checkboxes in window " & i & ": " & (popupCBCount as string) & return
                        end try
                    end repeat
                end if
                
                -- Check for sheets
                try
                    set sheetList to every sheet of window 1
                    set sheetCount to count of sheetList
                    set output to output & "Sheets: " & (sheetCount as string) & return
                    
                    if sheetCount > 0 then
                        set sheetCBs to every checkbox of sheet 1 of window 1
                        set output to output & "Checkboxes in sheet: " & (count of sheetCBs as string) & return
                    end if
                end try
                
                -- Check for groups
                set groupList to every group of window 1
                set groupCount to count of groupList
                set output to output & "Groups: " & (groupCount as string) & return
                
                repeat with i from 1 to groupCount
                    try
                        set grp to item i of groupList
                        set grpCBs to every checkbox of grp
                        if (count of grpCBs) > 0 then
                            set output to output & "  Group " & i & " has " & (count of grpCBs as string) & " checkboxes" & return
                        end if
                    end try
                end repeat
                
                -- List all UI elements
                set output to output & return & "All UI elements:" & return
                set allElements to every UI element of window 1
                repeat with elem in allElements
                    set elemClass to class of elem as string
                    set output to output & "  - " & elemClass & return
                end repeat
                
                return output
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', check_script], 
                              capture_output=True, text=True)
        print(result.stdout)
    
    # Now try to find and click Apple TV
    print("\n2️⃣ Attempting to find Apple TV option...")
    
    find_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== FINDING APPLE TV ===" & return
            
            -- Method 1: Direct checkbox search
            set cbList to every checkbox of window 1
            set cbCount to count of cbList
            set output to output & "Method 1 - Direct checkboxes: " & (cbCount as string) & return
            
            if cbCount >= 2 then
                set cb2 to item 2 of cbList
                set cb2Pos to position of cb2
                set output to output & "  Checkbox 2 position: " & (item 1 of cb2Pos as string) & "," & (item 2 of cb2Pos as string) & return
                click cb2
                set output to output & "  Clicked checkbox 2!" & return
            end if
            
            -- Method 2: Search in groups
            set groupList to every group of window 1
            repeat with grp in groupList
                set grpCBs to every checkbox of grp
                if (count of grpCBs) >= 2 then
                    set output to output & "Method 2 - Found checkboxes in group" & return
                    set cb to item 2 of grpCBs
                    click cb
                    set output to output & "  Clicked group checkbox 2!" & return
                    exit repeat
                end if
            end repeat
            
            -- Method 3: Search all UI elements for checkboxes
            set allElements to every UI element of window 1
            set foundCheckboxes to {}
            repeat with elem in allElements
                if class of elem is checkbox then
                    set end of foundCheckboxes to elem
                end if
            end repeat
            
            set output to output & "Method 3 - UI element search found: " & (count of foundCheckboxes as string) & " checkboxes" & return
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', find_script], 
                          capture_output=True, text=True)
    print(result.stdout)


if __name__ == "__main__":
    debug_airplay_popup()