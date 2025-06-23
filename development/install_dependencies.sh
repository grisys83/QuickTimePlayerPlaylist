#!/bin/bash
# 의존성 설치 스크립트

echo "QuickTime Playlist 의존성 설치"
echo "=============================="

# Homebrew 확인
if ! command -v brew &> /dev/null; then
    echo "Homebrew가 필요합니다. 설치하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew 설치를 건너뜁니다."
    fi
fi

# ffmpeg 설치
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg 설치 중..."
    brew install ffmpeg
else
    echo "✓ ffmpeg 이미 설치됨"
fi

# cliclick 설치
if ! command -v cliclick &> /dev/null; then
    echo "cliclick 설치 중..."
    brew install cliclick
else
    echo "✓ cliclick 이미 설치됨"
fi

# Python 패키지 설치
echo ""
echo "Python 패키지 설치 중..."

# 기본 패키지
pip3 install --upgrade pip

# GUI 관련
pip3 install pyautogui pillow

# 메타데이터 처리
pip3 install mutagen

# AirPlay 지원 (선택사항)
echo ""
echo "AirPlay 지원을 설치하시겠습니까? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    pip3 install pyobjc-framework-AVFoundation
fi

echo ""
echo "설치 완료!"
echo ""
echo "실행 방법:"
echo "  기본 플레이리스트: python3 quicktime_playlist_gui.py"
echo "  큐 시스템: python3 quicktime_playlist_queue.py"
echo "  카페 모드: python3 cafe_playlist_living_final.py"
echo "  오디오 변환: python3 audio_to_video_enhanced.py [audio_file]"