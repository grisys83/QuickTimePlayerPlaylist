# Automator 오류 -212 해결 방법

## 🔧 해결책들

### 1. Automator 권한 확인
1. 시스템 설정 > 개인정보 보호 및 보안 > 자동화
2. Automator가 QuickTime Player를 제어할 수 있도록 허용

### 2. 간단한 AppleScript 사용 (PlayVideosSimple.applescript)
Automator에서 다음과 같이 설정:
1. 새 Automator 문서 생성 > "빠른 동작" 선택
2. "AppleScript 실행" 동작 추가
3. PlayVideosSimple.applescript 내용 복사/붙여넣기
4. 저장 시 "이미지 파일 및 Finder 항목"으로 설정

### 3. Shell Script 직접 실행
터미널에서:
```bash
./play_videos_shell.sh video1.mp4 video2.mp4 video3.mp4
```

### 4. 직접 실행 방법 (가장 안정적)
터미널에서:
```bash
# 단일 명령으로 실행
osascript PlayVideosInOrder.applescript
```

또는 Finder에서:
1. PlayVideosInOrder.applescript 파일을 더블클릭
2. 스크립트 편집기에서 실행 버튼 클릭

### 5. 서비스로 등록 (Automator 대체)
1. 시스템 설정 > 키보드 > 키보드 단축키 > 서비스
2. "+" 버튼으로 새 서비스 추가
3. QuickTimePlaylist.app을 연결

## 🎯 권장 방법

**가장 안정적**: QuickTimePlaylist.app 사용
- Finder에서 파일 선택 → 앱에 드래그 앤 드롭
- 또는 앱 실행 후 파일 선택

**명령줄 선호**: shell script 사용
```bash
./play_videos_shell.sh *.mp4
```