#!/usr/bin/env python3
"""
Test AirPlay menu navigation with keyboard
"""

import subprocess
import time


def test_keyboard_navigation():
    """Test selecting TV using keyboard navigation"""
    print("\n⌨️ Testing AirPlay Keyboard Navigation")
    print("=" * 40)
    
    # Activate QuickTime
    print("1️⃣ Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Click AirPlay button
    print("\n2️⃣ Clicking AirPlay button...")
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Click AirPlay button
            click button "외장 재생 메뉴 보기" of window 1
            delay 1.0
            
            -- Navigate with keyboard
            -- Down arrow twice to get to TV (3rd item)
            key code 125 -- Down arrow
            delay 0.3
            key code 125 -- Down arrow  
            delay 0.3
            
            -- Press Enter to select
            key code 36 -- Return key
            
            return "Selected TV with keyboard"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    print(f"✅ Result: {result.stdout.strip()}")
    
    # Alternative: Try "living" (2nd item)
    print("\n3️⃣ Alternative - Selecting 'living'...")
    
    alt_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            -- Click AirPlay button again
            delay 1
            click button "외장 재생 메뉴 보기" of window 1
            delay 1.0
            
            -- Down arrow once to get to living (2nd item)
            key code 125 -- Down arrow
            delay 0.3
            
            -- Press Enter to select
            key code 36 -- Return key
            
            return "Selected living with keyboard"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', alt_script], 
                          capture_output=True, text=True)
    print(f"✅ Result: {result.stdout.strip()}")
    
    print("\n💡 Note: ")
    print("- 1st item: Park의 MacBook Air (current)")
    print("- 2nd item: living")
    print("- 3rd item: TV")


if __name__ == "__main__":
    test_keyboard_navigation()