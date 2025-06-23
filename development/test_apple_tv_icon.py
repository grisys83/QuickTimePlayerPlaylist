#!/usr/bin/env python3
"""
Test Apple TV icon detection
"""

import pyautogui
import time
import subprocess
from pathlib import Path

def test_icon_detection():
    print("🧪 Apple TV 아이콘 검색 테스트")
    print("=" * 50)
    
    template_dir = Path(__file__).parent / "templates"
    icon_path = template_dir / "apple_tv_icon.png"
    
    if not icon_path.exists():
        print(f"❌ 아이콘 파일이 없습니다: {icon_path}")
        return
    
    print(f"✅ 아이콘 파일 확인: {icon_path}")
    
    # Activate QuickTime and open AirPlay menu
    print("\n📍 QuickTime 활성화 및 AirPlay 메뉴 열기...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Show controls
    width, height = pyautogui.size()
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # Click AirPlay
    airplay_x = width - 150
    airplay_y = height - 50
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(2)
    
    # Search for Apple TV icon
    print("\n🔍 Apple TV 아이콘 검색...")
    
    # Try different confidence levels
    for confidence in [0.9, 0.8, 0.7, 0.6, 0.5]:
        print(f"\n시도 중... (신뢰도: {confidence})")
        try:
            result = pyautogui.locateCenterOnScreen(str(icon_path), confidence=confidence)
            if result:
                print(f"✅ 발견! 위치: {result}")
                print(f"   신뢰도 {confidence}에서 찾았습니다")
                
                # Show checkbox position
                scale = 2.0  # Retina
                logical_x = result.x / scale
                logical_y = result.y / scale
                checkbox_x = logical_x + 246
                checkbox_y = logical_y
                
                print(f"\n📍 예상 체크박스 위치: ({checkbox_x:.0f}, {checkbox_y:.0f})")
                
                # Move mouse to show location
                pyautogui.moveTo(logical_x, logical_y, duration=0.5)
                time.sleep(1)
                pyautogui.moveTo(checkbox_x, checkbox_y, duration=0.5)
                
                return
        except Exception as e:
            print(f"   실패: {e}")
    
    print("\n❌ Apple TV 아이콘을 찾을 수 없습니다")
    
    # Take a debug screenshot
    print("\n📸 디버그 스크린샷 저장...")
    debug_shot = pyautogui.screenshot()
    debug_path = Path.home() / "apple_tv_debug.png"
    debug_shot.save(debug_path)
    print(f"💾 저장됨: {debug_path}")

if __name__ == "__main__":
    test_icon_detection()