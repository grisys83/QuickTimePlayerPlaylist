#!/usr/bin/env python3
"""
Analyze AirPlay popup window in detail
"""

import subprocess
import time


def analyze_airplay_popup():
    """Analyze AirPlay popup window"""
    print("\n🔍 Analyzing AirPlay Popup")
    print("=" * 40)
    
    # Activate and click AirPlay
    print("1️⃣ Opening AirPlay popup...")
    
    open_popup_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            click button "외장 재생 메뉴 보기" of window 1
            delay 1.0
            return "Popup opened"
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', open_popup_script], capture_output=True)
    
    # Analyze popup structure
    print("\n2️⃣ Analyzing popup structure...")
    
    analyze_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== POPUP ANALYSIS ===" & return
            set winCount to count of windows
            set output to output & "Total windows: " & (winCount as string) & return & return
            
            if winCount > 1 then
                set popup to window 2
                set popupName to name of popup
                set popupRole to role of popup
                set popupPos to position of popup
                set popupSize to size of popup
                
                set output to output & "Popup window:" & return
                set output to output & "  Name: " & popupName & return
                set output to output & "  Role: " & popupRole & return
                set output to output & "  Position: (" & (item 1 of popupPos as string) & "," & (item 2 of popupPos as string) & ")" & return
                set output to output & "  Size: " & (item 1 of popupSize as string) & "x" & (item 2 of popupSize as string) & return & return
                
                -- Get all UI elements
                set allElements to every UI element of popup
                set elemCount to count of allElements
                set output to output & "UI Elements (" & (elemCount as string) & "):" & return
                
                repeat with i from 1 to elemCount
                    set elem to item i of allElements
                    set elemClass to class of elem as string
                    set elemPos to position of elem
                    set output to output & i & ". " & elemClass & " at (" & (item 1 of elemPos as string) & "," & (item 2 of elemPos as string) & ")"
                    
                    -- Get more details
                    if elemClass contains "button" then
                        try
                            set btnTitle to title of elem
                            set btnDesc to description of elem
                            if btnTitle is not missing value then
                                set output to output & " title='" & btnTitle & "'"
                            end if
                            if btnDesc is not missing value then
                                set output to output & " desc='" & btnDesc & "'"
                            end if
                        end try
                    else if elemClass contains "static text" then
                        try
                            set txtValue to value of elem
                            set output to output & " text='" & txtValue & "'"
                        end try
                    else if elemClass contains "checkbox" then
                        try
                            set cbValue to value of elem
                            set cbTitle to title of elem
                            set output to output & " checked=" & (cbValue as string)
                            if cbTitle is not missing value then
                                set output to output & " title='" & cbTitle & "'"
                            end if
                        end try
                    else if elemClass contains "radio" then
                        try
                            set radioValue to value of elem
                            set radioTitle to title of elem
                            set output to output & " selected=" & (radioValue as string)
                            if radioTitle is not missing value then
                                set output to output & " title='" & radioTitle & "'"
                            end if
                        end try
                    end if
                    
                    set output to output & return
                end repeat
                
                -- Check for specific container types
                set output to output & return & "Looking for containers:" & return
                
                -- Radio groups
                try
                    set radioGroups to every radio group of popup
                    set rgCount to count of radioGroups
                    if rgCount > 0 then
                        set output to output & "Found " & (rgCount as string) & " radio groups!" & return
                        repeat with rg in radioGroups
                            set radioButtons to every radio button of rg
                            set rbCount to count of radioButtons
                            set output to output & "  Radio group with " & (rbCount as string) & " buttons:" & return
                            repeat with rb in radioButtons
                                try
                                    set rbTitle to title of rb
                                    set rbValue to value of rb
                                    set output to output & "    - " & rbTitle & " (selected=" & (rbValue as string) & ")" & return
                                end try
                            end repeat
                        end repeat
                    end if
                end try
                
                -- Lists
                try
                    set lists to every list of popup
                    if (count of lists) > 0 then
                        set output to output & "Found lists!" & return
                    end if
                end try
            else
                set output to output & "No popup window found" & return
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', analyze_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Try to click Apple TV
    print("\n3️⃣ Attempting to select Apple TV...")
    
    select_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set popup to window 2
                
                -- Method 1: Look for radio buttons
                try
                    set radioGroups to every radio group of popup
                    if (count of radioGroups) > 0 then
                        set rg to item 1 of radioGroups
                        set radioButtons to every radio button of rg
                        
                        -- Usually Apple TV is the second option
                        if (count of radioButtons) >= 2 then
                            set appleTVButton to item 2 of radioButtons
                            click appleTVButton
                            return "Clicked Apple TV radio button"
                        end if
                    end if
                end try
                
                -- Method 2: Look for any clickable element with "TV" in name
                set allElements to every UI element of popup
                repeat with elem in allElements
                    try
                        set elemTitle to title of elem
                        if elemTitle contains "TV" or elemTitle contains "Apple" then
                            click elem
                            return "Clicked element: " & elemTitle
                        end if
                    end try
                end repeat
                
                -- Method 3: Click second button
                set btnList to every button of popup
                if (count of btnList) >= 2 then
                    click item 2 of btnList
                    return "Clicked second button"
                end if
                
                return "Could not find Apple TV option"
            else
                return "No popup window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', select_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())


if __name__ == "__main__":
    analyze_airplay_popup()