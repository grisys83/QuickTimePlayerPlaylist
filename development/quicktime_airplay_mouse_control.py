#!/usr/bin/env python3
"""
마우스 자동화를 통한 QuickTime AirPlay 제어
PyAutoGUI를 사용하여 QuickTime Player의 AirPlay 버튼을 클릭
"""

import subprocess
import time
import sys

try:
    import pyautogui
except ImportError:
    print("PyAutoGUI 설치 필요: pip3 install pyautogui")
    print("추가로 필요: pip3 install pillow pyobjc-core pyobjc")
    sys.exit(1)

class QuickTimeAirPlayController:
    def __init__(self):
        # 안전 장치 비활성화 (마우스가 화면 모서리로 이동해도 중단 안됨)
        pyautogui.FAILSAFE = False
        
        # 마우스 이동 속도
        pyautogui.PAUSE = 0.5
        
    def open_quicktime_with_video(self, video_path):
        """QuickTime Player로 비디오 열기"""
        script = f'''
        tell application "QuickTime Player"
            activate
            open POSIX file "{video_path}"
            delay 2
            play document 1
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        time.sleep(3)  # QuickTime이 완전히 로드될 때까지 대기
        
    def find_airplay_button(self):
        """AirPlay 버튼 찾기 (이미지 인식 또는 좌표)"""
        # 방법 1: 화면 스크린샷에서 AirPlay 아이콘 찾기
        # AirPlay 아이콘 이미지가 필요함
        try:
            # airplay_icon.png 파일이 있다면
            location = pyautogui.locateOnScreen('airplay_icon.png', confidence=0.8)
            if location:
                return pyautogui.center(location)
        except:
            pass
            
        # 방법 2: QuickTime 컨트롤바의 일반적인 위치 사용
        # QuickTime Player 창 찾기
        screen_width, screen_height = pyautogui.size()
        
        # 컨트롤바는 보통 하단에 위치
        # AirPlay 버튼은 오른쪽에서 두 번째 정도
        estimated_x = screen_width * 0.85
        estimated_y = screen_height * 0.90
        
        return (estimated_x, estimated_y)
        
    def show_quicktime_controls(self):
        """QuickTime 컨트롤바 표시"""
        # 마우스를 비디오 위로 이동하여 컨트롤 표시
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width/2, screen_height/2, duration=0.5)
        time.sleep(0.5)
        
        # 하단으로 이동하여 컨트롤바 유지
        pyautogui.moveTo(screen_width/2, screen_height * 0.9, duration=0.5)
        
    def click_airplay_button(self):
        """AirPlay 버튼 클릭"""
        # 컨트롤 표시
        self.show_quicktime_controls()
        
        # AirPlay 버튼 위치 찾기
        airplay_pos = self.find_airplay_button()
        
        if airplay_pos:
            # AirPlay 버튼 클릭
            pyautogui.click(airplay_pos[0], airplay_pos[1])
            time.sleep(1)
            return True
        return False
        
    def select_airplay_device(self, device_name):
        """AirPlay 기기 선택"""
        # 기기 목록이 나타날 때까지 대기
        time.sleep(1)
        
        # 텍스트로 기기 찾기 (OCR 필요)
        # 또는 목록에서 위치로 선택
        # 예: 첫 번째 AirPlay 기기 선택
        pyautogui.press('down')  # 첫 번째 기기로 이동
        pyautogui.press('enter')  # 선택
        
    def enable_airplay_with_mouse(self, video_path, device_index=0):
        """마우스 자동화로 AirPlay 활성화"""
        print("QuickTime Player 실행 중...")
        self.open_quicktime_with_video(video_path)
        
        print("AirPlay 버튼 찾는 중...")
        if self.click_airplay_button():
            print("AirPlay 메뉴 열림")
            
            # 기기 선택 (인덱스 기반)
            for _ in range(device_index + 1):
                pyautogui.press('down')
            pyautogui.press('enter')
            
            print("AirPlay 기기 선택 완료")
            return True
        else:
            print("AirPlay 버튼을 찾을 수 없습니다")
            return False

# AppleScript를 사용한 대체 방법
def enable_airplay_with_system_events(video_path):
    """System Events를 사용한 UI 자동화"""
    script = '''
    tell application "QuickTime Player"
        activate
        open POSIX file "''' + video_path + '''"
        delay 2
        play document 1
    end tell
    
    tell application "System Events"
        tell process "QuickTime Player"
            -- 메뉴바에서 AirPlay 찾기
            click menu bar item "AirPlay" of menu bar 1
            delay 1
            
            -- 첫 번째 AirPlay 기기 선택
            click menu item 2 of menu 1 of menu bar item "AirPlay" of menu bar 1
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except:
        return False

# 더 정확한 좌표 기반 방법
def enable_airplay_with_coordinates(video_path):
    """정확한 좌표를 사용한 AirPlay 활성화"""
    script = f'''
    tell application "QuickTime Player"
        activate
        open POSIX file "{video_path}"
        delay 2
        play document 1
        
        -- 창 크기와 위치 가져오기
        set windowBounds to bounds of window 1
        set windowX to item 1 of windowBounds
        set windowY to item 2 of windowBounds
        set windowWidth to (item 3 of windowBounds) - windowX
        set windowHeight to (item 4 of windowBounds) - windowY
        
        -- AirPlay 버튼 예상 위치 계산
        set airplayX to windowX + (windowWidth * 0.85)
        set airplayY to windowY + (windowHeight * 0.95)
        
        return (airplayX as string) & "," & (airplayY as string)
    end tell
    '''
    
    # 좌표 가져오기
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout:
        coords = result.stdout.strip().split(',')
        x, y = float(coords[0]), float(coords[1])
        
        # 마우스로 클릭
        pyautogui.moveTo(x, y - 50, duration=0.5)  # 컨트롤 표시
        time.sleep(0.5)
        pyautogui.click(x, y)  # AirPlay 버튼 클릭
        
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("사용법: python quicktime_airplay_mouse_control.py <video_file>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    print("방법 1: PyAutoGUI 사용")
    controller = QuickTimeAirPlayController()
    # controller.enable_airplay_with_mouse(video_path)
    
    print("\n방법 2: System Events 사용")
    if not enable_airplay_with_system_events(video_path):
        print("System Events 방법 실패")
        
    print("\n방법 3: 정확한 좌표 사용")
    # enable_airplay_with_coordinates(video_path)

if __name__ == "__main__":
    main()