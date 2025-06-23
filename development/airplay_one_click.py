#!/usr/bin/env python3
"""
One-Click AirPlay Enabler
Uses your saved exact positions
"""

import subprocess
import time
import json
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI not installed")
    print("Install: pip install pyautogui pillow")
    exit(1)

def enable_airplay_one_click():
    """Enable AirPlay with one click using saved positions"""
    
    # Load saved positions
    config_file = Path.home() / '.airplay_exact_positions.json'
    if not config_file.exists():
        print("❌ No saved positions found!")
        print("   Run airplay_manual_identify.py first")
        return False
    
    with open(config_file, 'r') as f:
        positions = json.load(f)
    
    print("🚀 One-Click AirPlay Enabler")
    print("=" * 40)
    print(f"✅ Using saved positions from {positions['timestamp']}")
    print(f"   AirPlay: ({positions['airplay_button']['x']}, {positions['airplay_button']['y']})")
    print(f"   Checkbox: ({positions['checkbox']['x']}, {positions['checkbox']['y']})")
    
    # Check if QuickTime has video
    script = '''
    tell application "QuickTime Player"
        if (count of documents) > 0 then
            return name of document 1
        else
            return "no_video"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.stdout.strip() == "no_video":
        print("\n❌ No video loaded in QuickTime!")
        return False
    
    print(f"\n📹 Video: {result.stdout.strip()}")
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    # Show controls
    print("📍 Showing controls...")
    control_x = positions['window']['x'] + positions['window']['width'] // 2
    control_y = positions['window']['y'] + positions['window']['height'] - 80
    
    # Move to control area
    pyautogui.moveTo(control_x, control_y, duration=0.3)
    time.sleep(0.5)
    
    # Small movement to ensure controls stay visible
    pyautogui.moveTo(control_x + 20, control_y, duration=0.2)
    time.sleep(0.3)
    
    # Click AirPlay button
    print(f"\n📍 Clicking AirPlay button...")
    pyautogui.click(positions['airplay_button']['x'], positions['airplay_button']['y'])
    
    # Wait for menu
    print("⏳ Waiting for menu...")
    time.sleep(1.5)
    
    # Click checkbox
    print(f"📍 Clicking checkbox...")
    pyautogui.click(positions['checkbox']['x'], positions['checkbox']['y'])
    
    print("\n✅ AirPlay enabled!")
    return True

def quick_test():
    """Quick test to verify positions still work"""
    config_file = Path.home() / '.airplay_exact_positions.json'
    if not config_file.exists():
        return False
    
    with open(config_file, 'r') as f:
        positions = json.load(f)
    
    # Just show where we would click
    print("\n🧪 Quick position test...")
    print(f"   Would click AirPlay at: ({positions['airplay_button']['x']}, {positions['airplay_button']['y']})")
    print(f"   Would click checkbox at: ({positions['checkbox']['x']}, {positions['checkbox']['y']})")
    
    # Move mouse to show positions
    print("\n   Moving to AirPlay position...")
    pyautogui.moveTo(positions['airplay_button']['x'], positions['airplay_button']['y'], duration=0.5)
    time.sleep(1)
    
    print("   Moving to checkbox position...")
    pyautogui.moveTo(positions['checkbox']['x'], positions['checkbox']['y'], duration=0.5)
    time.sleep(1)
    
    return True

def main():
    print("🎬 QuickTime AirPlay - One Click")
    print("\nOptions:")
    print("1. Enable AirPlay")
    print("2. Test positions")
    print("3. Auto-run (default)")
    
    # Auto-run after 2 seconds
    print("\nAuto-running in 2 seconds...")
    time.sleep(2)
    
    enable_airplay_one_click()

if __name__ == "__main__":
    main()