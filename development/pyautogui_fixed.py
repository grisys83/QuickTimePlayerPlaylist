#!/usr/bin/env python3
"""
PyAutoGUI with proper Retina handling
"""

import pyautogui
import time
import subprocess
from pathlib import Path

# macOS Retina 디스플레이 대응
# pyautogui의 스크린샷은 물리적 픽셀을 사용하지만
# 클릭은 논리적 픽셀을 사용

def get_scale_factor():
    """Retina 스케일 팩터 가져오기"""
    # 논리적 화면 크기
    logical_width, logical_height = pyautogui.size()
    
    # 실제 스크린샷 크기 확인
    screenshot = pyautogui.screenshot()
    physical_width = screenshot.width
    
    scale = physical_width / logical_width
    print(f"📐 스케일 팩터: {scale}")
    return scale

def enable_airplay_smart():
    """스마트 AirPlay 활성화"""
    print("🚀 PyAutoGUI Smart AirPlay Enabler")
    print("=" * 50)
    
    # 스케일 팩터 확인
    scale = get_scale_factor()
    
    # 화면 크기
    width, height = pyautogui.size()
    print(f"📐 논리적 화면 크기: {width}x{height}")
    
    # QuickTime 활성화
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # 컨트롤 표시
    print("📍 컨트롤 표시...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(0.8)
    
    # AirPlay 찾기
    template_path = Path(__file__).parent / "templates" / "airplay_icon.png"
    
    if template_path.exists():
        print("\n🔍 AirPlay 아이콘 검색...")
        
        try:
            # locateCenterOnScreen은 물리적 픽셀을 반환
            location = pyautogui.locateCenterOnScreen(str(template_path), confidence=0.7)
            
            if location:
                # Retina 디스플레이 조정
                logical_x = location.x / scale
                logical_y = location.y / scale
                
                print(f"✅ AirPlay 발견:")
                print(f"   물리적 좌표: ({location.x}, {location.y})")
                print(f"   논리적 좌표: ({logical_x:.0f}, {logical_y:.0f})")
                
                # 클릭 (논리적 좌표 사용)
                pyautogui.click(logical_x, logical_y)
                time.sleep(1.5)
                
                # 체크박스 클릭
                checkbox_x = logical_x - 94
                checkbox_y = logical_y - 160
                
                print(f"\n📍 체크박스 클릭: ({checkbox_x:.0f}, {checkbox_y:.0f})")
                pyautogui.click(checkbox_x, checkbox_y)
                
                print("\n✅ 완료!")
                return True
            else:
                print("❌ AirPlay 아이콘을 찾을 수 없습니다")
        
        except Exception as e:
            print(f"❌ 오류: {e}")
    
    # 폴백: 고정 위치
    print("\n📍 고정 위치 사용...")
    airplay_x = width - 150
    airplay_y = height - 50
    
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    pyautogui.click(airplay_x - 94, airplay_y - 160)
    
    return True

def test_coordinates():
    """좌표 테스트"""
    print("🧪 좌표 시스템 테스트")
    print("=" * 50)
    
    # 스케일 확인
    scale = get_scale_factor()
    
    # 화면 정보
    width, height = pyautogui.size()
    print(f"\n논리적 화면: {width}x{height}")
    
    screenshot = pyautogui.screenshot()
    print(f"물리적 화면: {screenshot.width}x{screenshot.height}")
    
    # 마우스 위치
    x, y = pyautogui.position()
    print(f"\n현재 마우스 (논리적): ({x}, {y})")
    
    # 중앙으로 이동 테스트
    print("\n화면 중앙으로 이동...")
    pyautogui.moveTo(width // 2, height // 2, duration=1)
    
    # 우하단으로 이동
    print("우하단으로 이동...")
    pyautogui.moveTo(width - 100, height - 100, duration=1)

def create_better_templates():
    """더 나은 템플릿 생성"""
    print("📸 템플릿 개선 도구")
    print("=" * 50)
    
    print("\n1. 5초 후 전체 화면을 캡처합니다")
    print("2. QuickTime 컨트롤이 보이는 상태로 준비하세요")
    
    for i in range(5, 0, -1):
        print(f"\r{i}초...", end='', flush=True)
        time.sleep(1)
    
    print("\n📸 캡처!")
    screenshot = pyautogui.screenshot()
    
    output_path = Path.home() / "pyautogui_capture.png"
    screenshot.save(output_path)
    
    print(f"\n💾 저장됨: {output_path}")
    print("\n이제 이 이미지에서:")
    print("1. AirPlay 아이콘 부분만 잘라서 templates/airplay_icon.png로 저장")
    print("2. 체크박스 부분만 잘라서 templates/checkbox_unchecked.png로 저장")

def main():
    print("🎯 PyAutoGUI AirPlay (수정판)")
    print("\n1. AirPlay 활성화")
    print("2. 좌표 테스트")
    print("3. 템플릿 생성")
    
    # 자동으로 1번 실행
    print("\nAirPlay 활성화를 시작합니다...")
    time.sleep(2)
    
    enable_airplay_smart()

if __name__ == "__main__":
    main()