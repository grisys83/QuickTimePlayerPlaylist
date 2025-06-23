#!/usr/bin/env python3
"""
Reliable AirPlay Enabler
Uses the offset that we know works from testing
"""

import subprocess
import time
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

class ReliableAirPlayEnabler:
    def __init__(self):
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True
        self.scale_factor = self.get_scale_factor()
        
    def get_scale_factor(self):
        """Get Retina display scale factor"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        physical_width = screenshot.width
        return physical_width / logical_width
    
    def enable_airplay(self):
        """Enable AirPlay using the most reliable method"""
        print("🚀 Reliable AirPlay Enabler")
        print("=" * 50)
        
        print(f"\n📐 Display scale: {self.scale_factor}x")
        width, height = pyautogui.size()
        print(f"📐 Screen size: {width}x{height}")
        
        # Step 1: Activate QuickTime
        print("\n📍 Activating QuickTime...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # Step 2: Show controls
        print("📍 Showing controls...")
        pyautogui.moveTo(width // 2, height - 100, duration=0.5)
        time.sleep(0.8)
        
        # Step 3: Find and click AirPlay
        template_dir = Path(__file__).parent / "templates"
        airplay_icon = template_dir / "airplay_icon.png"
        
        airplay_pos = None
        
        if airplay_icon.exists():
            print("\n🔍 Searching for AirPlay icon...")
            try:
                location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
                if location:
                    # Convert to logical coordinates
                    logical_x = location.x / self.scale_factor
                    logical_y = location.y / self.scale_factor
                    airplay_pos = (logical_x, logical_y)
                    print(f"✅ AirPlay found at ({logical_x:.0f}, {logical_y:.0f})")
            except Exception as e:
                print(f"⚠️ Icon search failed: {e}")
        
        # If not found, use typical position
        if not airplay_pos:
            print("\n📍 Using typical AirPlay position...")
            airplay_pos = (width - 150, height - 50)
        
        # Click AirPlay
        print(f"\n📍 Clicking AirPlay at {airplay_pos}...")
        pyautogui.click(airplay_pos[0], airplay_pos[1])
        time.sleep(1.5)
        
        # Step 4: Click checkbox using the working offset
        # From testing: checkbox is at offset (-94, -160) from AirPlay button
        checkbox_x = airplay_pos[0] - 94
        checkbox_y = airplay_pos[1] - 160
        
        print(f"\n📍 Clicking checkbox at ({checkbox_x:.0f}, {checkbox_y:.0f})")
        print("   (Using tested offset: -94, -160 from AirPlay)")
        
        # Move mouse slowly to show where we're clicking
        pyautogui.moveTo(checkbox_x, checkbox_y, duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        
        print("\n✅ AirPlay should now be enabled!")
        
        # Save successful positions
        self.save_positions(airplay_pos[0], airplay_pos[1], checkbox_x, checkbox_y)
        
    def save_positions(self, airplay_x, airplay_y, checkbox_x, checkbox_y):
        """Save working positions for future use"""
        import json
        
        settings = {
            'last_working_positions': {
                'airplay': {'x': airplay_x, 'y': airplay_y},
                'checkbox': {'x': checkbox_x, 'y': checkbox_y},
                'offset': {'x': -94, 'y': -160}
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        settings_file = Path.home() / '.airplay_enabler_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"\n💾 Positions saved to {settings_file}")

def main():
    print("🎬 QuickTime AirPlay Enabler (Reliable Version)")
    print("\nThis uses the offset that worked in your testing:")
    print("  • Checkbox is 94 pixels left, 160 pixels up from AirPlay")
    
    print("\nMake sure:")
    print("  1. QuickTime Player is open with a video")
    print("  2. Your Apple TV is on the same network")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    enabler = ReliableAirPlayEnabler()
    enabler.enable_airplay()

if __name__ == "__main__":
    main()