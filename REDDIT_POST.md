# Reddit Post Draft

## Title Options:

1. "I made an open source playlist app for QuickTime Player that works with HomePod/AirPlay"
2. "Finally! A way to play local music playlists on HomePod without Apple Music subscription"
3. "[Open Source] QuickTime Playlist Pro - Continuous playback for your local music on HomePod"

## Post Content:

Hey r/HomePod (or r/apple),

I got frustrated with QuickTime Player only playing one file at a time, especially when trying to enjoy my local music collection on my HomePod. So I built an open source solution!

**What it does:**
- Adds playlist functionality to QuickTime Player
- Automatically connects to your AirPlay devices (HomePod, Apple TV, etc.)
- Supports shuffle, repeat, and queue management
- Works with both audio and video files
- Includes a 24/7 cafe mode for continuous playback

**Key Features:**
- 🎵 Full playlist management (add folders, save/load playlists)
- 🏠 Automatic AirPlay device selection
- 🔀 Shuffle and repeat modes
- 🎯 Play single tracks or entire playlists
- ⚙️ Configurable settings for different setups

**Technical Details:**
- Written in Python with PyQt5 GUI
- Uses AppleScript for QuickTime control
- Mouse automation for AirPlay selection (configurable offsets)
- Works on macOS 10.14+

**Why I made this:**
QuickTime Player doesn't support playlists natively, and playing local music files on HomePod typically requires an Apple Music subscription. This provides a free, open source alternative for those of us with local music libraries.

**Screenshots:**
[Include 2-3 screenshots of the app in action]

**Get it here:**
- GitHub: [your-repo-link]
- Direct download: [release-link]

**Installation:**
```bash
# Clone and run
git clone [repo]
cd quicktime-playlist-pro
pip3 install -r requirements.txt
brew install cliclick
python3 QuickTimePlayerAudioPlaylist.py
```

The project is completely open source (MIT license) and I'd love contributions or feedback! Whether it's bug reports, feature requests, or code contributions, all are welcome.

Hope this helps someone else who's been looking for a solution like this!

\#openhomepod #openairplay2 #quicktimeplaylist #opensource

---

## Subreddit Suggestions:

**Best subreddits to post:**
1. r/HomePod - Primary target audience
2. r/apple - Larger audience, general Apple users
3. r/macapps - Mac software focused
4. r/opensource - Open source community
5. r/Python - If focusing on technical aspects

**Posting tips:**
- Post during peak hours (9-10 AM or 2-3 PM EST)
- Include 2-3 screenshots showing the app
- Respond quickly to initial comments
- Cross-post after initial post gains traction
- Consider posting a demo video to r/HomePod

**Potential follow-up posts:**
- "Update: Added [new feature] to QuickTime Playlist Pro based on your feedback!"
- Technical deep-dive in r/Python
- Tutorial/guide post for specific use cases