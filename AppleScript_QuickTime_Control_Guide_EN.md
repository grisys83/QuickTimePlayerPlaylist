# Controlling QuickTime Player with AppleScript

## Overview

AppleScript is a powerful automation tool for macOS that allows programmatic control of QuickTime Player. This enables automation of video/audio playback and creation of complex workflows.

## Basic Commands

### 1. Application Control
```applescript
-- Launch QuickTime
tell application "QuickTime Player"
    activate
end tell

-- Quit QuickTime
tell application "QuickTime Player"
    quit
end tell
```

### 2. Opening Files
```applescript
tell application "QuickTime Player"
    -- Open file with POSIX path
    open POSIX file "/Users/username/Movies/video.mp4"
    
    -- Open multiple files
    open {POSIX file "/path/to/file1.mp4", POSIX file "/path/to/file2.mp4"}
end tell
```

### 3. Playback Control
```applescript
tell application "QuickTime Player"
    -- Play
    play front document
    
    -- Pause
    pause front document
    
    -- Stop (also exits fullscreen mode)
    stop front document
end tell
```

## Advanced Property Control

### 1. Playback Position Control
```applescript
tell application "QuickTime Player"
    tell front document
        -- Get current playback time (in seconds)
        set currentTime to current time
        
        -- Jump to specific position (30 seconds)
        set current time to 30
        
        -- Get total duration
        set totalDuration to duration
    end tell
end tell
```

### 2. Volume Control
```applescript
tell application "QuickTime Player"
    tell front document
        -- Get current volume (0.0 to 1.0)
        set currentVolume to audio volume
        
        -- Set volume to 50%
        set audio volume to 0.5
        
        -- Mute audio
        set output muted to true
    end tell
end tell
```

### 3. Playback State Monitoring
```applescript
tell application "QuickTime Player"
    tell front document
        -- Check if playing
        if playing then
            display dialog "Currently playing"
        else
            display dialog "Not playing"
        end if
        
        -- Check playback rate (1.0 = normal speed)
        set playbackRate to rate
    end tell
end tell
```

## Practical Examples

### 1. Detecting Playback Completion
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

### 2. Simple Playlist
```applescript
set videoList to {"/path/to/video1.mp4", "/path/to/video2.mp4", "/path/to/video3.mp4"}

repeat with videoPath in videoList
    tell application "QuickTime Player"
        close every document
        open POSIX file videoPath
        play front document
        
        -- Wait for playback to complete
        repeat while (exists front document) and playing of front document
            delay 2
        end repeat
    end tell
end repeat
```

### 3. Extracting Video Information
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

### 4. Loop Playback of Specific Section
```applescript
tell application "QuickTime Player"
    tell front document
        set startTime to 10 -- From 10 seconds
        set endTime to 30   -- To 30 seconds
        
        repeat 5 times -- Repeat 5 times
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

## Window Control

```applescript
tell application "QuickTime Player"
    -- Fullscreen mode
    present front document
    
    -- Resize window
    tell window 1
        set bounds to {100, 100, 800, 600}
    end tell
    
    -- Minimize window
    set miniaturized of window 1 to true
end tell
```

## Limitations and Workarounds

### 1. AirPlay Control
AppleScript cannot directly control AirPlay. UI automation through System Events is required:

```applescript
tell application "System Events"
    tell process "QuickTime Player"
        -- Click AirPlay button
        click button "AirPlay" of window 1
    end tell
end tell
```

### 2. Playlist Functionality
QuickTime doesn't support native playlists. To work around this:
- Open and play files sequentially
- Detect playback completion to play next file
- Manage through external scripts or applications

### 3. Video Effects
Video filters and effects cannot be controlled via AppleScript. For such functionality, use tools like FFmpeg in conjunction.

## Tips and Best Practices

1. **Error Handling**: Use try blocks
```applescript
try
    tell application "QuickTime Player"
        play front document
    end tell
on error
    display dialog "No document is open"
end try
```

2. **Check Document Existence**
```applescript
tell application "QuickTime Player"
    if (count documents) > 0 then
        -- Execute only when document exists
        play front document
    end if
end tell
```

3. **Python Integration**
```python
import subprocess

script = '''
tell application "QuickTime Player"
    play front document
end tell
'''

subprocess.run(['osascript', '-e', script])
```

## Conclusion

AppleScript provides sufficient functionality for basic QuickTime Player playback control. While it has limitations for advanced features, creative scripting combined with other tools can build powerful media automation systems. For automating media workflows in macOS environments, the combination of AppleScript and QuickTime offers a simple yet effective solution.