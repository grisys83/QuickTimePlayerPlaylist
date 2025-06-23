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

# Install dependencies
pip3 install -r requirements.txt

# Install cliclick for AirPlay automation (optional)
brew install cliclick
```

## Usage

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
├── requirements.txt                 # Python dependencies
├── SECURITY_SETUP.md               # Security setup guide
└── development/                    # Features in development
```

## Technical Features

- **PyQt5-based GUI**: Modern, responsive interface
- **AppleScript Integration**: Direct QuickTime Player control
- **JSON Configuration**: Save playlists and settings
- **Multi-threaded**: Smooth playback without UI blocking

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