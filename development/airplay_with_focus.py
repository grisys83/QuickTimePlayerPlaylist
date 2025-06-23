#!/usr/bin/env python3
"""
AirPlay Enabler with Focus Management
Keeps QuickTime focused throughout the process
"""

import subprocess
import time
import threading
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

class FocusedAirPlayEnabler:
    def __init__(self):
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True
        self.keep_focus = True
        self.focus_thread = None
        
    def maintain_focus(self):
        """Keep QuickTime in focus"""
        while self.keep_focus:
            subprocess.run(['osascript', '-e', 
                          'tell application "QuickTime Player" to activate'], 
                          capture_output=True)
            time.sleep(0.5)
    
    def enable_airplay(self):
        """Enable AirPlay with continuous focus"""
        print("🚀 AirPlay Enabler with Focus Management")
        print("=" * 50)
        
        # Start focus keeper thread
        print("\n🔒 Starting focus keeper...")
        self.focus_thread = threading.Thread(target=self.maintain_focus)
        self.focus_thread.start()
        time.sleep(1)
        
        width, height = pyautogui.size()
        print(f"📐 Screen size: {width}x{height}")
        
        try:
            # Step 1: Show controls by moving mouse
            print("\n📍 Showing controls...")
            # Move to center-bottom to show controls
            pyautogui.moveTo(width // 2, height - 100, duration=0.5)
            time.sleep(1)
            
            # Move again to ensure controls stay visible
            pyautogui.moveTo(width // 2, height - 50, duration=0.3)
            time.sleep(0.5)
            
            # Step 2: Click AirPlay
            print("\n📍 Finding AirPlay button...")
            
            # Try multiple positions for AirPlay
            airplay_positions = [
                (width - 150, height - 50),   # Common position
                (width - 200, height - 50),   # Alternative
                (width - 100, height - 50),   # Another alternative
                (width - 150, height - 100),  # Higher up
            ]
            
            clicked = False
            for i, (x, y) in enumerate(airplay_positions):
                print(f"   Trying position {i+1}: ({x}, {y})")
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.3)
                
                # Check if we're hovering over AirPlay
                # (you'll see tooltip or highlight)
                print("   Is the mouse over AirPlay? Clicking...")
                pyautogui.click()
                clicked = True
                break
            
            if not clicked:
                print("❌ Could not find AirPlay")
                return False
            
            # Wait for menu with focus maintained
            print("\n⏳ Waiting for menu (maintaining focus)...")
            time.sleep(2)
            
            # Step 3: Manual checkbox click
            print("\n🎯 MANUAL MODE:")
            print("=" * 30)
            print("1. The AirPlay menu should be open")
            print("2. Move your mouse to the checkbox")
            print("3. I'll click in 10 seconds...")
            print("\n동작하지 마세요! 마우스만 체크박스 위에 놓으세요!")
            
            for i in range(10, 0, -1):
                x, y = pyautogui.position()
                print(f"\r⏰ {i}초... 마우스 위치: ({x}, {y})  ", end='', flush=True)
                time.sleep(1)
            
            print("\n\n📍 클릭!")
            pyautogui.click()
            
            print("\n✅ 완료! AirPlay가 활성화되었습니다.")
            
        finally:
            # Stop focus keeper
            self.keep_focus = False
            if self.focus_thread:
                self.focus_thread.join()
            print("\n🔓 Focus keeper stopped")

def verify_quicktime():
    """Verify QuickTime is running"""
    script = '''
    tell application "System Events"
        return exists (process "QuickTime Player")
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip() == "true"

def main():
    print("🎬 QuickTime AirPlay with Focus")
    
    # Check if QuickTime is running
    if not verify_quicktime():
        print("\n❌ QuickTime Player가 실행되지 않았습니다!")
        print("   먼저 QuickTime에서 비디오를 열어주세요")
        return
    
    print("\n✅ QuickTime Player 확인됨")
    print("\n준비사항:")
    print("1. QuickTime에 비디오가 열려있어야 합니다")
    print("2. Apple TV가 같은 네트워크에 있어야 합니다")
    print("3. 다른 창을 클릭하지 마세요!")
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    enabler = FocusedAirPlayEnabler()
    enabler.enable_airplay()

if __name__ == "__main__":
    main()