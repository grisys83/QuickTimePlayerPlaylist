#!/usr/bin/env python3
"""
PyAutoGUI를 사용한 더 쉬운 AirPlay 활성화
CV2보다 훨씬 간단!
"""

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치하려면: pip install pyautogui pillow")
    exit(1)

import time
import subprocess
from pathlib import Path

class PyAutoGUIAirPlayEnabler:
    def __init__(self):
        # 각 동작 사이 대기 시간
        pyautogui.PAUSE = 0.5
        
        # Fail-safe: 마우스를 화면 모서리로 이동하면 중지
        pyautogui.FAILSAFE = True
        
        self.template_dir = Path(__file__).parent / "templates"
        
    def enable_airplay(self):
        """PyAutoGUI로 간단하게 AirPlay 활성화"""
        print("🚀 PyAutoGUI AirPlay Enabler")
        print("=" * 50)
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 컨트롤 표시 (화면 하단으로 마우스 이동)
        print("\n📍 컨트롤 표시...")
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, screen_height - 100, duration=0.5)
        time.sleep(0.5)
        
        # AirPlay 아이콘 찾기
        print("\n🔍 AirPlay 아이콘 찾는 중...")
        airplay_icon = self.template_dir / "airplay_icon.png"
        
        if airplay_icon.exists():
            try:
                # confidence 파라미터로 유사도 조정 (0.8 = 80% 일치)
                airplay_location = pyautogui.locateCenterOnScreen(
                    str(airplay_icon), 
                    confidence=0.8
                )
                
                if airplay_location:
                    print(f"✅ AirPlay 아이콘 발견: {airplay_location}")
                    
                    # 클릭
                    pyautogui.click(airplay_location)
                    time.sleep(1.5)
                    
                    # 메뉴에서 체크박스 찾기
                    self.click_checkbox_smart()
                else:
                    print("❌ AirPlay 아이콘을 찾을 수 없습니다")
                    self.use_fixed_positions()
                    
            except Exception as e:
                print(f"❌ 오류: {e}")
                self.use_fixed_positions()
        else:
            print("⚠️ AirPlay 템플릿이 없습니다. 고정 위치 사용")
            self.use_fixed_positions()
    
    def click_checkbox_smart(self):
        """여러 방법으로 체크박스 찾기"""
        print("\n🔍 체크박스 찾는 중...")
        
        # 방법 1: 체크박스 템플릿으로 찾기
        checkbox_template = self.template_dir / "checkbox_unchecked.png"
        if checkbox_template.exists():
            try:
                checkboxes = list(pyautogui.locateAllOnScreen(
                    str(checkbox_template), 
                    confidence=0.6
                ))
                
                if checkboxes:
                    print(f"✅ {len(checkboxes)}개의 체크박스 발견")
                    
                    # 화면 중앙에 가장 가까운 체크박스 선택
                    screen_width, screen_height = pyautogui.size()
                    center_y = screen_height // 2
                    
                    best_checkbox = min(checkboxes, 
                                      key=lambda box: abs(box.top + box.height//2 - center_y))
                    
                    pyautogui.click(pyautogui.center(best_checkbox))
                    print("✅ 체크박스 클릭 완료")
                    return
            except:
                pass
        
        # 방법 2: 텍스트 근처 클릭 (OCR 없이 추정)
        print("⚠️ 체크박스를 찾을 수 없어 추정 위치 사용")
        
        # 현재 마우스 위치 (AirPlay 메뉴가 열린 상태)
        current_x, current_y = pyautogui.position()
        
        # 일반적인 오프셋으로 클릭
        pyautogui.click(current_x - 80, current_y - 160)
    
    def use_fixed_positions(self):
        """고정 위치 사용 (폴백)"""
        print("\n📍 고정 위치 사용...")
        
        screen_width, screen_height = pyautogui.size()
        
        # AirPlay는 보통 우측 하단
        airplay_x = screen_width - 300
        airplay_y = screen_height - 100
        
        pyautogui.click(airplay_x, airplay_y)
        time.sleep(1.5)
        
        # 체크박스는 위쪽
        pyautogui.click(airplay_x - 80, airplay_y - 160)
    
    def create_templates(self):
        """템플릿 생성 도우미"""
        print("📸 템플릿 생성 도우미")
        print("=" * 50)
        
        print("\n1. AirPlay 아이콘 캡처")
        print("   컨트롤이 보이는 상태에서 AirPlay 아이콘 영역을 선택하세요")
        input("   준비되면 Enter...")
        
        # 선택 영역 캡처
        print("   마우스로 영역을 드래그하세요...")
        region = pyautogui.screenshot()
        region.save(self.template_dir / "airplay_icon_new.png")
        
        print("\n2. 체크박스 캡처")
        print("   AirPlay 메뉴에서 빈 체크박스를 선택하세요")
        input("   준비되면 Enter...")
        
        region = pyautogui.screenshot()
        region.save(self.template_dir / "checkbox_new.png")
        
        print("\n✅ 템플릿 저장 완료!")


def main():
    enabler = PyAutoGUIAirPlayEnabler()
    
    print("🎯 PyAutoGUI AirPlay Enabler")
    print("\n옵션:")
    print("1. AirPlay 활성화")
    print("2. 템플릿 생성")
    print("3. 화면 정보 보기")
    
    choice = input("\n선택 (1-3): ")
    
    if choice == '1':
        print("\nQuickTime에 비디오가 열려있는지 확인하세요")
        input("준비되면 Enter...")
        enabler.enable_airplay()
        
    elif choice == '2':
        enabler.create_templates()
        
    elif choice == '3':
        width, height = pyautogui.size()
        print(f"\n화면 크기: {width}x{height}")
        print(f"현재 마우스: {pyautogui.position()}")
        
        # 스크린샷 테스트
        print("\n스크린샷 테스트...")
        screenshot = pyautogui.screenshot()
        test_path = Path.home() / "pyautogui_test.png"
        screenshot.save(test_path)
        print(f"저장됨: {test_path}")


if __name__ == "__main__":
    main()