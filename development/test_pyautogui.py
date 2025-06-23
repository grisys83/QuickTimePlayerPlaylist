#!/usr/bin/env python3
"""
PyAutoGUI 테스트 - 직접 실행
"""

try:
    import pyautogui
    print("✅ PyAutoGUI 설치 확인됨")
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    exit(1)

import time
import subprocess
from pathlib import Path

def test_pyautogui():
    print("🧪 PyAutoGUI 테스트")
    print("=" * 50)
    
    # 화면 크기 확인
    width, height = pyautogui.size()
    print(f"\n📐 화면 크기: {width}x{height}")
    
    # 현재 마우스 위치
    x, y = pyautogui.position()
    print(f"🖱️  현재 마우스 위치: ({x}, {y})")
    
    # QuickTime 활성화
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # 컨트롤 표시
    print("\n📍 컨트롤 표시 (화면 하단으로 이동)...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(1)
    
    # AirPlay 아이콘 찾기
    print("\n🔍 AirPlay 아이콘 찾기...")
    template_dir = Path(__file__).parent / "templates"
    airplay_icon = template_dir / "airplay_icon.png"
    
    if airplay_icon.exists():
        print(f"   템플릿 파일 확인: {airplay_icon}")
        
        try:
            # 화면에서 아이콘 찾기
            print("   화면에서 검색 중...")
            location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
            
            if location:
                print(f"✅ AirPlay 아이콘 발견: {location}")
                
                # 마우스 이동 후 클릭
                pyautogui.moveTo(location, duration=0.5)
                time.sleep(0.5)
                pyautogui.click()
                
                print("\n⏳ 메뉴 열림 대기...")
                time.sleep(1.5)
                
                # 체크박스 위치 (오프셋 사용)
                checkbox_x = location.x - 80
                checkbox_y = location.y - 160
                
                print(f"\n📍 체크박스 클릭 위치: ({checkbox_x}, {checkbox_y})")
                pyautogui.click(checkbox_x, checkbox_y)
                
                print("\n✅ 완료!")
            else:
                print("❌ AirPlay 아이콘을 찾을 수 없습니다")
                print("\n💡 팁:")
                print("   - QuickTime 컨트롤이 보이는지 확인하세요")
                print("   - 템플릿 이미지가 현재 UI와 일치하는지 확인하세요")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    else:
        print("❌ AirPlay 템플릿 파일이 없습니다")
        print("\n📍 고정 위치 사용...")
        
        # 일반적인 AirPlay 위치
        airplay_x = width - 300
        airplay_y = height - 100
        
        print(f"   AirPlay 추정 위치: ({airplay_x}, {airplay_y})")
        pyautogui.click(airplay_x, airplay_y)
        time.sleep(1.5)
        
        # 체크박스 추정 위치
        checkbox_x = airplay_x - 80
        checkbox_y = airplay_y - 160
        
        print(f"   체크박스 추정 위치: ({checkbox_x}, {checkbox_y})")
        pyautogui.click(checkbox_x, checkbox_y)

def check_templates():
    """템플릿 파일 확인"""
    print("\n📁 템플릿 파일 확인")
    template_dir = Path(__file__).parent / "templates"
    
    if template_dir.exists():
        templates = list(template_dir.glob("*.png"))
        if templates:
            print(f"   {len(templates)}개의 템플릿 발견:")
            for t in templates:
                print(f"   - {t.name}")
        else:
            print("   템플릿이 없습니다")
    else:
        print("   templates 디렉토리가 없습니다")

if __name__ == "__main__":
    print("🚀 PyAutoGUI AirPlay 테스트")
    print("\nQuickTime에 비디오가 열려있는지 확인하세요")
    time.sleep(2)
    
    check_templates()
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    test_pyautogui()