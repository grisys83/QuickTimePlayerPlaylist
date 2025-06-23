#!/usr/bin/env python3
"""
Test QuickTime audio playback behavior
"""

import subprocess
import time
import sys
from pathlib import Path

def test_direct_open(audio_file):
    """Test 1: Direct open with QuickTime"""
    print("\n1. Testing direct open...")
    subprocess.run(['open', '-a', 'QuickTime Player', audio_file])
    time.sleep(3)
    
    # Check if document is open
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to count documents'
    ], capture_output=True, text=True)
    
    print(f"   Documents open: {result.stdout.strip()}")

def test_open_and_play(audio_file):
    """Test 2: Open and immediately play"""
    print("\n2. Testing open and play...")
    
    # Close any existing documents
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to close every document'
    ], capture_output=True)
    time.sleep(1)
    
    # Open file
    subprocess.run(['open', '-a', 'QuickTime Player', audio_file])
    time.sleep(2)
    
    # Try to play
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to play front document'
    ], capture_output=True, text=True)
    
    if result.stderr:
        print(f"   Error: {result.stderr}")
    else:
        print("   Play command sent successfully")
    
    time.sleep(2)
    
    # Check if playing
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
    ], capture_output=True, text=True)
    
    print(f"   Is playing: {result.stdout.strip()}")

def test_applescript_open(audio_file):
    """Test 3: Open using AppleScript"""
    print("\n3. Testing AppleScript open...")
    
    script = f'''
    tell application "QuickTime Player"
        activate
        open POSIX file "{audio_file}"
        delay 1
        play front document
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    
    if result.stderr:
        print(f"   Error: {result.stderr}")
    else:
        print("   AppleScript executed successfully")
    
    time.sleep(2)
    
    # Check status
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else false'
    ], capture_output=True, text=True)
    
    print(f"   Is playing: {result.stdout.strip()}")

def test_new_audio_recording():
    """Test 4: Create new audio recording (to keep QuickTime open)"""
    print("\n4. Testing new audio recording trick...")
    
    # First create a new audio recording to keep QuickTime active
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to new audio recording'
    ], capture_output=True)
    
    time.sleep(1)
    
    print("   New audio recording created to keep QuickTime active")

def test_activate_first(audio_file):
    """Test 5: Activate QuickTime first"""
    print("\n5. Testing activate first...")
    
    # Activate QuickTime
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to activate'
    ], capture_output=True)
    time.sleep(1)
    
    # Then open file
    subprocess.run(['open', '-a', 'QuickTime Player', audio_file])
    time.sleep(2)
    
    # Check status
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to count documents'
    ], capture_output=True, text=True)
    
    print(f"   Documents open: {result.stdout.strip()}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_quicktime_audio.py <audio_file>")
        print("Example: python3 test_quicktime_audio.py song.mp3")
        return
    
    audio_file = sys.argv[1]
    if not Path(audio_file).exists():
        print(f"Error: File not found: {audio_file}")
        return
    
    print(f"Testing QuickTime audio playback with: {audio_file}")
    print("=" * 50)
    
    # Run tests
    test_direct_open(audio_file)
    input("\nPress Enter to continue to next test...")
    
    test_open_and_play(audio_file)
    input("\nPress Enter to continue to next test...")
    
    test_applescript_open(audio_file)
    input("\nPress Enter to continue to next test...")
    
    test_activate_first(audio_file)
    input("\nPress Enter to continue to next test...")
    
    test_new_audio_recording()
    
    print("\n\nTest complete!")
    print("\nConclusions:")
    print("- If QuickTime closes immediately, it might be a file format issue")
    print("- Try using AppleScript to open and play")
    print("- Creating a new audio recording can keep QuickTime active")

if __name__ == "__main__":
    main()