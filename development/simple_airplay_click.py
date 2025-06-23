#!/usr/bin/env python3
"""
간단한 AirPlay 클릭 스크립트
living 체크박스만 클릭하는 것이 목표
"""

import subprocess
import time
import pyautogui


def simple_airplay_click():
    """단순하게 AirPlay 버튼 클릭하고 living 선택"""
    
    print("🎯 Simple AirPlay Click")
    print("=" * 40)
    
    # Step 1: AirPlay 버튼 위치 찾기
    find_airplay = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- 버튼 찾기
            set btnList to every button of window 1
            repeat with i from 1 to count of btnList
                try
                    set btnDesc to description of button i of window 1
                    if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                        set btnPos to position of button i of window 1
                        return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                    end if
                end try
            end repeat
            
            return "not found"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', find_airplay], 
                          capture_output=True, text=True)
    
    if result.stdout.strip() == "not found":
        print("❌ AirPlay 버튼을 찾을 수 없습니다")
        return False
    
    # AirPlay 버튼 위치
    pos = result.stdout.strip().split(',')
    airplay_x = int(pos[0])
    airplay_y = int(pos[1])
    print(f"✅ AirPlay 버튼 위치: ({airplay_x}, {airplay_y})")
    
    # Step 2: AirPlay 버튼 클릭
    print("\n🖱️ AirPlay 버튼 클릭...")
    pyautogui.click(airplay_x, airplay_y)
    time.sleep(1.5)
    
    # Step 3: living 체크박스 클릭
    print("\n🎯 living 체크박스 클릭...")
    
    # 방법 1: 상대 위치로 클릭 (AirPlay 버튼 기준)
    # living은 보통 AirPlay 버튼에서 약간 아래, 오른쪽에 있음
    living_x = airplay_x + 50  # 오른쪽으로 50픽셀
    living_y = airplay_y + 40  # 아래로 40픽셀
    
    print(f"   living 예상 위치: ({living_x}, {living_y})")
    pyautogui.click(living_x, living_y)
    
    print("\n✅ 완료!")
    
    # 대안: 정확한 위치를 사용자가 지정
    print("\n💡 만약 작동하지 않으면:")
    print(f"   1. AirPlay 메뉴가 열린 상태에서")
    print(f"   2. living 체크박스의 정확한 위치를 클릭")
    print(f"   3. 아래 값을 조정해서 다시 시도:")
    print(f"      living_x = airplay_x + ?? (현재: +50)")
    print(f"      living_y = airplay_y + ?? (현재: +40)")
    
    return True


def click_specific_position(x, y):
    """특정 위치 클릭 (테스트용)"""
    print(f"\n🖱️ 클릭 위치: ({x}, {y})")
    pyautogui.click(x, y)


def main():
    print("Simple AirPlay Automation")
    print("\n주의: QuickTime에 오디오 파일이 열려있어야 합니다!")
    
    # 옵션 선택
    print("\n옵션:")
    print("1. 자동으로 시도")
    print("2. 수동으로 위치 입력")
    
    choice = input("\n선택 (1 또는 2): ")
    
    if choice == "1":
        simple_airplay_click()
    elif choice == "2":
        print("\nAirPlay 버튼을 먼저 클릭하세요.")
        input("준비되면 Enter...")
        
        x = int(input("living 체크박스 X 좌표: "))
        y = int(input("living 체크박스 Y 좌표: "))
        
        click_specific_position(x, y)
        print("✅ 클릭 완료!")
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()