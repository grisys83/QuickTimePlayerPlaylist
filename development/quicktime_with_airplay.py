#!/usr/bin/env python3
"""
QuickTime Player with AirPlay device selection
Requires: pip install pyobjc-framework-AVFoundation
"""

import subprocess
import os
import sys

try:
    from Foundation import NSObject
    from AVFoundation import AVAudioSession
    AIRPLAY_AVAILABLE = True
except ImportError:
    AIRPLAY_AVAILABLE = False
    print("Warning: AirPlay support not available. Install with: pip install pyobjc-framework-AVFoundation")

class AirPlayController:
    def __init__(self):
        self.audio_session = AVAudioSession.sharedInstance()
    
    def get_available_devices(self):
        """Get list of available audio output devices including AirPlay"""
        devices = []
        
        # Get available audio routes
        routes = self.audio_session.availableInputs()
        
        # Also check system audio devices using system_profiler
        try:
            result = subprocess.run(
                ['system_profiler', 'SPAudioDataType', '-json'],
                capture_output=True,
                text=True
            )
            # Parse JSON output for devices
            import json
            audio_data = json.loads(result.stdout)
            # Extract device names from the complex structure
            # This is a simplified version - actual parsing would be more complex
        except:
            pass
            
        # Use SwitchAudioSource if available
        try:
            result = subprocess.run(
                ['SwitchAudioSource', '-a'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')
        except FileNotFoundError:
            print("SwitchAudioSource not found. Install with: brew install switchaudio-osx")
            
        return devices
    
    def set_output_device(self, device_name):
        """Set the system audio output device"""
        try:
            subprocess.run(
                ['SwitchAudioSource', '-s', device_name],
                check=True
            )
            return True
        except:
            return False

def play_videos_with_airplay(video_files, airplay_device=None):
    """Play videos in QuickTime with optional AirPlay device selection"""
    
    # Set AirPlay device if specified
    if airplay_device:
        controller = AirPlayController()
        print(f"Setting output to: {airplay_device}")
        if not controller.set_output_device(airplay_device):
            print(f"Warning: Could not set output device to {airplay_device}")
    
    # Play videos
    for video_file in video_files:
        if not os.path.exists(video_file):
            print(f"File not found: {video_file}")
            continue
            
        print(f"Playing: {video_file}")
        
        applescript = f'''
        tell application "QuickTime Player"
            activate
            set videoDoc to open POSIX file "{os.path.abspath(video_file)}"
            
            -- Try to set presentation mode for better AirPlay experience
            present videoDoc
            
            play videoDoc
            
            -- Wait for playback to complete
            repeat while (playing of videoDoc)
                delay 1
            end repeat
            
            close videoDoc saving no
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error playing {video_file}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quicktime_with_airplay.py [--device 'Device Name'] video1.mp4 video2.mp4 ...")
        print("\nList available devices:")
        print("  python3 quicktime_with_airplay.py --list-devices")
        sys.exit(1)
    
    if sys.argv[1] == '--list-devices':
        controller = AirPlayController()
        devices = controller.get_available_devices()
        print("Available audio devices:")
        for device in devices:
            print(f"  - {device}")
        sys.exit(0)
    
    # Parse arguments
    airplay_device = None
    video_files = []
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--device' and i + 1 < len(sys.argv):
            airplay_device = sys.argv[i + 1]
            i += 2
        else:
            video_files.append(sys.argv[i])
            i += 1
    
    if not video_files:
        print("Error: No video files specified")
        sys.exit(1)
    
    play_videos_with_airplay(video_files, airplay_device)

if __name__ == "__main__":
    main()