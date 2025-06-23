#!/bin/bash
# QuickTime AirPlay를 cliclick으로 제어하는 스크립트
# cliclick: 명령줄에서 마우스를 제어하는 도구

# cliclick 설치 확인
if ! command -v cliclick &> /dev/null; then
    echo "cliclick이 설치되어 있지 않습니다."
    echo "설치: brew install cliclick"
    exit 1
fi

# 사용법 확인
if [ $# -lt 1 ]; then
    echo "사용법: $0 <video_file> [airplay_device_index]"
    echo "예시: $0 video.mp4 1"
    exit 1
fi

VIDEO_FILE="$1"
DEVICE_INDEX="${2:-1}"  # 기본값: 첫 번째 AirPlay 기기

# QuickTime Player 실행 및 비디오 열기
osascript -e "
tell application \"QuickTime Player\"
    activate
    open POSIX file \"$VIDEO_FILE\"
    delay 2
    play document 1
    
    -- 창 정보 가져오기
    set windowBounds to bounds of window 1
    set windowX to item 1 of windowBounds
    set windowY to item 2 of windowBounds
    set windowWidth to (item 3 of windowBounds) - windowX
    set windowHeight to (item 4 of windowBounds) - windowY
    
    -- 좌표 반환
    return (windowX as string) & \",\" & (windowY as string) & \",\" & (windowWidth as string) & \",\" & (windowHeight as string)
end tell
" > /tmp/qt_window_info.txt

# 창 정보 파싱
WINDOW_INFO=$(cat /tmp/qt_window_info.txt)
IFS=',' read -r WIN_X WIN_Y WIN_WIDTH WIN_HEIGHT <<< "$WINDOW_INFO"

echo "QuickTime 창 정보: X=$WIN_X, Y=$WIN_Y, Width=$WIN_WIDTH, Height=$WIN_HEIGHT"

# 컨트롤바 표시를 위해 마우스를 비디오 중앙으로 이동
CENTER_X=$((WIN_X + WIN_WIDTH / 2))
CENTER_Y=$((WIN_Y + WIN_HEIGHT / 2))
BOTTOM_Y=$((WIN_Y + WIN_HEIGHT - 50))

echo "컨트롤바 표시 중..."
cliclick m:$CENTER_X,$CENTER_Y
sleep 0.5
cliclick m:$CENTER_X,$BOTTOM_Y
sleep 1

# AirPlay 버튼 위치 계산 (보통 오른쪽에서 두 번째)
AIRPLAY_X=$((WIN_X + WIN_WIDTH - 100))
AIRPLAY_Y=$((WIN_Y + WIN_HEIGHT - 30))

echo "AirPlay 버튼 클릭: X=$AIRPLAY_X, Y=$AIRPLAY_Y"
cliclick c:$AIRPLAY_X,$AIRPLAY_Y
sleep 1

# AirPlay 메뉴가 나타났으면 기기 선택
# 메뉴는 보통 클릭 위치 위에 나타남
MENU_Y=$((AIRPLAY_Y - 50 - (DEVICE_INDEX * 25)))
echo "AirPlay 기기 선택: Y=$MENU_Y"
cliclick c:$AIRPLAY_X,$MENU_Y

echo "AirPlay 설정 완료"