#!/usr/bin/osascript
(*
HTTP URL 기반 QuickTime 플레이리스트
고정 URL을 통해 동적으로 비디오를 교체하며 재생
*)

on run argv
    -- 설정
    set httpURL to "http://grisys.synology.me/video.mp4"
    set localPath to "/Volumes/web/video.mp4"
    
    -- 비디오 파일 목록 (인자로 받거나 직접 지정)
    set videoFiles to {}
    if (count of argv) > 0 then
        repeat with i from 1 to count of argv
            set end of videoFiles to item i of argv
        end repeat
    else
        -- 테스트용 기본 파일들
        set videoFiles to {"video1.mp4", "video2.mp4", "video3.mp4"}
    end if
    
    -- 원본 파일 백업
    do shell script "cp '" & localPath & "' '" & localPath & ".backup' 2>/dev/null || true"
    
    -- QuickTime Player 활성화
    tell application "QuickTime Player"
        activate
    end tell
    
    -- 각 비디오 재생
    repeat with videoFile in videoFiles
        -- 파일 교체
        display notification "재생 중: " & videoFile
        do shell script "cp '" & videoFile & "' '" & localPath & "'"
        delay 1 -- 파일 시스템 동기화 대기
        
        -- QuickTime에서 URL 열기
        tell application "QuickTime Player"
            -- 기존 문서 닫기
            if (count documents) > 0 then
                close every document
            end if
            
            delay 0.5
            
            -- HTTP URL 열기
            open location httpURL
            
            delay 2 -- 로딩 대기
            
            -- 재생 시작
            tell document 1
                play
                
                -- 전체화면 (선택사항)
                -- set presentation mode to true
            end tell
            
            -- 재생 완료 대기
            repeat while (playing of document 1 is true)
                delay 1
            end repeat
            
            delay 0.5
        end tell
    end repeat
    
    -- QuickTime 종료
    tell application "QuickTime Player"
        if (count documents) > 0 then
            close every document
        end if
        quit
    end tell
    
    -- 원본 파일 복원
    do shell script "mv '" & localPath & ".backup' '" & localPath & "' 2>/dev/null || true"
    
    display notification "플레이리스트 재생 완료" with title "QuickTime HTTP Playlist"
    
end run