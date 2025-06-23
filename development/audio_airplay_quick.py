#!/usr/bin/env python3
"""
Quick Audio AirPlay Activator
Uses saved coordinates from accessibility detection
"""

import subprocess
import time
import json
from pathlib import Path
import pyautogui


def activate_airplay_with_saved_coords():
    """Activate AirPlay using saved coordinates"""
    print("\n🚀 Quick Audio AirPlay Activation")
    print("=" * 40)
    
    # Load saved coordinates
    settings_file = Path.home() / '.korean_audio_airplay_settings.json'
    
    if not settings_file.exists():
        print("❌ No saved coordinates found")
        print("Run audio_airplay_korean.py first to detect coordinates")
        return False
    
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    print(f"\n📍 Using saved coordinates from {settings['timestamp']}")
    print(f"   Detection method: {settings['detection_method']}")
    
    # Get coordinates
    airplay_center = settings['airplay_button']['center']
    apple_tv_pos = settings['apple_tv']['position']
    
    # Make sure QuickTime is frontmost
    subprocess.run(['osascript', '-e', 
                   'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    # Click AirPlay button
    print(f"\n1️⃣ Clicking AirPlay button at {airplay_center}")
    pyautogui.click(airplay_center[0], airplay_center[1])
    time.sleep(1.5)
    
    # Click Apple TV option
    print(f"2️⃣ Clicking Apple TV at {apple_tv_pos}")
    pyautogui.click(apple_tv_pos[0], apple_tv_pos[1])
    
    print("\n✅ AirPlay activation complete!")
    return True


def verify_audio_playing():
    """Verify audio is playing in QuickTime"""
    script = '''
    tell application "QuickTime Player"
        if exists document 1 then
            set isPlaying to playing of document 1
            set docName to name of document 1
            return docName & "|" & isPlaying
        else
            return "none|false"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    if result.stdout:
        name, playing = result.stdout.strip().split('|')
        return name != "none", name, playing == "true"
    
    return False, "", False


def main():
    # Verify QuickTime state
    has_doc, doc_name, is_playing = verify_audio_playing()
    
    if not has_doc:
        print("❌ No audio file open in QuickTime")
        return
    
    print(f"📄 Current file: {doc_name}")
    
    if not is_playing:
        print("▶️  Starting playback...")
        subprocess.run(['osascript', '-e', 
                       'tell application "QuickTime Player" to play document 1'])
        time.sleep(1)
    
    # Activate AirPlay
    success = activate_airplay_with_saved_coords()
    
    if not success:
        print("\n💡 Try these steps:")
        print("1. Run audio_airplay_korean.py to detect coordinates")
        print("2. Make sure QuickTime window is visible")
        print("3. Check that AirPlay devices are available")


if __name__ == "__main__":
    main()