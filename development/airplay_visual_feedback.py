#!/usr/bin/env python3
"""
AirPlay Enabler with Visual Feedback
Shows exactly where it's clicking
"""

import subprocess
import time
import pyautogui
from pathlib import Path

def visual_enable_airplay():
    """Enable AirPlay with visual feedback"""
    print("🚀 Visual AirPlay Enabler")
    print("=" * 50)
    
    # Check QuickTime
    script = '''
    tell application "QuickTime Player"
        if (count of documents) > 0 then
            return "Video loaded: " & (name of document 1)
        else
            return "No video"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"\n📹 {result.stdout.strip()}")
    
    if "No video" in result.stdout:
        print("❌ Please open a video first!")
        return
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    width, height = pyautogui.size()
    
    # Show controls with visual feedback
    print("\n📍 Showing controls...")
    print("   Moving mouse to trigger controls...")
    
    # Draw a small circle by moving mouse
    center_x = width // 2
    center_y = height - 80
    
    for i in range(4):
        x = center_x + (i % 2) * 20 - 10
        y = center_y + (i // 2) * 20 - 10
        pyautogui.moveTo(x, y, duration=0.2)
    
    time.sleep(1)
    
    # Move to AirPlay position slowly
    print("\n📍 Moving to AirPlay button...")
    airplay_x = width - 150
    airplay_y = height - 50
    
    # Show path to AirPlay
    steps = 5
    current_x, current_y = pyautogui.position()
    
    for i in range(steps + 1):
        progress = i / steps
        x = current_x + (airplay_x - current_x) * progress
        y = current_y + (airplay_y - current_y) * progress
        pyautogui.moveTo(x, y, duration=0.1)
        print(f"   Step {i+1}/{steps+1}: ({x:.0f}, {y:.0f})")
    
    print(f"\n🎯 At AirPlay position: ({airplay_x}, {airplay_y})")
    print("   ⏸️  Pausing 2 seconds - check if mouse is on AirPlay button...")
    time.sleep(2)
    
    print("   📍 Clicking...")
    pyautogui.click()
    
    print("\n⏳ Waiting for menu to open...")
    time.sleep(2)
    
    # Load saved position
    import json
    saved_file = Path.home() / '.airplay_manual_positions.json'
    
    if saved_file.exists():
        with open(saved_file, 'r') as f:
            data = json.load(f)
            checkbox = data['manual_positions']['last_checkbox']
        
        print(f"\n📍 Moving to saved checkbox position...")
        current_x, current_y = pyautogui.position()
        
        # Animate movement to checkbox
        steps = 10
        for i in range(steps + 1):
            progress = i / steps
            x = current_x + (checkbox['x'] - current_x) * progress
            y = current_y + (checkbox['y'] - current_y) * progress
            pyautogui.moveTo(x, y, duration=0.05)
            
            if i % 2 == 0:
                print(f"   → ({x:.0f}, {y:.0f})")
        
        print(f"\n🎯 At checkbox: ({checkbox['x']}, {checkbox['y']})")
        print("   ⏸️  Pausing 2 seconds - check if mouse is on checkbox...")
        time.sleep(2)
        
        print("   📍 Clicking...")
        pyautogui.click()
    else:
        print("\n❌ No saved checkbox position")
        print("   Please run airplay_manual_clicker.py first")
    
    print("\n✅ Process completed!")
    
    # Take a screenshot for debugging
    print("\n📸 Taking screenshot for debugging...")
    screenshot = pyautogui.screenshot()
    debug_path = Path.home() / "airplay_debug_final.png"
    screenshot.save(debug_path)
    print(f"   💾 Saved: {debug_path}")

def main():
    print("🎯 Visual Feedback AirPlay Enabler")
    print("\nThis version shows exactly where it's clicking")
    print("Watch the mouse movements carefully!")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    visual_enable_airplay()

if __name__ == "__main__":
    main()