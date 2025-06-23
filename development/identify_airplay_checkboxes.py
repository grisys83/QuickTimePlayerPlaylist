#!/usr/bin/env python3
"""
Identify what each checkbox represents in AirPlay popup
"""

import subprocess
import time
import pyautogui


def identify_checkboxes():
    """Identify AirPlay checkboxes by hovering over them"""
    print("\n🔍 Identifying AirPlay Checkboxes")
    print("=" * 50)
    
    # First click AirPlay button
    print("\n1️⃣ Opening AirPlay menu...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- Find and click AirPlay button
            set airplayButton to first button of window 1 whose description contains "외장"
            set btnPos to position of airplayButton
            click airplayButton
            
            return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', click_script], 
                          capture_output=True, text=True)
    airplay_pos = result.stdout.strip().split(',')
    print(f"✅ AirPlay button clicked at ({airplay_pos[0]}, {airplay_pos[1]})")
    
    time.sleep(2)
    
    # Get checkbox positions and help tags
    print("\n2️⃣ Getting checkbox information...")
    
    checkbox_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== CHECKBOX DETAILS ===" & return
            
            -- Get all checkboxes
            set cbList to every checkbox of window 1
            set cbCount to count of cbList
            
            repeat with i from 1 to cbCount
                set cb to item i of cbList
                set cbPos to position of cb
                set cbValue to value of cb
                set cbEnabled to enabled of cb
                
                set output to output & "Checkbox " & i & ":" & return
                set output to output & "  Position: (" & (item 1 of cbPos as string) & ", " & (item 2 of cbPos as string) & ")" & return
                set output to output & "  Checked: " & (cbValue as string) & return
                set output to output & "  Enabled: " & (cbEnabled as string) & return
                
                -- Try to get help or description
                try
                    set cbHelp to help of cb
                    set output to output & "  Help: " & cbHelp & return
                end try
                
                try
                    set cbDesc to description of cb
                    set output to output & "  Description: " & cbDesc & return
                end try
                
                try
                    set cbTitle to title of cb
                    if cbTitle is not "" then
                        set output to output & "  Title: " & cbTitle & return
                    end if
                end try
                
                -- Check for nearby text
                set nearbyText to ""
                set allTexts to every static text of window 1
                repeat with txt in allTexts
                    try
                        set txtValue to value of txt
                        set txtPos to position of txt
                        set txtX to item 1 of txtPos
                        set txtY to item 2 of txtPos
                        set cbX to item 1 of cbPos
                        set cbY to item 2 of cbPos
                        
                        -- Check if text is near this checkbox (within 100 pixels)
                        if (txtX - cbX) * (txtX - cbX) + (txtY - cbY) * (txtY - cbY) < 10000 then
                            set nearbyText to nearbyText & " '" & txtValue & "'"
                        end if
                    end try
                end repeat
                
                if nearbyText is not "" then
                    set output to output & "  Nearby text:" & nearbyText & return
                end if
                
                set output to output & return
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', checkbox_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Take a screenshot for visual reference
    print("\n3️⃣ Taking screenshot of AirPlay popup...")
    screenshot = pyautogui.screenshot()
    screenshot.save('airplay_popup_screenshot.png')
    print("✅ Screenshot saved as 'airplay_popup_screenshot.png'")
    
    # Try clicking checkboxes based on typical positions
    print("\n4️⃣ Testing checkbox interactions...")
    
    test_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set cbList to every checkbox of window 1
            
            -- Typically:
            -- Checkbox 1: This Computer (이 컴퓨터)
            -- Checkbox 2: Apple TV or other AirPlay device
            -- Checkbox 3: Another device if available
            
            if (count of cbList) >= 2 then
                -- Click the second checkbox (usually Apple TV)
                set appleTVCheckbox to item 2 of cbList
                set wasChecked to value of appleTVCheckbox
                
                click appleTVCheckbox
                delay 0.5
                
                set isChecked to value of appleTVCheckbox
                
                if wasChecked = 0 and isChecked = 1 then
                    return "Successfully checked Apple TV (checkbox 2)"
                else if wasChecked = 1 and isChecked = 0 then
                    return "Unchecked Apple TV (checkbox 2) - was already selected"
                else
                    return "Checkbox 2 state: was " & (wasChecked as string) & ", now " & (isChecked as string)
                end if
            else
                return "Not enough checkboxes found"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', test_script], 
                          capture_output=True, text=True)
    print(f"\n✅ Result: {result.stdout.strip()}")
    
    print("\n💡 Typical checkbox order in AirPlay popup:")
    print("  1. This Computer (이 컴퓨터)")
    print("  2. Apple TV or first AirPlay device")
    print("  3. Additional AirPlay devices (if any)")


if __name__ == "__main__":
    identify_checkboxes()