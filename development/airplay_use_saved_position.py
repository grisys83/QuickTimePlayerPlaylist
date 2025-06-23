#!/usr/bin/env python3
"""
AirPlay Enabler using saved positions
Uses the positions you manually found
"""

import subprocess
import time
import json
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

def load_saved_positions():
    """Load saved positions from manual clicking"""
    settings_file = Path.home() / '.airplay_manual_positions.json'
    
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            data = json.load(f)
            return data
    return None

def enable_airplay_with_saved_position():
    """Enable AirPlay using saved checkbox position"""
    print("🚀 AirPlay Enabler (Using Saved Position)")
    print("=" * 50)
    
    # Load saved positions
    saved = load_saved_positions()
    if saved:
        checkbox_pos = saved['manual_positions']['last_checkbox']
        print(f"\n✅ Found saved checkbox position: ({checkbox_pos['x']}, {checkbox_pos['y']})")
        print(f"   Saved at: {saved['timestamp']}")
    else:
        print("\n❌ No saved positions found")
        print("   Run airplay_manual_clicker.py first")
        return False
    
    # Get current screen size
    width, height = pyautogui.size()
    print(f"\n📐 Screen size: {width}x{height}")
    
    # Step 1: Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Step 2: Show controls
    print("📍 Showing controls...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # Step 3: Find and click AirPlay
    # First try to find the icon
    template_dir = Path(__file__).parent / "templates"
    airplay_icon = template_dir / "airplay_icon.png"
    airplay_pos = None
    
    if airplay_icon.exists():
        print("\n🔍 Searching for AirPlay icon...")
        try:
            # Get scale factor
            screenshot = pyautogui.screenshot()
            scale = screenshot.width / width
            
            location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
            if location:
                logical_x = location.x / scale
                logical_y = location.y / scale
                airplay_pos = (logical_x, logical_y)
                print(f"✅ AirPlay found at ({logical_x:.0f}, {logical_y:.0f})")
        except Exception as e:
            print(f"⚠️ Icon search failed: {e}")
    
    # If not found, calculate from saved checkbox position
    if not airplay_pos:
        print("\n📍 Calculating AirPlay position from saved checkbox...")
        # The checkbox was at (963, 809)
        # Estimate AirPlay button position (typically below and to the right)
        estimated_x = checkbox_pos['x'] + 94
        estimated_y = checkbox_pos['y'] + 160
        airplay_pos = (estimated_x, estimated_y)
        print(f"   Estimated AirPlay at ({estimated_x}, {estimated_y})")
    
    # Click AirPlay
    print(f"\n📍 Clicking AirPlay...")
    pyautogui.click(airplay_pos[0], airplay_pos[1])
    time.sleep(1.5)
    
    # Step 4: Click checkbox at saved position
    print(f"\n📍 Clicking checkbox at saved position ({checkbox_pos['x']}, {checkbox_pos['y']})...")
    pyautogui.moveTo(checkbox_pos['x'], checkbox_pos['y'], duration=0.5)
    time.sleep(0.3)
    pyautogui.click()
    
    print("\n✅ AirPlay should now be enabled!")
    return True

def calculate_offset():
    """Calculate offset between AirPlay and checkbox"""
    saved = load_saved_positions()
    if not saved:
        print("No saved positions found")
        return
    
    checkbox = saved['manual_positions']['last_checkbox']
    print(f"\nCheckbox position: ({checkbox['x']}, {checkbox['y']})")
    
    # If we know where AirPlay typically is
    width, height = pyautogui.size()
    typical_airplay = (width - 150, height - 50)
    
    offset_x = checkbox['x'] - typical_airplay[0]
    offset_y = checkbox['y'] - typical_airplay[1]
    
    print(f"Offset from typical AirPlay position: ({offset_x:+d}, {offset_y:+d})")
    
    # Also calculate from your found position
    # You clicked AirPlay around (719, 800) according to the log
    actual_offset_x = checkbox['x'] - 719
    actual_offset_y = checkbox['y'] - 800
    
    print(f"Offset from your AirPlay click: ({actual_offset_x:+d}, {actual_offset_y:+d})")

def main():
    print("🎬 QuickTime AirPlay Enabler")
    print("\nUsing your manually saved positions")
    
    # Show saved info
    calculate_offset()
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    enable_airplay_with_saved_position()

if __name__ == "__main__":
    main()