#!/usr/bin/env python3
"""
QuickTime AirPlay 고급 제어
여러 방법을 조합하여 안정적으로 AirPlay 활성화
"""

import subprocess
import time
import sys
import os
from pathlib import Path

class QuickTimeAirPlayAdvanced:
    def __init__(self):
        self.cliclick_available = self.check_cliclick()
        
    def check_cliclick(self):
        """cliclick 설치 확인"""
        try:
            subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
            return True
        except:
            print("cliclick이 설치되지 않음. brew install cliclick")
            return False
            
    def get_window_info(self):
        """QuickTime 창 정보 가져오기"""
        script = '''
        tell application "QuickTime Player"
            if (count windows) = 0 then return ""
            
            set windowBounds to bounds of window 1
            set windowX to item 1 of windowBounds
            set windowY to item 2 of windowBounds
            set windowWidth to (item 3 of windowBounds) - windowX
            set windowHeight to (item 4 of windowBounds) - windowY
            
            return (windowX as string) & "," & (windowY as string) & "," & ¬
                   (windowWidth as string) & "," & (windowHeight as string)
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            return {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
        return None
        
    def show_controls(self, window_info):
        """컨트롤바 표시"""
        if not self.cliclick_available:
            return False
            
        # 마우스를 중앙으로 이동
        center_x = window_info['x'] + window_info['width'] // 2
        center_y = window_info['y'] + window_info['height'] // 2
        
        subprocess.run(['cliclick', f'm:{center_x},{center_y}'])
        time.sleep(0.5)
        
        # 하단으로 이동하여 컨트롤 유지
        bottom_y = window_info['y'] + window_info['height'] - 50
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        time.sleep(0.5)
        
        return True
        
    def find_airplay_button(self, window_info):
        """AirPlay 버튼 위치 찾기"""
        # 여러 가능한 위치 시도
        possible_positions = [
            # 표준 위치 (오른쪽에서 두 번째)
            (window_info['x'] + window_info['width'] - 100, 
             window_info['y'] + window_info['height'] - 30),
            # 대체 위치 1
            (window_info['x'] + window_info['width'] - 80, 
             window_info['y'] + window_info['height'] - 30),
            # 대체 위치 2
            (window_info['x'] + window_info['width'] - 120, 
             window_info['y'] + window_info['height'] - 30),
        ]
        
        return possible_positions
        
    def click_airplay_button(self, positions):
        """AirPlay 버튼 클릭 시도"""
        if not self.cliclick_available:
            return False
            
        for x, y in positions:
            print(f"AirPlay 버튼 클릭 시도: ({x}, {y})")
            subprocess.run(['cliclick', f'c:{x},{y}'])
            time.sleep(1)
            
            # 메뉴가 나타났는지 확인
            if self.check_airplay_menu():
                return True
                
        return False
        
    def check_airplay_menu(self):
        """AirPlay 메뉴가 표시되었는지 확인"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                -- 팝업이나 메뉴가 있는지 확인
                if exists pop up button 1 of window 1 then
                    return "popup"
                else if exists menu 1 then
                    return "menu"
                else
                    return "none"
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return result.stdout.strip() != "none"
        
    def select_airplay_device(self, device_index=1):
        """AirPlay 기기 선택"""
        if self.cliclick_available:
            # 마우스로 선택
            window_info = self.get_window_info()
            if window_info:
                # 메뉴 항목 위치 계산
                menu_x = window_info['x'] + window_info['width'] - 100
                menu_y = window_info['y'] + window_info['height'] - 50 - (device_index * 25)
                
                subprocess.run(['cliclick', f'c:{menu_x},{menu_y}'])
                return True
        
        # 키보드로 선택
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                repeat {device_index} times
                    key code 125 -- 아래 화살표
                    delay 0.2
                end repeat
                key code 36 -- Enter
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
        return True
        
    def enable_airplay(self, video_path, device_index=1):
        """전체 AirPlay 활성화 프로세스"""
        # QuickTime 실행
        print("QuickTime Player 실행 중...")
        script = f'''
        tell application "QuickTime Player"
            activate
            open POSIX file "{video_path}"
            delay 2
            play document 1
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        time.sleep(3)
        
        # 창 정보 가져오기
        window_info = self.get_window_info()
        if not window_info:
            print("QuickTime 창을 찾을 수 없습니다.")
            return False
            
        print(f"QuickTime 창 찾음: {window_info}")
        
        # 컨트롤 표시
        print("컨트롤바 표시 중...")
        self.show_controls(window_info)
        
        # AirPlay 버튼 찾기 및 클릭
        print("AirPlay 버튼 찾는 중...")
        positions = self.find_airplay_button(window_info)
        
        if self.click_airplay_button(positions):
            print("AirPlay 메뉴 열림")
            time.sleep(0.5)
            
            # 기기 선택
            print(f"AirPlay 기기 선택 중 (인덱스: {device_index})...")
            if self.select_airplay_device(device_index):
                print("AirPlay 활성화 완료!")
                return True
        
        print("AirPlay 버튼을 찾을 수 없습니다.")
        return False

def create_playlist_with_airplay(playlist, airplay_device_index=1):
    """AirPlay를 사용한 플레이리스트 재생"""
    controller = QuickTimeAirPlayAdvanced()
    
    for i, video in enumerate(playlist):
        print(f"\n재생 중: {video} ({i+1}/{len(playlist)})")
        
        # 첫 번째 비디오에서만 AirPlay 설정
        if i == 0:
            controller.enable_airplay(video, airplay_device_index)
        else:
            # 이후 비디오는 그냥 열기
            script = f'''
            tell application "QuickTime Player"
                close document 1
                delay 0.5
                open POSIX file "{video}"
                delay 1
                play document 1
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
        
        # 재생 완료 대기
        while True:
            check_script = '''
            tell application "QuickTime Player"
                if (count documents) > 0 then
                    if playing of document 1 then
                        return "playing"
                    else
                        return "stopped"
                    end if
                else
                    return "no_document"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', check_script], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() != "playing":
                break
                
            time.sleep(2)
    
    print("\n플레이리스트 재생 완료!")

def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  단일 비디오: python quicktime_airplay_advanced.py <video_file> [device_index]")
        print("  플레이리스트: python quicktime_airplay_advanced.py -p <video1> <video2> ...")
        sys.exit(1)
    
    if sys.argv[1] == "-p":
        # 플레이리스트 모드
        playlist = [os.path.abspath(v) for v in sys.argv[2:]]
        create_playlist_with_airplay(playlist)
    else:
        # 단일 비디오 모드
        video_path = os.path.abspath(sys.argv[1])
        device_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        controller = QuickTimeAirPlayAdvanced()
        controller.enable_airplay(video_path, device_index)

if __name__ == "__main__":
    main()