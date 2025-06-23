#!/usr/bin/osascript
(*
QuickTime AirPlay - Living 기기 전용
스크린샷에서 확인한 정확한 좌표 사용
*)

on run argv
    if (count of argv) < 1 then
        return "사용법: osascript quicktime_airplay_living.applescript <video_file>"
    end if
    
    set videoPath to item 1 of argv
    
    -- QuickTime Player 실행 및 비디오 열기
    tell application "QuickTime Player"
        activate
        
        -- 파일 경로를 안전하게 처리
        set videoFile to POSIX file videoPath
        open videoFile
        delay 2
        
        -- 전체화면으로 전환
        tell document 1
            set presentation mode to true
            play
        end tell
        
        delay 1
    end tell
    
    -- cliclick으로 정확한 좌표 클릭
    try
        -- 컨트롤바 표시를 위해 마우스를 하단으로 이동
        do shell script "cliclick m:640,700"
        delay 1
        
        -- AirPlay 버튼 클릭 (실제 측정한 좌표)
        do shell script "cliclick c:970,784"  -- AirPlay 버튼
        delay 1
        
        -- Living 선택 (실제 측정한 좌표)
        do shell script "cliclick c:842,710"  -- Living 항목
        
        return "Living으로 AirPlay 설정 완료"
        
    on error errMsg
        return "에러: " & errMsg
    end try
    
end run