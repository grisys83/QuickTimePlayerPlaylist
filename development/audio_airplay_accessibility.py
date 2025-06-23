#!/usr/bin/env python3
"""
Audio AirPlay Accessibility Detector - Using macOS Accessibility API
"""

import subprocess
import time
import json
from pathlib import Path


class AudioAirPlayAccessibilityDetector:
    def __init__(self):
        self.debug_output = []
        
    def detect_airplay_controls(self):
        """Detect AirPlay controls using Accessibility API"""
        print("\n♿ Audio AirPlay Accessibility Detection")
        print("=" * 50)
        print("\nUsing macOS Accessibility API for accurate detection")
        print("\n⚠️  Note: You may need to grant accessibility permissions")
        
        # Check if we have accessibility permissions
        if not self._check_accessibility_permission():
            print("\n❌ Accessibility permission required!")
            print("Please grant permission in:")
            print("System Preferences > Security & Privacy > Privacy > Accessibility")
            print("Add Terminal or your Python app to the list")
            return None
        
        input("\nMake sure QuickTime is playing audio. Press Enter...")
        
        # Step 1: Find QuickTime window and controls
        print("\n🔍 Finding QuickTime controls...")
        qt_elements = self._get_quicktime_ui_elements()
        
        if not qt_elements:
            print("❌ Could not find QuickTime UI elements")
            return None
        
        # Step 2: Find AirPlay button
        airplay_button = self._find_airplay_button(qt_elements)
        if not airplay_button:
            print("❌ Could not find AirPlay button")
            return None
        
        print(f"✅ Found AirPlay button: {airplay_button}")
        
        # Step 3: Click AirPlay and find Apple TV
        apple_tv_item = self._find_apple_tv_option(airplay_button)
        if not apple_tv_item:
            print("❌ Could not find Apple TV option")
            return None
        
        print(f"✅ Found Apple TV option: {apple_tv_item}")
        
        # Convert to coordinates
        results = {
            'airplay_icon_coords': self._element_to_coords(airplay_button),
            'apple_tv_coords': self._element_to_coords(apple_tv_item),
            'detection_method': 'accessibility_api'
        }
        
        self._save_results(results)
        return results
    
    def _check_accessibility_permission(self):
        """Check if we have accessibility permissions"""
        script = '''
        tell application "System Events"
            set isEnabled to UI elements enabled
            return isEnabled
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        return result.stdout.strip() == "true"
    
    def _get_quicktime_ui_elements(self):
        """Get QuickTime UI element hierarchy"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.5
                
                -- Get all UI elements
                set allElements to {}
                
                -- Get main window
                if exists window 1 then
                    tell window 1
                        -- Get all buttons
                        set buttonList to every button
                        repeat with btn in buttonList
                            try
                                set btnDesc to description of btn
                                set btnPos to position of btn
                                set btnSize to size of btn
                                set btnTitle to title of btn
                                set btnRole to role of btn
                                set btnSubrole to subrole of btn
                                
                                set elementInfo to "BUTTON|" & btnTitle & "|" & btnDesc & "|" & ¬
                                    (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & "|" & ¬
                                    (item 1 of btnSize as string) & "," & (item 2 of btnSize as string) & "|" & ¬
                                    btnRole & "|" & btnSubrole
                                
                                set end of allElements to elementInfo
                            end try
                        end repeat
                        
                        -- Get all UI elements in groups/toolbars
                        set groupList to every group
                        repeat with grp in groupList
                            try
                                set grpButtons to every button of grp
                                repeat with btn in grpButtons
                                    try
                                        set btnDesc to description of btn
                                        set btnPos to position of btn
                                        set btnSize to size of btn
                                        set btnTitle to title of btn
                                        
                                        set elementInfo to "GROUP_BUTTON|" & btnTitle & "|" & btnDesc & "|" & ¬
                                            (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & "|" & ¬
                                            (item 1 of btnSize as string) & "," & (item 2 of btnSize as string)
                                        
                                        set end of allElements to elementInfo
                                    end try
                                end repeat
                            end try
                        end repeat
                    end tell
                end if
                
                return allElements
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout:
            elements = []
            for line in result.stdout.strip().split(', '):
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 5:
                        elem_type = parts[0]
                        title = parts[1]
                        desc = parts[2]
                        pos = parts[3].split(',')
                        size = parts[4].split(',')
                        
                        elements.append({
                            'type': elem_type,
                            'title': title,
                            'description': desc,
                            'x': int(pos[0]) if pos[0] else 0,
                            'y': int(pos[1]) if pos[1] else 0,
                            'width': int(size[0]) if size[0] else 0,
                            'height': int(size[1]) if size[1] else 0
                        })
            
            # Debug output
            print(f"\n📋 Found {len(elements)} UI elements:")
            for elem in elements:
                print(f"   - {elem['type']}: {elem['title']} ({elem['description']})")
            
            return elements
        
        return None
    
    def _find_airplay_button(self, elements):
        """Find AirPlay button in UI elements"""
        print("\n🔍 Looking for AirPlay button...")
        
        # Look for AirPlay in descriptions or titles
        airplay_keywords = ['airplay', 'AirPlay', 'air play', 'stream']
        
        for elem in elements:
            desc = elem['description'].lower()
            title = elem['title'].lower()
            
            for keyword in airplay_keywords:
                if keyword in desc or keyword in title:
                    print(f"   Found potential AirPlay button: {elem['description']}")
                    return elem
        
        # If not found by name, try by position (usually right side of control bar)
        # Look for buttons in the bottom right area
        control_buttons = [e for e in elements if e['y'] > 500 and e['x'] > 600]
        
        if control_buttons:
            # Sort by x position (rightmost)
            control_buttons.sort(key=lambda e: e['x'], reverse=True)
            print(f"   Using rightmost control button as AirPlay")
            return control_buttons[0]
        
        return None
    
    def _find_apple_tv_option(self, airplay_button):
        """Click AirPlay and find Apple TV option"""
        print("\n🖱️ Clicking AirPlay button...")
        
        # Click using Accessibility API
        click_script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                click at {{{airplay_button['x'] + airplay_button['width']//2}, {airplay_button['y'] + airplay_button['height']//2}}}
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', click_script], capture_output=True)
        time.sleep(2)  # Wait for menu
        
        # Get menu items
        menu_script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                -- Get all menu items from any visible menus/popups
                set menuItems to {}
                
                -- Check for popup menus
                if exists menu 1 of group 1 of window 1 then
                    set popupMenu to menu 1 of group 1 of window 1
                    set menuItemList to every menu item of popupMenu
                    
                    repeat with mi in menuItemList
                        try
                            set miTitle to title of mi
                            set miPos to position of mi
                            set miSize to size of mi
                            
                            set itemInfo to miTitle & "|" & ¬
                                (item 1 of miPos as string) & "," & (item 2 of miPos as string) & "|" & ¬
                                (item 1 of miSize as string) & "," & (item 2 of miSize as string)
                            
                            set end of menuItems to itemInfo
                        end try
                    end repeat
                end if
                
                -- Also check for any floating windows
                set windowList to every window
                repeat with win in windowList
                    try
                        if exists checkbox 1 of win then
                            set checkboxList to every checkbox of win
                            repeat with cb in checkboxList
                                try
                                    set cbTitle is title of cb
                                    set cbPos to position of cb
                                    set cbSize to size of cb
                                    
                                    set itemInfo to "CHECKBOX|" & cbTitle & "|" & ¬
                                        (item 1 of cbPos as string) & "," & (item 2 of cbPos as string) & "|" & ¬
                                        (item 1 of cbSize as string) & "," & (item 2 of cbSize as string)
                                    
                                    set end of menuItems to itemInfo
                                end try
                            end repeat
                        end if
                    end try
                end repeat
                
                return menuItems
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', menu_script], 
                              capture_output=True, text=True)
        
        if result.stdout:
            items = []
            for line in result.stdout.strip().split(', '):
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        if parts[0] == "CHECKBOX":
                            title = parts[1]
                        else:
                            title = parts[0]
                        
                        pos = parts[-2].split(',')
                        size = parts[-1].split(',')
                        
                        items.append({
                            'title': title,
                            'x': int(pos[0]) if pos[0] else 0,
                            'y': int(pos[1]) if pos[1] else 0,
                            'width': int(size[0]) if size[0] else 0,
                            'height': int(size[1]) if size[1] else 0
                        })
            
            print(f"\n📋 Found {len(items)} menu items:")
            for item in items:
                print(f"   - {item['title']}")
            
            # Look for Apple TV
            apple_tv_keywords = ['apple tv', 'tv', 'living', 'bedroom', 'homepod']
            
            for item in items:
                title_lower = item['title'].lower()
                for keyword in apple_tv_keywords:
                    if keyword in title_lower:
                        print(f"   Found Apple TV: {item['title']}")
                        # Close menu
                        subprocess.run(['osascript', '-e', 
                                      'tell application "System Events" to key code 53'])
                        return item
            
            # If not found, use the second item (first is usually "This Computer")
            if len(items) > 1:
                # Close menu
                subprocess.run(['osascript', '-e', 
                              'tell application "System Events" to key code 53'])
                return items[1]
        
        # Close menu
        subprocess.run(['osascript', '-e', 
                      'tell application "System Events" to key code 53'])
        
        # Fallback
        return {
            'title': 'Apple TV (estimated)',
            'x': airplay_button['x'] + 50,
            'y': airplay_button['y'] + 70,
            'width': 100,
            'height': 20
        }
    
    def _element_to_coords(self, element):
        """Convert UI element to center coordinates"""
        return {
            'x': element['x'] + element['width'] // 2,
            'y': element['y'] + element['height'] // 2
        }
    
    def _save_results(self, results):
        """Save detection results"""
        settings_file = Path.home() / '.audio_accessibility_airplay_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Settings saved to: {settings_file}")
        
        # Update main templates
        templates_file = Path.home() / '.airplay_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        templates['audio_accessibility'] = results
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)


def main():
    print("♿ Audio AirPlay Accessibility Detector")
    print("Using macOS native UI detection")
    
    detector = AudioAirPlayAccessibilityDetector()
    result = detector.detect_airplay_controls()
    
    if result:
        print("\n✅ Detection complete!")
        print(f"\n📍 Coordinates:")
        print(f"   AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"   Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        
        # Test
        test = input("\n🧪 Test detection? (y/n): ")
        if test.lower() == 'y':
            import pyautogui
            
            print("\nTesting...")
            time.sleep(2)
            
            # Click AirPlay
            pyautogui.click(
                result['airplay_icon_coords']['x'],
                result['airplay_icon_coords']['y']
            )
            time.sleep(1.5)
            
            # Click Apple TV
            pyautogui.click(
                result['apple_tv_coords']['x'],
                result['apple_tv_coords']['y']
            )
            
            print("✅ Test complete!")
    else:
        print("\n❌ Detection failed")
        print("\nTroubleshooting:")
        print("1. Grant accessibility permissions")
        print("2. Make sure QuickTime is visible")
        print("3. Try the template-based detector instead")


if __name__ == "__main__":
    main()