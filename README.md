# QuickTime Playlist Pro 🎵

> **QuickTime Player를 위한 플레이리스트 기능 확장**  
> HomePod 및 AirPlay 디바이스에서 로컬 음악 연속 재생 지원

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/quicktime-playlist-pro)
[![macOS](https://img.shields.io/badge/macOS-10.14+-green.svg)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

## 🌟 왜 이 앱이 필요한가?

QuickTime Player는 기본적으로 한 번에 하나의 파일만 재생할 수 있습니다. 이 프로젝트는 플레이리스트 기능을 추가하여 여러 파일을 연속으로 재생할 수 있게 해주며, 특히 HomePod과 같은 AirPlay 디바이스에서 로컬 음악 파일을 편리하게 감상할 수 있도록 지원합니다.

## ✨ 주요 기능

### 🎯 플레이리스트 자동 재생
- QuickTime의 단일 파일 제한 극복
- 순차/셔플/반복 재생 지원
- 실시간 재생 큐 관리

### 🏠 HomePod AirPlay 자동화
- "Living" 디바이스 자동 연결
- 매 트랙마다 AirPlay 설정
- 연결 끊김 자동 복구

### 🎨 오디오 시각화
- 오디오 파일을 아름다운 비디오로 변환
- 앨범 아트, 제목, 아티스트 표시
- HD 품질 출력

### ☕ 카페/매장 모드
- 24시간 연속 재생
- 자동 오류 복구
- 운영 시간 설정

## 📋 필요 사항

- macOS (QuickTime Player 필수)
- Python 3.x
- cliclick (AirPlay 자동화용): `brew install cliclick`

### 선택적 요구사항
- PyAutoGUI (마우스 자동화): `pip3 install pyautogui`
- PyObjC (AirPlay 기능): `pip3 install pyobjc-framework-AVFoundation`

## ⚠️ 중요: AirPlay 자동화를 위한 보안 설정

**AirPlay 기능을 사용하려면 반드시 macOS 보안 설정을 변경해야 합니다!**

1. **시스템 설정** → **개인정보 보호 및 보안** → **손쉬운 사용**
2. 자물쇠🔒를 클릭하여 변경 허용
3. **+** 버튼을 눌러 다음 앱들을 추가:
   - Python (`/usr/local/bin/python3` 또는 `/Library/Frameworks/Python.framework/`)
   - Terminal (`/Applications/Utilities/`)
4. 체크박스 ✅가 모두 선택되었는지 확인

**이 설정 없이는 AirPlay 자동화가 작동하지 않습니다!**

자세한 설정 방법: [SECURITY_SETUP.md](SECURITY_SETUP.md) 참조

## 🚀 빠른 시작

### 1. 기본 플레이리스트 재생

```bash
# AppleScript 버전 (드래그 앤 드롭 지원)
osascript PlayVideosInOrder.applescript

# Python GUI 버전
python3 quicktime_playlist_gui.py

# 명령줄에서 직접 재생
osascript PlayVideosDirect.applescript video1.mp4 video2.mp4
```

### 2. AirPlay로 재생 (Living 기기)

```bash
# 단일 비디오
osascript quicktime_airplay_living.applescript "video.mp4"

# 플레이리스트
./play_living_playlist.sh video1.mp4 video2.mp4 video3.mp4
```

### 3. 카페/매장용 자동 재생

```bash
# 설정 파일 생성
python3 cafe_playlist_manager.py --create-config

# videos 폴더에 비디오 추가 후 실행
./cafe_playlist_launcher.sh start
```

## 📁 파일 구조

### 핵심 스크립트

| 파일명 | 설명 | 사용법 |
|--------|------|--------|
| `PlayVideosInOrder.applescript` | 드래그 앤 드롭 플레이리스트 | 파일을 스크립트에 드롭 |
| `quicktime_playlist_gui.py` | GUI 플레이리스트 관리자 | `python3 quicktime_playlist_gui.py` |
| `quicktime_airplay_living.applescript` | Living AirPlay 재생 | `osascript quicktime_airplay_living.applescript video.mp4` |
| `cafe_playlist_manager.py` | 카페용 자동 재생 시스템 | `python3 cafe_playlist_manager.py` |

### AirPlay 관련

| 파일명 | 설명 |
|--------|------|
| `quicktime_with_airplay.py` | PyObjC 기반 AirPlay 제어 |
| `quicktime_airplay_mouse_control.py` | 마우스 자동화로 AirPlay 제어 |
| `quicktime_airplay_fullscreen.applescript` | 전체화면 모드에서 AirPlay |

### 유틸리티

| 파일명 | 설명 |
|--------|------|
| `http_playlist_controller.py` | HTTP URL 기반 동적 플레이리스트 |
| `cafe_playlist_launcher.sh` | 카페 플레이리스트 관리 도구 |
| `create_automator_workflow.sh` | Automator 워크플로우 생성 |

## 🎮 사용 예시

### 1. 간단한 플레이리스트
```bash
# GUI로 플레이리스트 관리
python3 quicktime_playlist_gui.py

# 파일 3개 순서대로 재생
osascript PlayVideosDirect.applescript movie1.mp4 movie2.mp4 movie3.mp4
```

### 2. AirPlay로 TV에서 재생
```bash
# Living 기기로 재생
osascript quicktime_airplay_living.applescript "presentation.mp4"

# 여러 비디오를 Living으로 재생
./play_living_playlist.sh intro.mp4 main.mp4 outro.mp4
```

### 3. 카페에서 하루종일 재생
```bash
# 1. 비디오 파일을 스크립트와 같은 폴더에 복사
cp ~/Movies/*.mp4 ./

# 2. 카페 플레이리스트 실행
python3 cafe_playlist_living.py

# 또는 런처 사용
./cafe_playlist_launcher.sh

# 특정 폴더의 비디오 재생
python3 cafe_playlist_living.py ~/Movies/
```

## ⚙️ 카페 플레이리스트 설정

`cafe_playlist_config.json` 파일로 세부 설정 가능:

```json
{
    "playlist_folder": ".",  // 현재 폴더 (기본값)
    "shuffle": true,
    "repeat": true,
    "volume": 70,
    "airplay_device_index": 1,
    "business_hours": {
        "enabled": true,
        "start": "09:00",
        "end": "22:00"
    },
    "fullscreen": true
}
```

## 🔧 문제 해결

### QuickTime이 AirPlay 기기를 찾지 못할 때
1. 같은 Wi-Fi 네트워크에 연결되어 있는지 확인
2. AirPlay 기기의 전원이 켜져 있는지 확인
3. 시스템 환경설정 > 디스플레이에서 AirPlay 확인

### cliclick 관련 오류
```bash
# cliclick 설치
brew install cliclick

# 권한 문제 시
시스템 환경설정 > 보안 및 개인 정보 보호 > 접근성에서 터미널 허용
```

### Python 모듈 오류
```bash
# 필요한 모듈 설치
pip3 install pyautogui pillow
pip3 install pyobjc-framework-AVFoundation
```

## 📝 주요 제한사항

1. **macOS 전용**: QuickTime Player와 AppleScript 의존
2. **순차 재생만 가능**: QuickTime의 한계로 동시 재생 불가
3. **AirPlay 제어 제한**: QuickTime의 AirPlay는 프로그래밍 방식으로 직접 제어 불가 (마우스 자동화 필요)

## 🤝 기여하기

이 프로젝트는 Apple의 제한적인 정책에 맞서는 오픈소스 프로젝트입니다.

1. Fork 하기
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 커밋하기 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 열기

### 기여 가이드라인
- Apple의 API 제한을 우회하는 창의적인 방법 환영
- HomePod 사용자 경험 개선 아이디어
- 버그 수정 및 성능 개선
- 문서화 개선

## 📖 추가 문서

- [프로젝트 선언문](PROJECT_MANIFESTO.md) - 왜 이 앱이 필요한가
- [기술 분석](TECHNICAL_BREAKDOWN.md) - 어떻게 Apple의 제한을 극복했나
- [CLAUDE.md](CLAUDE.md) - AI 어시스턴트를 위한 가이드

## ⚖️ 라이선스

MIT License - 자유롭게 사용하고 수정하세요!

```
MIT License

Copyright (c) 2024 QuickTime Playlist Pro Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 감사의 말

- HomePod 커뮤니티
- r/HomePod 레딧 사용자들
- 이 프로젝트를 함께 만든 모든 기여자들
- 오픈소스 커뮤니티

## 📢 언론 보도 (예정)

이 프로젝트가 화제가 되면 여기에 기록됩니다!

---

> **로컬 미디어 파일의 자유로운 재생을 위한 오픈소스 솔루션**

### 🌐 링크

- [GitHub 저장소](https://github.com/yourusername/quicktime-playlist-pro) *(곧 공개 예정)*
- [HomePod 커뮤니티](https://reddit.com/r/HomePod)
- [프로젝트 웹사이트](https://quicktime-playlist-pro.com) *(준비 중)*

### #️⃣ 해시태그

`#openhomepod` `#openairplay2` `#quicktimeplaylist` `#opensource`