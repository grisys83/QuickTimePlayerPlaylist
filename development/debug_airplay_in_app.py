#!/usr/bin/env python3
"""
Debug why AirPlay button is not found in SimpleAudioPlaylist
"""

import subprocess
import time


def debug_airplay_button():
    """Debug AirPlay button detection"""
    print("\n🔍 Debugging AirPlay Button Detection")
    print("=" * 40)
    
    # Step 1: Check if QuickTime is running and has windows
    print("\n1️⃣ Checking QuickTime status...")
    
    check_qt_script = '''
    tell application "System Events"
        set qtRunning to exists process "QuickTime Player"
        if qtRunning then
            tell process "QuickTime Player"
                set winCount to count of windows
                set output to "QuickTime is running with " & (winCount as string) & " windows" & return
                
                if winCount > 0 then
                    set winName to name of window 1
                    set winPos to position of window 1
                    set output to output & "Window 1: " & winName & " at (" & ¬
                        (item 1 of winPos as string) & "," & (item 2 of winPos as string) & ")" & return
                    
                    -- Check for audio file
                    if winName contains ".mp3" or winName contains ".m4a" or winName contains ".aac" then
                        set output to output & "Audio file detected!" & return
                    else
                        set output to output & "WARNING: May not be an audio file" & return
                    end if
                end if
                
                return output
            end tell
        else
            return "QuickTime is NOT running"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', check_qt_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Step 2: List all buttons
    print("\n2️⃣ Listing all buttons in QuickTime...")
    
    list_buttons_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            if exists window 1 then
                set btnList to every button of window 1
                set btnCount to count of btnList
                set output to "Found " & (btnCount as string) & " buttons:" & return
                
                repeat with i from 1 to btnCount
                    set btn to item i of btnList
                    try
                        set btnDesc to description of btn
                        set btnPos to position of btn
                        set output to output & i & ". " & btnDesc & " at (" & ¬
                            (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ")" & return
                    on error
                        set output to output & i & ". (unknown button)" & return
                    end try
                end repeat
                
                return output
            else
                return "No windows found"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', list_buttons_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Step 3: Try different methods to find AirPlay
    print("\n3️⃣ Testing different methods to find AirPlay...")
    
    # Method A: By Korean description
    test_korean = '''
    tell application "System Events"
        tell process "QuickTime Player"
            try
                set btn to button "외장 재생 메뉴 보기" of window 1
                return "Method A: Found by Korean name"
            on error
                return "Method A: Not found by Korean name"
            end try
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', test_korean], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Method B: By partial description
    test_partial = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set found to false
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    if description of btn contains "외장" then
                        set found to true
                        exit repeat
                    end if
                end try
            end repeat
            
            if found then
                return "Method B: Found by partial Korean text '외장'"
            else
                return "Method B: Not found by partial text"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', test_partial], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Method C: By English
    test_english = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set found to false
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    set btnDesc to description of btn
                    if btnDesc contains "AirPlay" or btnDesc contains "airplay" then
                        set found to true
                        exit repeat
                    end if
                end try
            end repeat
            
            if found then
                return "Method C: Found by English 'AirPlay'"
            else
                return "Method C: Not found by English"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', test_english], 
                          capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Step 4: Check UI element hierarchy
    print("\n4️⃣ Checking UI hierarchy...")
    
    hierarchy_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if exists window 1 then
                -- Check if buttons are in a toolbar or group
                set groupList to every group of window 1
                set output to "Groups: " & (count of groupList as string) & return
                
                repeat with grp in groupList
                    set grpButtons to buttons of grp
                    if (count of grpButtons) > 0 then
                        set output to output & "Found " & (count of grpButtons as string) & " buttons in a group" & return
                    end if
                end repeat
                
                -- Check toolbar
                if exists toolbar 1 of window 1 then
                    set output to output & "Toolbar exists!" & return
                end if
                
                return output
            else
                return "No window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', hierarchy_script], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    print("\n💡 Possible issues:")
    print("1. QuickTime window might not be frontmost")
    print("2. Audio file might not be loaded yet")
    print("3. UI elements might be in different language")
    print("4. Timing issue - window not ready")


if __name__ == "__main__":
    debug_airplay_button()