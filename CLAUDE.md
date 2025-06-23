# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a macOS-specific application that provides playlist functionality for QuickTime Player, which natively only supports playing one video at a time. The codebase offers multiple implementation approaches: AppleScript-based solutions, Python GUI applications, and shell script wrappers.

## Key Commands

### Running the Applications

```bash
# AppleScript version (drag & drop support)
osascript PlayVideosInOrder.applescript

# Python GUI version
python3 quicktime_playlist_gui.py

# Shell script wrapper
./play_videos_shell.sh video1.mp4 video2.mp4

# Direct playback (no UI)
osascript PlayVideosDirect.applescript /path/to/video1.mp4 /path/to/video2.mp4
```

### Testing

```bash
# Test QuickTime capabilities
./quicktime_capabilities_test.sh

# Test basic QuickTime controls
osascript TestQuickTime.applescript

# Test UI automation
osascript test_ui_automation.applescript
```

## Architecture & Code Structure

### Core Components

1. **AppleScript Solutions** (`*.applescript`)
   - Direct QuickTime Player automation via AppleScript
   - Event-driven approach monitoring playback completion
   - Each script represents different complexity levels and features

2. **Python GUI** (`quicktime_playlist_gui.py`)
   - tkinter-based interface for playlist management
   - Spawns AppleScript commands via subprocess
   - Optional drag-and-drop support with tkinterdnd2

3. **AirPlay Support** (`quicktime_with_airplay.py`, `quicktime_airplay_simple.py`)
   - Requires PyObjC (pyobjc-framework-AVFoundation)
   - Works around QuickTime's AirPlay limitations

### Key Technical Considerations

1. **Sequential Playback Only**: QuickTime Player can only play one video at a time. All solutions monitor playback completion before starting the next video.

2. **AppleScript Integration**: The core functionality relies on AppleScript's ability to control QuickTime Player. Python/shell scripts wrap these AppleScript commands.

3. **Event Monitoring**: Scripts use either:
   - Polling QuickTime's playback state
   - Event-based monitoring for efficiency

4. **Platform Dependency**: This codebase is macOS-only and requires:
   - QuickTime Player installed
   - AppleScript support enabled
   - Python 3.x for GUI versions

## Development Guidelines

### When Modifying AppleScript Files

- Test changes using `osascript` command directly
- Preserve the event-monitoring logic for playback completion
- Maintain compatibility with both file paths and drag-drop inputs

### When Working on Python GUI

- Keep tkinter as the primary dependency (standard library)
- Optional dependencies should remain optional
- Test both with and without drag-drop support

### Adding New Features

- Consider QuickTime's limitations (single video playback)
- Provide both simple and advanced implementations when possible
- Document any new macOS permissions required

## Important Limitations

1. QuickTime Player does not support true playlists
2. Videos must play sequentially, not simultaneously
3. AirPlay support is limited and may require workarounds
4. Drag-and-drop functionality requires additional setup on some macOS versions