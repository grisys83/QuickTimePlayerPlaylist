#!/usr/bin/env python3
"""
Test AirPlay with retry logic
"""

import subprocess
import time


def wait_for_quicktime_ready(max_attempts=10):
    """Wait for QuickTime to be ready with an audio file"""
    print("\n⏳ Waiting for QuickTime to be ready...")
    
    for attempt in range(max_attempts):
        check_script = '''
        tell application "System Events"
            if exists process "QuickTime Player" then
                tell process "QuickTime Player"
                    if exists window 1 then
                        set winName to name of window 1
                        set btnCount to count of buttons of window 1
                        
                        -- Check if it's an audio file and has enough buttons
                        if (winName contains ".mp3" or winName contains ".m4a") and btnCount >= 7 then
                            return "ready"
                        else
                            return "not ready: " & btnCount & " buttons"
                        end if
                    else
                        return "no window"
                    end if
                end tell
            else
                return "not running"
            end if
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', check_script], 
                              capture_output=True, text=True)
        
        status = result.stdout.strip()
        print(f"   Attempt {attempt + 1}: {status}")
        
        if status == "ready":
            return True
        
        time.sleep(0.5)
    
    return False


def click_airplay_with_retry():
    """Click AirPlay button with retry logic"""
    print("\n🎯 Clicking AirPlay with retry...")
    
    # First make sure QuickTime is ready
    if not wait_for_quicktime_ready():
        print("❌ QuickTime not ready after waiting")
        return False
    
    # Try to click AirPlay
    for attempt in range(3):
        print(f"\n   Attempt {attempt + 1}...")
        
        click_script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.2
                
                -- Try to find and click AirPlay
                set btnList to every button of window 1
                repeat with btn in btnList
                    try
                        set btnDesc to description of btn
                        if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                            set btnPos to position of btn
                            click btn
                            return "success: " & btnDesc & " at " & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                        end if
                    end try
                end repeat
                
                return "not found"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', click_script], 
                              capture_output=True, text=True)
        
        if "success" in result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ {result.stdout.strip()}")
            time.sleep(1)
    
    return False


def main():
    print("Testing AirPlay with proper timing")
    
    # Make sure QuickTime is playing audio
    print("\n1️⃣ Opening audio file...")
    
    open_script = '''
    tell application "QuickTime Player"
        activate
        -- Close any existing windows
        close every window
        delay 0.5
        
        -- Open a test audio file (you need to adjust the path)
        open POSIX file "/System/Library/Sounds/Glass.aiff"
        delay 1
        
        play front document
    end tell
    '''
    
    subprocess.run(['osascript', '-e', open_script])
    
    # Now try clicking AirPlay
    if click_airplay_with_retry():
        print("\n✅ Successfully clicked AirPlay!")
        
        # Try selecting device
        time.sleep(1.5)
        
        select_script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if (count of windows) > 1 then
                    -- Click second item (living)
                    click button 2 of window 2
                    return "selected"
                else
                    return "no popup"
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', select_script], 
                              capture_output=True, text=True)
        print(f"\nDevice selection: {result.stdout.strip()}")
    else:
        print("\n❌ Failed to click AirPlay")


if __name__ == "__main__":
    main()