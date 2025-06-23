#!/usr/bin/env python3
"""
Simple QuickTime Player with AirPlay device selection
Only plays _converted.mp4 files
Uses SwitchAudioSource for device switching
"""

import subprocess
import os
import sys
from pathlib import Path

def get_audio_devices():
    """Get list of available audio devices using SwitchAudioSource"""
    try:
        result = subprocess.run(
            ['SwitchAudioSource', '-a'],
            capture_output=True,
            text=True,
            check=True
        )
        devices = result.stdout.strip().split('\n')
        return [d.strip() for d in devices if d.strip()]
    except FileNotFoundError:
        print("Error: SwitchAudioSource not found.")
        print("Install with: brew install switchaudio-osx")
        return []
    except subprocess.CalledProcessError:
        print("Error getting audio devices")
        return []

def set_audio_device(device_name):
    """Set the system audio output device"""
    try:
        subprocess.run(
            ['SwitchAudioSource', '-s', device_name],
            check=True
        )
        print(f"✓ Audio output set to: {device_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to set audio output to: {device_name}")
        return False

def play_video_in_quicktime(video_path, repeat_mode='none'):
    """
    Play a video file in QuickTime Player
    repeat_mode: 'none', 'one', 'all'
    """
    if not os.path.exists(video_path):
        print(f"File not found: {video_path}")
        return False
    
    abs_path = os.path.abspath(video_path)
    print(f"Playing: {os.path.basename(video_path)}")
    
    # AppleScript based on repeat mode
    if repeat_mode == 'one':
        # 한 곡 반복
        applescript = f'''
        tell application "QuickTime Player"
            activate
            
            -- Open the video
            set videoDoc to open POSIX file "{abs_path}"
            
            -- Present in full screen for better AirPlay experience
            present videoDoc
            
            -- Enable loop (Option+Command+L)
            set looping of videoDoc to true
            
            -- Start playing
            play videoDoc
            
            -- Keep running (press Cmd+Q to stop)
            repeat
                delay 1
                if not (exists videoDoc) then exit repeat
            end repeat
        end tell
        '''
    else:
        # 반복 없음 (기본)
        applescript = f'''
        tell application "QuickTime Player"
            activate
            
            -- Open the video
            set videoDoc to open POSIX file "{abs_path}"
            
            -- Present in full screen for better AirPlay experience
            present videoDoc
            
            -- Start playing
            play videoDoc
            
            -- Wait for playback to complete
            repeat while (playing of videoDoc)
                delay 1
            end repeat
            
            -- Close the document
            close videoDoc saving no
        end tell
        '''
    
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error playing video: {e}")
        return False

def find_converted_videos(paths):
    """Find all _converted.mp4 files from given paths"""
    videos = []
    
    for path in paths:
        path_obj = Path(path)
        
        if path_obj.is_file():
            # 단일 파일
            if path_obj.suffix == '.mp4' and path_obj.stem.endswith('_converted'):
                videos.append(str(path_obj))
            else:
                # 오디오 파일이면 _converted.mp4 찾기
                converted = path_obj.parent / f"{path_obj.stem}_converted.mp4"
                if converted.exists():
                    videos.append(str(converted))
                else:
                    print(f"⚠️  No converted video for: {path_obj.name}")
        elif path_obj.is_dir():
            # 디렉토리의 모든 _converted.mp4 파일
            for mp4 in path_obj.glob("*_converted.mp4"):
                videos.append(str(mp4))
    
    return videos

def main():
    if len(sys.argv) < 2:
        print("QuickTime Playlist with AirPlay Support")
        print("==" * 20)
        print("\nUsage:")
        print("  python3 quicktime_airplay_simple.py [options] file1 file2 ...")
        print("\nOptions:")
        print("  --list-devices           List available audio devices")
        print("  --device 'Device Name'   Set audio output device")
        print("  --repeat-one            Repeat current song")
        print("  --repeat-all            Repeat all songs")
        print("\nNote: Only plays _converted.mp4 files")
        print("\nExamples:")
        print("  python3 quicktime_airplay_simple.py --list-devices")
        print("  python3 quicktime_airplay_simple.py song_converted.mp4")
        print("  python3 quicktime_airplay_simple.py --device 'living' *_converted.mp4")
        print("  python3 quicktime_airplay_simple.py --repeat-one video_converted.mp4")
        print("  python3 quicktime_airplay_simple.py --repeat-all /converted_videos/")
        sys.exit(1)
    
    # List devices option
    if sys.argv[1] == '--list-devices':
        devices = get_audio_devices()
        if devices:
            print("Available audio devices:")
            for device in devices:
                print(f"  • {device}")
        sys.exit(0)
    
    # Parse arguments
    device_name = None
    repeat_mode = 'none'  # none, one, all
    input_paths = []
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--device' and i + 1 < len(sys.argv):
            device_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--repeat-one':
            repeat_mode = 'one'
            i += 1
        elif sys.argv[i] == '--repeat-all':
            repeat_mode = 'all'
            i += 1
        else:
            input_paths.append(sys.argv[i])
            i += 1
    
    if not input_paths:
        print("Error: No files specified")
        sys.exit(1)
    
    # Find all converted videos
    video_files = find_converted_videos(input_paths)
    
    if not video_files:
        print("Error: No _converted.mp4 files found")
        print("Use audio_to_video_minimal.py to convert audio files first")
        sys.exit(1)
    
    print(f"\nFound {len(video_files)} converted videos")
    
    # Set audio device if specified
    if device_name:
        if not set_audio_device(device_name):
            print("Warning: Continuing with current audio device")
    
    # Play videos based on repeat mode
    if repeat_mode == 'one' and len(video_files) > 0:
        # 한 곡 반복 - 첫 번째 파일만 반복
        print("\n🔂 Single track repeat mode")
        play_video_in_quicktime(video_files[0], repeat_mode='one')
    
    elif repeat_mode == 'all':
        # 전체 반복
        print("\n🔁 All tracks repeat mode")
        loop_count = 0
        try:
            while True:
                loop_count += 1
                print(f"\n--- Loop {loop_count} ---")
                for idx, video_file in enumerate(video_files, 1):
                    print(f"\n[{idx}/{len(video_files)}] ", end='')
                    play_video_in_quicktime(video_file)
        except KeyboardInterrupt:
            print("\n\n✓ Playback stopped by user")
    
    else:
        # 반복 없음
        print("\n▶️  Normal playback mode")
        success_count = 0
        for idx, video_file in enumerate(video_files, 1):
            print(f"\n[{idx}/{len(video_files)}] ", end='')
            if play_video_in_quicktime(video_file):
                success_count += 1
        
        print(f"\n\n✓ Played {success_count}/{len(video_files)} videos successfully")

if __name__ == "__main__":
    main()