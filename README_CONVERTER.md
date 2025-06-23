# Audio to Video Converter for macOS 🎵 → 🎬

Convert your audio files into videos with beautiful visualizations. Perfect for sharing music on platforms that only accept video files.

![Screenshot](screenshot.png)

## Features

- 🎨 **Beautiful Visualizations**: Apple Music-style blurred album art backgrounds
- 🎵 **Metadata Display**: Shows title, artist, and album information
- 📦 **Batch Processing**: Convert multiple files at once
- 🖱️ **Drag & Drop**: Simple interface - just drop your audio files
- 🚀 **Fast Conversion**: Optimized for speed with minimal quality loss

## Installation

### Option 1: Download Pre-built App (Easiest)
1. Download `AudioVideoConverter.app` from [Releases](https://github.com/yourusername/quicktime-playlist/releases)
2. Move to Applications folder
3. Right-click and select "Open" (first time only)

### Option 2: Run from Source

1. **Install FFmpeg** (Required for conversion):
   ```bash
   # Using Homebrew (recommended)
   brew install ffmpeg
   
   # Or download from https://ffmpeg.org/download.html
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   python3 AudioVideoConverterGUI.py
   ```

## Usage

1. **Launch the app**
2. **Add audio files** by either:
   - Drag and drop files onto the window
   - Click the drop zone to browse and select files
3. **Click "Convert All"** to start conversion
4. **Find your videos** in the same folder as the originals (with `_converted.mp4` suffix)

## Supported Formats

**Input**: MP3, M4A, AAC, FLAC, WAV, AIFF
**Output**: MP4 (H.264 video + AAC audio)

## System Requirements

- macOS 10.14 or later
- 4GB RAM recommended
- FFmpeg installed

## Troubleshooting

### "FFmpeg not found" error
Make sure FFmpeg is installed and in your PATH:
```bash
which ffmpeg  # Should show the path to ffmpeg
```

### No album art in video
The converter extracts album art from the audio file's metadata. If no art is found, a default music note icon is displayed.

### Conversion seems slow
- The first file takes longer as FFmpeg initializes
- Files already converted (with `_converted.mp4` suffix) are automatically skipped

## Building from Source

To create a standalone app:
```bash
pip3 install pyinstaller
pyinstaller --onefile --windowed --name "AudioVideoConverter" AudioVideoConverterGUI.py
```

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Pull requests welcome! See [CONTRIBUTING.md](CONTRIBUTING_EN.md) for guidelines.

---

Made with ❤️ for the macOS community