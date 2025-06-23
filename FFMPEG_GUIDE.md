# FFmpeg Installation Guide

FFmpeg is required for converting audio files to video format. This guide will help you install it on macOS.

## What is FFmpeg?

FFmpeg is a free, open-source multimedia framework that can decode, encode, transcode, stream, filter, and play most multimedia files. It's used by many applications for audio and video processing.

## Installation Methods

### Method 1: Using Homebrew (Recommended) 🍺

This is the easiest method if you have Homebrew installed.

```bash
# Install FFmpeg
brew install ffmpeg
```

If you don't have Homebrew:
```bash
# Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install FFmpeg
brew install ffmpeg
```

### Method 2: Using MacPorts

If you prefer MacPorts:
```bash
sudo port install ffmpeg
```

### Method 3: Download Pre-built Binary

1. Visit https://evermeet.cx/ffmpeg/
2. Download the latest release
3. Extract the downloaded file
4. Move `ffmpeg` to `/usr/local/bin/`:
   ```bash
   sudo mkdir -p /usr/local/bin
   sudo cp ~/Downloads/ffmpeg /usr/local/bin/
   sudo chmod +x /usr/local/bin/ffmpeg
   ```

### Method 4: Official Download

1. Visit https://ffmpeg.org/download.html
2. Click on "macOS" under "Get packages & executable files"
3. Follow the instructions for your chosen distribution

## Verify Installation

After installation, verify FFmpeg is working:

```bash
ffmpeg -version
```

You should see version information like:
```
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
```

## Troubleshooting

### "ffmpeg: command not found"

1. Check if FFmpeg is installed:
   ```bash
   which ffmpeg
   ```

2. If installed via Homebrew on Apple Silicon (M1/M2):
   ```bash
   /opt/homebrew/bin/ffmpeg -version
   ```

3. If installed via Homebrew on Intel:
   ```bash
   /usr/local/bin/ffmpeg -version
   ```

### Permission Denied

If you get permission errors:
```bash
sudo chmod +x $(which ffmpeg)
```

### Path Issues

Add FFmpeg to your PATH:
```bash
# For Apple Silicon Macs
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For Intel Macs
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Why Do We Need FFmpeg?

Our Audio to Video Converter uses FFmpeg to:
- Combine audio files with visual frames
- Encode video in H.264 format
- Preserve audio quality during conversion
- Add metadata to the output file

## License Note

FFmpeg is licensed under LGPL 2.1 or later. When distributing applications that use FFmpeg, you must comply with the license terms. See https://ffmpeg.org/legal.html for details.

## Need Help?

If you continue to have issues:
1. Check the [FFmpeg FAQ](https://ffmpeg.org/faq.html)
2. Ask in our [GitHub Issues](https://github.com/yourusername/quicktime-playlist/issues)
3. Visit [FFmpeg Forums](https://ffmpeg.org/contact.html)