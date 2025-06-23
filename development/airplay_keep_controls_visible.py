#!/usr/bin/env python3
"""
AirPlay Enabler that keeps controls visible
Uses continuous mouse movement to prevent controls from hiding
"""

import subprocess
import time
import threading
import pyautogui
from pathlib import Path

class ControlKeeper:
    def __init__(self):
        self.keep_moving = True
        self.control_area = None
        
    def keep_controls_visible(self):
        """Keep moving mouse slightly to keep controls visible"""
        while self.keep_moving:
            if self.control_area:
                x = self.control_area['x']
                y = self.control_area['y']
                # Small circular movement
                for dx, dy in [(0, 0), (5, 0), (5, 5), (0, 5)]:
                    if not self.keep_moving:
                        break
                    pyautogui.moveTo(x + dx, y + dy, duration=0.1)
                    time.sleep(0.2)
            else:
                time.sleep(0.5)
    
    def set_control_area(self, x, y):
        """Set the area where mouse should hover"""
        self.control_area = {'x': x, 'y': y}
    
    def stop(self):
        """Stop the movement"""
        self.keep_moving = False

def find_airplay_button():
    """Find AirPlay button by looking at the control bar"""
    print("\n🔍 Looking for AirPlay button...")
    
    # Get window info
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if exists window 1 then
                set windowPos to position of window 1
                set windowSize to size of window 1
                return (item 1 of windowPos as string) & "," & ¬
                       (item 2 of windowPos as string) & "," & ¬
                       (item 1 of windowSize as string) & "," & ¬
                       (item 2 of windowSize as string)
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    coords = result.stdout.strip().split(',')
    win_x = int(coords[0])
    win_y = int(coords[1])
    win_width = int(coords[2])
    win_height = int(coords[3])
    
    # AirPlay is typically in the right portion of the control bar
    # But not at the very edge - usually around 150-250 pixels from right
    control_y = win_y + win_height - 50
    
    # Try different positions
    positions = [
        (win_x + win_width - 200, control_y, "Standard"),
        (win_x + win_width - 250, control_y, "More left"),
        (win_x + win_width - 150, control_y, "More right"),
        (win_x + win_width - 300, control_y, "Far left"),
    ]
    
    return positions, {'x': win_x, 'y': win_y, 'width': win_width, 'height': win_height}

def main():
    print("🚀 AirPlay Enabler - Keep Controls Visible")
    print("=" * 50)
    
    # Check video is loaded
    script = '''
    tell application "QuickTime Player"
        if (count of documents) > 0 then
            return "ready"
        else
            return "no_video"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.stdout.strip() != "ready":
        print("❌ No video loaded!")
        return
    
    print("✅ Video loaded")
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Start control keeper
    keeper = ControlKeeper()
    control_thread = threading.Thread(target=keeper.keep_controls_visible)
    control_thread.start()
    
    try:
        # Get window info and show controls
        positions, window = find_airplay_button()
        
        # Set control keeper position
        control_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 100
        keeper.set_control_area(control_x, control_y)
        
        print("\n🎮 Keeping controls visible...")
        time.sleep(1)
        
        # Try each AirPlay position
        print("\n🔍 Testing AirPlay positions...")
        
        for i, (x, y, desc) in enumerate(positions):
            print(f"\n{i+1}. Testing {desc} position ({x}, {y})")
            
            # Move to position
            pyautogui.moveTo(x, y, duration=0.5)
            
            # Pause keeper briefly
            keeper.keep_moving = False
            time.sleep(0.5)
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            test_path = Path.home() / f"airplay_test_{i+1}.png"
            screenshot.save(test_path)
            print(f"   💾 Screenshot: {test_path}")
            
            # Click
            print("   Clicking...")
            pyautogui.click()
            
            # Wait to see if menu appears
            time.sleep(1.5)
            
            # Check if menu opened by looking for change
            print("   Checking if menu opened...")
            
            # Resume keeper
            keeper.keep_moving = True
            keeper.set_control_area(x - 100, y - 200)  # Move to menu area
            
            # Manual check
            print("\n❓ Did the AirPlay menu open?")
            print("   If yes, move mouse to checkbox")
            print("   Clicking in 7 seconds...")
            
            for j in range(7, 0, -1):
                mx, my = pyautogui.position()
                print(f"\r   {j}초... Mouse at: ({mx}, {my})  ", end='', flush=True)
                time.sleep(1)
            
            print("\n   Clicking checkbox...")
            pyautogui.click()
            
            # Save position if it worked
            mx, my = pyautogui.position()
            import json
            data = {
                'working_positions': {
                    'airplay': {'x': x, 'y': y},
                    'checkbox': {'x': mx, 'y': my}
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            settings_file = Path.home() / '.airplay_working_positions.json'
            with open(settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n💾 Positions saved to {settings_file}")
            break
            
    finally:
        # Stop control keeper
        keeper.stop()
        control_thread.join()
        print("\n🔓 Control keeper stopped")

if __name__ == "__main__":
    print("🎬 QuickTime AirPlay - Control Keeper")
    print("\nThis version keeps the controls visible")
    print("by continuously moving the mouse slightly")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    main()