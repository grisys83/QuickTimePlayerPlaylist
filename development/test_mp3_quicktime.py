#!/usr/bin/env python3
"""
Test MP3 playback in QuickTime with different methods
"""

import subprocess
import time
import sys
from pathlib import Path

def test_method_1(mp3_file):
    """Method 1: Keep QuickTime alive with new movie recording"""
    print("\n1. Testing with new movie recording to keep QuickTime alive...")
    
    # First, create a new movie recording to keep QuickTime running
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to new movie recording'
    ], capture_output=True)
    time.sleep(1)
    
    # Now open the MP3
    script = f'''
    tell application "QuickTime Player"
        open POSIX file "{mp3_file}"
        delay 1
        close window 2  -- Close the movie recording window
        play front document
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"   Result: {result.stdout}")
    if result.stderr:
        print(f"   Error: {result.stderr}")

def test_method_2(mp3_file):
    """Method 2: Use 'open with' command"""
    print("\n2. Testing with 'open -W' command...")
    
    # Close existing documents
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to close every document'
    ], capture_output=True)
    
    # Open with -W flag (waits for app to open)
    subprocess.Popen(['open', '-W', '-a', 'QuickTime Player', mp3_file])
    time.sleep(2)
    
    # Try to play
    subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to play front document'
    ], capture_output=True)

def test_method_3(mp3_file):
    """Method 3: Force QuickTime to stay open"""
    print("\n3. Testing with ignoring application responses...")
    
    script = f'''
    ignoring application responses
        tell application "QuickTime Player"
            activate
        end tell
    end ignoring
    
    delay 1
    
    tell application "QuickTime Player"
        open POSIX file "{mp3_file}"
        delay 1
        set frontDoc to front document
        play frontDoc
        
        -- Get some info
        set docName to name of frontDoc
        return "Playing: " & docName
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"   Result: {result.stdout}")

def test_method_4(mp3_file):
    """Method 4: Open as URL"""
    print("\n4. Testing open as URL...")
    
    # Convert to file URL
    file_url = Path(mp3_file).as_uri()
    
    script = f'''
    tell application "QuickTime Player"
        activate
        open location "{file_url}"
        delay 1
        play front document
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    print(f"   Result: {result.stdout}")
    if result.stderr:
        print(f"   Error: {result.stderr}")

def check_quicktime_status():
    """Check QuickTime status"""
    print("\n   Checking QuickTime status...")
    
    # Count documents
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to count documents'
    ], capture_output=True, text=True)
    print(f"   Documents open: {result.stdout.strip()}")
    
    # Check if playing
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to if (count documents) > 0 then playing of front document else "no documents"'
    ], capture_output=True, text=True)
    print(f"   Playing status: {result.stdout.strip()}")
    
    # Get document name
    result = subprocess.run([
        'osascript', '-e',
        'tell application "QuickTime Player" to if (count documents) > 0 then name of front document else "no documents"'
    ], capture_output=True, text=True)
    print(f"   Document name: {result.stdout.strip()}")

def main():
    if len(sys.argv) < 2:
        # Try to find an MP3 file
        mp3_files = []
        
        # Search in common locations
        search_paths = [
            Path.home() / "Music",
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            Path.cwd()
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                mp3_files.extend(search_path.glob("*.mp3"))
                mp3_files.extend(search_path.glob("*.MP3"))
        
        mp3_files = list(set(mp3_files))[:10]  # Remove duplicates, limit to 10
        
        if mp3_files:
            print("Found MP3 files:")
            for i, f in enumerate(mp3_files):
                print(f"{i+1}. {f.name} ({f.parent.name})")
            choice = input("\nSelect a file (1-10) or enter path: ")
            
            if choice.isdigit() and 1 <= int(choice) <= len(mp3_files):
                mp3_file = str(mp3_files[int(choice)-1])
            else:
                mp3_file = choice
        else:
            print("No MP3 files found. Please provide a path:")
            mp3_file = input("MP3 file path: ")
            if not mp3_file:
                print("No file provided. Exiting.")
                return
    else:
        mp3_file = sys.argv[1]
    
    if not Path(mp3_file).exists():
        print(f"Error: File not found: {mp3_file}")
        return
    
    print(f"Testing MP3 playback: {Path(mp3_file).name}")
    print("=" * 50)
    
    # Test each method
    methods = [test_method_1, test_method_2, test_method_3, test_method_4]
    
    successful_methods = []
    
    for i, method in enumerate(methods):
        print(f"\n{'='*50}")
        print(f"Test {i+1}/{len(methods)}")
        
        method(mp3_file)
        time.sleep(2)
        check_quicktime_status()
        
        response = input("\nDid this method work? (y/n/q to quit all tests): ")
        if response.lower() == 'y':
            successful_methods.append(method.__name__)
            print(f"✅ {method.__name__} worked!")
        elif response.lower() == 'q':
            break
            
        # Close QuickTime before next test
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to quit'
        ], capture_output=True)
        time.sleep(1)
    
    print(f"\n\n{'='*50}")
    print("Test Summary:")
    print(f"Successful methods: {', '.join(successful_methods) if successful_methods else 'None'}")
    
    if successful_methods:
        print(f"\n✅ Recommended method: {successful_methods[0]}")

if __name__ == "__main__":
    main()