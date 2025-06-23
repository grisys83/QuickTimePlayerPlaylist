#!/usr/bin/env python3
"""
Test direct checkbox clicking for audio AirPlay
"""

import subprocess
import time


def test_direct_checkbox():
    """Test clicking checkbox 2 directly"""
    print("\n🎯 Direct Checkbox Click Test")
    print("=" * 40)
    
    # Make sure QuickTime is frontmost
    print("1️⃣ Activating QuickTime...")
    
    activate_script = '''
    tell application "QuickTime Player"
        activate
    end tell
    '''
    subprocess.run(['osascript', '-e', activate_script])
    time.sleep(1)
    
    # Get current state
    print("\n2️⃣ Current checkbox states:")
    
    state_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to ""
            set cbList to every checkbox of window 1
            
            repeat with i from 1 to count of cbList
                set cb to item i of cbList
                set cbValue to value of cb
                set cbPos to position of cb
                set output to output & "Checkbox " & i & " at (" & (item 1 of cbPos as string) & "," & (item 2 of cbPos as string) & ") = " & (cbValue as string) & return
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', state_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Click checkbox 2
    print("\n3️⃣ Clicking checkbox 2 (Apple TV)...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set cbList to every checkbox of window 1
            
            if (count of cbList) >= 2 then
                set targetCB = item 2 of cbList
                set beforeValue = value of targetCB
                
                click targetCB
                
                delay 0.5
                set afterValue to value of targetCB
                
                return "Clicked CB2: " & (beforeValue as string) & " -> " & (afterValue as string)
            else
                return "Not enough checkboxes"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', click_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Click AirPlay button
    print("\n4️⃣ Clicking AirPlay button...")
    
    airplay_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    set btnDesc to description of btn
                    if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                        set btnPos to position of btn
                        click btn
                        return "Clicked AirPlay button at (" & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ")"
                    end if
                end try
            end repeat
            return "AirPlay button not found"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', airplay_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Final state
    print("\n5️⃣ Final checkbox states:")
    
    result = subprocess.run(['osascript', '-e', state_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    print("\n✅ Test complete!")
    print("\n💡 If checkbox 2 didn't change:")
    print("   - Check if QuickTime has an audio file loaded")
    print("   - Try clicking checkbox 1 or 3 instead")
    print("   - Make sure accessibility permissions are granted")


if __name__ == "__main__":
    test_direct_checkbox()