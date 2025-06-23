# ⚠️ IMPORTANT: Security Settings for AirPlay Automation

## 🚨 MUST READ BEFORE USING AIRPLAY FEATURES

The AirPlay automation feature in QuickTime Playlist apps requires special permissions to control your mouse and keyboard. **Without these permissions, AirPlay automation will NOT work.**

## Why These Permissions Are Needed

When you enable AirPlay, the app needs to:
1. **Move your mouse** to the AirPlay button
2. **Click** the AirPlay button
3. **Click** your AirPlay device (e.g., "living" room)

This is done using macOS automation tools, which require explicit permission for security reasons.

## 🔧 Required Settings (Step by Step)

### 1. Enable Accessibility Permissions

1. Open **System Settings** (or System Preferences)
2. Go to **Privacy & Security** → **Accessibility**
3. Click the lock 🔒 to make changes (enter your password)
4. Click the **+** button
5. Navigate to and add:
   - **Python** (usually in `/usr/local/bin/python3` or `/Library/Frameworks/Python.framework/`)
   - **Terminal** (in `/Applications/Utilities/`)
   - The app itself if you're using the compiled version
6. Make sure the checkboxes ✅ are checked for these apps

### 2. Install cliclick (Required for AirPlay)

```bash
brew install cliclick
```

If you don't have Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. First Run Setup

When you first use AirPlay:
1. macOS will show a dialog: **"Terminal" wants to control "System Events"**
2. Click **OK** to allow
3. You may see another: **"Python" wants to control "QuickTime Player"**
4. Click **OK** to allow

## 📍 Visual Guide

### System Settings → Privacy & Security → Accessibility

```
┌─────────────────────────────────────┐
│ Privacy & Security                  │
│ ├── Location Services               │
│ ├── Contacts                        │
│ ├── Calendars                       │
│ ├── Reminders                       │
│ ├── Photos                          │
│ ├── Bluetooth                       │
│ ├── Microphone                      │
│ ├── Camera                          │
│ ├── HomeKit                         │
│ ├── Media & Apple Music             │
│ └── Accessibility ← Click here      │
│     │                               │
│     └── Allow the apps below to     │
│         control your computer:      │
│         ☑ Terminal                  │
│         ☑ Python                    │
│         ☑ QuickTimeAudioPlaylist    │
└─────────────────────────────────────┘
```

## ⚙️ Configure AirPlay Settings

The app includes a **Settings** button where you can adjust:
- **X Offset**: Horizontal position adjustment
- **Y Offset**: Vertical position adjustment
- **AirPlay Delay**: Time to wait before clicking
- **Menu Wait Time**: Time to wait for menu to appear

Default values work for most setups, but you may need to adjust if:
- Your screen resolution is different
- Your AirPlay device is in a different position in the menu

## 🚫 Common Issues

### "AirPlay button not found"
- Make sure QuickTime Player is the active window
- The video/audio must be loaded first
- Try increasing the AirPlay Delay in settings

### "Click at wrong position"
- Adjust X/Y offsets in Settings
- Default: X=135, Y=80 (works for "living" device)
- Use positive values to move right/down
- Use negative values to move left/up

### "Permission denied" errors
- Revisit System Settings → Privacy & Security → Accessibility
- Make sure ALL required apps are added AND checked ✅
- Restart the app after changing permissions

## 🔒 Security Notes

- These permissions allow the app to control your mouse/keyboard
- Only grant these permissions to apps you trust
- You can revoke permissions at any time in System Settings
- The app ONLY uses these permissions for AirPlay control

## 💡 Tips

1. **Test without AirPlay first** - Make sure basic playback works
2. **Manual test** - Try clicking AirPlay manually in QuickTime first
3. **Screen recording** - Use QuickTime's screen recording to see what the automation is doing
4. **Check logs** - The app prints click coordinates in the console

## Alternative: Manual AirPlay

If you prefer not to grant these permissions, you can:
1. Disable AirPlay automation (uncheck AirPlay button)
2. Manually click AirPlay in QuickTime after each track starts
3. Use the "Play One" feature for single tracks

---

⚠️ **Remember**: Without proper accessibility permissions, AirPlay automation will NOT work. This is a macOS security feature, not a bug in the app.