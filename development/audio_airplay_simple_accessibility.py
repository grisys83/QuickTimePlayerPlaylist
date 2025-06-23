#!/usr/bin/env python3
"""
Simple Audio AirPlay Automation using Accessibility API
"""

import subprocess
import time


def enable_airplay_for_audio():
    """Enable AirPlay for audio playback - simple and reliable"""
    print("\n🎵 Enabling AirPlay for Audio")
    print("=" * 40)
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- Step 1: Find and click AirPlay button
            set airplayButton to missing value
            set buttonList to every button of window 1
            
            -- Try Korean description first
            repeat with btn in buttonList
                try
                    if description of btn contains "외장" then
                        set airplayButton to btn
                        exit repeat
                    end if
                end try
            end repeat
            
            -- If not found, try English
            if airplayButton is missing value then
                repeat with btn in buttonList
                    try
                        if description of btn contains "AirPlay" then
                            set airplayButton to btn
                            exit repeat
                        end if
                    end try
                end repeat
            end if
            
            if airplayButton is not missing value then
                click airplayButton
                delay 1.5
                
                -- Step 2: Select Apple TV checkbox
                set cbList to every checkbox of window 1
                set cbCount to count of cbList
                
                if cbCount >= 2 then
                    -- Usually checkbox 1 is "This Computer" and checkbox 2 is "Apple TV"
                    -- But let's check if checkbox 2 is already selected
                    set appleTVCheckbox to item 2 of cbList
                    set isChecked to value of appleTVCheckbox
                    
                    if isChecked = 0 then
                        -- Not checked, so check it
                        click appleTVCheckbox
                        return "SUCCESS: Apple TV selected"
                    else
                        -- Already checked
                        return "SUCCESS: Apple TV was already selected"
                    end if
                else if cbCount = 1 then
                    -- Only one checkbox, probably Apple TV
                    set cb to item 1 of cbList
                    if value of cb = 0 then
                        click cb
                    end if
                    return "SUCCESS: Selected the only available device"
                else
                    return "ERROR: No checkboxes found"
                end if
            else
                return "ERROR: AirPlay button not found"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    print(f"\n📺 Result: {result.stdout.strip()}")
    return result.stdout.strip().startswith("SUCCESS")


def test_airplay():
    """Test AirPlay automation"""
    print("Testing Audio AirPlay Automation")
    
    # Make sure QuickTime is open with audio
    input("\nMake sure QuickTime is open with an audio file. Press Enter to continue...")
    
    # Enable AirPlay
    success = enable_airplay_for_audio()
    
    if success:
        print("\n✅ AirPlay enabled successfully!")
    else:
        print("\n❌ Failed to enable AirPlay")


if __name__ == "__main__":
    test_airplay()