#!/usr/bin/osascript
(*
QuickTime AirPlay 제어 - 전체화면 모드 활용
전체화면에서 UI 요소가 고정되는 특성을 이용
*)

on run argv
    if (count of argv) < 1 then
        return "사용법: osascript quicktime_airplay_fullscreen.applescript <video_file> [airplay_device_index]"
    end if
    
    set videoPath to item 1 of argv
    set deviceIndex to 1
    
    if (count of argv) ≥ 2 then
        set deviceIndex to item 2 of argv as integer
    end if
    
    -- QuickTime Player 실행 및 비디오 열기
    tell application "QuickTime Player"
        activate
        open POSIX file videoPath
        delay 2
        
        -- 전체화면으로 전환 (UI 요소 고정)
        tell document 1
            set presentation mode to true
            play
        end tell
        
        delay 1
    end tell
    
    -- UI 자동화로 AirPlay 제어
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- 마우스를 움직여 컨트롤 표시
            -- 전체화면에서는 하단에 마우스를 가져가면 컨트롤이 나타남
            do shell script "cliclick m:640,719"  -- 화면 하단 (1280x720 기준)
            delay 1
            
            -- 전체화면 모드의 고정된 UI 구조
            tell window 1
                try
                    -- 컨트롤바 group 찾기
                    tell group 1
                        -- AirPlay 버튼은 보통 오른쪽에서 2-3번째
                        set buttonList to every button
                        set buttonCount to count of buttonList
                        
                        -- 뒤에서부터 버튼 확인
                        repeat with i from (buttonCount - 3) to buttonCount
                            if i > 0 and i ≤ buttonCount then
                                set targetButton to button i
                                
                                -- 버튼 정보 로깅
                                try
                                    set btnDesc to description of targetButton
                                    set btnHelp to help of targetButton
                                    set btnTitle to title of targetButton
                                    
                                    -- AirPlay 버튼 찾기
                                    if btnDesc contains "AirPlay" or btnHelp contains "AirPlay" then
                                        click targetButton
                                        delay 1
                                        
                                        -- AirPlay 기기 선택
                                        repeat deviceIndex times
                                            key code 125 -- 아래 화살표
                                            delay 0.2
                                        end repeat
                                        key code 36 -- Enter
                                        
                                        return "AirPlay 활성화 성공"
                                    end if
                                end try
                            end if
                        end repeat
                    end tell
                end try
                
                -- 대체 방법: 좌표 기반 클릭
                try
                    -- 전체화면에서 AirPlay 버튼의 예상 위치
                    do shell script "cliclick c:1180,680"  -- 1280x720 기준
                    delay 1
                    
                    -- 메뉴에서 기기 선택
                    do shell script "cliclick c:1180," & (680 - (deviceIndex * 25))
                    
                    return "AirPlay 활성화 (좌표 기반)"
                end try
            end tell
        end tell
    end tell
    
    return "AirPlay 버튼을 찾을 수 없습니다"
end run

-- 디버깅용: UI 요소 구조 출력
on debugUIElements()
    tell application "System Events"
        tell process "QuickTime Player"
            tell window 1
                set elementInfo to {}
                
                -- 모든 group 정보
                set groupList to every group
                repeat with grp in groupList
                    try
                        set grpBounds to position of grp & size of grp
                        set grpButtons to count of buttons of grp
                        set end of elementInfo to "Group: " & (grpBounds as string) & " - Buttons: " & grpButtons
                        
                        -- group 내 버튼 정보
                        repeat with btn in buttons of grp
                            try
                                set btnInfo to "  Button: " & (description of btn)
                                set end of elementInfo to btnInfo
                            end try
                        end repeat
                    end try
                end repeat
                
                return elementInfo
            end tell
        end tell
    end tell
end debugUIElements