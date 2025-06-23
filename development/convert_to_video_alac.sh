#!/bin/bash

# Audio to Video Converter with ALAC
# Converts audio files to video with Apple Lossless audio codec

# Check if ffmpeg and ffprobe are installed
FFMPEG=$(which ffmpeg || echo "/opt/homebrew/bin/ffmpeg")
FFPROBE=$(which ffprobe || echo "/opt/homebrew/bin/ffprobe")

if [ ! -f "$FFMPEG" ]; then
    echo "Error: ffmpeg not found. Please install with: brew install ffmpeg"
    exit 1
fi

if [ ! -f "$FFPROBE" ]; then
    echo "Error: ffprobe not found. Please install with: brew install ffmpeg"
    exit 1
fi

# Function to convert a single file
convert_file() {
    local input_file="$1"
    local output_file="${input_file%.*}_converted.mp4"
    
    echo "Converting: $(basename "$input_file")"
    
    # Get exact duration using ffprobe
    duration=$("$FFPROBE" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input_file")
    
    if [ -z "$duration" ]; then
        echo "Error: Could not determine duration for $input_file"
        return 1
    fi
    
    echo "Duration: ${duration}s"
    
    # Convert with ALAC audio codec
    "$FFMPEG" -y \
        -f lavfi -i "color=c=black:s=1920x1080:r=1" \
        -i "$input_file" \
        -map 0:v \
        -map 1:a \
        -c:v h264 \
        -preset ultrafast \
        -tune stillimage \
        -pix_fmt yuv420p \
        -c:a alac \
        -ac 2 \
        -t "$duration" \
        -shortest \
        -movflags +faststart \
        "$output_file" \
        -loglevel error
    
    if [ $? -eq 0 ]; then
        echo "✓ Success: $output_file"
        return 0
    else
        echo "✗ Failed: $input_file"
        return 1
    fi
}

# Main script
if [ $# -eq 0 ]; then
    echo "Usage: $0 <audio_file1> [audio_file2] ..."
    echo "Supported formats: mp3, m4a, aac, wav, flac, aiff"
    exit 1
fi

echo "Audio to Video Converter (ALAC)"
echo "==============================="
echo "Using ffmpeg: $FFMPEG"
echo "Using ffprobe: $FFPROBE"
echo ""

success_count=0
total_count=$#

# Process each file
for file in "$@"; do
    if [ -f "$file" ]; then
        convert_file "$file"
        if [ $? -eq 0 ]; then
            ((success_count++))
        fi
    else
        echo "Warning: File not found: $file"
    fi
    echo ""
done

echo "==============================="
echo "Conversion complete: $success_count/$total_count files converted successfully"