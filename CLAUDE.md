# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a macOS-specific application suite that provides playlist functionality for QuickTime Player, which natively only supports playing one file at a time. The project includes three main PyQt5-based GUI applications with AirPlay automation support, plus an audio-to-video converter using ALAC (Apple Lossless) codec.

## Key Commands

### Running the Applications

```bash
# Main Applications (PyQt5 GUI with AirPlay support)
python3 QuickTimePlayerAudioPlaylist.py   # Audio playlist
python3 QuickTimePlayerVideoPlaylist.py   # Video playlist
python3 AudioVideoConverterGUI.py         # Audio to video converter (ALAC)

# Legacy/Development versions (in development folder)
osascript development/PlayVideosInOrder.applescript
python3 development/quicktime_playlist_gui.py
```

### Testing

```bash
# Test audio to video conversion
python3 audio_to_video_minimal.py audio_file.mp3

# Test QuickTime capabilities (in development folder)
./development/quicktime_capabilities_test.sh

# Test basic QuickTime controls
osascript development/TestQuickTime.applescript
```

## Architecture & Code Structure

### Core Components

1. **Main Applications** (PyQt5-based)
   - `QuickTimePlayerAudioPlaylist.py`: Full-featured audio playlist with AirPlay automation
   - `QuickTimePlayerVideoPlaylist.py`: Video playlist with drag-and-drop support
   - `AudioVideoConverterGUI.py`: Converts audio to video with minimal visuals
   - All use inline AppleScript via subprocess for QuickTime control

2. **Audio to Video Converter Module**
   - `audio_to_video_minimal.py`: Core conversion module
   - Uses ALAC (Apple Lossless) codec for audio
   - Accurate duration handling with ffprobe
   - Creates videos with album art or minimal visuals

3. **AirPlay Automation**
   - Uses `cliclick` for mouse automation
   - Accessibility permissions required
   - Automatic HomePod/Apple TV connection
   - Visual detection for AirPlay UI elements

### Key Technical Considerations

1. **Sequential Playback Only**: QuickTime Player can only play one video at a time. All solutions monitor playback completion before starting the next video.

2. **AppleScript Integration**: The core functionality relies on AppleScript's ability to control QuickTime Player. Python/shell scripts wrap these AppleScript commands.

3. **Event Monitoring**: Scripts use either:
   - Polling QuickTime's playback state
   - Event-based monitoring for efficiency

4. **Platform Dependency**: This codebase is macOS-only and requires:
   - QuickTime Player installed
   - Python 3.x with PyQt5
   - FFmpeg (for audio conversion)
   - cliclick (for AirPlay automation)
   - Accessibility permissions for UI automation

## Development Guidelines

### When Modifying AppleScript Files

- Test changes using `osascript` command directly
- Preserve the event-monitoring logic for playback completion
- Maintain compatibility with both file paths and drag-drop inputs

### When Working on Python GUI

- PyQt5 is the primary GUI framework (not tkinter)
- Test AirPlay automation features with proper permissions
- Handle audio-to-video conversion dependencies (mutagen, pillow)

### Adding New Features

- Consider QuickTime's limitations (single video playback)
- Provide both simple and advanced implementations when possible
- Document any new macOS permissions required

## Important Limitations

1. QuickTime Player does not support true playlists - sequential playback only
2. AirPlay automation requires mouse control (no direct API)
3. Audio files must be converted to video for QuickTime playback
4. macOS Accessibility permissions required for UI automation
5. ALAC codec used for lossless audio quality in converted videos