#!/usr/bin/env python3
"""
Smart AirPlay Detector
Finds UI elements dynamically without relying on fixed offsets
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

class SmartAirPlayDetector:
    def __init__(self):
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True
        self.scale_factor = self.get_scale_factor()
        self.template_dir = Path(__file__).parent / "templates"
        
    def get_scale_factor(self):
        """Get Retina display scale factor"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        physical_width = screenshot.width
        return physical_width / logical_width
    
    def enable_airplay(self):
        """Enable AirPlay with smart detection"""
        print("🚀 Smart AirPlay Detector")
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
        airplay_pos = self.find_airplay_button()
        if not airplay_pos:
            print("❌ Could not find AirPlay button")
            return False
        
        print(f"\n📍 Clicking AirPlay at {airplay_pos}...")
        pyautogui.click(airplay_pos[0], airplay_pos[1])
        time.sleep(2)  # Give menu time to open
        
        # Step 4: Find checkbox in the menu
        success = self.find_and_click_checkbox()
        
        if success:
            print("\n✅ AirPlay should now be enabled!")
        else:
            print("\n❌ Could not find checkbox")
        
        return success
    
    def find_airplay_button(self):
        """Find AirPlay button with multiple methods"""
        # Method 1: Template matching
        airplay_icon = self.template_dir / "airplay_icon.png"
        if airplay_icon.exists():
            print("\n🔍 Searching for AirPlay icon...")
            try:
                location = pyautogui.locateCenterOnScreen(str(airplay_icon), confidence=0.7)
                if location:
                    logical_x = location.x / self.scale_factor
                    logical_y = location.y / self.scale_factor
                    print(f"✅ AirPlay found at ({logical_x:.0f}, {logical_y:.0f})")
                    return (logical_x, logical_y)
            except Exception as e:
                print(f"⚠️ Template search failed: {e}")
        
        # Method 2: Common position
        print("\n📍 Using common AirPlay position...")
        width, height = pyautogui.size()
        return (width - 150, height - 50)
    
    def find_and_click_checkbox(self):
        """Find checkbox in the open menu"""
        print("\n🔍 Searching for checkbox in menu...")
        
        # Take screenshot of current screen
        screenshot = pyautogui.screenshot()
        
        # Method 1: Look for checkbox template
        checkbox_unchecked = self.template_dir / "checkbox_unchecked.png"
        if checkbox_unchecked.exists():
            try:
                # Search for all checkboxes
                checkboxes = list(pyautogui.locateAllOnScreen(
                    str(checkbox_unchecked), 
                    confidence=0.6
                ))
                
                if checkboxes:
                    print(f"✅ Found {len(checkboxes)} checkbox(es)")
                    
                    # Click the first one (usually the "This Computer" checkbox)
                    first_checkbox = checkboxes[0]
                    center = pyautogui.center(first_checkbox)
                    
                    # Convert to logical coordinates
                    logical_x = center.x / self.scale_factor
                    logical_y = center.y / self.scale_factor
                    
                    print(f"📍 Clicking checkbox at ({logical_x:.0f}, {logical_y:.0f})")
                    pyautogui.click(logical_x, logical_y)
                    return True
            except Exception as e:
                print(f"⚠️ Checkbox search failed: {e}")
        
        # Method 2: Pattern-based search
        # Look for typical menu structure
        print("\n📍 Using pattern-based search...")
        
        # The menu typically appears near where we clicked
        # Search in a grid pattern around the last click position
        current_x, current_y = pyautogui.position()
        
        # Common checkbox positions relative to menu
        search_patterns = [
            (-100, -150),  # Top left
            (-80, -160),   # Our tested offset
            (-120, -140),  # Alternative
            (-60, -170),   # Another alternative
        ]
        
        for dx, dy in search_patterns:
            test_x = current_x + dx
            test_y = current_y + dy
            
            print(f"   Testing position ({test_x:.0f}, {test_y:.0f})...")
            
            # Move mouse to show where we're testing
            pyautogui.moveTo(test_x, test_y, duration=0.3)
            time.sleep(0.2)
            
            # Ask user for confirmation
            print("   Is the mouse on a checkbox? Clicking in 2 seconds...")
            time.sleep(2)
            
            pyautogui.click()
            return True
        
        return False
    
    def create_better_templates(self):
        """Interactive template creation"""
        print("\n📸 Template Creation Mode")
        print("=" * 50)
        
        self.template_dir.mkdir(exist_ok=True)
        
        print("\nThis will help create better templates")
        print("Follow the prompts carefully")
        
        # Create checkbox template
        print("\n1️⃣ Checkbox Template")
        print("   - Open AirPlay menu in QuickTime")
        print("   - Make sure checkbox is visible")
        input("\nPress Enter when ready...")
        
        print("\n5 seconds to position mouse on checkbox...")
        for i in range(5, 0, -1):
            print(f"\r{i}...", end='', flush=True)
            time.sleep(1)
        
        # Capture small region around mouse
        x, y = pyautogui.position()
        region = pyautogui.screenshot(region=(x-20, y-20, 40, 40))
        
        checkbox_path = self.template_dir / "checkbox_better.png"
        region.save(checkbox_path)
        print(f"\n💾 Saved: {checkbox_path}")
        
        print("\n✅ Template creation complete!")

def main():
    detector = SmartAirPlayDetector()
    
    print("🎯 Smart AirPlay Detector")
    print("\nOptions:")
    print("1. Enable AirPlay")
    print("2. Create better templates")
    
    # Auto-run option 1
    print("\nStarting AirPlay enabler...")
    time.sleep(2)
    
    detector.enable_airplay()

if __name__ == "__main__":
    main()