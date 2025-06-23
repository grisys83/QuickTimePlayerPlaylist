#!/usr/bin/env python3
"""
Manual AirPlay Button Identifier
Helps you find and save the exact AirPlay button location
"""

import subprocess
import time
import pyautogui
import json
from pathlib import Path

def identify_airplay_button():
    """Manually identify the AirPlay button"""
    print("🎯 AirPlay Button Identifier")
    print("=" * 50)
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
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
    
    print(f"\n📐 Window: ({win_x}, {win_y}), size {win_width}x{win_height}")
    
    # Show controls
    print("\n🎮 Showing controls...")
    control_x = win_x + win_width // 2
    control_y = win_y + win_height - 80
    
    pyautogui.moveTo(control_x, control_y, duration=0.5)
    time.sleep(1)
    
    # Keep controls visible with small movements
    print("\n📍 Keeping controls visible...")
    for _ in range(3):
        pyautogui.moveTo(control_x + 10, control_y, duration=0.2)
        pyautogui.moveTo(control_x - 10, control_y, duration=0.2)
    
    # Take screenshot with controls
    print("\n📸 Taking screenshot with controls...")
    screenshot = pyautogui.screenshot()
    controls_path = Path.home() / "quicktime_controls_visible.png"
    screenshot.save(controls_path)
    print(f"   💾 Saved: {controls_path}")
    
    print("\n" + "="*50)
    print("🎯 STEP 1: FIND AIRPLAY BUTTON")
    print("="*50)
    print("\n1. Look at the control bar at the bottom")
    print("2. Find the AirPlay button (rectangle with triangle)")
    print("3. It's usually on the right side of the controls")
    print("4. Move your mouse to the AirPlay button")
    print("\nYou have 15 seconds...")
    
    for i in range(15, 0, -1):
        x, y = pyautogui.position()
        print(f"\r⏰ {i}초... Mouse position: ({x}, {y})  ", end='', flush=True)
        time.sleep(1)
    
    airplay_x, airplay_y = pyautogui.position()
    print(f"\n\n✅ AirPlay button position saved: ({airplay_x}, {airplay_y})")
    
    # Click AirPlay
    print("\n📍 Clicking AirPlay button...")
    pyautogui.click()
    
    print("\n⏳ Waiting for menu to open...")
    time.sleep(2)
    
    # Take screenshot of menu
    print("\n📸 Taking screenshot of menu...")
    menu_screenshot = pyautogui.screenshot()
    menu_path = Path.home() / "airplay_menu_open.png"
    menu_screenshot.save(menu_path)
    print(f"   💾 Saved: {menu_path}")
    
    print("\n" + "="*50)
    print("🎯 STEP 2: FIND CHECKBOX")
    print("="*50)
    print("\n1. The AirPlay menu should be open")
    print("2. Find the checkbox next to 'This Computer'")
    print("3. Move your mouse to the checkbox")
    print("\nYou have 15 seconds...")
    
    for i in range(15, 0, -1):
        x, y = pyautogui.position()
        print(f"\r⏰ {i}초... Mouse position: ({x}, {y})  ", end='', flush=True)
        time.sleep(1)
    
    checkbox_x, checkbox_y = pyautogui.position()
    print(f"\n\n✅ Checkbox position saved: ({checkbox_x}, {checkbox_y})")
    
    # Click checkbox
    print("\n📍 Clicking checkbox...")
    pyautogui.click()
    
    # Save all positions
    positions = {
        'airplay_button': {'x': airplay_x, 'y': airplay_y},
        'checkbox': {'x': checkbox_x, 'y': checkbox_y},
        'window': {
            'x': win_x, 
            'y': win_y, 
            'width': win_width, 
            'height': win_height
        },
        'offset': {
            'x': checkbox_x - airplay_x,
            'y': checkbox_y - airplay_y
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to multiple files for redundancy
    files_saved = []
    
    for filename in ['.airplay_exact_positions.json', 
                     '.quicktime_airplay_config.json',
                     'airplay_positions_backup.json']:
        filepath = Path.home() / filename
        with open(filepath, 'w') as f:
            json.dump(positions, f, indent=2)
        files_saved.append(filepath)
    
    print("\n💾 Positions saved to:")
    for f in files_saved:
        print(f"   - {f}")
    
    print("\n✅ Setup complete!")
    print(f"\n📊 Summary:")
    print(f"   AirPlay button: ({airplay_x}, {airplay_y})")
    print(f"   Checkbox: ({checkbox_x}, {checkbox_y})")
    print(f"   Offset: ({positions['offset']['x']:+d}, {positions['offset']['y']:+d})")
    
    return positions

def test_saved_positions():
    """Test the saved positions"""
    print("\n\n🧪 Testing saved positions...")
    
    config_file = Path.home() / '.airplay_exact_positions.json'
    if not config_file.exists():
        print("❌ No saved positions found")
        return
    
    with open(config_file, 'r') as f:
        positions = json.load(f)
    
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Show controls
    control_x = positions['window']['x'] + positions['window']['width'] // 2
    control_y = positions['window']['y'] + positions['window']['height'] - 80
    pyautogui.moveTo(control_x, control_y, duration=0.5)
    time.sleep(1)
    
    # Click AirPlay
    print(f"\n📍 Clicking AirPlay at ({positions['airplay_button']['x']}, {positions['airplay_button']['y']})...")
    pyautogui.click(positions['airplay_button']['x'], positions['airplay_button']['y'])
    time.sleep(2)
    
    # Click checkbox
    print(f"📍 Clicking checkbox at ({positions['checkbox']['x']}, {positions['checkbox']['y']})...")
    pyautogui.click(positions['checkbox']['x'], positions['checkbox']['y'])
    
    print("\n✅ Test complete!")

def main():
    print("🎬 QuickTime AirPlay Manual Setup")
    print("\nThis tool will help you:")
    print("1. Identify the exact AirPlay button location")
    print("2. Identify the exact checkbox location")
    print("3. Save these positions for automatic use")
    
    print("\n⚠️ Make sure:")
    print("- QuickTime has a video loaded")
    print("- You can see the QuickTime window")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    positions = identify_airplay_button()
    
    print("\n\nWould you like to test the saved positions?")
    print("Testing in 3 seconds...")
    time.sleep(3)
    
    test_saved_positions()

if __name__ == "__main__":
    main()