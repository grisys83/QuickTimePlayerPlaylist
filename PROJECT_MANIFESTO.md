# QuickTime Playlist Pro: 플레이리스트 기능 확장 프로젝트

## 🎯 프로젝트의 비전

이 프로젝트는 QuickTime Player의 기본 기능을 확장하여 플레이리스트 재생을 가능하게 합니다. HomePod과 같은 AirPlay 디바이스에서 로컬 음악 파일을 연속으로 재생할 수 있도록 지원하는 **오픈소스 솔루션**입니다.

## 🚫 기술적 제약사항

### 1. QuickTime Player의 기본 기능
- **단일 파일 재생**: QuickTime은 한 번에 하나의 파일만 재생
- **AirPlay 제어**: 프로그래머틱 인터페이스 미제공
- **플레이리스트 기능**: 기본적으로 지원하지 않음

### 2. 사용자가 겪는 불편함
- QuickTime Player는 한 번에 하나의 파일만 재생
- HomePod에서 로컬 파일 플레이리스트 재생의 어려움
- 로컬 음악 파일의 AirPlay 재생 제한
- 카페/매장에서 사용할 수 있는 대안 부재

## 💡 우리의 해결책

### 1. 시스템 레벨 자동화
```python
# AirPlay 디바이스 선택을 위한 마우스 자동화
subprocess.run(['cliclick', 'c:844,714'])  # AirPlay 버튼
subprocess.run(['cliclick', 'c:970,784'])  # Living 디바이스 선택
```

### 2. 오디오→비디오 변환 엔진
- 오디오 파일에 시각적 메타데이터 추가
- 앨범 아트, 아티스트 정보를 아름다운 비디오로 변환
- HomePod에서도 시각적 피드백 제공 (Apple TV 연결 시)

### 3. 스마트 큐 시스템
- Roon 스타일의 실시간 큐 관리
- 재생 중에도 다음 곡 추가/수정 가능
- JSON 기반 상태 저장으로 앱 재시작 후에도 큐 유지

## 🏆 주요 기능들

### 1. 카페/매장 모드
- 24시간 연속 재생
- 자동 AirPlay 재연결
- 재생 오류 자동 복구

### 2. 통합 플레이리스트 관리
- 오디오/비디오 통합 재생
- 드래그 앤 드롭 지원
- 실시간 재생 상태 추적

### 3. 메타데이터 시각화
- ID3 태그 자동 추출
- 프로페셔널한 비주얼 생성
- HD 품질 출력

## 📊 기술적 우회 전략

### 1. AppleScript의 한계 극복
```python
# 한국어 macOS의 AppleScript 버그 우회
subprocess.run(['open', '-a', 'QuickTime Player', video_path])
# 직접 변수 설정 대신 POSIX 파일 경로 사용
```

### 2. 시스템 권한 우회
- cliclick을 통한 UI 자동화
- 접근성 권한만으로 전체 제어
- 시스템 무결성 보호(SIP) 우회 불필요

### 3. 실시간 상태 모니터링
```python
# QuickTime의 재생 상태를 지속적으로 체크
def is_video_playing(self):
    result = subprocess.run(['osascript', '-e', 
        'tell application "QuickTime Player" to return playing of front document'])
    return result.stdout.strip() == "true"
```

## 🌍 커뮤니티 임팩

### 1. HomePod 사용자들을 위한 해방
- Apple Music 구독 없이도 플레이리스트 재생
- 로컬 음악 파일의 완전한 활용
- 카페/매장 운영자를 위한 완벽한 솔루션

### 2. 오픈소스 정신
- 모든 코드 공개
- 커뮤니티 기여 환영
- Apple의 제한에 대한 공개적 도전

### 3. 미래 비전
- iOS 컴패니언 앱 (Shortcuts 통합)
- 클라우드 동기화
- 멀티룸 오디오 해킹
- Spotify/YouTube Music 통합

## 🔥 사용자 필요사항

이 프로젝트는 다음과 같은 사용자 요구사항을 해결합니다:

1. **로컬 파일의 연속 재생**
2. **AirPlay 디바이스 자동 선택**
3. **플레이리스트 관리 기능**
4. **안정적인 장시간 재생**

## 🚀 설치 및 사용

### 빠른 시작
```bash
# 의존성 설치
./install_dependencies.sh

# 실행
python3 QuickTimePlaylistPro.py
```

### 주요 컴포넌트
1. **QuickTimePlaylistSimple.py** - 안정적인 기본 버전
2. **audio_to_video_enhanced.py** - 메타데이터 시각화 엔진
3. **cafe_playlist_living_final.py** - 24시간 운영 모드
4. **quicktime_playlist_queue.py** - Roon 스타일 큐 시스템

## 📈 성과

- ✅ QuickTime의 단일 파일 재생 한계 극복
- ✅ AirPlay 자동화 성공
- ✅ 오디오 파일의 시각적 변환
- ✅ 실시간 큐 관리 시스템
- ✅ 24시간 안정적 운영 검증

## 🤝 함께하기

이 프로젝트는 로컬 미디어 파일의 편리한 재생을 원하는 모든 사용자를 환영합니다.

- GitHub: [프로젝트 저장소]
- Reddit: r/HomePod
- Discord: 오픈소스 오디오 커뮤니티

---

**로컬 미디어 파일의 자유로운 재생을 위한 오픈소스 솔루션**

**#openhomepod #openairplay2 #quicktimeplaylist #opensource**