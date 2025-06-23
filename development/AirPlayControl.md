# QuickTime AirPlay 제어 방법

## 🚫 QuickTime의 한계
- QuickTime Player는 CLI 인수를 지원하지 않음
- AppleScript로 AirPlay 장치 선택 불가
- 프로그램적으로 출력 장치 변경 불가

## 🔧 대안 솔루션

### 1. 시스템 오디오 라우팅 도구

#### SwitchAudioSource 설치 및 사용
```bash
# 설치
brew install switchaudio-osx

# 사용 가능한 장치 목록
SwitchAudioSource -a

# 특정 장치로 전환
SwitchAudioSource -s "Apple TV"
```

#### 스크립트에 통합
```bash
#!/bin/bash
# AirPlay 장치로 전환 후 QuickTime 실행
SwitchAudioSource -s "거실 TV"
osascript PlayVideosInOrder.applescript
```

### 2. 시스템 환경설정 사용
```applescript
-- 시스템 환경설정으로 AirPlay 제어 (제한적)
tell application "System Preferences"
    activate
    set current pane to pane "com.apple.preference.sound"
end tell
```

### 3. 키보드 단축키 활용
QuickTime에서 AirPlay 메뉴 접근:
- ⌃⌘A (Control+Command+A) - AirPlay 메뉴 열기

### 4. Python + PyObjC 솔루션
```python
# 오디오 출력 장치 목록 가져오기
from AppKit import NSSound
import AudioToolbox

# 사용 가능한 장치 확인
devices = AudioToolbox.AudioHardwareGetProperty(
    AudioToolbox.kAudioHardwarePropertyDevices
)
```

### 5. 추천 워크플로우

1. **자동화 스크립트 생성**
```bash
#!/bin/bash
# set_airplay_and_play.sh

# AirPlay 장치 설정
echo "Setting AirPlay device..."
SwitchAudioSource -s "$1"

# QuickTime으로 비디오 재생
shift  # 첫 번째 인수(장치명) 제거
osascript PlayVideosInOrder.applescript "$@"
```

2. **사용 예시**
```bash
./set_airplay_and_play.sh "Apple TV" video1.mp4 video2.mp4
```

## 📱 iOS 기기 활용

AirPlay를 더 쉽게 제어하려면:
1. iPhone/iPad의 단축어 앱 사용
2. HomeKit 자동화와 연동
3. Shortcuts를 Mac에서 실행

## 🔍 디버깅 팁

현재 오디오 출력 확인:
```bash
# 현재 출력 장치
system_profiler SPAudioDataType | grep "Default Output Device"

# AirPlay 상태 확인
defaults read com.apple.airplay
```