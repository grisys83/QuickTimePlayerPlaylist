# QuickTime Player Playlist 🎵

A macOS application that adds playlist functionality to QuickTime Player, enabling continuous playback of multiple files.

## Key Features

### 🎯 Core Features
- **Playlist Management**: Add audio/video files via drag & drop
- **Automatic Continuous Playback**: Overcomes QuickTime's single-file limitation
- **AirPlay Automation**: Auto-connect to HomePod and other AirPlay devices
- **Audio-to-Video Conversion**: Convert audio files to video for playback

### 🎮 Playback Controls
- Play/Pause/Stop
- Previous/Next track
- Shuffle playback
- Repeat modes (One/All)
- Save/Load playlists

## Installation

### Requirements
- macOS 10.14 or later
- Python 3.x
- QuickTime Player

### Setup
```bash
# Clone repository
git clone https://github.com/grisys83/QuickTimePlayerPlaylist.git
cd QuickTimePlayerPlaylist

# Install Python dependencies
pip3 install -r requirements.txt

# Install required tools
brew install ffmpeg          # Required for audio-to-video conversion
brew install cliclick        # Required for AirPlay automation
```

## Usage

⚠️ **Important**: Run these applications directly from Terminal for full functionality. Standalone app bundles (e.g., created with PyInstaller) may not support AirPlay automation due to macOS security restrictions.

### Audio Playlist
```bash
python3 QuickTimePlayerAudioPlaylist.py
```

### Video Playlist
```bash
python3 QuickTimePlayerVideoPlaylist.py
```

### Audio-to-Video Converter
```bash
python3 AudioVideoConverterGUI.py
```

## ⚠️ Important: AirPlay Automation Setup

To use AirPlay automation features, you must configure macOS security settings:

1. Go to **System Settings** → **Privacy & Security** → **Accessibility**
2. Add and grant permissions to Python and Terminal apps
3. See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed instructions

## Project Structure

```
QuickTimePlayerPlaylist/
├── QuickTimePlayerAudioPlaylist.py  # Audio playlist app
├── QuickTimePlayerVideoPlaylist.py  # Video playlist app
├── AudioVideoConverterGUI.py        # Audio-to-video converter
├── audio_to_video_minimal.py       # Core converter module (ALAC support)
├── requirements.txt                 # Python dependencies
├── SECURITY_SETUP.md               # Security setup guide
└── development/                    # Features in development
```

## Technical Features

- **PyQt5-based GUI**: Modern, responsive interface
- **AppleScript Integration**: Direct QuickTime Player control
- **JSON Configuration**: Save playlists and settings
- **Multi-threaded**: Smooth playback without UI blocking
- **ALAC Audio Codec**: Lossless audio quality for converted videos
- **Accurate Duration Handling**: Proper video length using ffprobe

## Known Limitations

- QuickTime Player can only play one file at a time (solved with sequential playback)
- AirPlay control requires mouse automation (macOS API limitation)
- macOS only (QuickTime Player dependency)

## Contributing

Pull requests and issue reports are welcome!

## License

MIT License - Use and modify freely.

---

#openhomepod #openairplay2

## 🌏 Other Languages

- [한국어 (Korean)](README_KR.md)