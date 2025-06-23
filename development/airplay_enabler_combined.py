#!/usr/bin/env python3
"""
Combined AirPlay Enabler - All Working Methods
Combines PyAutoGUI (simpler) and CV2 (more precise) approaches
"""

import subprocess
import time
from pathlib import Path
import sys

def check_dependencies():
    """Check which vision libraries are available"""
    available = []
    
    try:
        import pyautogui
        available.append('pyautogui')
    except ImportError:
        pass
    
    try:
        import cv2
        import numpy
        available.append('cv2')
    except ImportError:
        pass
    
    return available

def enable_with_pyautogui():
    """PyAutoGUI method - simpler and handles Retina displays well"""
    import pyautogui
    
    print("🚀 Using PyAutoGUI method")
    
    # Get scale factor for Retina displays
    logical_width, _ = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale = screenshot.width / logical_width
    
    print(f"📐 Display scale: {scale}x")
    
    # Activate QuickTime
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Show controls
    width, height = pyautogui.size()
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # Try to find AirPlay icon
    template_dir = Path(__file__).parent / "templates"
    airplay_icon = template_dir / "airplay_icon.png"
    
    if airplay_icon.exists():
        try:
            location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
            if location:
                # Convert physical to logical coordinates
                logical_x = location.x / scale
                logical_y = location.y / scale
                
                print(f"✅ AirPlay found at ({logical_x:.0f}, {logical_y:.0f})")
                pyautogui.click(logical_x, logical_y)
                time.sleep(1.5)
                
                # Click checkbox using known offset from AirPlay icon
                checkbox_x = logical_x - 94  # 94 pixels to the left of AirPlay
                checkbox_y = logical_y - 160  # 160 pixels up from AirPlay
                
                print(f"📍 Clicking checkbox at ({checkbox_x:.0f}, {checkbox_y:.0f})")
                pyautogui.click(checkbox_x, checkbox_y)
                return True
        except Exception as e:
            print(f"⚠️ Template matching failed: {e}")
    
    # Fallback to fixed positions
    print("📍 Using fixed positions...")
    airplay_x = width - 150
    airplay_y = height - 50
    
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    # Checkbox position (from testing)
    pyautogui.click(airplay_x - 94, airplay_y - 160)
    
    return True

def enable_with_cv2():
    """CV2 method - more precise but requires coordinate conversion"""
    import cv2
    import numpy as np
    
    print("🚀 Using CV2 method")
    
    # Implementation would go here
    # (Using the working CV2 code from earlier)
    print("⚠️ CV2 method not fully implemented in this combined version")
    return False

def enable_with_simple_offset():
    """Simplest method - just use known offsets"""
    print("🚀 Using simple offset method")
    
    # Get QuickTime window
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
    
    # Activate QuickTime
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if not result.stdout.strip():
        print("❌ QuickTime window not found")
        return False
    
    coords = result.stdout.strip().split(',')
    win_x = int(coords[0])
    win_y = int(coords[1])
    win_width = int(coords[2])
    win_height = int(coords[3])
    
    # Show controls
    center_x = win_x + win_width // 2
    control_y = win_y + win_height - 250
    subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
    time.sleep(0.8)
    
    # Click AirPlay (typical position)
    airplay_x = win_x + win_width - 150
    airplay_y = win_y + win_height - 50
    
    print(f"📍 Clicking AirPlay at ({airplay_x}, {airplay_y})")
    subprocess.run(['cliclick', f'c:{airplay_x},{airplay_y}'])
    time.sleep(1.5)
    
    # Click checkbox (working offset)
    checkbox_x = airplay_x - 94
    checkbox_y = airplay_y - 160
    
    print(f"📍 Clicking checkbox at ({checkbox_x}, {checkbox_y})")
    subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
    
    return True

def main():
    print("🎬 QuickTime AirPlay Enabler")
    print("=" * 50)
    
    # Check available methods
    available = check_dependencies()
    
    print("\n📋 Available methods:")
    print(f"   - PyAutoGUI: {'✅' if 'pyautogui' in available else '❌'}")
    print(f"   - OpenCV: {'✅' if 'cv2' in available else '❌'}")
    print("   - Simple offset: ✅ (always available)")
    
    # Try methods in order of preference
    success = False
    
    if 'pyautogui' in available:
        print("\n" + "="*50)
        try:
            success = enable_with_pyautogui()
        except Exception as e:
            print(f"❌ PyAutoGUI failed: {e}")
    
    if not success and 'cv2' in available:
        print("\n" + "="*50)
        try:
            success = enable_with_cv2()
        except Exception as e:
            print(f"❌ CV2 failed: {e}")
    
    if not success:
        print("\n" + "="*50)
        try:
            success = enable_with_simple_offset()
        except Exception as e:
            print(f"❌ Simple offset failed: {e}")
    
    if success:
        print("\n✅ AirPlay should now be enabled!")
        print("\n💡 Tips:")
        print("   - If it didn't work, try adjusting your QuickTime window position")
        print("   - Make sure AirPlay devices are available on your network")
        print("   - The video should now appear on your Apple TV")
    else:
        print("\n❌ All methods failed")
        print("\n💡 Troubleshooting:")
        print("   - Make sure QuickTime Player is open with a video")
        print("   - Install PyAutoGUI: pip install pyautogui pillow")
        print("   - Try running with different window sizes")

if __name__ == "__main__":
    main()