#!/bin/bash
# 카페 플레이리스트 런처
# 자동 시작 및 에러 복구 기능 포함

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 로그 디렉토리 생성
mkdir -p logs

# PID 파일
PID_FILE="cafe_playlist.pid"

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 상태 확인
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}실행 중${NC} (PID: $PID)"
            return 0
        else
            echo -e "${RED}중지됨${NC} (이전 PID: $PID)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${RED}실행되지 않음${NC}"
        return 1
    fi
}

# 시작
start_playlist() {
    if check_status > /dev/null; then
        echo -e "${YELLOW}이미 실행 중입니다.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}카페 플레이리스트 시작 중...${NC}"
    
    # 설정 파일 확인
    if [ ! -f "cafe_playlist_config.json" ]; then
        echo "설정 파일 생성 중..."
        python3 cafe_playlist_manager.py --create-config
    fi
    
    # 비디오 파일 확인
    VIDEO_COUNT=$(find . -maxdepth 1 \( -name "*.mp4" -o -name "*.mov" -o -name "*.m4v" -o -name "*.avi" \) | wc -l)
    if [ $VIDEO_COUNT -eq 0 ]; then
        echo -e "${YELLOW}현재 폴더에 비디오 파일이 없습니다.${NC}"
        echo -e "${YELLOW}지원 형식: .mp4, .mov, .m4v, .avi${NC}"
    fi
    
    # 백그라운드에서 실행
    nohup python3 cafe_playlist_manager.py > logs/cafe_playlist_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    if check_status > /dev/null; then
        echo -e "${GREEN}성공적으로 시작되었습니다.${NC}"
    else
        echo -e "${RED}시작 실패. 로그를 확인하세요.${NC}"
        return 1
    fi
}

# 중지
stop_playlist() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}플레이리스트 중지 중...${NC}"
        
        # Python 프로세스에 SIGTERM 전송
        kill -TERM "$PID" 2>/dev/null
        
        # 최대 10초 대기
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # 여전히 실행 중이면 강제 종료
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        
        # QuickTime도 종료
        osascript -e 'tell application "QuickTime Player" to quit'
        
        echo -e "${GREEN}중지되었습니다.${NC}"
    else
        echo -e "${YELLOW}실행 중이 아닙니다.${NC}"
    fi
}

# 재시작
restart_playlist() {
    stop_playlist
    sleep 2
    start_playlist
}

# 로그 보기
view_logs() {
    if [ -d "logs" ]; then
        # 최신 로그 파일 찾기
        LATEST_LOG=$(ls -t logs/cafe_playlist_*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            echo -e "${GREEN}로그 파일: $LATEST_LOG${NC}"
            tail -f "$LATEST_LOG"
        else
            echo -e "${YELLOW}로그 파일이 없습니다.${NC}"
        fi
    else
        echo -e "${YELLOW}로그 디렉토리가 없습니다.${NC}"
    fi
}

# 자동 시작 설정 (macOS LaunchAgent)
setup_autostart() {
    PLIST_FILE="$HOME/Library/LaunchAgents/com.cafe.playlist.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cafe.playlist</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/cafe_playlist_launcher.sh</string>
        <string>start</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd_error.log</string>
</dict>
</plist>
EOF
    
    launchctl load "$PLIST_FILE"
    echo -e "${GREEN}자동 시작이 설정되었습니다.${NC}"
}

# 자동 시작 해제
remove_autostart() {
    PLIST_FILE="$HOME/Library/LaunchAgents/com.cafe.playlist.plist"
    
    if [ -f "$PLIST_FILE" ]; then
        launchctl unload "$PLIST_FILE"
        rm -f "$PLIST_FILE"
        echo -e "${GREEN}자동 시작이 해제되었습니다.${NC}"
    else
        echo -e "${YELLOW}자동 시작이 설정되어 있지 않습니다.${NC}"
    fi
}

# 메인 메뉴
show_menu() {
    echo
    echo "=== 카페 플레이리스트 매니저 ==="
    echo "1. 시작"
    echo "2. 중지"
    echo "3. 재시작"
    echo "4. 상태 확인"
    echo "5. 로그 보기"
    echo "6. 자동 시작 설정"
    echo "7. 자동 시작 해제"
    echo "8. 종료"
    echo
    echo -n "선택: "
}

# 명령줄 인자 처리
case "$1" in
    start)
        start_playlist
        ;;
    stop)
        stop_playlist
        ;;
    restart)
        restart_playlist
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    autostart)
        setup_autostart
        ;;
    remove-autostart)
        remove_autostart
        ;;
    *)
        # 대화형 메뉴
        while true; do
            show_menu
            read choice
            
            case $choice in
                1) start_playlist ;;
                2) stop_playlist ;;
                3) restart_playlist ;;
                4) check_status ;;
                5) view_logs ;;
                6) setup_autostart ;;
                7) remove_autostart ;;
                8) echo "종료합니다."; exit 0 ;;
                *) echo -e "${RED}잘못된 선택입니다.${NC}" ;;
            esac
            
            echo
            read -p "계속하려면 Enter를 누르세요..."
        done
        ;;
esac