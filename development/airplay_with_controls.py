#!/usr/bin/env python3
"""
AirPlay Enabler that ensures controls are visible
"""

import subprocess
import time
import pyautogui
from pathlib import Path

def ensure_controls_visible():
    """Make sure QuickTime controls are visible"""
    print("🎮 Ensuring controls are visible...")
    
    # Get QuickTime window info
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
    if not result.stdout.strip():
        print("❌ Could not get window info")
        return None
    
    coords = result.stdout.strip().split(',')
    win_x = int(coords[0])
    win_y = int(coords[1])
    win_width = int(coords[2])
    win_height = int(coords[3])
    
    print(f"   Window at ({win_x}, {win_y}), size {win_width}x{win_height}")
    
    # Move mouse inside the video window to show controls
    center_x = win_x + win_width // 2
    bottom_y = win_y + win_height - 100
    
    print(f"   Moving to video area ({center_x}, {bottom_y})...")
    pyautogui.moveTo(center_x, bottom_y, duration=0.5)
    time.sleep(0.5)
    
    # Move slightly to ensure controls stay visible
    pyautogui.moveTo(center_x + 50, bottom_y, duration=0.3)
    time.sleep(0.5)
    
    return {
        'x': win_x,
        'y': win_y,
        'width': win_width,
        'height': win_height,
        'center_x': center_x,
        'bottom_y': bottom_y
    }

def click_airplay_in_window(window_info):
    """Click AirPlay button based on window position"""
    # AirPlay is typically at the right side of the control bar
    airplay_x = window_info['x'] + window_info['width'] - 150
    airplay_y = window_info['y'] + window_info['height'] - 50
    
    print(f"\n📍 Calculated AirPlay position: ({airplay_x}, {airplay_y})")
    
    # Move to AirPlay button
    print("   Moving to AirPlay button...")
    pyautogui.moveTo(airplay_x, airplay_y, duration=0.5)
    time.sleep(1)  # Pause to verify position
    
    print("   Clicking AirPlay...")
    pyautogui.click()
    
    return (airplay_x, airplay_y)

def main():
    print("🚀 AirPlay Enabler with Control Detection")
    print("=" * 50)
    
    # Check if video is loaded
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
        print("❌ No video loaded in QuickTime!")
        return
    
    print("✅ Video is loaded")
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Ensure controls are visible
    window_info = ensure_controls_visible()
    if not window_info:
        print("❌ Could not show controls")
        return
    
    # Take screenshot to verify controls
    print("\n📸 Taking screenshot to verify controls...")
    screenshot = pyautogui.screenshot()
    debug_path = Path.home() / "quicktime_controls_check.png"
    screenshot.save(debug_path)
    print(f"   💾 Saved: {debug_path}")
    
    print("\n⏸️  Pausing 2 seconds - check if controls are visible...")
    time.sleep(2)
    
    # Click AirPlay
    airplay_pos = click_airplay_in_window(window_info)
    
    print("\n⏳ Waiting for AirPlay menu...")
    time.sleep(2)
    
    # Use saved checkbox position or manual mode
    import json
    saved_file = Path.home() / '.airplay_manual_positions.json'
    
    if saved_file.exists():
        with open(saved_file, 'r') as f:
            data = json.load(f)
            checkbox = data['manual_positions']['last_checkbox']
        
        print(f"\n📍 Clicking saved checkbox position: ({checkbox['x']}, {checkbox['y']})")
        pyautogui.moveTo(checkbox['x'], checkbox['y'], duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
    else:
        print("\n🎯 MANUAL MODE")
        print("Move mouse to checkbox position...")
        for i in range(10, 0, -1):
            x, y = pyautogui.position()
            print(f"\r{i}초... Position: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        print("\nClicking!")
        pyautogui.click()
    
    print("\n✅ Process completed!")
    
    # Final screenshot
    print("\n📸 Taking final screenshot...")
    time.sleep(1)
    final_screenshot = pyautogui.screenshot()
    final_path = Path.home() / "airplay_final_result.png"
    final_screenshot.save(final_path)
    print(f"   💾 Saved: {final_path}")

if __name__ == "__main__":
    print("🎬 QuickTime AirPlay Control Detector")
    print("\nThis version:")
    print("1. Detects the QuickTime window position")
    print("2. Ensures controls are visible")
    print("3. Calculates AirPlay position based on window")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    main()