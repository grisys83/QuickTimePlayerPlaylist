#!/usr/bin/env python3
"""
macOS Accessibility API를 사용한 QuickTime AirPlay 제어
더 정확한 UI 요소 접근
"""

import subprocess
import time
import sys

try:
    from AppKit import NSWorkspace, NSRunningApplication
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
        CGWindowListCreateDescriptionFromArray
    )
    import pyobjc
except ImportError:
    print("필요한 패키지 설치:")
    print("pip3 install pyobjc-core pyobjc-framework-Quartz pyobjc-framework-AppKit")
    sys.exit(1)

def get_quicktime_window_info():
    """QuickTime Player 창 정보 가져오기"""
    windows = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly, 
        kCGNullWindowID
    )
    
    for window in windows:
        if window.get('kCGWindowOwnerName') == 'QuickTime Player':
            return {
                'bounds': window.get('kCGWindowBounds'),
                'number': window.get('kCGWindowNumber'),
                'name': window.get('kCGWindowName', '')
            }
    return None

def click_airplay_with_accessibility():
    """Accessibility API를 사용한 정밀한 AirPlay 제어"""
    script = '''
    -- Accessibility Inspector를 통해 얻은 정보 사용
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            delay 0.5
            
            -- 창의 모든 UI 요소 검사
            tell window 1
                -- toolbar 찾기
                try
                    tell toolbar 1
                        -- AirPlay 버튼은 보통 toolbar의 마지막 부분에 위치
                        set buttonCount to count of buttons
                        repeat with i from 1 to buttonCount
                            set btn to button i
                            try
                                -- AirPlay 관련 속성 확인
                                if (help of btn contains "AirPlay") or ¬
                                   (description of btn contains "AirPlay") or ¬
                                   (title of btn contains "AirPlay") then
                                    click btn
                                    return "AirPlay button clicked"
                                end if
                            end try
                        end repeat
                    end tell
                end try
                
                -- group 내부의 버튼 찾기
                try
                    tell group 1
                        set allButtons to every button
                        repeat with btn in allButtons
                            try
                                set btnDesc to description of btn
                                if btnDesc contains "AirPlay" then
                                    click btn
                                    return "AirPlay button clicked in group"
                                end if
                            end try
                        end repeat
                    end tell
                end try
                
                -- 직접 버튼 찾기
                set allButtons to every button
                repeat with btn in allButtons
                    try
                        -- role description 확인
                        if role description of btn is "button" then
                            -- 위치 기반으로 AirPlay 버튼 추정
                            set btnPosition to position of btn
                            set btnSize to size of btn
                            
                            -- AirPlay 버튼은 보통 오른쪽 하단
                            if (item 1 of btnPosition) > 600 then
                                click btn
                                delay 0.5
                                
                                -- 팝업이 나타났는지 확인
                                if exists sheet 1 then
                                    return "Possible AirPlay button clicked"
                                end if
                            end if
                        end if
                    end try
                end repeat
            end tell
        end tell
    end tell
    
    return "AirPlay button not found"
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def simulate_keyboard_shortcut():
    """키보드 단축키로 AirPlay 접근 시도"""
    # 다양한 단축키 조합 시도
    shortcuts = [
        # QuickTime 특정 단축키들
        "keystroke \"a\" using {control down, command down}",
        "keystroke \"p\" using {control down, command down}",
        "keystroke \"k\" using {control down, command down}",
        # 일반적인 비디오 플레이어 단축키
        "keystroke \"o\" using {option down, command down}",
    ]
    
    for shortcut in shortcuts:
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.5
                {shortcut}
                delay 1
                
                -- 팝업이나 메뉴가 나타났는지 확인
                if exists sheet 1 of window 1 then
                    return "Shortcut worked: {shortcut}"
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        if "worked" in result.stdout:
            return True
    
    return False

def control_playback_bar():
    """재생 컨트롤바를 통한 AirPlay 접근"""
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- 마우스를 움직여 컨트롤 표시
            do shell script "cliclick m:640,400"  -- 화면 중앙
            delay 0.5
            do shell script "cliclick m:640,580"  -- 하단으로
            delay 0.5
            
            tell window 1
                -- 재생 컨트롤 영역 찾기
                try
                    -- 컨트롤바는 보통 window의 하위 group에 위치
                    repeat with grp in groups
                        set grpPos to position of grp
                        set grpSize to size of grp
                        
                        -- 하단에 위치한 group 찾기
                        if (item 2 of grpPos) > 500 then
                            tell grp
                                -- group 내의 모든 버튼 확인
                                set buttons to every button
                                repeat with btn in buttons
                                    try
                                        click btn
                                        delay 0.3
                                        
                                        -- AirPlay 메뉴가 나타났는지 확인
                                        if exists pop up button 1 then
                                            return "Found AirPlay control"
                                        end if
                                    end try
                                end repeat
                            end tell
                        end if
                    end repeat
                end try
            end tell
        end tell
    end tell
    '''
    
    # cliclick이 없으면 설치 안내
    try:
        subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
    except:
        print("cliclick 설치 필요: brew install cliclick")
        return False
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return "Found" in result.stdout

def main():
    if len(sys.argv) < 2:
        print("사용법: python quicktime_airplay_accessibility.py <video_file>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # QuickTime 실행
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
    
    print("AirPlay 버튼 찾는 중...")
    
    # 방법 1: Accessibility API
    result = click_airplay_with_accessibility()
    print(f"Accessibility 결과: {result}")
    
    # 방법 2: 키보드 단축키
    if not "clicked" in result:
        print("키보드 단축키 시도 중...")
        if simulate_keyboard_shortcut():
            print("키보드 단축키 성공")
    
    # 방법 3: 컨트롤바 직접 제어
    if not "clicked" in result:
        print("컨트롤바 접근 시도 중...")
        if control_playback_bar():
            print("컨트롤바 제어 성공")

if __name__ == "__main__":
    main()