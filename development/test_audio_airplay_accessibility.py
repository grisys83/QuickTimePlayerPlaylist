#!/usr/bin/env python3
"""
Test Audio AirPlay Accessibility - Debug version
"""

import subprocess
import time
import json
from pathlib import Path


def test_accessibility_airplay():
    """Test AirPlay activation with detailed debug output"""
    print("\n🧪 Testing Audio AirPlay with Accessibility API")
    print("=" * 50)
    
    # First, let's see what UI elements we can find
    print("\n1️⃣ Enumerating all QuickTime UI elements...")
    
    enum_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            set output to "=== WINDOW INFO ===" & return
            if exists window 1 then
                set winName to name of window 1
                set winPos to position of window 1
                set winSize to size of window 1
                set output to output & "Window: " & winName & return
                set output to output & "Position: " & (item 1 of winPos as string) & "," & (item 2 of winPos as string) & return
                set output to output & "Size: " & (item 1 of winSize as string) & "," & (item 2 of winSize as string) & return
            end if
            
            set output to output & return & "=== BUTTONS ===" & return
            set buttonList to every button of window 1
            set buttonCount to count of buttonList
            set output to output & "Total buttons: " & (buttonCount as string) & return
            
            repeat with i from 1 to buttonCount
                set btn to item i of buttonList
                try
                    set btnDesc to description of btn
                    set btnPos to position of btn
                    set btnEnabled to enabled of btn
                    set output to output & "Button " & i & ": " & btnDesc & " at (" & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ") enabled=" & (btnEnabled as string) & return
                on error
                    set output to output & "Button " & i & ": (error reading properties)" & return
                end try
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', enum_script], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    # Now try to click AirPlay
    print("\n2️⃣ Attempting to click AirPlay button...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- Debug: Count buttons
            set buttonList to every button of window 1
            set buttonCount to count of buttonList
            set output to "Found " & (buttonCount as string) & " buttons" & return
            
            -- Try different methods to find AirPlay
            set airplayButton to missing value
            
            -- Method 1: By description (Korean)
            try
                set airplayButton to first button of window 1 whose description contains "외장"
                set output to output & "Found by Korean description" & return
            end try
            
            -- Method 2: By description (English)
            if airplayButton is missing value then
                try
                    set airplayButton to first button of window 1 whose description contains "AirPlay"
                    set output to output & "Found by English description" & return
                end try
            end if
            
            -- Method 3: By position (last button)
            if airplayButton is missing value and buttonCount > 0 then
                set airplayButton to item buttonCount of buttonList
                set output to output & "Using last button as AirPlay" & return
            end if
            
            if airplayButton is not missing value then
                set btnDesc to description of airplayButton
                set btnPos to position of airplayButton
                set output to output & "Clicking: " & btnDesc & " at (" & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ")" & return
                
                click airplayButton
                set output to output & "Click sent!" & return
            else
                set output to output & "ERROR: Could not find AirPlay button" & return
            end if
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', click_script], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    # Wait for popup
    print("\n⏳ Waiting 2 seconds for popup...")
    time.sleep(2)
    
    # Try to find Apple TV in popup
    print("\n3️⃣ Looking for Apple TV option...")
    
    popup_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== POPUP SEARCH ===" & return
            
            -- Method 1: Look for menu
            try
                if exists menu 1 of group 1 of window 1 then
                    set airplayMenu to menu 1 of group 1 of window 1
                    set menuItems to every menu item of airplayMenu
                    set menuCount to count of menuItems
                    set output to output & "Found menu with " & (menuCount as string) & " items:" & return
                    
                    repeat with i from 1 to menuCount
                        set mi to item i of menuItems
                        try
                            set miTitle to title of mi
                            set output to output & "  Item " & i & ": " & miTitle & return
                        end try
                    end repeat
                else
                    set output to output & "No menu found in group 1" & return
                end if
            on error errMsg
                set output to output & "Menu error: " & errMsg & return
            end try
            
            -- Method 2: Look for floating window
            set output to output & return & "=== ALL WINDOWS ===" & return
            set allWindows to every window
            set winCount to count of allWindows
            set output to output & "Total windows: " & (winCount as string) & return
            
            repeat with i from 1 to winCount
                try
                    set win to item i of allWindows
                    set winName to name of win
                    set output to output & "Window " & i & ": " & winName & return
                    
                    -- Check for UI elements in this window
                    try
                        set uiElements to every UI element of win
                        set output to output & "  UI elements: " & (count of uiElements as string) & return
                    end try
                end try
            end repeat
            
            -- Method 3: Look for checkboxes anywhere
            set output to output & return & "=== CHECKBOXES ===" & return
            try
                set allCheckboxes to every checkbox of window 1
                set cbCount to count of allCheckboxes
                set output to output & "Found " & (cbCount as string) & " checkboxes:" & return
                
                repeat with i from 1 to cbCount
                    set cb to item i of allCheckboxes
                    try
                        set cbTitle to title of cb
                        set cbValue to value of cb
                        set output to output & "  Checkbox " & i & ": " & cbTitle & " (checked=" & (cbValue as string) & ")" & return
                    end try
                end repeat
            end try
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', popup_script], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    # Try to click Apple TV
    print("\n4️⃣ Attempting to select Apple TV...")
    
    select_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== SELECTING APPLE TV ===" & return
            
            -- First try menu items
            try
                if exists menu 1 of group 1 of window 1 then
                    set airplayMenu to menu 1 of group 1 of window 1
                    set menuItems to every menu item of airplayMenu
                    
                    -- Try to click item 2 (usually Apple TV)
                    if (count of menuItems) > 1 then
                        set targetItem to item 2 of menuItems
                        click targetItem
                        set output to output & "Clicked menu item 2" & return
                        return output
                    end if
                end if
            end try
            
            -- Try checkboxes
            try
                set allCheckboxes to every checkbox of window 1
                repeat with cb in allCheckboxes
                    set cbTitle to title of cb
                    if cbTitle contains "TV" or cbTitle contains "Apple" then
                        click cb
                        set output to output & "Clicked checkbox: " & cbTitle & return
                        return output
                    end if
                end repeat
            end try
            
            set output to output & "Could not find Apple TV option" & return
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', select_script], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    print("\n✅ Test complete!")
    print("\nNote: If AirPlay button was not found, make sure:")
    print("1. QuickTime Player is open with an audio file")
    print("2. The audio player window is visible")
    print("3. You have granted accessibility permissions")


if __name__ == "__main__":
    test_accessibility_airplay()