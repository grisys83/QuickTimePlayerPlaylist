#!/usr/bin/env python3
"""
Apple TV Icon Capture Tool
Helps create a template for the Apple TV icon in the AirPlay menu
"""

import subprocess
import time
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

def capture_apple_tv_icon():
    """Interactive tool to capture Apple TV icon"""
    print("🎯 Apple TV 아이콘 캡처 도구")
    print("=" * 50)
    
    # Create templates directory
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    
    print("\n준비 단계:")
    print("1. QuickTime Player에서 비디오를 엽니다")
    print("2. 마우스를 비디오 위로 움직여 컨트롤을 표시합니다")
    print("3. AirPlay 버튼이 보이는지 확인합니다")
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    # Step 1: Activate QuickTime
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # Step 2: Show controls
    width, height = pyautogui.size()
    print("📍 컨트롤 표시...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # Step 3: Click AirPlay to open menu
    print("\n📍 AirPlay 메뉴 열기...")
    print("   일반적인 AirPlay 위치 클릭...")
    
    # Use typical AirPlay position
    airplay_x = width - 150
    airplay_y = height - 50
    
    pyautogui.click(airplay_x, airplay_y)
    
    print("\n⏳ 메뉴가 열리기를 기다립니다...")
    time.sleep(2)
    
    # Step 4: Take screenshot
    print("\n📸 전체 화면 캡처...")
    screenshot = pyautogui.screenshot()
    
    # Save full screenshot
    full_path = Path.home() / "airplay_menu_full.png"
    screenshot.save(full_path)
    print(f"💾 전체 스크린샷 저장: {full_path}")
    
    # Step 5: Interactive region selection
    print("\n🎯 이제 Apple TV 아이콘 영역을 선택해야 합니다")
    print("\n방법 1: 자동 영역 캡처")
    print("   5초 후에 마우스 위치 주변을 캡처합니다")
    print("   Apple TV 아이콘 위에 마우스를 올려놓으세요")
    
    for i in range(5, 0, -1):
        print(f"\r   {i}초...", end='', flush=True)
        time.sleep(1)
    
    # Get mouse position
    mouse_x, mouse_y = pyautogui.position()
    print(f"\n\n📍 마우스 위치: ({mouse_x}, {mouse_y})")
    
    # Capture region around mouse
    region_size = 100
    region = pyautogui.screenshot(region=(
        mouse_x - region_size // 2,
        mouse_y - region_size // 2,
        region_size,
        region_size
    ))
    
    # Save region
    icon_path = template_dir / "apple_tv_icon.png"
    region.save(icon_path)
    print(f"💾 아이콘 영역 저장: {icon_path}")
    
    print("\n✅ 캡처 완료!")
    print("\n확인 사항:")
    print(f"1. {icon_path} 파일을 열어보세요")
    print("2. Apple TV 아이콘이 잘 캡처되었는지 확인하세요")
    print("3. 필요하면 Preview에서 수동으로 잘라내세요")
    
    # Also save checkbox position info
    print("\n💡 체크박스 위치 정보:")
    print(f"   Apple TV 아이콘에서 오른쪽으로 +246 픽셀")
    print(f"   예상 체크박스 위치: ({mouse_x + 246}, {mouse_y})")
    
    # Test the captured icon
    print("\n🧪 캡처된 아이콘 테스트...")
    time.sleep(1)
    
    try:
        found = pyautogui.locateCenterOnScreen(str(icon_path), confidence=0.7)
        if found:
            print("✅ 아이콘을 성공적으로 찾을 수 있습니다!")
        else:
            print("⚠️ 아이콘을 찾을 수 없습니다. 수동으로 편집이 필요할 수 있습니다")
    except Exception as e:
        print(f"⚠️ 테스트 실패: {e}")

def capture_manual():
    """Manual capture with guided steps"""
    print("\n📸 수동 캡처 모드")
    print("=" * 50)
    
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    
    print("\n단계별 가이드:")
    print("1. QuickTime에서 AirPlay 메뉴를 엽니다")
    print("2. Apple TV 디바이스가 보이는지 확인합니다")
    print("3. 전체 화면을 캡처합니다")
    
    print("\n2초 후 시작합니다...")
    time.sleep(2)
    
    print("\n📸 5초 후 캡처...")
    for i in range(5, 0, -1):
        print(f"\r{i}초...", end='', flush=True)
        time.sleep(1)
    
    screenshot = pyautogui.screenshot()
    path = Path.home() / "apple_tv_manual_capture.png"
    screenshot.save(path)
    
    print(f"\n\n💾 저장됨: {path}")
    print("\n다음 단계:")
    print("1. Preview.app에서 이미지 열기")
    print("2. Apple TV 아이콘 부분만 선택")
    print("3. 자르기 (Cmd+K)")
    print(f"4. 저장: {template_dir / 'apple_tv_icon.png'}")

def main():
    print("🍎 Apple TV 아이콘 캡처 도구")
    
    # 자동으로 옵션 1 실행
    print("\n자동 캡처를 시작합니다...")
    capture_apple_tv_icon()
    
    print("\n🎯 팁:")
    print("- Apple TV 아이콘은 일반적으로 집 모양 아이콘입니다")
    print("- 디바이스 이름(예: 거실, Living Room)은 무시하세요")
    print("- 아이콘만 정확히 캡처하는 것이 중요합니다")

if __name__ == "__main__":
    main()