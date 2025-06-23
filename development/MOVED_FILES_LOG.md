# Files Moved to Development Folder

This log documents all files that were moved from the root directory to the development folder on 2025-06-23.

## Test Files
- All files starting with `test_` (Python, AppleScript, shell scripts)
- All files containing `test` in the name
- Test audio/video files (Our Conversation.mp3, President Election.mp3, etc.)

## Debug Files
- All files starting with `debug_`
- Debug folders (debug/, debug_output/, debug_output_v2/)
- AirPlay debug folders (airplay_debug_enhanced/, airplay_debug_fixed/, audio_airplay_debug_v2/)

## Experimental/Development Scripts
- AirPlay experimental scripts (airplay_*.py, *_airplay_*.py)
- Detector scripts (*_detector.py)
- Enabler scripts (*_enabler*.py)
- Creator scripts (create_*.py, template_creator*.py)
- Utility scripts (capture_*.py, analyze_*.py, check_*.py, find_*.py, etc.)
- Version variants (*_v2.py, *_fixed.py, *_enhanced.py)
- Automation scripts (*_automation.py, *_automation.applescript)

## Build Artifacts
- build/ folder
- dist/ folder
- PyInstaller spec files (*.spec)
- App bundles (QuickTime AirPlay Simple.app, QuickTime AirPlay.app, QuickTime Playlist.app)

## Template Resources
- templates/ folder
- universal_templates/ folder
- roi_templates/ folder

## Experimental Variations
- Cafe playlist variations (cafe_*.py, cafe_*.sh, cafe_*.log)
- Converter variations (QuickTimeConverter*.py, audio_to_video_*.py)
- GUI variations (AudioPlaylistPyQt.py, QuickTimePlaylistPro.py)
- Controller variations (*_controller.py, *_clicker.py)

## Development Documentation
- Technical documentation (ROI_DETECTION_README.md, TECHNICAL_BREAKDOWN.md, etc.)
- Setup guides (vmware_airplay_setup.md, howtouse_quicktime_airplay_simple.md)
- Control documentation (AirPlayControl.md, AutomatorFix.md)

## Other Development Files
- Shell scripts for development (install_*.sh, run_*.sh, create_*.sh)
- Image files used for testing (*.png, *.json)
- HTTP and advanced features (QuickTimeHTTPPlaylist.applescript, http_playlist_controller.py)

## Files Kept in Root (Production-Ready)
- Main applications:
  - QuickTimePlayerAudioPlaylist.py (main audio playlist app)
  - SimpleAudioPlaylist.py (simplified version)
  - QuickDrop.py (drag-and-drop player)
  - quicktime_playlist_gui.py (GUI version)
  - QuickTimePlaylistSimple.py (simple integrated version)
  
- Production AppleScript files:
  - PlayVideosDirect.applescript
  - PlayVideosFixed.applescript
  - PlayVideosInOrder.applescript
  - PlayVideosSimple.applescript
  
- Essential documentation:
  - README.md
  - CLAUDE.md
  - CONTRIBUTING.md
  - PROJECT_MANIFESTO.md
  - LICENSE
  
- Production app:
  - QuickTimePlaylist.app (Automator droplet)