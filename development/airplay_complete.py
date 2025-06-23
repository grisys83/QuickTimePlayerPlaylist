#!/usr/bin/env python3
"""
Complete AirPlay Solution
Handles everything from opening video to enabling AirPlay
"""

import subprocess
import time
import sys
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

def open_video_in_quicktime(video_path=None):
    """Open a video in QuickTime"""
    if video_path and Path(video_path).exists():
        # Open specific video
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        print(f"✅ Opened: {video_path}")
    else:
        # Just open QuickTime
        subprocess.run(['open', '-a', 'QuickTime Player'])
        print("✅ Opened QuickTime Player")
    
    time.sleep(2)  # Give time to load

def check_quicktime_ready():
    """Check if QuickTime has a video open"""
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
    return result.stdout.strip() == "ready"

def enable_airplay_complete():
    """Complete AirPlay enablement process"""
    print("🚀 Complete AirPlay Enabler")
    print("=" * 50)
    
    # Check if video is open
    if not check_quicktime_ready():
        print("\n❌ No video open in QuickTime!")
        print("   Please drag a video file to QuickTime first")
        print("   Or provide a video path as argument")
        return False
    
    print("\n✅ Video is loaded in QuickTime")
    
    # Activate QuickTime
    print("\n📍 Activating QuickTime...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    width, height = pyautogui.size()
    
    # Show controls
    print("📍 Showing controls...")
    pyautogui.moveTo(width // 2, height - 80, duration=0.5)
    time.sleep(0.8)
    
    # Move to keep controls visible
    pyautogui.moveTo(width // 2, height - 50, duration=0.3)
    time.sleep(0.5)
    
    # Click AirPlay
    print("\n📍 Clicking AirPlay button...")
    
    # Try different positions based on window size
    airplay_positions = [
        (width - 150, height - 50),   # Standard
        (width - 180, height - 50),   # Slightly left
        (width - 120, height - 50),   # Slightly right
        (width - 150, height - 80),   # Higher
    ]
    
    for i, (x, y) in enumerate(airplay_positions):
        if i == 0:
            print(f"   Primary position: ({x}, {y})")
        else:
            print(f"   Alternative {i}: ({x}, {y})")
        
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.3)
        break  # Use first position
    
    pyautogui.click()
    
    print("\n⏳ Waiting for AirPlay menu...")
    time.sleep(2)
    
    # Use saved position or manual mode
    import json
    saved_file = Path.home() / '.airplay_manual_positions.json'
    
    if saved_file.exists():
        with open(saved_file, 'r') as f:
            data = json.load(f)
            pos = data['manual_positions']['last_checkbox']
            print(f"\n📍 Clicking saved checkbox position: ({pos['x']}, {pos['y']})")
            pyautogui.click(pos['x'], pos['y'])
    else:
        print("\n🎯 MANUAL MODE")
        print("=" * 30)
        print("Move your mouse to the checkbox")
        print("Next to 'This Computer' or your Apple TV")
        print("\nYou have 10 seconds...")
        
        for i in range(10, 0, -1):
            x, y = pyautogui.position()
            print(f"\r{i}초... Position: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        print("\n\nClicking!")
        pyautogui.click()
        
        # Save this position
        data = {
            'manual_positions': {
                'last_checkbox': {'x': x, 'y': y}
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(saved_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("💾 Position saved for next time")
    
    print("\n✅ AirPlay should now be enabled!")
    print("\n💡 If it didn't work:")
    print("   1. Make sure your Apple TV is on")
    print("   2. Check that both devices are on the same network")
    print("   3. Try moving the QuickTime window to a different position")
    
    return True

def main():
    print("🎬 QuickTime AirPlay Complete Solution")
    
    # Check arguments
    video_path = None
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if Path(video_path).exists():
            print(f"\n📹 Video file: {video_path}")
            open_video_in_quicktime(video_path)
        else:
            print(f"\n❌ File not found: {video_path}")
            return
    
    # Check if QuickTime has video
    if not check_quicktime_ready():
        print("\n⚠️ No video loaded in QuickTime")
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]} /path/to/video.mp4")
        print("\nOr drag a video file to QuickTime Player first")
        return
    
    print("\nStarting AirPlay enabler in 3 seconds...")
    time.sleep(3)
    
    enable_airplay_complete()

if __name__ == "__main__":
    main()