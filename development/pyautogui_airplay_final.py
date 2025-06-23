#!/usr/bin/env python3
"""
PyAutoGUI AirPlay Enabler - Final Version
Incorporates all learnings from testing
"""

import pyautogui
import time
import subprocess
from pathlib import Path

class PyAutoGUIAirPlayFinal:
    def __init__(self):
        # 각 동작 사이 대기 시간
        pyautogui.PAUSE = 0.3
        
        # Fail-safe: 마우스를 화면 모서리로 이동하면 중지
        pyautogui.FAILSAFE = True
        
        self.template_dir = Path(__file__).parent / "templates"
        self.scale_factor = self.get_scale_factor()
        
    def get_scale_factor(self):
        """Retina 디스플레이 스케일 팩터 감지"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        physical_width = screenshot.width
        return physical_width / logical_width
    
    def enable_airplay(self):
        """AirPlay 활성화 - 최종 버전"""
        print("🚀 PyAutoGUI AirPlay Enabler (Final)")
        print("=" * 50)
        
        # 스케일 팩터 확인
        print(f"\n📐 디스플레이 스케일: {self.scale_factor}x")
        
        # 화면 크기
        width, height = pyautogui.size()
        print(f"📐 화면 크기: {width}x{height}")
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 컨트롤 표시
        print("📍 컨트롤 표시...")
        pyautogui.moveTo(width // 2, height - 100, duration=0.5)
        time.sleep(0.8)
        
        # AirPlay 아이콘 찾기
        airplay_icon = self.template_dir / "airplay_icon.png"
        
        if airplay_icon.exists():
            print("\n🔍 AirPlay 아이콘 검색...")
            try:
                # PyAutoGUI는 물리적 픽셀 좌표를 반환
                location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
                
                if location:
                    # Retina 디스플레이 조정
                    logical_x = location.x / self.scale_factor
                    logical_y = location.y / self.scale_factor
                    
                    print(f"✅ AirPlay 발견:")
                    print(f"   물리적: ({location.x}, {location.y})")
                    print(f"   논리적: ({logical_x:.0f}, {logical_y:.0f})")
                    
                    # AirPlay 클릭
                    pyautogui.click(logical_x, logical_y)
                    time.sleep(1.5)
                    
                    # Apple TV 아이콘 찾기
                    return self.find_and_click_appletv()
                else:
                    print("❌ AirPlay 아이콘을 찾을 수 없습니다")
                    return self.use_fallback()
                    
            except Exception as e:
                print(f"❌ 오류: {e}")
                return self.use_fallback()
        else:
            print("⚠️ AirPlay 템플릿이 없습니다")
            return self.use_fallback()
    
    def find_and_click_appletv(self):
        """Apple TV 아이콘을 찾고 체크박스 클릭"""
        print("\n🔍 Apple TV 아이콘 검색...")
        
        # Apple TV 아이콘 템플릿
        appletv_icon = self.template_dir / "apple_tv_icon.png"
        
        if appletv_icon.exists():
            try:
                # Apple TV 아이콘 찾기
                location = pyautogui.locateCenterOnScreen(str(appletv_icon), confidence=0.7)
                
                if location:
                    # Retina 조정
                    logical_x = location.x / self.scale_factor
                    logical_y = location.y / self.scale_factor
                    
                    print(f"✅ Apple TV 아이콘 발견: ({logical_x:.0f}, {logical_y:.0f})")
                    
                    # 체크박스는 Apple TV 아이콘 오른쪽 246픽셀
                    checkbox_x = logical_x + 246
                    checkbox_y = logical_y
                    
                    print(f"📍 체크박스 클릭: ({checkbox_x:.0f}, {checkbox_y:.0f})")
                    pyautogui.click(checkbox_x, checkbox_y)
                    
                    print("\n✅ AirPlay 활성화 완료!")
                    return True
                else:
                    print("❌ Apple TV 아이콘을 찾을 수 없습니다")
                    return self.click_by_offset()
            except Exception as e:
                print(f"❌ 오류: {e}")
                return self.click_by_offset()
        else:
            return self.click_by_offset()
    
    def click_by_offset(self):
        """오프셋 기반 클릭 (폴백)"""
        print("\n📍 오프셋 방식 사용...")
        
        # 현재 마우스 위치 (AirPlay 메뉴가 열린 상태)
        x, y = pyautogui.position()
        
        # 테스트에서 확인된 오프셋
        checkbox_x = x - 94
        checkbox_y = y - 160
        
        print(f"📍 체크박스 추정 위치: ({checkbox_x}, {checkbox_y})")
        pyautogui.click(checkbox_x, checkbox_y)
        
        return True
    
    def use_fallback(self):
        """완전 폴백 - 고정 위치"""
        print("\n📍 고정 위치 사용...")
        
        width, height = pyautogui.size()
        
        # AirPlay 위치
        airplay_x = width - 150
        airplay_y = height - 50
        
        pyautogui.click(airplay_x, airplay_y)
        time.sleep(1.5)
        
        # 체크박스
        pyautogui.click(airplay_x - 94, airplay_y - 160)
        
        return True
    
    def create_templates_interactive(self):
        """대화형 템플릿 생성"""
        print("📸 템플릿 생성 도우미")
        print("=" * 50)
        
        # templates 디렉토리 생성
        self.template_dir.mkdir(exist_ok=True)
        
        print("\n이 도구는 AirPlay 아이콘과 Apple TV 아이콘 템플릿을 만듭니다.")
        
        # Step 1: AirPlay 아이콘
        print("\n1️⃣ AirPlay 아이콘 캡처")
        print("   - QuickTime 컨트롤이 보이는 상태로 만드세요")
        print("   - AirPlay 아이콘이 잘 보이는지 확인하세요")
        input("\n준비되면 Enter...")
        
        print("\n5초 후 전체 화면을 캡처합니다...")
        for i in range(5, 0, -1):
            print(f"\r{i}초...", end='', flush=True)
            time.sleep(1)
        
        screenshot1 = pyautogui.screenshot()
        temp_path1 = Path.home() / "airplay_full_screenshot.png"
        screenshot1.save(temp_path1)
        print(f"\n💾 저장됨: {temp_path1}")
        
        # Step 2: Apple TV 아이콘
        print("\n2️⃣ Apple TV 아이콘 캡처")
        print("   - AirPlay 메뉴를 열어주세요")
        print("   - Apple TV 디바이스가 보이는지 확인하세요")
        input("\n준비되면 Enter...")
        
        print("\n5초 후 전체 화면을 캡처합니다...")
        for i in range(5, 0, -1):
            print(f"\r{i}초...", end='', flush=True)
            time.sleep(1)
        
        screenshot2 = pyautogui.screenshot()
        temp_path2 = Path.home() / "appletv_full_screenshot.png"
        screenshot2.save(temp_path2)
        print(f"\n💾 저장됨: {temp_path2}")
        
        print("\n✅ 캡처 완료!")
        print("\n📋 다음 단계:")
        print("1. Preview.app에서 스크린샷을 열기")
        print("2. 각 아이콘 부분만 선택하고 자르기 (Cmd+K)")
        print("3. 다음 이름으로 저장:")
        print(f"   - AirPlay 아이콘: {self.template_dir / 'airplay_icon.png'}")
        print(f"   - Apple TV 아이콘: {self.template_dir / 'apple_tv_icon.png'}")
        
def main():
    enabler = PyAutoGUIAirPlayFinal()
    
    print("🎯 PyAutoGUI AirPlay Enabler (최종판)")
    
    # 자동으로 AirPlay 활성화 실행
    print("\nAirPlay 활성화를 시작합니다...")
    print("QuickTime에 비디오가 열려있는지 확인하세요")
    time.sleep(2)
    enabler.enable_airplay()

if __name__ == "__main__":
    main()