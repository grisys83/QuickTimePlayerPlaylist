#!/usr/bin/env python3
"""
QuickTime Player AirPlay 자동화 스크립트
AppleScript를 Python에서 실행하여 더 유연한 제어 가능
"""

import subprocess
import os
import time
from pathlib import Path

class QuickTimeAirPlayController:
    def __init__(self, airplay_device_name):
        self.airplay_device = airplay_device_name
        
    def play_with_airplay(self, file_path):
        """음악 파일을 QuickTime에서 열고 AirPlay로 재생"""
        
        # 파일 존재 확인
        if not Path(file_path).exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        # 파일 확장자 확인
        file_ext = Path(file_path).suffix.lower()
        is_audio = file_ext in ['.mp3', '.m4a', '.aac', '.wav', '.aiff']
        
        if is_audio:
            # 오디오 파일용 AppleScript
            applescript = f'''
            tell application "QuickTime Player"
                activate
                open POSIX file "{file_path}"
                play document 1
                delay 2
            end tell
            
            tell application "System Events"
                tell process "QuickTime Player"
                    set frontmost to true
                    
                    -- 오디오 플레이어의 AirPlay 버튼 찾기
                    set airplayClicked to false
                    set btnList to every button of window 1
                    repeat with i from 1 to count of btnList
                        try
                            set btnDesc to description of button i of window 1
                            if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                                click button i of window 1
                                set airplayClicked to true
                                exit repeat
                            end if
                        end try
                    end repeat
                    
                    if not airplayClicked then
                        return "Error: AirPlay button not found"
                    end if
                    
                    delay 1.5
                    
                    -- AirPlay 메뉴에서 기기 선택
                    if (count of windows) > 1 then
                        set menuWindow to window 2
                        
                        -- 기기 이름으로 찾기
                        set found to false
                        set allElements to every UI element of menuWindow
                        repeat with elem in allElements
                            try
                                if name of elem contains "{self.airplay_device}" then
                                    click elem
                                    set found to true
                                    exit repeat
                                end if
                            end try
                        end repeat
                        
                        -- 못 찾으면 위치로 클릭 (2번째 = living, 3번째 = TV)
                        if not found then
                            if "{self.airplay_device}" contains "living" then
                                click UI element 2 of menuWindow
                            else if "{self.airplay_device}" contains "TV" then
                                click UI element 3 of menuWindow
                            end if
                        end if
                        
                        return "Success"
                    else
                        return "Error: AirPlay menu not found"
                    end if
                end tell
            end tell
            '''
        else:
            # 비디오 파일용 AppleScript (기존 방식)
            applescript = f'''
            tell application "QuickTime Player"
                activate
                open POSIX file "{file_path}"
                play document 1
                delay 1
            end tell
            
            tell application "System Events"
                tell process "QuickTime Player"
                    set frontmost to true
                    
                    -- 비디오 플레이어의 AirPlay 버튼
                    repeat with i from 1 to 5
                        try
                            click button "AirPlay" of window 1
                            delay 0.5
                            exit repeat
                        on error
                            delay 0.5
                        end try
                    end repeat
                    
                    -- AirPlay 기기 선택
                    try
                        click menu item "{self.airplay_device}" of menu 1 of button "AirPlay" of window 1
                        return "Success"
                    on error errMsg
                        return "Error: " & errMsg
                    end try
                end tell
            end tell
            '''
        
        # AppleScript 실행
        result = self.run_applescript(applescript)
        return result
    
    def run_applescript(self, script):
        """AppleScript 실행"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"AppleScript 실행 오류: {e.stderr}")
            return None
    
    def list_airplay_devices(self):
        """사용 가능한 AirPlay 기기 목록 확인"""
        # 먼저 테스트 파일 열기
        test_audio = "/System/Library/Sounds/Glass.aiff"
        
        script = f'''
        tell application "QuickTime Player"
            activate
            open POSIX file "{test_audio}"
            delay 2
        end tell
        
        tell application "System Events"
            tell process "QuickTime Player"
                try
                    -- 먼저 어떤 버튼들이 있는지 확인
                    set btnList to every button of window 1
                    set btnCount to count of btnList
                    set debugInfo to "Total buttons: " & (btnCount as string) & return
                    
                    -- AirPlay 버튼 찾기
                    set airplayFound to false
                    repeat with i from 1 to btnCount
                        try
                            set btnDesc to description of button i of window 1
                            set debugInfo to debugInfo & "Button " & i & ": " & btnDesc & return
                            
                            if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                                click button i of window 1
                                set airplayFound to true
                                exit repeat
                            end if
                        end try
                    end repeat
                    
                    if not airplayFound then
                        return "Debug info:" & return & debugInfo & return & "AirPlay button not found"
                    end if
                    
                    delay 1
                    
                    -- 메뉴 항목 확인
                    if (count of windows) > 1 then
                        set menuWindow to window 2
                        set deviceList to {{}}
                        
                        set allButtons to every button of menuWindow
                        repeat with i from 1 to count of allButtons
                            try
                                set btnName to name of button i of menuWindow
                                set end of deviceList to "Position " & i & ": " & btnName
                            on error
                                set end of deviceList to "Position " & i & ": (unnamed)"
                            end try
                        end repeat
                        
                        -- 메뉴 닫기
                        click button 1 of window 1
                        
                        return deviceList as string
                    else
                        return "No AirPlay menu found"
                    end if
                on error errMsg
                    return "Error: " & errMsg
                end try
            end tell
        end tell
        
        tell application "QuickTime Player"
            close every window
        end tell
        '''
        
        return self.run_applescript(script)
    
    def debug_quicktime_buttons(self):
        """QuickTime 버튼 디버깅"""
        script = '''
        tell application "QuickTime Player"
            if (count of windows) = 0 then
                return "No QuickTime windows open"
            end if
        end tell
        
        tell application "System Events"
            tell process "QuickTime Player"
                set winName to name of window 1
                set btnList to every button of window 1
                set btnCount to count of btnList
                set output to "Window: " & winName & return
                set output to output & "Button count: " & (btnCount as string) & return & return
                
                repeat with i from 1 to btnCount
                    try
                        set btnDesc to description of button i of window 1
                        set btnPos to position of button i of window 1
                        set output to output & i & ". " & btnDesc & " at (" & (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & ")" & return
                    on error
                        set output to output & i & ". (error reading button)" & return
                    end try
                end repeat
                
                return output
            end tell
        end tell
        '''
        return self.run_applescript(script)
    
    def enable_accessibility(self):
        """접근성 권한 확인 및 안내"""
        print("중요: 이 스크립트가 작동하려면 접근성 권한이 필요합니다.")
        print("시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > 접근성")
        print("에서 Terminal 또는 Python을 허용해주세요.\n")
        
        # 권한 확인
        check_script = '''
        tell application "System Events"
            set isEnabled to UI elements enabled
            return isEnabled
        end tell
        '''
        
        result = self.run_applescript(check_script)
        if result == "true":
            print("✅ 접근성 권한이 활성화되어 있습니다.\n")
            return True
        else:
            print("❌ 접근성 권한이 필요합니다!")
            print("설정을 열어드릴까요? (y/n): ", end="")
            if input().lower() == 'y':
                subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
            return False

# 사용 예제
if __name__ == "__main__":
    # 설정
    AIRPLAY_DEVICE = "living"  # 또는 "TV", "Apple TV" 등
    MUSIC_FILE = "/Users/parkbyeongsu/Hyang/QuicktimePlaylist/Our Conversation.mp3"  # 프로젝트 폴더의 실제 파일
    
    # 컨트롤러 생성
    controller = QuickTimeAirPlayController(AIRPLAY_DEVICE)
    
    # 접근성 권한 확인
    if controller.enable_accessibility():
        
        # 먼저 QuickTime 창 상태 디버깅
        print("🔍 QuickTime 창 디버깅...")
        # 파일 먼저 열기
        subprocess.run(['osascript', '-e', f'tell application "QuickTime Player" to open POSIX file "{MUSIC_FILE}"'])
        time.sleep(2)
        
        debug_info = controller.debug_quicktime_buttons()
        print(f"디버깅 정보:\n{debug_info}\n")
        
        # 사용 가능한 기기 목록 확인 (선택사항)
        print("🔍 AirPlay 기기 목록 확인 중...")
        devices = controller.list_airplay_devices()
        print(f"사용 가능한 기기:\n{devices}\n")
        
        # AirPlay로 재생
        print(f"재생 중: {MUSIC_FILE}")
        print(f"AirPlay 기기: {AIRPLAY_DEVICE}")
        
        result = controller.play_with_airplay(MUSIC_FILE)
        
        if result == "Success":
            print("✅ AirPlay 연결 성공!")
        else:
            print(f"❌ 오류 발생: {result}")
    else:
        print("접근성 권한을 활성화한 후 다시 시도해주세요.")