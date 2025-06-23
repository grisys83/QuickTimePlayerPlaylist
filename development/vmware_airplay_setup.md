# VMware Fusion으로 QuickTime AirPlay 전용 환경 구축

## VMware Fusion Player (무료 버전)
- 개인/비상업적 사용 무료
- macOS 게스트 OS 지원 (macOS 10.15+)

## 설정 아이디어

### 1. 가상 macOS 설치
```bash
# VMware Fusion Player 다운로드
# https://www.vmware.com/products/fusion/fusion-evaluation.html

# macOS 설치 (합법적으로는 Mac에서만 가능)
# macOS Monterey 이상 권장 (AirPlay 2 지원)
```

### 2. 네트워크 설정
```
VMware 네트워크 옵션:
- NAT: 호스트와 격리, 인터넷 접속 가능
- Bridged: 같은 네트워크, AirPlay 장치 접근 가능 ✅
- Host-only: 격리된 내부 네트워크
```

### 3. 최소 리소스 할당
```
- RAM: 4GB (음악 재생만)
- CPU: 2 cores
- 디스크: 40GB
- 그래픽: 최소 설정
```

### 4. 자동화 스크립트 (게스트 OS)
```bash
#!/bin/bash
# vm_airplay_daemon.sh

# 부팅 시 자동 실행
# ~/Library/LaunchAgents/com.quicktime.airplay.plist

# QuickTime 자동 시작
osascript -e 'tell application "QuickTime Player" to activate'

# 파일 감시 및 자동 재생
fswatch -o ~/Music/Queue/ | while read f; do
    python3 /Users/Shared/quicktime_airplay_simple.py \
        --device "HomePod" \
        --repeat-all \
        ~/Music/Queue/*_converted.mp4
done
```

### 5. 호스트-게스트 통신
```bash
# 호스트에서 게스트로 파일 전송
# VMware Shared Folders 사용

# 또는 SSH
ssh vmuser@vm-ip "python3 quicktime_play.py new_song.mp4"
```

### 6. 리소스 최적화
```bash
# 불필요한 서비스 끄기
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.Spotlight.plist
sudo launchctl unload -w /System/Library/LaunchAgents/com.apple.Siri.agent.plist

# 시각 효과 끄기
defaults write com.apple.universalaccess reduceMotion -bool true
defaults write com.apple.universalaccess reduceTransparency -bool true
```

## 장단점

### 장점 ✅
- 완전한 격리 환경
- 호스트 시스템 자유롭게 사용
- 스냅샷으로 안정적 상태 유지
- 여러 프로파일 관리 가능

### 단점 ❌
- RAM 사용 (최소 4GB)
- 초기 설정 복잡
- macOS 라이선스 (Mac에서만 합법)
- 네트워크 브리지 설정 필요

## 더 가벼운 대안

### 1. 별도 사용자 계정
```bash
# 전용 사용자 생성
sudo dscl . -create /Users/airplay
sudo dscl . -create /Users/airplay UserShell /bin/bash

# Fast User Switching
# 메뉴바에서 빠른 전환
```

### 2. Screen Sharing + 헤드리스
```bash
# 별도 사용자로 로그인 후
# Screen Sharing으로만 제어
# 실제 화면은 안 봐도 됨
```

### 3. Playground 모드
```bash
# macOS Sandbox 활용
sandbox-exec -f custom.sb /Applications/QuickTime\ Player.app/Contents/MacOS/QuickTime\ Player
```

## 추천 구성

**"QuickTime VM Jukebox"**
1. VMware Fusion Player (무료)
2. 최소 macOS 설치 
3. QuickTime + 변환 스크립트만
4. 웹 인터페이스로 제어

```python
# 호스트에서 실행하는 웹 컨트롤러
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/play/<song>')
def play(song):
    # VM에 SSH 명령 전송
    subprocess.run([
        'ssh', 'vm-airplay@vm-ip',
        f'python3 play.py {song}'
    ])
    return "Playing!"
```

이렇게 하면 완벽한 AirPlay 전용 머신 완성! 🎵