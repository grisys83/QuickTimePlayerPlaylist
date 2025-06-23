#!/usr/bin/env python3
"""
Capture what happens when clicking AirPlay button
"""

import subprocess
import time
import pyautogui
from datetime import datetime


def capture_airplay_click():
    """Capture screenshots before and after AirPlay click"""
    print("\n📸 Capturing AirPlay Click Process")
    print("=" * 40)
    
    # Activate QuickTime
    print("1️⃣ Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(2)
    
    # Take screenshot before
    print("\n2️⃣ Taking screenshot before click...")
    before_screenshot = pyautogui.screenshot()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    before_screenshot.save(f'airplay_before_{timestamp}.png')
    print(f"   Saved: airplay_before_{timestamp}.png")
    
    # Get AirPlay button position
    print("\n3️⃣ Getting AirPlay button position...")
    
    get_pos_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    if description of btn contains "외장" then
                        set btnPos to position of btn
                        return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                    end if
                end try
            end repeat
            return "not found"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', get_pos_script], 
                          capture_output=True, text=True)
    
    if result.stdout.strip() != "not found":
        pos = result.stdout.strip().split(',')
        airplay_x = int(pos[0])
        airplay_y = int(pos[1])
        print(f"   AirPlay button at: ({airplay_x}, {airplay_y})")
        
        # Click AirPlay button
        print("\n4️⃣ Clicking AirPlay button...")
        pyautogui.click(airplay_x, airplay_y)
        
        # Wait for popup
        print("   Waiting 2 seconds for popup...")
        time.sleep(2)
        
        # Take screenshot after
        print("\n5️⃣ Taking screenshot after click...")
        after_screenshot = pyautogui.screenshot()
        after_screenshot.save(f'airplay_after_{timestamp}.png')
        print(f"   Saved: airplay_after_{timestamp}.png")
        
        # Check what changed
        print("\n6️⃣ Checking UI changes...")
        
        check_script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                set output to "=== CURRENT STATE ===" & return
                set winCount to count of windows
                set output to output & "Windows: " & (winCount as string) & return
                
                -- Check window 1
                set output to output & return & "Window 1 elements:" & return
                set cbCount to count of checkboxes of window 1
                set btnCount to count of buttons of window 1
                set output to output & "  Checkboxes: " & (cbCount as string) & return
                set output to output & "  Buttons: " & (btnCount as string) & return
                
                -- Check for popup
                if winCount > 1 then
                    set output to output & return & "Popup window found!" & return
                    set popup to window 2
                    set popupName to name of popup
                    set output to output & "  Name: " & popupName & return
                    
                    -- Count elements in popup
                    set popupCB to count of checkboxes of popup
                    set popupBtn to count of buttons of popup
                    set popupRadio to count of radio buttons of popup
                    set output to output & "  Checkboxes: " & (popupCB as string) & return
                    set output to output & "  Buttons: " & (popupBtn as string) & return
                    set output to output & "  Radio buttons: " & (popupRadio as string) & return
                end if
                
                return output
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', check_script], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        print("\n✅ Screenshots saved!")
        print("Please check the screenshots to see what happened when clicking AirPlay")
        print("\n💡 If the AirPlay popup appears:")
        print("   - It might be a dropdown menu")
        print("   - It might be inline controls")
        print("   - It might be a floating window")
    else:
        print("❌ Could not find AirPlay button")


if __name__ == "__main__":
    capture_airplay_click()