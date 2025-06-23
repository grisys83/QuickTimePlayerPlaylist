# QuickTime Playlist Pro: Playlist Extension Project

## 🎯 Project Vision

This project extends QuickTime Player's basic functionality to enable playlist playback. It's an **open source solution** that supports continuous playback of local music files on AirPlay devices like HomePod.

## 🚫 Technical Constraints

### 1. QuickTime Player's Basic Features
- **Single file playback**: QuickTime only plays one file at a time
- **AirPlay control**: No programmatic interface provided
- **Playlist functionality**: Not natively supported

### 2. User Challenges
- Difficulty playing local file playlists on HomePod
- Limited AirPlay device management
- No continuous playback for cafes/stores

## 💡 Our Solutions

### 1. System-Level Automation
```python
# Mouse automation for AirPlay device selection
subprocess.run(['cliclick', 'c:844,714'])  # AirPlay button
subprocess.run(['cliclick', 'c:970,784'])  # Living device selection
```

### 2. Audio→Video Conversion Engine
- Adds visual metadata to audio files
- Converts album art and artist info into beautiful videos
- Provides visual feedback on HomePod (when connected to Apple TV)

### 3. Smart Queue System
- Roon-style real-time queue management
- Add/modify next tracks while playing
- JSON-based state saving preserves queue after app restart

## 🏆 Key Features

### 1. Cafe/Store Mode
- 24-hour continuous playback
- Automatic AirPlay reconnection
- Automatic playback error recovery

### 2. Unified Playlist Management
- Combined audio/video playback
- Drag & drop support
- Real-time playback status tracking

### 3. Advanced Playback Controls
- Shuffle mode with smart queue
- Repeat one/all functionality
- Single track playback option
- Auto-close when finished

## 🔧 Technical Implementation

### Core Technologies
- **AppleScript**: Direct QuickTime Player control
- **PyQt5**: Modern GUI framework
- **cliclick**: Mouse automation for AirPlay
- **JSON**: Settings and playlist persistence

### Key Innovations
1. **Event-driven playback monitoring**
2. **Offset-based UI element targeting**
3. **Graceful error recovery**
4. **Cross-environment compatibility**

## 📊 Project Status

### Completed
- ✅ Basic playlist functionality
- ✅ AirPlay automation
- ✅ Audio visualization
- ✅ Queue management system
- ✅ 24/7 operation mode

### Future Vision
- iOS companion app (Shortcuts integration)
- Cloud sync capabilities
- Multi-room audio exploration
- Streaming service integration

## 🔥 User Requirements

This project addresses the following user needs:

1. **Continuous playback of local files**
2. **Automatic AirPlay device selection**
3. **Playlist management features**
4. **Stable long-duration playback**

## 🚀 Installation & Usage

### Quick Start
```bash
# Install dependencies
./install_dependencies.sh

# Run
python3 QuickTimePlayerAudioPlaylist.py
```

### Main Components
1. **QuickTimePlayerAudioPlaylist.py** - Full-featured audio playlist
2. **QuickTimePlayerVideoPlaylist.py** - Video playlist version
3. **QuickDrop.py** - Simple drag & drop player
4. **quicktime_playlist_gui.py** - Basic GUI version

## 📈 Achievements

- ✅ Overcame QuickTime's single-file playback limitation
- ✅ Successful AirPlay automation
- ✅ Visual transformation of audio files
- ✅ Real-time queue management system
- ✅ Verified 24-hour stable operation

## 🤝 Join Us

This project welcomes all users who want convenient playback of local media files.

- GitHub: [Project Repository]
- Reddit: r/HomePod
- Discord: Open Source Audio Community

---

**Open source solution for free playback of local media files**

**#openhomepod #openairplay2 #quicktimeplaylist #opensource**