# Installation Guide

## System Requirements

- macOS 10.14 or later
- Python 3.7 or later
- QuickTime Player (pre-installed on macOS)

## Required Dependencies

### 1. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Install FFmpeg

FFmpeg is required for audio-to-video conversion. It cannot be installed via pip.

#### Option A: Using Homebrew (Recommended)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

#### Option B: Using MacPorts
```bash
sudo port install ffmpeg
```

#### Option C: Download Binary
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH.

### 3. Install cliclick (Optional, for AirPlay automation)

```bash
brew install cliclick
```

## Verify Installation

Check that all dependencies are installed:

```bash
# Check Python
python3 --version

# Check FFmpeg
ffmpeg -version

# Check cliclick (optional)
cliclick -V
```

## Quick Start

### For Audio/Video Converter GUI:
```bash
python3 AudioVideoConverterGUI.py
```

### For QuickTime Playlist:
```bash
python3 QuickTimePlayerAudioPlaylist.py
```

## Troubleshooting

### FFmpeg not found
If you get "FFmpeg not found" error:
1. Make sure FFmpeg is installed: `which ffmpeg`
2. If installed via Homebrew on Apple Silicon: `/opt/homebrew/bin/ffmpeg`
3. If installed via Homebrew on Intel: `/usr/local/bin/ffmpeg`

### Permission Issues
If you get permission errors:
```bash
chmod +x AudioVideoConverterGUI.py
chmod +x QuickTimePlayerAudioPlaylist.py
```

### Missing Python Packages
If imports fail:
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```