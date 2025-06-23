#!/usr/bin/env python3
"""
Fast playlist player using CV2-based AirPlay
Simple command-line interface for playing video playlists
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from cv2_airplay_enabler import CV2AirPlayEnabler

class FastPlaylistPlayer:
    def __init__(self):
        self.load_settings()
        self.cv2_enabler = CV2AirPlayEnabler(self.settings)
        self.is_playing = False
        
    def load_settings(self):
        """Load AirPlay settings"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {}
            print("⚠️  No settings found. Run reset_airplay_coordinates.py first")
    
    def play_video(self, video_path, enable_airplay=True):
        """Play a single video"""
        print(f"\n▶️  Playing: {Path(video_path).name}")
        
        # Close existing windows
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        
        time.sleep(0.3)
        
        # Open video
        subprocess.run(['open', '-a', 'QuickTime Player', str(video_path)])
        time.sleep(1.0)  # Wait for video to load
        
        # Enable AirPlay if requested
        if enable_airplay:
            print("🔄 Enabling AirPlay...")
            start_time = time.time()
            
            if self.cv2_enabler.enable_airplay_fast():
                elapsed = time.time() - start_time
                print(f"✅ AirPlay enabled in {elapsed:.2f}s")
            else:
                print("⚠️  AirPlay enable failed")
        
        # Start playback
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], capture_output=True)
        
        self.is_playing = True
        
    def wait_for_completion(self):
        """Wait for current video to finish"""
        print("⏳ Waiting for playback to complete...")
        
        while self.is_playing:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
            ], capture_output=True, text=True)
            
            if result.stdout.strip() != "true":
                self.is_playing = False
                break
                
            time.sleep(2)
        
        print("✅ Playback completed")
    
    def play_playlist(self, video_files, enable_airplay=True):
        """Play a playlist of videos"""
        print(f"\n🎵 Playing playlist with {len(video_files)} videos")
        
        for i, video in enumerate(video_files, 1):
            if not Path(video).exists():
                print(f"❌ File not found: {video}")
                continue
                
            print(f"\n[{i}/{len(video_files)}]", end="")
            self.play_video(video, enable_airplay)
            
            if i < len(video_files):  # Not the last video
                self.wait_for_completion()
        
        print("\n✅ Playlist completed!")
    
    def stop(self):
        """Stop playback"""
        self.is_playing = False
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], capture_output=True)
        print("⏹ Playback stopped")


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Fast Playlist Player with CV2 AirPlay")
        print("Usage:")
        print("  python3 fast_playlist_player.py <video1> [video2] [video3] ...")
        print("  python3 fast_playlist_player.py playlist.m3u")
        print("  python3 fast_playlist_player.py --no-airplay <videos>")
        print("\nOptions:")
        print("  --no-airplay    Disable AirPlay (play locally)")
        print("  --test          Test with a single video")
        sys.exit(1)
    
    # Parse arguments
    enable_airplay = True
    video_files = []
    
    for arg in sys.argv[1:]:
        if arg == "--no-airplay":
            enable_airplay = False
        elif arg == "--test":
            # Test mode
            print("🧪 Test mode - please select a video file")
            from tkinter import filedialog
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            file = filedialog.askopenfilename(
                title="Select a video file",
                filetypes=[("Video files", "*.mp4 *.mov *.m4v"), ("All files", "*.*")]
            )
            if file:
                video_files = [file]
            root.destroy()
        elif arg.endswith('.m3u') or arg.endswith('.m3u8'):
            # Load playlist file
            playlist_path = Path(arg)
            if playlist_path.exists():
                with open(playlist_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            video_files.append(line)
        else:
            video_files.append(arg)
    
    if not video_files:
        print("❌ No video files specified")
        sys.exit(1)
    
    # Create player
    player = FastPlaylistPlayer()
    
    try:
        # Check if templates exist
        if enable_airplay and not player.cv2_enabler.templates_available:
            print("⚠️  AirPlay templates not found")
            print("Run 'python3 universal_airplay_automation.py' first to create templates")
            print("Or use saved coordinates by running 'python3 reset_airplay_coordinates.py'")
            response = input("\nContinue without AirPlay? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
            enable_airplay = False
        
        # Play the playlist
        player.play_playlist(video_files, enable_airplay)
        
    except KeyboardInterrupt:
        print("\n\n⏸ Interrupted by user")
        player.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        player.stop()


if __name__ == "__main__":
    main()