#!/bin/bash
# Shell script to play videos in QuickTime sequentially

# Check if files are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <video1.mp4> <video2.mp4> ..."
    exit 1
fi

# Play each video file
for video in "$@"; do
    if [ -f "$video" ]; then
        echo "Playing: $video"
        
        # Use osascript to control QuickTime
        osascript <<EOF
        tell application "QuickTime Player"
            activate
            set videoDoc to open POSIX file "$video"
            play videoDoc
            
            -- Wait for video to finish
            repeat while (playing of videoDoc)
                delay 1
            end repeat
            
            close videoDoc saving no
        end tell
EOF
    else
        echo "File not found: $video"
    fi
done

echo "All videos played."