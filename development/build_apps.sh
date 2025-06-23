#!/bin/bash

# Build script for QuickTime Playlist apps
echo "Building QuickTime Playlist applications (single file)..."

# Clean previous builds
rm -rf build dist *.spec

# Build Audio Playlist
echo "Building Audio Playlist..."
pyinstaller --onefile --windowed \
    --name "QuickTime Audio Playlist" \
    --add-data "../requirements.txt:." \
    --hidden-import PyQt5 \
    --hidden-import PyQt5.QtCore \
    --hidden-import PyQt5.QtGui \
    --hidden-import PyQt5.QtWidgets \
    --noconfirm \
    ../QuickTimePlayerAudioPlaylist.py

# Build Video Playlist
echo "Building Video Playlist..."
pyinstaller --onefile --windowed \
    --name "QuickTime Video Playlist" \
    --add-data "../requirements.txt:." \
    --hidden-import PyQt5 \
    --hidden-import PyQt5.QtCore \
    --hidden-import PyQt5.QtGui \
    --hidden-import PyQt5.QtWidgets \
    --noconfirm \
    ../QuickTimePlayerVideoPlaylist.py

# Build Audio Video Converter
echo "Building Audio Video Converter..."
pyinstaller --onefile --windowed \
    --name "Audio Video Converter" \
    --add-data "../requirements.txt:." \
    --add-data "audio_to_video_minimal.py:." \
    --hidden-import PyQt5 \
    --hidden-import PyQt5.QtCore \
    --hidden-import PyQt5.QtGui \
    --hidden-import PyQt5.QtWidgets \
    --hidden-import mutagen \
    --hidden-import PIL \
    --noconfirm \
    ../AudioVideoConverterGUI.py

echo "Build complete! Apps are in the dist folder."
echo ""
echo "Note: Users will still need to install:"
echo "  - ffmpeg (brew install ffmpeg) for audio-to-video conversion"
echo "  - cliclick (brew install cliclick) for AirPlay automation"