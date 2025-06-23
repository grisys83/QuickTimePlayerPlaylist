# QuickTime Playlist Pro 🎵

> **Playlist Extension for QuickTime Player**  
> Continuous playback support for local music on HomePod and AirPlay devices

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/quicktime-playlist-pro)
[![macOS](https://img.shields.io/badge/macOS-10.14+-green.svg)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

## 🌟 Why This App?

QuickTime Player can only play one file at a time by default. This project adds playlist functionality, allowing continuous playback of multiple files. It especially supports convenient listening of local music files on AirPlay devices like HomePod.

## ✨ Key Features

### 🎯 Automatic Playlist Playback
- Overcomes QuickTime's single-file limitation
- Supports sequential/shuffle/repeat playback
- Real-time playback queue management

### 🏠 HomePod AirPlay Automation
- Automatic "Living" device connection
- AirPlay setup for each track
- Automatic reconnection recovery

### 🎨 Audio Visualization
- Converts audio files to beautiful videos
- Displays album art, title, and artist
- HD quality output

### ☕ Cafe/Store Mode
- 24-hour continuous playback
- Automatic error recovery
- Operating hours settings

## 📋 Requirements

- macOS (QuickTime Player required)
- Python 3.x
- cliclick (for AirPlay automation): `brew install cliclick`

### Optional Requirements
- PyAutoGUI (mouse automation): `pip3 install pyautogui`
- PyObjC (AirPlay features): `pip3 install pyobjc-framework-AVFoundation`

## ⚠️ IMPORTANT: Security Settings for AirPlay Automation

**To use AirPlay features, you MUST configure macOS security settings!**

1. Go to **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the lock 🔒 to make changes
3. Click **+** to add these apps:
   - Python (`/usr/local/bin/python3` or `/Library/Frameworks/Python.framework/`)
   - Terminal (`/Applications/Utilities/`)
4. Ensure all checkboxes ✅ are checked

**AirPlay automation will NOT work without these permissions!**

See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed instructions

## 🚀 Quick Start

### 1. Basic Playlist Playback

```bash
# Simple GUI version
python3 quicktime_playlist_gui.py

# Drag & drop player
python3 QuickDrop.py
```

### 2. HomePod AirPlay Automation

```bash
# Audio playlist with AirPlay support
python3 QuickTimePlayerAudioPlaylist.py

# Video playlist with AirPlay
python3 QuickTimePlayerVideoPlaylist.py
```

### 3. Advanced Features

```bash
# Convert audio to video with metadata
python3 audio_to_video_enhanced.py input.mp3 output.mp4

# 24/7 cafe mode
python3 cafe_playlist_living_final.py
```

## 🛠 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/quicktime-playlist-pro.git
cd quicktime-playlist-pro

# Install dependencies
pip3 install -r requirements.txt
brew install cliclick

# Run
python3 QuickTimePlayerAudioPlaylist.py
```

## 🎮 Usage Guide

### Basic Usage
1. Launch the application
2. Add audio/video files via "Add Files" or "Add Folder"
3. Click "Play All" to start
4. Enable AirPlay for automatic HomePod connection

### Advanced Options
- **Shuffle**: Random playback order
- **Repeat One/All**: Loop single track or entire playlist
- **Save/Load**: Preserve playlists for later use
- **Settings**: Configure AirPlay offsets for your setup

## 🏗 Architecture

### Core Components
- **AppleScript Integration**: Direct QuickTime control
- **PyQt5 GUI**: Modern interface with drag & drop
- **Offset-based AirPlay**: Reliable device selection
- **JSON State Management**: Persistent settings and playlists

### Technical Approach
```python
# AirPlay device selection via mouse automation
subprocess.run(['cliclick', 'c:844,714'])  # AirPlay button
subprocess.run(['cliclick', 'c:970,784'])  # Living device selection
```

## 🤝 Contributing

This project welcomes all contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas to Contribute
- Code improvements and bug fixes
- Documentation and translations
- UI/UX enhancements
- Testing and bug reports

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Features Implemented

- ✅ Playlist functionality for QuickTime
- ✅ Automatic AirPlay device selection
- ✅ Audio file visualization
- ✅ Real-time queue management
- ✅ 24-hour stable operation

## 💬 Community

- [GitHub Issues](https://github.com/yourusername/quicktime-playlist-pro/issues)
- [r/HomePod](https://reddit.com/r/HomePod)
- [r/apple](https://reddit.com/r/apple)

## 🙏 Acknowledgments

- HomePod community
- r/HomePod Reddit users
- All contributors to this project
- Open source community

## 📢 Media Coverage

Notable mentions will be listed here!

---

> **Open source solution for free playback of local media files**

### 🌐 Links

- [GitHub Repository](https://github.com/yourusername/quicktime-playlist-pro)
- [HomePod Community](https://reddit.com/r/HomePod)
- [Project Website](https://quicktime-playlist-pro.com) *(coming soon)*

### #️⃣ Hashtags

`#openhomepod` `#openairplay2` `#quicktimeplaylist` `#opensource`