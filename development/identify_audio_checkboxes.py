#!/usr/bin/env python3
"""
Identify all checkboxes in audio player
"""

import subprocess
import time


def identify_checkboxes():
    """Identify what each checkbox does"""
    print("\n🔍 Identifying Audio Player Checkboxes")
    print("=" * 50)
    
    # Get initial state
    print("\n1️⃣ Getting initial checkbox states...")
    
    initial_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            set output to "=== INITIAL STATE ===" & return
            set cbList to every checkbox of window 1
            
            repeat with i from 1 to count of cbList
                set cb to item i of cbList
                set cbPos to position of cb
                set cbValue to value of cb
                set cbEnabled to enabled of cb
                
                set output to output & "Checkbox " & i & ":" & return
                set output to output & "  Position: (" & (item 1 of cbPos as string) & ", " & (item 2 of cbPos as string) & ")" & return
                set output to output & "  Checked: " & (cbValue as string) & return
                set output to output & "  Enabled: " & (cbEnabled as string) & return
                
                -- Get size
                try
                    set cbSize to size of cb
                    set output to output & "  Size: " & (item 1 of cbSize as string) & "x" & (item 2 of cbSize as string) & return
                end try
                
                set output to output & return
            end repeat
            
            -- Also check button positions
            set output to output & "=== BUTTONS ===" & return
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    set btnDesc to description of btn
                    set btnPos to position of btn
                    if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                        set output to output & "AirPlay button at: (" & (item 1 of btnPos as string) & ", " & (item 2 of btnPos as string) & ")" & return
                    end if
                end try
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', initial_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Test clicking each checkbox
    print("\n2️⃣ Testing each checkbox...")
    
    for i in range(1, 4):  # Test checkboxes 1, 2, 3
        print(f"\n--- Testing Checkbox {i} ---")
        
        test_script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set cbList to every checkbox of window 1
                if (count of cbList) >= {i} then
                    set targetCB to item {i} of cbList
                    set beforeValue to value of targetCB
                    
                    click targetCB
                    delay 0.5
                    
                    set afterValue to value of targetCB
                    
                    return "Checkbox {i}: was " & (beforeValue as string) & ", now " & (afterValue as string)
                else
                    return "Checkbox {i} not found"
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', test_script], 
                              capture_output=True, text=True)
        print(result.stdout.strip())
        time.sleep(1)
    
    # Check if AirPlay button behavior changed
    print("\n3️⃣ Checking AirPlay button behavior...")
    
    airplay_test = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Click AirPlay button
            set airplayButton to first button of window 1 whose description contains "외장"
            click airplayButton
            delay 1
            
            -- Count windows and checkboxes
            set winCount to count of windows
            set cbCount to count of checkboxes of window 1
            
            return "After AirPlay click: Windows=" & (winCount as string) & ", Checkboxes=" & (cbCount as string)
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', airplay_test], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    print("\n💡 Summary:")
    print("- The audio player seems to have permanent checkboxes")
    print("- Checkbox positions suggest they might be:")
    print("  1. @ (61,100) - Possibly loop/repeat?")
    print("  2. @ (345,100) - Possibly shuffle or AirPlay device?")
    print("  3. @ (209,131) - Possibly another playback option?")


if __name__ == "__main__":
    identify_checkboxes()