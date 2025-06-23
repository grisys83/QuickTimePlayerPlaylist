#!/usr/bin/env python3
"""
AirPlay Living Final - The definitive solution
Combines all working methods with fallbacks
"""

import subprocess
import time
import json
from pathlib import Path


class AirPlayLivingController:
    def __init__(self):
        self.settings_file = Path.home() / '.airplay_living_settings.json'
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load saved positions"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_settings(self):
        """Save positions for future use"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def open_test_file(self):
        """Open audio file in QuickTime"""
        music_file = "/Users/parkbyeongsu/Hyang/QuicktimePlaylist/Our Conversation.mp3"
        
        script = f'''
        tell application "QuickTime Player"
            activate
            close every window
            delay 0.5
            open POSIX file "{music_file}"
            play document 1
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
        time.sleep(2)
    
    def click_airplay_button(self):
        """Click the AirPlay button to open menu"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                
                -- Find AirPlay button
                set btnList to every button of window 1
                repeat with i from 1 to count of btnList
                    try
                        set btnDesc to description of button i of window 1
                        if btnDesc contains "외장" or btnDesc contains "AirPlay" then
                            -- Get position before clicking
                            set btnPos to position of button i of window 1
                            click button i of window 1
                            
                            -- Return button position for reference
                            return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string)
                        end if
                    end try
                end repeat
                
                return "not found"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        pos = result.stdout.strip()
        if pos != "not found" and ',' in pos:
            x, y = pos.split(',')
            self.settings['airplay_button'] = {'x': int(x), 'y': int(y)}
            print(f"✅ Clicked AirPlay button at ({x}, {y})")
            return True
        
        print("❌ AirPlay button not found")
        return False
    
    def click_living_method_ui_element(self):
        """Method 1: Direct UI element click"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if (count of windows) > 1 then
                    -- Click the 2nd menu item (living)
                    try
                        click UI element 2 of window 2
                        return "success"
                    on error
                        try
                            click button 2 of window 2
                            return "success"
                        end try
                    end try
                end if
                return "failed"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return result.stdout.strip() == "success"
    
    def click_living_method_coordinates(self):
        """Method 2: Calculate checkbox coordinates"""
        # Get menu item position
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if (count of windows) > 1 then
                    set menuWindow to window 2
                    set allElements to every UI element of menuWindow
                    
                    -- Get 2nd item (living)
                    if (count of allElements) >= 2 then
                        set livingItem to item 2 of allElements
                        set itemPos to position of livingItem
                        set itemSize to size of livingItem
                        
                        -- Return position and size
                        return (item 1 of itemPos as string) & "," & (item 2 of itemPos as string) & "," & (item 1 of itemSize as string) & "," & (item 2 of itemSize as string)
                    end if
                end if
                return "not found"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        data = result.stdout.strip()
        if data != "not found" and ',' in data:
            parts = data.split(',')
            x, y, w, h = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            
            # Checkbox is on the right side
            checkbox_x = x + w - 25
            checkbox_y = y + (h // 2)
            
            print(f"📍 Living item at ({x}, {y}), size {w}x{h}")
            print(f"🎯 Clicking checkbox at ({checkbox_x}, {checkbox_y})")
            
            # Save position
            self.settings['living_checkbox'] = {'x': checkbox_x, 'y': checkbox_y}
            self.save_settings()
            
            # Click using cliclick
            subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
            return True
        
        return False
    
    def click_living_method_saved(self):
        """Method 3: Use saved coordinates"""
        if 'living_checkbox' in self.settings:
            pos = self.settings['living_checkbox']
            print(f"📍 Using saved position ({pos['x']}, {pos['y']})")
            subprocess.run(['cliclick', f"c:{pos['x']},{pos['y']}"])
            return True
        return False
    
    def click_living_method_offset(self):
        """Method 4: Calculate from AirPlay button position"""
        if 'airplay_button' in self.settings:
            btn = self.settings['airplay_button']
            # Living checkbox is typically below and to the right of AirPlay button
            checkbox_x = btn['x'] + 135  # Changed from 130 to 135 (+5)
            checkbox_y = btn['y'] + 80   # Changed from 60 to 80 (+20)
            
            print(f"📍 Calculated position ({checkbox_x}, {checkbox_y})")
            subprocess.run(['cliclick', f'c:{checkbox_x},{checkbox_y}'])
            return True
        return False
    
    def manual_position_finder(self):
        """Let user manually find the checkbox"""
        print("\n🔍 Manual Position Finder")
        print("1. Make sure the AirPlay menu is open")
        print("2. Move your mouse to the 'living' checkbox")
        print("3. Press Enter when ready")
        
        input("\nPress Enter when mouse is on living checkbox...")
        
        # Get mouse position
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        pos = result.stdout.strip()
        
        if ':' in pos:
            x, y = pos.split(':')
            x, y = int(x), int(y)
            
            print(f"\n✅ Got position: ({x}, {y})")
            self.settings['living_checkbox'] = {'x': x, 'y': y}
            self.save_settings()
            
            # Test click
            print("Testing click...")
            subprocess.run(['cliclick', f'c:{x},{y}'])
            return True
        
        return False
    
    def select_living(self):
        """Main method to select living device"""
        print("\n🎯 Attempting to select 'living' device...")
        
        # Try all methods in order
        methods = [
            ("UI Element Click", self.click_living_method_ui_element),
            ("Coordinate Calculation", self.click_living_method_coordinates),
            ("Saved Position", self.click_living_method_saved),
            ("Offset from AirPlay", self.click_living_method_offset),
        ]
        
        for name, method in methods:
            print(f"\n   Trying {name}...")
            try:
                if method():
                    print(f"   ✅ Success with {name}!")
                    return True
                else:
                    print(f"   ❌ {name} failed")
            except Exception as e:
                print(f"   ❌ {name} error: {e}")
            
            time.sleep(0.5)
        
        # All methods failed, try manual
        print("\n❌ All automatic methods failed")
        print("\nWould you like to manually position the mouse? (y/n)")
        
        if input().lower() == 'y':
            return self.manual_position_finder()
        
        return False


def main():
    print("🎵 AirPlay Living Selector - Final Version")
    print("=" * 50)
    
    controller = AirPlayLivingController()
    
    # Step 1: Open file
    print("\n1️⃣ Opening audio file...")
    controller.open_test_file()
    
    # Step 2: Click AirPlay
    print("\n2️⃣ Opening AirPlay menu...")
    if not controller.click_airplay_button():
        print("Failed to open AirPlay menu")
        return
    
    time.sleep(1.5)
    
    # Step 3: Select living
    print("\n3️⃣ Selecting 'living' device...")
    if controller.select_living():
        print("\n🎉 Successfully selected living device!")
    else:
        print("\n😔 Could not select living device")
        print("\nTroubleshooting:")
        print("1. Make sure 'living' is visible in the AirPlay menu")
        print("2. Try running the script again")
        print("3. Use manual positioning mode")


if __name__ == "__main__":
    main()