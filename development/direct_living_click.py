#!/usr/bin/env python3
"""
직접 living 선택하기
AirPlay 메뉴가 열린 상태에서 2번째 항목 클릭
"""

import subprocess
import time


def click_living_directly():
    """AirPlay 메뉴에서 living(2번째 항목) 직접 클릭"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- Step 1: AirPlay 버튼 클릭
            set clicked to false
            set btnList to every button of window 1
            repeat with i from 1 to count of btnList
                try
                    set btnDesc to description of button i of window 1
                    if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                        click button i of window 1
                        set clicked to true
                        exit repeat
                    end if
                end try
            end repeat
            
            if not clicked then
                return "Error: AirPlay button not found"
            end if
            
            delay 1.5
            
            -- Step 2: 메뉴에서 2번째 항목(living) 클릭
            if (count of windows) > 1 then
                -- 팝업 창이 있으면
                set popup to window 2
                
                -- 방법 1: UI element로 클릭
                try
                    click UI element 2 of popup
                    return "Success: Clicked UI element 2 (living)"
                on error
                    -- 방법 2: button으로 시도
                    try
                        click button 2 of popup
                        return "Success: Clicked button 2 (living)"
                    on error
                        -- 방법 3: 모든 클릭 가능한 요소 찾기
                        set allElements to every UI element of popup
                        if (count of allElements) >= 2 then
                            click item 2 of allElements
                            return "Success: Clicked element 2 (living)"
                        else
                            return "Error: Not enough elements in popup"
                        end if
                    end try
                end try
            else
                return "Error: No popup window found"
            end if
        end tell
    end tell
    '''
    
    print("🎯 Living 선택 시도 중...")
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    print(f"결과: {result.stdout}")
    return "Success" in result.stdout


def main():
    print("Direct Living Click")
    print("=" * 40)
    print("\n주의: QuickTime에 오디오 파일이 열려있어야 합니다!")
    
    # 파일 열기
    music_file = "/Users/parkbyeongsu/Hyang/QuicktimePlaylist/Our Conversation.mp3"
    print(f"\n1️⃣ 파일 열기: {music_file}")
    
    open_script = f'''
    tell application "QuickTime Player"
        activate
        open POSIX file "{music_file}"
        play document 1
        delay 2
    end tell
    '''
    
    subprocess.run(['osascript', '-e', open_script])
    
    # Living 선택
    print("\n2️⃣ Living 선택...")
    if click_living_directly():
        print("\n✅ 성공!")
    else:
        print("\n❌ 실패!")
        print("\n대안: 수동으로 시도해보세요")
        print("1. AirPlay 버튼 클릭")
        print("2. 메뉴에서 living (2번째 항목) 클릭")


if __name__ == "__main__":
    main()