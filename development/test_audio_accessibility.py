#!/usr/bin/env python3
"""
Test Audio AirPlay Accessibility Detection Non-Interactively
"""

import subprocess
import time
import json
from pathlib import Path


def check_accessibility_permission():
    """Check if we have accessibility permissions"""
    script = '''
    tell application "System Events"
        set isEnabled to UI elements enabled
        return isEnabled
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    return result.stdout.strip() == "true"


def test_quicktime_ui_detection():
    """Test if we can detect QuickTime UI elements"""
    print("\n♿ Testing Audio AirPlay Accessibility Detection")
    print("=" * 50)
    
    # Check permissions
    print("\n1️⃣ Checking accessibility permissions...")
    if not check_accessibility_permission():
        print("❌ Accessibility permission NOT granted!")
        print("\nTo grant permission:")
        print("1. Open System Preferences > Security & Privacy > Privacy")
        print("2. Click on 'Accessibility' in the left panel")
        print("3. Add Terminal (or your Python app) to the list")
        print("4. Make sure the checkbox is checked")
        return False
    
    print("✅ Accessibility permissions granted")
    
    # Test basic UI detection
    print("\n2️⃣ Testing QuickTime UI detection...")
    
    script = '''
    tell application "System Events"
        if not (exists process "QuickTime Player") then
            return "QuickTime not running"
        end if
        
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- Get window count
            set winCount to count of windows
            
            if winCount is 0 then
                return "No QuickTime windows open"
            end if
            
            -- Get window info
            tell window 1
                set winTitle to title
                set winPos to position
                set winSize to size
                
                -- Count UI elements
                set buttonCount to count of buttons
                set groupCount to count of groups
                
                return "Window: " & winTitle & " | Position: " & (item 1 of winPos as string) & "," & (item 2 of winPos as string) & " | Buttons: " & buttonCount & " | Groups: " & groupCount
            end tell
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    print(f"Result: {result.stdout.strip()}")
    
    if "not running" in result.stdout:
        print("\n❌ QuickTime is not running")
        return False
    
    if "No QuickTime windows" in result.stdout:
        print("\n❌ No QuickTime windows are open")
        print("Please open an audio file in QuickTime first")
        return False
    
    # Detailed UI element scan
    print("\n3️⃣ Scanning for UI elements...")
    
    detailed_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            tell window 1
                set elementList to {}
                
                -- Get all buttons with details
                set allButtons to every button
                repeat with btn in allButtons
                    try
                        set btnDesc to description of btn
                        set btnTitle to title of btn
                        set btnEnabled to enabled of btn
                        set btnPos to position of btn
                        
                        set elementInfo to "Button: " & btnTitle & " | Desc: " & btnDesc & " | Enabled: " & btnEnabled & " | Pos: " & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                        set end of elementList to elementInfo
                    on error
                        set end of elementList to "Button: (unnamed)"
                    end try
                end repeat
                
                -- Check groups and their buttons
                set allGroups to every group
                set groupIndex to 1
                repeat with grp in allGroups
                    try
                        set grpButtons to every button of grp
                        repeat with btn in grpButtons
                            try
                                set btnDesc to description of btn
                                set btnTitle to title of btn
                                set btnPos to position of btn
                                
                                set elementInfo to "Group " & groupIndex & " Button: " & btnTitle & " | Desc: " & btnDesc & " | Pos: " & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                                set end of elementList to elementInfo
                            on error
                                set end of elementList to "Group " & groupIndex & " Button: (unnamed)"
                            end try
                        end repeat
                    end try
                    set groupIndex to groupIndex + 1
                end repeat
                
                return elementList
            end tell
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', detailed_script], 
                          capture_output=True, text=True)
    
    if result.stdout:
        elements = result.stdout.strip().split(', ')
        print(f"\nFound {len(elements)} UI elements:")
        
        airplay_found = False
        for elem in elements:
            print(f"  • {elem}")
            if 'airplay' in elem.lower():
                airplay_found = True
                print("    ⭐ Potential AirPlay control detected!")
        
        if not airplay_found:
            print("\n⚠️  No obvious AirPlay controls found by name")
            print("The AirPlay button might not have a descriptive name")
            print("It's typically in the bottom-right area of the control bar")
    
    return True


def main():
    # First, let's play an audio file
    print("🎵 Opening audio file in QuickTime...")
    audio_file = "./영앤올드.mp3"
    
    if Path(audio_file).exists():
        subprocess.run(['open', '-a', 'QuickTime Player', audio_file])
        time.sleep(3)  # Wait for QuickTime to open
        
        # Start playback
        print("▶️  Starting playback...")
        play_script = '''
        tell application "QuickTime Player"
            if exists document 1 then
                play document 1
            end if
        end tell
        '''
        subprocess.run(['osascript', '-e', play_script])
        time.sleep(1)
    
    # Run the test
    success = test_quicktime_ui_detection()
    
    if success:
        print("\n✅ Accessibility API is working!")
        print("\nNext steps:")
        print("1. The accessibility approach can detect UI elements")
        print("2. AirPlay button location depends on QuickTime's UI state")
        print("3. The button might not have 'AirPlay' in its name/description")
        print("4. Position-based detection (rightmost control) might be needed")
    else:
        print("\n❌ Accessibility API test failed")
        print("Please address the issues above and try again")


if __name__ == "__main__":
    main()