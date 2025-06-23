#!/usr/bin/env python3
"""
Universal Audio AirPlay Automation
Works across different macOS environments
"""

import subprocess
import time
import json
from pathlib import Path


class UniversalAirPlayAutomation:
    def __init__(self):
        self.config_file = Path.home() / '.audio_airplay_config.json'
        self.config = self.load_config()
        
    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def enable_airplay(self, target_device="living"):
        """Enable AirPlay with multiple fallback methods"""
        print(f"\n🎯 Enabling AirPlay for: {target_device}")
        
        methods = [
            self.method1_menu_item_click,
            self.method2_ui_scripting,
            self.method3_relative_positioning,
            self.method4_user_calibration
        ]
        
        for i, method in enumerate(methods, 1):
            print(f"\n📍 Trying Method {i}...")
            try:
                if method(target_device):
                    print(f"✅ Success with Method {i}")
                    return True
            except Exception as e:
                print(f"❌ Method {i} failed: {e}")
        
        print("\n❌ All methods failed")
        return False
    
    def method1_menu_item_click(self, target_device):
        """Method 1: Direct menu item click using Accessibility API"""
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.5
                
                -- Click AirPlay button
                click button "외장 재생 메뉴 보기" of window 1
                delay 1.5
                
                -- Look for menu in different possible locations
                set foundMenu to false
                
                -- Check for popup window
                if (count of windows) > 1 then
                    set menuWindow to window 2
                    
                    -- Try to find and click the target device
                    set allElements to every UI element of menuWindow
                    repeat with elem in allElements
                        try
                            -- Check various properties
                            set elemProps to properties of elem
                            
                            -- Look for menu items, buttons, or radio buttons
                            if class of elem is menu item or class of elem is button or class of elem is radio button then
                                try
                                    set elemName to name of elem
                                    if elemName contains "{target_device}" then
                                        click elem
                                        return "success: clicked " & elemName
                                    end if
                                end try
                                
                                try
                                    set elemTitle to title of elem
                                    if elemTitle contains "{target_device}" then
                                        click elem
                                        return "success: clicked " & elemTitle
                                    end if
                                end try
                            end if
                        end try
                    end repeat
                end if
                
                -- Alternative: Check for menu attached to button
                try
                    set airplayBtn to button "외장 재생 메뉴 보기" of window 1
                    if exists menu 1 of airplayBtn then
                        set menuItems to menu items of menu 1 of airplayBtn
                        repeat with mi in menuItems
                            if title of mi contains "{target_device}" then
                                click mi
                                return "success: clicked menu item"
                            end if
                        end repeat
                    end if
                end try
                
                return "failed: menu item not found"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return "success" in result.stdout
    
    def method2_ui_scripting(self, target_device):
        """Method 2: UI scripting with pattern matching"""
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.5
                
                -- Click AirPlay button
                click button "외장 재생 메뉴 보기" of window 1
                delay 1.5
                
                -- Find clickable elements that might be our target
                set targetFound to false
                
                repeat with win in windows
                    set winElements to entire contents of win
                    repeat with elem in winElements
                        try
                            if class of elem is in {{button, checkbox, radio button, menu item}} then
                                set elemDesc to description of elem
                                if elemDesc contains "{target_device}" then
                                    click elem
                                    return "success: found by description"
                                end if
                            end if
                        end try
                    end repeat
                end repeat
                
                return "failed: UI element not found"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return "success" in result.stdout
    
    def method3_relative_positioning(self, target_device):
        """Method 3: Click based on relative positioning"""
        # Get menu structure
        analyze_script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                -- Click AirPlay
                click button "외장 재생 메뉴 보기" of window 1
                delay 1.5
                
                -- Analyze menu structure
                if (count of windows) > 1 then
                    set menuWindow to window 2
                    set menuPos to position of menuWindow
                    set menuSize to size of menuWindow
                    
                    -- Count items
                    set buttonCount to count of buttons of menuWindow
                    set radioCount to count of radio buttons of menuWindow
                    
                    return (item 1 of menuPos as string) & "," & (item 2 of menuPos as string) & "," & ¬
                           (item 1 of menuSize as string) & "," & (item 2 of menuSize as string) & "," & ¬
                           (buttonCount as string) & "," & (radioCount as string)
                else
                    return "no menu"
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', analyze_script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip() != "no menu":
            parts = result.stdout.strip().split(',')
            menu_x = int(parts[0])
            menu_y = int(parts[1])
            menu_width = int(parts[2])
            menu_height = int(parts[3])
            item_count = max(int(parts[4]), int(parts[5]))
            
            if item_count > 0:
                # Calculate item positions
                item_height = menu_height / item_count
                
                # Determine which item to click
                item_index = 2 if target_device == "living" else 3  # Default positions
                
                # Click position
                click_x = menu_x + menu_width - 30  # Near right edge for checkbox
                click_y = menu_y + (item_height * (item_index - 0.5))
                
                # Use cliclick or pyautogui
                try:
                    import pyautogui
                    pyautogui.click(click_x, click_y)
                    return True
                except:
                    # Fallback to cliclick
                    subprocess.run(['cliclick', f'c:{click_x},{click_y}'])
                    return True
        
        return False
    
    def method4_user_calibration(self, target_device):
        """Method 4: User calibration for first-time setup"""
        print("\n🎯 User Calibration Mode")
        print("This will help set up AirPlay for your specific system")
        
        if 'calibrated' in self.config and self.config['calibrated']:
            # Use saved calibration
            return self._use_calibrated_positions(target_device)
        
        # Calibration process
        print("\n📋 Calibration Steps:")
        print("1. I'll open the AirPlay menu")
        print("2. You'll tell me the position of items")
        print("3. I'll save this for future use")
        
        input("\nPress Enter to start calibration...")
        
        # Open AirPlay menu
        subprocess.run(['osascript', '-e', '''
            tell application "System Events"
                tell process "QuickTime Player"
                    set frontmost to true
                    click button "외장 재생 메뉴 보기" of window 1
                end tell
            end tell
        '''])
        
        time.sleep(1.5)
        
        # Get user input
        print("\n🔍 Looking at the AirPlay menu...")
        print("Which position is 'living' in the menu?")
        print("1. First item")
        print("2. Second item")
        print("3. Third item")
        
        position = input("Enter number (1-3): ").strip()
        
        # Save calibration
        self.config['calibrated'] = True
        self.config['living_position'] = int(position)
        self.config['menu_item_height'] = 30  # Approximate
        self.save_config()
        
        print("✅ Calibration saved!")
        
        # Now use the calibration
        return self._use_calibrated_positions(target_device)
    
    def _use_calibrated_positions(self, target_device):
        """Use saved calibration data"""
        position = self.config.get('living_position', 2)
        
        # Click based on saved position
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                -- Already showing menu, find and click item
                if (count of windows) > 1 then
                    set menuWindow to window 2
                    set allButtons to buttons of menuWindow
                    
                    if (count of allButtons) >= {position} then
                        click button {position} of menuWindow
                        return "success"
                    end if
                end if
                return "failed"
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return "success" in result.stdout


def main():
    """Test the universal automation"""
    automation = UniversalAirPlayAutomation()
    automation.enable_airplay("living")


if __name__ == "__main__":
    main()