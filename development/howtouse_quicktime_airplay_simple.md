# QuickTime AirPlay Simple 사용법

## 개요
`quicktime_airplay_simple.py`는 오디오 파일을 변환한 `_converted.mp4` 비디오를 QuickTime Player로 재생하는 간단한 도구입니다. AirPlay 기기 선택과 반복 재생을 지원합니다.

## 사전 준비

### 1. 필요한 도구 설치
```bash
# SwitchAudioSource 설치 (AirPlay 기기 선택용)
brew install switchaudio-osx

# Python 패키지 설치 (오디오 변환용)
pip3 install mutagen pillow
```

### 2. 오디오 파일을 비디오로 변환
```bash
# 단일 파일 변환
python3 audio_to_video_minimal.py "song.mp3"

# 여러 파일 일괄 변환
python3 audio_to_video_minimal.py *.flac *.mp3

# 변환된 파일은 *_converted.mp4로 저장됨
```

## 기본 사용법

### AirPlay 기기 목록 확인
```bash
python3 quicktime_airplay_simple.py --list-devices
```

### 기본 재생
```bash
# 변환된 비디오 직접 재생
python3 quicktime_airplay_simple.py song_converted.mp4

# 오디오 파일 경로로 재생 (자동으로 _converted.mp4 찾음)
python3 quicktime_airplay_simple.py song.mp3 song2.flac

# 디렉토리의 모든 변환된 비디오 재생
python3 quicktime_airplay_simple.py /music/folder/
```

### AirPlay 기기 지정
```bash
# 'living' 기기로 재생
python3 quicktime_airplay_simple.py --device 'living' *.mp3

# HomePod으로 재생
python3 quicktime_airplay_simple.py --device 'HomePod' song.mp3
```

### 반복 재생 옵션

#### 한 곡 반복 (--repeat-one)
```bash
# 첫 번째 곡만 무한 반복
python3 quicktime_airplay_simple.py --repeat-one song.mp3

# QuickTime의 루프 기능 사용 (Option+Command+L)
# 중지하려면 Cmd+Q
```

#### 전체 반복 (--repeat-all)
```bash
# 모든 곡을 순서대로 반복
python3 quicktime_airplay_simple.py --repeat-all *.mp3

# 중지하려면 Ctrl+C
```

## 실전 예제

### 카페/매장 운영
```bash
# 1. 플레이리스트 폴더의 모든 음악을 비디오로 변환
python3 audio_to_video_minimal.py /카페음악/*.mp3

# 2. HomePod으로 전체 반복 재생
python3 quicktime_airplay_simple.py --device 'HomePod' --repeat-all /카페음악/
```

### 파티 모드
```bash
# 파티 음악을 랜덤하게 재생
ls 파티음악/*_converted.mp4 | sort -R | xargs python3 quicktime_airplay_simple.py --device 'living'
```

### 수면 음악
```bash
# 한 곡만 반복 재생
python3 quicktime_airplay_simple.py --repeat-one --device 'bedroom' 수면음악_converted.mp4
```

## 주의사항

1. **변환 필수**: 오디오 파일은 먼저 `audio_to_video_minimal.py`로 변환해야 합니다
2. **파일명 규칙**: 변환된 파일은 `원본파일명_converted.mp4` 형식입니다
3. **전체화면**: QuickTime은 자동으로 전체화면으로 재생됩니다
4. **중지 방법**: 
   - 일반 재생: 자동 종료
   - 한 곡 반복: Cmd+Q로 QuickTime 종료
   - 전체 반복: Ctrl+C로 스크립트 중지

## 문제 해결

### "No converted video found" 오류
```bash
# 해결: 먼저 비디오로 변환
python3 audio_to_video_minimal.py 음악파일.mp3
```

### AirPlay 기기가 목록에 없음
```bash
# 시스템 환경설정 > 사운드에서 기기 확인
# Wi-Fi 연결 상태 확인
```

### SwitchAudioSource not found
```bash
# Homebrew 설치 후
brew install switchaudio-osx
```

---

## 가상머신에서 QuickTime + AirPlay 활용 아이디어 🤔

### 목표
- 가상머신에서 QuickTime Player를 AirPlay 전용으로 실행
- 호스트 시스템은 자유롭게 사용하면서 백그라운드 음악 재생

### 가능한 접근 방법

1. **macOS 가상머신 (VMware/Parallels)**
   - 장점: 완전한 macOS 환경, QuickTime 네이티브 실행
   - 단점: 리소스 소모 큼, 라이선스 문제, AirPlay 네트워킹 복잡

2. **Docker + VNC**
   - macOS 컨테이너는 불가능
   - Linux에서 QuickTime 대체품 사용 필요

3. **별도 사용자 계정 활용**
   - Fast User Switching으로 별도 계정 생성
   - QuickTime을 해당 계정에서만 실행
   - 메인 계정에서 자유롭게 작업

4. **헤드리스 모드 연구**
   ```bash
   # QuickTime을 백그라운드로 실행 시도
   nohup osascript -e 'tell app "QuickTime Player" to play...' &
   ```

### 추천 방안: "QuickTime 전용 미니 맥"
- 중고 Mac Mini를 AirPlay 서버로 활용
- SSH로 원격 제어
- 메인 컴퓨터는 완전히 자유롭게 사용

이 방향으로 더 연구해볼까요? 🎵