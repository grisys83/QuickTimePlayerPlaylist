#!/usr/bin/env python3
"""
Manual AirPlay Clicker
Lets you position the mouse manually for precise clicking
"""

import subprocess
import time
import pyautogui

def manual_airplay_enabler():
    """Enable AirPlay with manual positioning"""
    print("🎯 Manual AirPlay Enabler")
    print("=" * 50)
    
    print("\n이 도구는 수동으로 마우스를 위치시켜 정확하게 클릭합니다")
    
    # Step 1: Activate QuickTime
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Step 2: Show controls
    width, height = pyautogui.size()
    print("\n📍 컨트롤 표시...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # Step 3: Click AirPlay
    print("\n🎯 단계 1: AirPlay 버튼 클릭")
    print("   마우스를 AirPlay 버튼 위에 놓으세요")
    print("   5초 후 자동 클릭됩니다...")
    
    for i in range(5, 0, -1):
        x, y = pyautogui.position()
        print(f"\r   {i}초... 현재 위치: ({x}, {y})", end='', flush=True)
        time.sleep(1)
    
    print("\n   클릭!")
    pyautogui.click()
    
    # Wait for menu
    print("\n⏳ 메뉴가 열리기를 기다립니다...")
    time.sleep(2)
    
    # Step 4: Click checkbox
    print("\n🎯 단계 2: 체크박스 클릭")
    print("   'This Computer' 옆의 체크박스에 마우스를 놓으세요")
    print("   10초 드립니다...")
    
    for i in range(10, 0, -1):
        x, y = pyautogui.position()
        print(f"\r   {i}초... 현재 위치: ({x}, {y})", end='', flush=True)
        time.sleep(1)
    
    print("\n   클릭!")
    pyautogui.click()
    
    print("\n✅ 완료!")
    
    # Save positions
    import json
    from pathlib import Path
    
    positions = {
        'manual_positions': {
            'last_checkbox': {'x': x, 'y': y}
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    settings_file = Path.home() / '.airplay_manual_positions.json'
    with open(settings_file, 'w') as f:
        json.dump(positions, f, indent=2)
    
    print(f"\n💾 위치 저장됨: {settings_file}")

def position_finder():
    """Help find exact positions"""
    print("🔍 Position Finder")
    print("=" * 50)
    
    print("\n마우스를 움직이면서 정확한 위치를 찾으세요")
    print("Ctrl+C로 종료")
    
    try:
        while True:
            x, y = pyautogui.position()
            print(f"\r마우스 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n종료됨")

if __name__ == "__main__":
    print("🎬 QuickTime AirPlay Manual Clicker")
    print("\n1. AirPlay 활성화 (수동)")
    print("2. 위치 찾기 도구")
    
    # Auto-run option 1
    print("\n수동 모드를 시작합니다...")
    time.sleep(2)
    
    manual_airplay_enabler()