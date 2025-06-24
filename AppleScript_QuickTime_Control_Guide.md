# AppleScript로 QuickTime Player 제어하기

## 개요

AppleScript는 macOS의 강력한 자동화 도구로, QuickTime Player를 프로그래밍 방식으로 제어할 수 있게 해줍니다. 이를 통해 비디오/오디오 재생을 자동화하고, 복잡한 워크플로우를 구축할 수 있습니다.

## 기본 명령어

### 1. 애플리케이션 제어
```applescript
-- QuickTime 실행
tell application "QuickTime Player"
    activate
end tell

-- QuickTime 종료
tell application "QuickTime Player"
    quit
end tell
```

### 2. 파일 열기
```applescript
tell application "QuickTime Player"
    -- POSIX 경로로 파일 열기
    open POSIX file "/Users/username/Movies/video.mp4"
    
    -- 여러 파일 열기
    open {POSIX file "/path/to/file1.mp4", POSIX file "/path/to/file2.mp4"}
end tell
```

### 3. 재생 제어
```applescript
tell application "QuickTime Player"
    -- 재생
    play front document
    
    -- 일시정지
    pause front document
    
    -- 정지 (전체화면 모드도 종료)
    stop front document
end tell
```

## 고급 속성 제어

### 1. 재생 위치 제어
```applescript
tell application "QuickTime Player"
    tell front document
        -- 현재 재생 시간 가져오기 (초 단위)
        set currentTime to current time
        
        -- 특정 위치로 이동 (30초 지점)
        set current time to 30
        
        -- 전체 길이 확인
        set totalDuration to duration
    end tell
end tell
```

### 2. 볼륨 제어
```applescript
tell application "QuickTime Player"
    tell front document
        -- 현재 볼륨 확인 (0.0 ~ 1.0)
        set currentVolume to audio volume
        
        -- 볼륨 50%로 설정
        set audio volume to 0.5
        
        -- 음소거
        set output muted to true
    end tell
end tell
```

### 3. 재생 상태 모니터링
```applescript
tell application "QuickTime Player"
    tell front document
        -- 재생 중인지 확인
        if playing then
            display dialog "Currently playing"
        else
            display dialog "Not playing"
        end if
        
        -- 재생 속도 확인 (1.0 = 정상 속도)
        set playbackRate to rate
    end tell
end tell
```

## 실용적인 예제

### 1. 재생 완료 감지
```applescript
tell application "QuickTime Player"
    tell front document
        play
        repeat while playing
            delay 1
        end repeat
        display notification "Playback completed"
    end tell
end tell
```

### 2. 간단한 플레이리스트
```applescript
set videoList to {"/path/to/video1.mp4", "/path/to/video2.mp4", "/path/to/video3.mp4"}

repeat with videoPath in videoList
    tell application "QuickTime Player"
        close every document
        open POSIX file videoPath
        play front document
        
        -- 재생 완료 대기
        repeat while (exists front document) and playing of front document
            delay 2
        end repeat
    end tell
end repeat
```

### 3. 비디오 정보 추출
```applescript
tell application "QuickTime Player"
    tell front document
        set videoInfo to "File: " & name & return
        set videoInfo to videoInfo & "Duration: " & (duration as string) & " seconds" & return
        set videoInfo to videoInfo & "Data Rate: " & (data rate as string) & " bps" & return
        set videoInfo to videoInfo & "Dimensions: " & (width of natural dimensions as string) & "x" & (height of natural dimensions as string)
        
        display dialog videoInfo
    end tell
end tell
```

### 4. 특정 구간 반복 재생
```applescript
tell application "QuickTime Player"
    tell front document
        set startTime to 10 -- 10초부터
        set endTime to 30   -- 30초까지
        
        repeat 5 times -- 5번 반복
            set current time to startTime
            play
            
            repeat while current time < endTime
                delay 0.1
            end repeat
            
            pause
        end repeat
    end tell
end tell
```

## 윈도우 제어

```applescript
tell application "QuickTime Player"
    -- 전체화면 모드
    present front document
    
    -- 창 크기 조절
    tell window 1
        set bounds to {100, 100, 800, 600}
    end tell
    
    -- 창 최소화
    set miniaturized of window 1 to true
end tell
```

## 한계점과 해결 방법

### 1. AirPlay 제어
AppleScript로는 AirPlay를 직접 제어할 수 없습니다. 대신 System Events를 통한 UI 자동화가 필요합니다:

```applescript
tell application "System Events"
    tell process "QuickTime Player"
        -- AirPlay 버튼 클릭
        click button "AirPlay" of window 1
    end tell
end tell
```

### 2. 플레이리스트 기능
QuickTime은 네이티브 플레이리스트를 지원하지 않습니다. 이를 해결하려면:
- 파일을 순차적으로 열고 재생
- 재생 완료를 감지하여 다음 파일 재생
- 외부 스크립트나 애플리케이션으로 관리

### 3. 비디오 효과
비디오 필터나 효과는 AppleScript로 제어할 수 없습니다. 이런 기능이 필요하다면 FFmpeg 같은 도구를 함께 사용해야 합니다.

## 팁과 모범 사례

1. **에러 처리**: try 블록 사용
```applescript
try
    tell application "QuickTime Player"
        play front document
    end tell
on error
    display dialog "No document is open"
end try
```

2. **문서 존재 확인**
```applescript
tell application "QuickTime Player"
    if (count documents) > 0 then
        -- 문서가 있을 때만 실행
        play front document
    end if
end tell
```

3. **Python과 통합**
```python
import subprocess

script = '''
tell application "QuickTime Player"
    play front document
end tell
'''

subprocess.run(['osascript', '-e', script])
```

## 결론

AppleScript는 QuickTime Player의 기본적인 재생 제어에는 충분한 기능을 제공합니다. 비록 고급 기능에는 한계가 있지만, 창의적인 스크립팅과 다른 도구들과의 조합으로 강력한 미디어 자동화 시스템을 구축할 수 있습니다. 특히 macOS 환경에서 미디어 워크플로우를 자동화하려는 경우, AppleScript와 QuickTime의 조합은 간단하면서도 효과적인 솔루션이 될 수 있습니다.