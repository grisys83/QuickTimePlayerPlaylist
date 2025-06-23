#!/usr/bin/env python3
"""
Test AirPlay toggle correctly
"""

import subprocess
import time


def test_airplay_toggle():
    """Test AirPlay toggle with correct approach"""
    print("\n🎵 Testing AirPlay Toggle for Audio")
    print("=" * 50)
    
    # First, count initial checkboxes
    print("\n1️⃣ Initial state (before clicking AirPlay)...")
    
    before_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            set cbList to every checkbox of window 1
            set cbCount to count of cbList
            
            return "Initial checkboxes: " & (cbCount as string)
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', before_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Click AirPlay button
    print("\n2️⃣ Clicking AirPlay button...")
    
    click_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Find AirPlay button
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
    
    result = subprocess.run(['osascript', '-e', click_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Wait and check multiple times
    print("\n3️⃣ Checking for popup/checkboxes...")
    
    for wait_time in [0.5, 1.0, 1.5, 2.0]:
        time.sleep(wait_time if wait_time == 0.5 else 0.5)
        
        check_script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set output to "After {wait_time}s: "
                
                -- Count windows
                set winCount to count of windows
                set output to output & "Windows=" & (winCount as string)
                
                -- Check window 1
                set cbList to every checkbox of window 1
                set cbCount to count of cbList
                set output to output & ", Window1 CBs=" & (cbCount as string)
                
                -- If there's a second window (popup)
                if winCount > 1 then
                    try
                        set popup to window 2
                        set popupName to name of popup
                        set popupCBs to every checkbox of popup
                        set popupCBCount to count of popupCBs
                        set output to output & ", Popup '" & popupName & "' CBs=" & (popupCBCount as string)
                    end try
                end if
                
                -- Check for any floating window
                repeat with i from 1 to winCount
                    try
                        set win to window i
                        set winName to name of win
                        if winName does not contain "Conversation" then
                            set winCBs to every checkbox of win
                            if (count of winCBs) > 0 then
                                set output to output & ", Found CBs in '" & winName & "'"
                            end if
                        end if
                    end try
                end repeat
                
                return output
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', check_script], 
                              capture_output=True, text=True)
        print(result.stdout.strip())
    
    # Final attempt - look everywhere
    print("\n4️⃣ Final comprehensive search...")
    
    final_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set output to "=== COMPREHENSIVE SEARCH ===" & return
            
            -- All windows
            set winList to every window
            repeat with win in winList
                try
                    set winName to name of win
                    set winCBs to every checkbox of win
                    set cbCount to count of winCBs
                    
                    if cbCount > 0 then
                        set output to output & "Window '" & winName & "' has " & (cbCount as string) & " checkboxes:" & return
                        
                        repeat with i from 1 to cbCount
                            set cb to item i of winCBs
                            set cbPos to position of cb
                            set cbVal to value of cb
                            set output to output & "  CB" & i & " at (" & (item 1 of cbPos as string) & "," & (item 2 of cbPos as string) & ") checked=" & (cbVal as string) & return
                        end repeat
                    end if
                end try
            end repeat
            
            return output
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', final_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Try to find and click Apple TV
    print("\n5️⃣ Attempting to select Apple TV...")
    
    select_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Look for checkboxes in all windows
            set foundAppleTV to false
            set winList to every window
            
            repeat with win in winList
                set cbList to every checkbox of win
                set cbCount to count of cbList
                
                -- If we find 2 or more checkboxes, assume 2nd is Apple TV
                if cbCount >= 2 and not foundAppleTV then
                    set appleTVCB to item 2 of cbList
                    if value of appleTVCB = 0 then
                        click appleTVCB
                        set foundAppleTV to true
                        return "Clicked Apple TV checkbox in " & (name of win)
                    end if
                end if
            end repeat
            
            if not foundAppleTV then
                return "Could not find Apple TV checkbox"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', select_script], 
                          capture_output=True, text=True)
    print(result.stdout.strip())


if __name__ == "__main__":
    test_airplay_toggle()