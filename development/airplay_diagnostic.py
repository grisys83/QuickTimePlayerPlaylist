#!/usr/bin/env python3
"""
AirPlay Diagnostic Tool
Helps diagnose why AirPlay enabling isn't working
"""

import subprocess
import time
import pyautogui
from pathlib import Path

def diagnose_quicktime():
    """Diagnose QuickTime state"""
    print("🔍 QuickTime Diagnostic")
    print("=" * 50)
    
    # Check if QuickTime is running
    script = '''
    tell application "System Events"
        if exists (process "QuickTime Player") then
            tell process "QuickTime Player"
                set windowCount to count of windows
                if windowCount > 0 then
                    set windowName to name of window 1
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    return "Running with " & windowCount & " window(s). First window: " & windowName & ¬
                           " at " & (item 1 of windowPos as string) & "," & (item 2 of windowPos as string) & ¬
                           " size " & (item 1 of windowSize as string) & "x" & (item 2 of windowSize as string)
                else
                    return "Running but no windows open"
                end if
            end tell
        else
            return "Not running"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"\n📍 QuickTime status: {result.stdout.strip()}")
    
    # Check if video is playing
    script2 = '''
    tell application "QuickTime Player"
        if (count of documents) > 0 then
            tell document 1
                return "Document: " & name & ", Playing: " & (playing as string)
            end tell
        else
            return "No documents open"
        end if
    end tell
    '''
    
    result2 = subprocess.run(['osascript', '-e', script2], capture_output=True, text=True)
    print(f"📍 Video status: {result2.stdout.strip()}")

def test_control_visibility():
    """Test if controls are visible"""
    print("\n\n🔍 Testing Control Visibility")
    print("=" * 50)
    
    # Activate QuickTime
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    width, height = pyautogui.size()
    
    print("\n1️⃣ Moving mouse to show controls...")
    positions = [
        (width // 2, height - 100, "Center bottom"),
        (width // 2, height - 50, "Very bottom"),
        (width - 150, height - 50, "Right bottom"),
    ]
    
    for x, y, desc in positions:
        print(f"   Moving to {desc} ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(1)
    
    print("\n2️⃣ Take a screenshot to check controls...")
    screenshot = pyautogui.screenshot()
    debug_path = Path.home() / "quicktime_controls_debug.png"
    screenshot.save(debug_path)
    print(f"   💾 Saved: {debug_path}")
    
    print("\n3️⃣ Common AirPlay button positions:")
    print("   Based on window at default position:")
    print(f"   - Typical: ({width - 150}, {height - 50})")
    print(f"   - Alternative 1: ({width - 200}, {height - 50})")
    print(f"   - Alternative 2: ({width - 300}, {height - 100})")

def interactive_position_finder():
    """Interactive tool to find exact positions"""
    print("\n\n🎯 Interactive Position Finder")
    print("=" * 50)
    
    print("\n마우스를 움직여서 정확한 위치를 찾으세요")
    print("숫자 키를 눌러 위치를 마크하세요:")
    print("1 - AirPlay 버튼")
    print("2 - 체크박스")
    print("ESC - 종료")
    
    positions = {}
    
    print("\n실시간 마우스 위치:")
    try:
        while True:
            x, y = pyautogui.position()
            rgb = pyautogui.pixel(x, y)
            print(f"\r위치: ({x:4d}, {y:4d})  색상: RGB{rgb}        ", end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n종료됨")

def test_click_sequence():
    """Test the full click sequence with pauses"""
    print("\n\n🧪 Testing Click Sequence")
    print("=" * 50)
    
    # Load saved position if available
    import json
    saved_file = Path.home() / '.airplay_manual_positions.json'
    checkbox_pos = None
    
    if saved_file.exists():
        with open(saved_file, 'r') as f:
            data = json.load(f)
            checkbox_pos = data['manual_positions']['last_checkbox']
            print(f"\n✅ Using saved checkbox position: ({checkbox_pos['x']}, {checkbox_pos['y']})")
    
    print("\n단계별 테스트를 시작합니다...")
    
    # Step 1
    print("\n1️⃣ QuickTime 활성화")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(2)
    
    # Step 2
    width, height = pyautogui.size()
    print("\n2️⃣ 컨트롤 표시")
    pyautogui.moveTo(width // 2, height - 50, duration=0.5)
    time.sleep(2)
    
    # Step 3
    print("\n3️⃣ AirPlay 클릭 (일반적인 위치)")
    airplay_x = width - 150
    airplay_y = height - 50
    print(f"   위치: ({airplay_x}, {airplay_y})")
    pyautogui.click(airplay_x, airplay_y)
    
    print("\n   ⏸️  AirPlay 메뉴가 열렸나요? (3초 대기)")
    time.sleep(3)
    
    # Step 4
    if checkbox_pos:
        print(f"\n4️⃣ 저장된 체크박스 위치 클릭: ({checkbox_pos['x']}, {checkbox_pos['y']})")
        pyautogui.moveTo(checkbox_pos['x'], checkbox_pos['y'], duration=0.5)
        time.sleep(1)
        pyautogui.click()
    else:
        print("\n4️⃣ 체크박스 위치를 수동으로 설정하세요")
        print("   10초 드립니다...")
        for i in range(10, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        print("\n   클릭!")
        pyautogui.click()

def main():
    print("🔧 AirPlay Diagnostic Tool")
    
    # Run diagnostics
    diagnose_quicktime()
    test_control_visibility()
    
    print("\n\n📋 다음 단계:")
    print("1. 스크린샷을 확인하여 컨트롤이 보이는지 확인")
    print("2. AirPlay 버튼의 정확한 위치 확인")
    print("3. test_click_sequence()로 단계별 테스트")
    
    # Run click sequence test
    print("\n\n클릭 시퀀스 테스트를 시작하시겠습니까?")
    print("3초 후 시작합니다...")
    time.sleep(3)
    
    test_click_sequence()

if __name__ == "__main__":
    main()