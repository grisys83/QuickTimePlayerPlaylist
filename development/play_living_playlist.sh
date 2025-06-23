#!/bin/bash
# Living AirPlay 플레이리스트 실행 스크립트

# 사용법 표시
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "사용법: $0 [비디오파일1] [비디오파일2] ..."
    echo "또는: $0 (videos 폴더의 모든 비디오 재생)"
    exit 0
fi

# 비디오 파일이 인자로 주어진 경우
if [ $# -gt 0 ]; then
    echo "Living으로 플레이리스트 재생 시작..."
    
    # 첫 번째 비디오로 AirPlay 설정
    FIRST_VIDEO="$1"
    osascript quicktime_airplay_living.applescript "$FIRST_VIDEO"
    
    # 첫 비디오 재생 완료 대기
    while true; do
        STATUS=$(osascript -e 'tell application "QuickTime Player"
            if (count documents) > 0 then
                if playing of document 1 then
                    return "playing"
                else
                    return "stopped"
                end if
            else
                return "no_document"
            end if
        end tell')
        
        if [ "$STATUS" != "playing" ]; then
            break
        fi
        sleep 2
    done
    
    # 나머지 비디오 재생
    shift  # 첫 번째 인자 제거
    for VIDEO in "$@"; do
        echo "재생: $VIDEO"
        
        osascript -e "
        tell application \"QuickTime Player\"
            close document 1
            delay 0.5
            open POSIX file \"$VIDEO\"
            delay 1
            tell document 1
                play
                set presentation mode to true
            end tell
        end tell"
        
        # 재생 완료 대기
        while true; do
            STATUS=$(osascript -e 'tell application "QuickTime Player"
                if (count documents) > 0 then
                    if playing of document 1 then
                        return "playing"
                    else
                        return "stopped"
                    end if
                else
                    return "no_document"
                end if
            end tell')
            
            if [ "$STATUS" != "playing" ]; then
                break
            fi
            sleep 2
        done
        
        sleep 2  # 비디오 간 대기
    done
    
else
    # 인자가 없으면 Python 스크립트 실행 (현재 폴더 사용)
    echo "현재 폴더의 비디오를 Living으로 재생합니다..."
    python3 cafe_playlist_living.py
fi

echo "플레이리스트 재생 완료"