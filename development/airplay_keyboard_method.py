#!/usr/bin/env python3
"""
AirPlay using keyboard navigation
Alternative method using keyboard shortcuts
"""

import subprocess
import time
import pyautogui

def enable_airplay_keyboard():
    """Enable AirPlay using keyboard navigation"""
    print("🚀 AirPlay Keyboard Method")
    print("=" * 50)
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Method 1: Try View menu
    print("\n🎹 Method 1: Using View menu")
    print("   Opening View menu...")
    
    # Cmd+Shift+/ to show menu bar (in case it's hidden)
    pyautogui.hotkey('cmd', 'shift', '/')
    time.sleep(0.5)
    
    # Try to access View menu
    # On Korean system, might need to use different approach
    pyautogui.hotkey('ctrl', 'f2')  # Access menu bar
    time.sleep(0.5)
    
    # Navigate to View menu (보기)
    for _ in range(3):  # Usually 3rd or 4th menu
        pyautogui.press('right')
        time.sleep(0.2)
    
    pyautogui.press('down')  # Open menu
    time.sleep(0.5)
    
    # Look for AirPlay option (usually near bottom)
    for _ in range(10):
        pyautogui.press('down')
        time.sleep(0.1)
    
    print("   If AirPlay menu is highlighted, press Enter...")
    time.sleep(2)
    
    # Method 2: Direct mouse movement with different approach
    print("\n🖱️ Method 2: Direct control bar access")
    
    # Get window center
    width, height = pyautogui.size()
    
    # First, ensure we're in the video area
    print("   Clicking in video area...")
    pyautogui.click(width // 2, height // 2)
    time.sleep(0.5)
    
    # Move mouse to bottom to show controls
    print("   Showing controls...")
    for y in range(height // 2, height - 50, 50):
        pyautogui.moveTo(width // 2, y, duration=0.1)
    
    time.sleep(1)
    
    # Now try to find AirPlay
    print("\n📍 Searching for AirPlay button...")
    
    # Scan the bottom area where controls should be
    control_y = height - 50
    
    for x in range(width - 300, width - 50, 25):
        pyautogui.moveTo(x, control_y, duration=0.1)
        print(f"   Checking position ({x}, {control_y})...")
        time.sleep(0.2)
    
    # Manual intervention
    print("\n🎯 MANUAL ASSISTANCE NEEDED")
    print("=" * 40)
    print("Please help:")
    print("1. Move your mouse to the AirPlay button")
    print("2. I'll click in 5 seconds...")
    
    for i in range(5, 0, -1):
        x, y = pyautogui.position()
        print(f"\r{i}초... Mouse at: ({x}, {y})  ", end='', flush=True)
        time.sleep(1)
    
    print("\nClicking AirPlay...")
    airplay_x, airplay_y = pyautogui.position()
    pyautogui.click()
    
    # Wait for menu
    time.sleep(2)
    
    print("\n📍 Now move to the checkbox...")
    print("You have 10 seconds...")
    
    for i in range(10, 0, -1):
        x, y = pyautogui.position()
        print(f"\r{i}초... Mouse at: ({x}, {y})  ", end='', flush=True)
        time.sleep(1)
    
    print("\nClicking checkbox...")
    checkbox_x, checkbox_y = pyautogui.position()
    pyautogui.click()
    
    # Save these positions
    import json
    data = {
        'manual_positions': {
            'airplay': {'x': airplay_x, 'y': airplay_y},
            'checkbox': {'x': checkbox_x, 'y': checkbox_y}
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    from pathlib import Path
    settings_file = Path.home() / '.airplay_positions_new.json'
    with open(settings_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Positions saved to {settings_file}")
    print("\n✅ Done!")

def show_quicktime_state():
    """Show current QuickTime state"""
    script = '''
    tell application "QuickTime Player"
        if (count of documents) > 0 then
            tell document 1
                set videoName to name
                set isPlaying to playing
                set currentTime to current time
                set videoDuration to duration
                
                return "Video: " & videoName & ¬
                    ", Playing: " & (isPlaying as string) & ¬
                    ", Time: " & (currentTime as string) & "/" & (videoDuration as string)
            end tell
        else
            return "No video open"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"\n📹 QuickTime State: {result.stdout.strip()}")

def main():
    print("🎬 QuickTime AirPlay - Keyboard Method")
    
    show_quicktime_state()
    
    print("\n⚠️ This method requires manual assistance")
    print("Be ready to position the mouse when prompted")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    enable_airplay_keyboard()

if __name__ == "__main__":
    main()