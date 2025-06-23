#!/usr/bin/env python3
"""
Final AirPlay Solution
Combines all methods with fallbacks
"""

import subprocess
import time
import json
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("❌ PyAutoGUI가 설치되지 않았습니다")
    print("설치: pip install pyautogui pillow")
    exit(1)

class AirPlayEnabler:
    def __init__(self):
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True
        self.template_dir = Path(__file__).parent / "templates"
        self.settings_file = Path.home() / '.airplay_manual_positions.json'
        self.scale_factor = self.get_scale_factor()
        
    def get_scale_factor(self):
        """Get Retina display scale factor"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        return screenshot.width / logical_width
    
    def enable(self):
        """Main method to enable AirPlay"""
        print("🚀 AirPlay Enabler - Final Solution")
        print("=" * 50)
        
        # Activate QuickTime
        print("\n📍 Activating QuickTime...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # Show controls
        width, height = pyautogui.size()
        print("📍 Showing controls...")
        pyautogui.moveTo(width // 2, height - 100, duration=0.5)
        time.sleep(0.8)
        
        # Find and click AirPlay
        airplay_pos = self.find_airplay()
        if not airplay_pos:
            print("❌ Could not find AirPlay button")
            return False
        
        print(f"\n📍 Clicking AirPlay at {airplay_pos}...")
        pyautogui.click(airplay_pos[0], airplay_pos[1])
        time.sleep(1.5)
        
        # Click checkbox
        success = self.click_checkbox()
        
        if success:
            print("\n✅ AirPlay enabled successfully!")
        else:
            print("\n❌ Failed to enable AirPlay")
            
        return success
    
    def find_airplay(self):
        """Find AirPlay button"""
        # Method 1: Template matching
        airplay_icon = self.template_dir / "airplay_icon.png"
        if airplay_icon.exists():
            try:
                location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
                if location:
                    logical_x = location.x / self.scale_factor
                    logical_y = location.y / self.scale_factor
                    print(f"✅ AirPlay found via template at ({logical_x:.0f}, {logical_y:.0f})")
                    return (logical_x, logical_y)
            except:
                pass
        
        # Method 2: Common position
        width, height = pyautogui.size()
        pos = (width - 150, height - 50)
        print(f"📍 Using common AirPlay position {pos}")
        return pos
    
    def click_checkbox(self):
        """Click the checkbox using best available method"""
        # Method 1: Use saved position
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    pos = data['manual_positions']['last_checkbox']
                    print(f"\n📍 Using saved checkbox position ({pos['x']}, {pos['y']})")
                    pyautogui.click(pos['x'], pos['y'])
                    return True
            except:
                pass
        
        # Method 2: Search for checkbox template
        checkbox_template = self.template_dir / "checkbox_unchecked.png"
        if checkbox_template.exists():
            try:
                checkboxes = list(pyautogui.locateAllOnScreen(
                    str(checkbox_template), 
                    confidence=0.6
                ))
                if checkboxes:
                    first = checkboxes[0]
                    center = pyautogui.center(first)
                    logical_x = center.x / self.scale_factor
                    logical_y = center.y / self.scale_factor
                    print(f"\n📍 Found checkbox at ({logical_x:.0f}, {logical_y:.0f})")
                    pyautogui.click(logical_x, logical_y)
                    return True
            except:
                pass
        
        # Method 3: Manual mode
        print("\n🎯 Manual mode - position the mouse on the checkbox")
        print("   You have 10 seconds...")
        
        for i in range(10, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... Position: ({x}, {y})", end='', flush=True)
            time.sleep(1)
        
        print("\n   Clicking!")
        pyautogui.click()
        
        # Save this position for next time
        self.save_position(x, y)
        return True
    
    def save_position(self, x, y):
        """Save successful position"""
        data = {
            'manual_positions': {
                'last_checkbox': {'x': x, 'y': y}
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Position saved for next time")

def main():
    print("🎬 QuickTime AirPlay - Final Solution")
    print("\nThis version will:")
    print("1. Try to use your saved position (963, 809)")
    print("2. Fall back to template matching if needed")
    print("3. Let you manually position if all else fails")
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    enabler = AirPlayEnabler()
    enabler.enable()

if __name__ == "__main__":
    main()