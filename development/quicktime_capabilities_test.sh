#!/bin/bash

echo "=== QuickTime Player Command Line and Control Methods Research ==="
echo

echo "1. Testing command line arguments:"
echo "-----------------------------------"
# Test various command line flags
for flag in --help -h --version -v --list --devices --airplay; do
    echo "Testing: $flag"
    "/System/Applications/QuickTime Player.app/Contents/MacOS/QuickTime Player" $flag 2>&1 | head -5 || echo "  No response or error"
    echo
done

echo "2. URL Schemes supported by QuickTime:"
echo "--------------------------------------"
plutil -p "/System/Applications/QuickTime Player.app/Contents/Info.plist" | grep -A 10 "CFBundleURLTypes"

echo
echo "3. AppleScript Dictionary Summary:"
echo "----------------------------------"
# Get main classes and commands
sdef "/System/Applications/QuickTime Player.app" | grep -E "<class name=|<command name=" | sed 's/.*name="\([^"]*\)".*/  - \1/' | sort -u

echo
echo "4. Testing System Events control:"
echo "---------------------------------"
osascript -e 'tell application "System Events" to tell process "QuickTime Player" to name of menu items of menu "Window" of menu bar 1' 2>&1

echo
echo "5. Available audio devices in system:"
echo "------------------------------------"
system_profiler SPAudioDataType | grep -E "^ {8}[^ ]|Transport:" | grep -B1 "Transport"

echo
echo "6. QuickTime Player preferences:"
echo "--------------------------------"
defaults read com.apple.QuickTimePlayerX 2>/dev/null || echo "No preferences set"

echo
echo "7. Testing open command with QuickTime:"
echo "---------------------------------------"
echo "The 'open' command supports these flags with QuickTime:"
echo "  open -a 'QuickTime Player' file.mp4"
echo "  open -a 'QuickTime Player' --args [arguments] file.mp4"
echo "  open -a 'QuickTime Player' -F file.mp4  # Fresh launch"
echo "  open -a 'QuickTime Player' -n file.mp4  # New instance"

echo
echo "8. Searching for AirPlay control methods:"
echo "----------------------------------------"
# Check if there are any AppleScript commands for AirPlay
osascript -e 'tell application "QuickTime Player" to name of every menu item of menu "View" of menu bar 1' 2>&1 | grep -i "airplay\|output" || echo "No AirPlay menu items found"

echo
echo "=== Summary of Findings ==="
echo "QuickTime Player does NOT support:"
echo "- Command line arguments (--help, --version, etc.)"
echo "- Direct AirPlay device selection via command line"
echo "- Hidden CLI options for output device control"
echo
echo "QuickTime Player DOES support:"
echo "- AppleScript automation for playback control"
echo "- Opening files via 'open' command"
echo "- Basic document properties access via AppleScript"
echo "- Recording device selection (audio/video input)"
echo
echo "AirPlay control must be done through:"
echo "- System UI (menu bar or QuickTime View menu)"
echo "- System-level audio routing (not available via CLI by default)"
echo "- Third-party tools like 'SwitchAudioSource' or 'audiodevice'"