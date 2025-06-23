#!/usr/bin/osascript
(*
QuickTime Player AirPlay UI 자동화
System Events를 사용하여 마우스 없이 AirPlay 제어
*)

on run argv
    if (count of argv) < 1 then
        display dialog "사용법: osascript quicktime_airplay_ui_automation.applescript <video_file> [airplay_device_name]"
        return
    end if
    
    set videoPath to item 1 of argv
    set airplayDevice to ""
    
    if (count of argv) ≥ 2 then
        set airplayDevice to item 2 of argv
    end if
    
    -- QuickTime Player 실행 및 비디오 열기
    tell application "QuickTime Player"
        activate
        open POSIX file videoPath
        delay 2
        play document 1
    end tell
    
    delay 1
    
    -- UI 자동화로 AirPlay 제어
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- 방법 1: 메뉴바에서 AirPlay 접근
            try
                -- View 메뉴에서 Show AirPlay Controls 찾기
                click menu item "Show AirPlay Controls" of menu "View" of menu bar 1
                delay 1
            end try
            
            -- 방법 2: 창 내 AirPlay 버튼 찾기
            tell window 1
                -- 모든 UI 요소 탐색
                set allButtons to every button
                repeat with aButton in allButtons
                    try
                        if description of aButton contains "AirPlay" then
                            click aButton
                            delay 1
                            exit repeat
                        end if
                    end try
                end repeat
                
                -- AirPlay 팝업이 나타나면 기기 선택
                try
                    -- 팝업 메뉴에서 기기 찾기
                    set airplayMenu to pop up button 1
                    click airplayMenu
                    delay 0.5
                    
                    if airplayDevice is not "" then
                        -- 특정 기기 선택
                        click menu item airplayDevice of menu 1 of airplayMenu
                    else
                        -- 첫 번째 AirPlay 기기 선택 (보통 index 2가 첫 기기)
                        click menu item 2 of menu 1 of airplayMenu
                    end if
                end try
            end tell
            
            -- 방법 3: 접근성 API 사용
            try
                set airplayButton to (first button whose help is "AirPlay")
                click airplayButton
                delay 1
                
                -- 키보드로 기기 선택
                key code 125 -- 아래 화살표
                key code 36  -- Enter
            end try
            
        end tell
    end tell
    
    display notification "AirPlay 설정 시도 완료" with title "QuickTime AirPlay"
    
end run

-- 헬퍼 함수: UI 요소 정보 출력 (디버깅용)
on logUIElements()
    tell application "System Events"
        tell process "QuickTime Player"
            tell window 1
                set elementList to {}
                
                -- 모든 버튼 정보 수집
                set allButtons to every button
                repeat with aButton in allButtons
                    try
                        set buttonInfo to "Button: " & (description of aButton) & " - " & (title of aButton)
                        set end of elementList to buttonInfo
                    end try
                end repeat
                
                -- 모든 UI 요소 정보 수집
                set allElements to every UI element
                repeat with anElement in allElements
                    try
                        set elementInfo to (class of anElement as string) & ": " & (description of anElement)
                        set end of elementList to elementInfo
                    end try
                end repeat
                
                return elementList
            end tell
        end tell
    end tell
end logUIElements