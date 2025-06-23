# QuickTime Player Playlist 🎵

QuickTime Player에 플레이리스트 기능을 추가하여 여러 파일을 연속 재생할 수 있게 해주는 macOS 앱입니다.

## 주요 기능

### 🎯 핵심 기능
- **플레이리스트 관리**: 오디오/비디오 파일을 드래그 앤 드롭으로 추가
- **자동 연속 재생**: QuickTime의 한 번에 하나만 재생되는 제한 극복
- **AirPlay 자동화**: HomePod 등 AirPlay 기기 자동 연결
- **오디오→비디오 변환**: 오디오 파일을 비디오로 변환하여 재생

### 🎮 재생 컨트롤
- 재생/일시정지/정지
- 이전/다음 트랙
- 셔플 재생
- 반복 재생 (한 곡/전체)
- 플레이리스트 저장/불러오기

## 설치 방법

### 필수 요구사항
- macOS 10.14 이상
- Python 3.x
- QuickTime Player

### 설치
```bash
# 저장소 클론
git clone https://github.com/grisys83/QuickTimePlayerPlaylist.git
cd QuickTimePlayerPlaylist

# Python 의존성 설치
pip3 install -r requirements.txt

# 필수 도구 설치
brew install ffmpeg          # 오디오→비디오 변환에 필요
brew install cliclick        # AirPlay 자동화에 필요
```

## 사용법

⚠️ **중요**: AirPlay 자동화를 포함한 모든 기능을 사용하려면 터미널에서 직접 실행하세요. PyInstaller로 빌드된 독립 실행형 앱은 macOS 보안 제한으로 인해 AirPlay 자동화가 작동하지 않을 수 있습니다.

### 오디오 플레이리스트
```bash
python3 QuickTimePlayerAudioPlaylist.py
```

### 비디오 플레이리스트
```bash
python3 QuickTimePlayerVideoPlaylist.py
```

### 오디오→비디오 변환기
```bash
python3 AudioVideoConverterGUI.py
```

## ⚠️ 중요: AirPlay 자동화 설정

AirPlay 자동화 기능을 사용하려면 macOS 보안 설정이 필요합니다:

1. **시스템 설정** → **개인정보 보호 및 보안** → **손쉬운 사용**
2. Python과 Terminal 앱 추가 및 권한 부여
3. 자세한 설정 방법: [SECURITY_SETUP.md](SECURITY_SETUP.md) 참조

## 프로젝트 구조

```
QuickTimePlayerPlaylist/
├── QuickTimePlayerAudioPlaylist.py  # 오디오 플레이리스트 앱
├── QuickTimePlayerVideoPlaylist.py  # 비디오 플레이리스트 앱
├── AudioVideoConverterGUI.py        # 오디오→비디오 변환기
├── audio_to_video_minimal.py       # 변환 핵심 모듈 (ALAC 지원)
├── requirements.txt                 # Python 의존성
├── SECURITY_SETUP.md               # 보안 설정 가이드
└── development/                    # 개발 중인 기능들
```

## 기술적 특징

- **PyQt5 기반 GUI**: 현대적이고 반응형 인터페이스
- **AppleScript 통합**: QuickTime Player 직접 제어
- **JSON 설정 관리**: 플레이리스트와 설정 저장
- **멀티스레드 처리**: UI 차단 없는 부드러운 재생
- **ALAC 오디오 코덱**: 변환된 비디오의 무손실 오디오 품질
- **정확한 재생시간 처리**: ffprobe를 이용한 올바른 비디오 길이

## 알려진 제한사항

- QuickTime Player는 한 번에 하나의 파일만 재생 가능 (순차 재생으로 해결)
- AirPlay 제어는 마우스 자동화 필요 (macOS API 제한)
- macOS 전용 (QuickTime Player 의존)

## 기여하기

Pull Request와 이슈 제보를 환영합니다!

## 라이선스

MIT License - 자유롭게 사용하고 수정하세요.

---

#openhomepod #openairplay2