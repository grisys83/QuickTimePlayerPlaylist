#!/usr/bin/env python3
"""
Universal AirPlay Automation System
- Works in any situation with QuickTime Player
- Step-by-step detection and automation
- Proper coordinate conversion for Retina displays
"""

import cv2
import numpy as np
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from coordinate_converter import CoordinateConverter

class UniversalAirPlayAutomation:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path(__file__).parent / "debug" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Templates
        self.templates = {
            'quicktime_window': self.template_dir / "quicktime_window.png",
            'control_bar': self.template_dir / "control_bar.png",
            'airplay_icon': self.template_dir / "airplay_icon.png",
            'apple_tv': self.template_dir / "apple_tv_checkbox.png",
            'checkbox_checked': self.template_dir / "checkbox_checked.png",
            'checkbox_unchecked': self.template_dir / "checkbox_unchecked.png"
        }
        
        print(f"🔧 Universal AirPlay Automation")
        print(f"📊 Scale factor: {self.converter.scale_factor}")
        print(f"📁 Debug output: {self.debug_dir}")
        
    def capture_screen(self, name="screenshot"):
        """Capture screen with debug save"""
        screenshot_path = "/tmp/universal_airplay_screen.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        # Save debug copy
        debug_path = self.debug_dir / f"{name}.png"
        cv2.imwrite(str(debug_path), screenshot)
        
        return screenshot
    
    def find_template_multiscale(self, screenshot, template_path, threshold=0.7, scales=None):
        """Find template with multiple scales and return screen coordinates"""
        if not template_path.exists():
            print(f"⚠️  Template not found: {template_path}")
            return None
            
        template = cv2.imread(str(template_path))
        if template is None:
            return None
            
        if scales is None:
            scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 2.0]
            
        best_match = None
        best_confidence = 0
        
        for scale in scales:
            # Resize template
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # Match
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val > threshold:
                best_confidence = max_val
                # Calculate center in CV2 coordinates
                cv2_x = max_loc[0] + width // 2
                cv2_y = max_loc[1] + height // 2
                
                # Convert to screen coordinates
                screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
                
                best_match = {
                    'cv2_coords': {'x': cv2_x, 'y': cv2_y},
                    'screen_coords': {'x': screen_x, 'y': screen_y},
                    'confidence': max_val,
                    'scale': scale,
                    'size': (width, height),
                    'top_left': max_loc
                }
        
        return best_match
    
    def find_all_templates(self, screenshot, template_path, threshold=0.7, scale=1.0):
        """Find all instances of a template"""
        if not template_path.exists():
            return []
            
        template = cv2.imread(str(template_path))
        if template is None:
            return []
            
        # Resize template
        width = int(template.shape[1] * scale)
        height = int(template.shape[0] * scale)
        resized = cv2.resize(template, (width, height))
        
        # Match
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # Find all locations above threshold
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            # Calculate center in CV2 coordinates
            cv2_x = pt[0] + width // 2
            cv2_y = pt[1] + height // 2
            
            # Convert to screen coordinates
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            matches.append({
                'cv2_coords': {'x': cv2_x, 'y': cv2_y},
                'screen_coords': {'x': screen_x, 'y': screen_y},
                'confidence': result[pt[1], pt[0]],
                'scale': scale,
                'size': (width, height),
                'top_left': pt
            })
        
        return matches
    
    def find_quicktime_window(self):
        """Step 1: Find and activate QuickTime window"""
        print("\n🔍 Step 1: Finding QuickTime Window")
        
        # First, check if QuickTime is running
        result = subprocess.run(['pgrep', '-x', 'QuickTime Player'], capture_output=True)
        if result.returncode != 0:
            print("❌ QuickTime Player is not running")
            return None
            
        # Get window info from AppleScript
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowBounds to {position, size} of window 1
                    set windowPos to item 1 of windowBounds
                    set windowSize to item 2 of windowBounds
                    return {item 1 of windowPos, item 2 of windowPos, ¬
                           item 1 of windowSize, item 2 of windowSize}
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if not result.stdout.strip():
            print("❌ No QuickTime window found")
            return None
            
        coords = [int(x) for x in result.stdout.strip().split(', ')]
        window = {
            'x': coords[0],
            'y': coords[1],
            'width': coords[2],
            'height': coords[3]
        }
        
        print(f"✅ QuickTime window found: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
        
        # Activate QuickTime
        print("🎬 Activating QuickTime Player...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        return window
    
    def show_control_bar(self, window):
        """Step 2: Show control bar by positioning mouse correctly"""
        print("\n🎮 Step 2: Showing Control Bar")
        
        # Calculate position: bottom 1/4 of window (CV2 coordinates), center horizontally
        # In CV2: y increases downward, so bottom 1/4 means 3/4 of height
        cv2_center_x = (window['x'] + window['width'] // 2) * self.converter.scale_factor
        cv2_control_y = (window['y'] + int(window['height'] * 0.75)) * self.converter.scale_factor
        
        # Convert to screen coordinates
        screen_x, screen_y = self.converter.cv2_to_screen(cv2_center_x, cv2_control_y)
        
        print(f"📍 Moving mouse to control area: ({screen_x}, {screen_y})")
        print(f"   Window bottom 1/4 position in CV2: ({cv2_center_x}, {cv2_control_y})")
        print(f"   Converted to screen: ({screen_x}, {screen_y})")
        
        # Move mouse smoothly
        self.move_mouse_smoothly(screen_x, screen_y)
        
        # Wait for controls to appear
        print("⏳ Waiting for controls to appear...")
        time.sleep(1.5)
        
        # Small movement to keep controls visible
        self.move_mouse_smoothly(screen_x + 5, screen_y)
        time.sleep(0.5)
        
        # Capture with controls
        screenshot = self.capture_screen("2_with_controls")
        
        # Verify controls are visible
        if self.verify_controls_visible(screenshot, window):
            print("✅ Control bar is visible")
            return True
        else:
            print("⚠️  Control bar might not be fully visible")
            # Try alternative positions
            for offset in [0.8, 0.85, 0.9]:
                cv2_alt_y = (window['y'] + int(window['height'] * offset)) * self.converter.scale_factor
                screen_x_alt, screen_y_alt = self.converter.cv2_to_screen(cv2_center_x, cv2_alt_y)
                print(f"   Trying offset {offset}: ({screen_x_alt}, {screen_y_alt})")
                self.move_mouse_smoothly(screen_x_alt, screen_y_alt)
                time.sleep(1)
                
                screenshot = self.capture_screen(f"2_controls_attempt_{offset}")
                if self.verify_controls_visible(screenshot, window):
                    print(f"✅ Control bar visible at offset {offset}")
                    return True
                    
        return False
    
    def verify_controls_visible(self, screenshot, window):
        """Verify control bar is visible"""
        if not window:
            return False
            
        # Convert window to CV2 coordinates
        cv2_window_y = window['y'] * self.converter.scale_factor
        cv2_window_height = window['height'] * self.converter.scale_factor
        
        # Check bottom portion of window for control bar elements
        bottom_region = screenshot[
            int(cv2_window_y + cv2_window_height * 0.7):int(cv2_window_y + cv2_window_height),
            :
        ]
        
        # Convert to grayscale and detect edges
        gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for horizontal lines (control bar typically has these)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        # Also check for UI elements
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ui_elements = sum(1 for c in contours if 100 < cv2.contourArea(c) < 5000)
        
        return (lines is not None and len(lines) > 2) or ui_elements > 5
    
    def find_airplay_icon(self, window=None, ensure_controls=True):
        """Step 3: Find AirPlay icon"""
        print("\n🔍 Step 3: Finding AirPlay Icon")
        
        # If we need to ensure controls are visible
        if ensure_controls and window:
            print("🔄 Re-activating QuickTime and showing controls...")
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(0.3)
            self.show_control_bar(window)
            
        screenshot = self.capture_screen("3_finding_airplay")
            
        result = self.find_template_multiscale(
            screenshot, 
            self.templates['airplay_icon'],
            threshold=0.6
        )
        
        if result:
            print(f"✅ Found AirPlay icon!")
            print(f"   Position: ({result['screen_coords']['x']}, {result['screen_coords']['y']})")
            print(f"   Confidence: {result['confidence']:.1%}")
            
            # Mark on debug image
            debug_img = screenshot.copy()
            cv2.rectangle(debug_img, 
                         result['top_left'], 
                         (result['top_left'][0] + result['size'][0], 
                          result['top_left'][1] + result['size'][1]),
                         (0, 255, 0), 3)
            cv2.imwrite(str(self.debug_dir / "3_airplay_found.png"), debug_img)
            
            return result['screen_coords']
        else:
            print("❌ Could not find AirPlay icon")
            # Check if controls are visible
            if self.verify_controls_visible(screenshot, window):
                print("   Controls are visible but AirPlay icon not found")
                print("   Check if AirPlay icon template exists and matches")
            else:
                print("   Controls are not visible - QuickTime may have lost focus")
            return None
    
    def click_airplay_and_find_appletv(self, airplay_coords, window=None):
        """Step 4: Click AirPlay and find Apple TV checkbox"""
        print("\n📺 Step 4: Opening AirPlay Menu")
        
        # Ensure QuickTime is active before clicking
        print("🔄 Ensuring QuickTime is active...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.3)
        
        # Move mouse to AirPlay position first (to show controls if needed)
        if window:
            print("🖱️  Moving to AirPlay position to ensure controls...")
            self.move_mouse_smoothly(airplay_coords['x'], airplay_coords['y'])
            time.sleep(0.5)
        
        # Click AirPlay icon
        print(f"🖱️  Clicking AirPlay at ({airplay_coords['x']}, {airplay_coords['y']})")
        subprocess.run(['cliclick', f"c:{airplay_coords['x']},{airplay_coords['y']}"])
        
        # Wait for menu
        print("⏳ Waiting for menu to open...")
        time.sleep(1.0)
        
        # Capture menu
        menu_screenshot = self.capture_screen("4_airplay_menu")
        
        # Look for Apple TV option and checkbox
        print("🔍 Looking for Apple TV option and checkbox...")
        
        # First find Apple TV text/icon
        appletv_result = None
        if self.templates['apple_tv'].exists():
            appletv_result = self.find_template_multiscale(
                menu_screenshot,
                self.templates['apple_tv'],
                threshold=0.6
            )
            
            if appletv_result:
                print(f"✅ Found Apple TV text/icon at: ({appletv_result['screen_coords']['x']}, {appletv_result['screen_coords']['y']})")
        
        # Now look for checkbox at the same Y level
        checkbox_coords = None
        
        # Check if we have checkbox templates
        if self.templates['checkbox_unchecked'].exists() or self.templates['checkbox_checked'].exists():
            print("🔍 Looking for checkbox...")
            
            # Try unchecked checkbox first
            if self.templates['checkbox_unchecked'].exists():
                checkbox_results = self.find_all_templates(
                    menu_screenshot,
                    self.templates['checkbox_unchecked'],
                    threshold=0.6
                )
                
                if checkbox_results and appletv_result:
                    # Find checkbox at same Y level as Apple TV
                    for checkbox in checkbox_results:
                        y_diff = abs(checkbox['cv2_coords']['y'] - appletv_result['cv2_coords']['y'])
                        if y_diff < 20:  # Within 20 pixels vertically
                            checkbox_coords = checkbox['screen_coords']
                            print(f"✅ Found unchecked checkbox at same level: ({checkbox_coords['x']}, {checkbox_coords['y']})")
                            break
            
            # Try checked checkbox if unchecked not found
            if not checkbox_coords and self.templates['checkbox_checked'].exists():
                checkbox_results = self.find_all_templates(
                    menu_screenshot,
                    self.templates['checkbox_checked'],
                    threshold=0.6
                )
                
                if checkbox_results and appletv_result:
                    for checkbox in checkbox_results:
                        y_diff = abs(checkbox['cv2_coords']['y'] - appletv_result['cv2_coords']['y'])
                        if y_diff < 20:
                            checkbox_coords = checkbox['screen_coords']
                            print(f"✅ Found checked checkbox at same level: ({checkbox_coords['x']}, {checkbox_coords['y']})")
                            break
        
        # If no checkbox found but Apple TV found, calculate position
        if not checkbox_coords and appletv_result:
            print("⚠️  No checkbox template found, calculating position...")
            # Checkbox is typically to the left of Apple TV text
            # Convert 50 screen pixels to the correct coordinate system
            offset_pixels = -50  # Negative because checkbox is to the left
            checkbox_coords = {
                'x': appletv_result['screen_coords']['x'] + offset_pixels,
                'y': appletv_result['screen_coords']['y']
            }
            print(f"📍 Estimated checkbox position: ({checkbox_coords['x']}, {checkbox_coords['y']})")
        
        # Complete fallback if nothing found
        if not checkbox_coords:
            print("⚠️  Using complete fallback for checkbox position")
            checkbox_coords = {
                'x': airplay_coords['x'] + 50,
                'y': airplay_coords['y'] + 70
            }
            print(f"📍 Fallback checkbox position: ({checkbox_coords['x']}, {checkbox_coords['y']})")
        
        return checkbox_coords
    
    def click_apple_tv(self, appletv_coords, airplay_coords=None, window=None):
        """Step 5: Click Apple TV checkbox"""
        print("\n✅ Step 5: Enabling Apple TV")
        
        # Re-activate QuickTime and re-open AirPlay menu
        if airplay_coords:
            print("🔄 Re-activating QuickTime and re-opening AirPlay menu...")
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(0.3)
            
            # Show controls if window info available
            if window:
                self.show_control_bar(window)
            else:
                # Move mouse to AirPlay position to show controls
                self.move_mouse_smoothly(airplay_coords['x'], airplay_coords['y'])
                time.sleep(0.5)
            
            # Re-click AirPlay to open menu
            print(f"🖱️  Re-clicking AirPlay at ({airplay_coords['x']}, {airplay_coords['y']})")
            subprocess.run(['cliclick', f"c:{airplay_coords['x']},{airplay_coords['y']}"])
            time.sleep(1.0)
        
        print(f"🖱️  Clicking Apple TV at ({appletv_coords['x']}, {appletv_coords['y']})")
        subprocess.run(['cliclick', f"c:{appletv_coords['x']},{appletv_coords['y']}"])
        
        time.sleep(0.5)
        print("✅ AirPlay to Apple TV should now be active!")
        
    def move_mouse_smoothly(self, target_x, target_y, steps=20):
        """Move mouse smoothly to target position"""
        # Get current position
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            current = result.stdout.strip().split(',')
            current_x, current_y = int(current[0]), int(current[1])
        else:
            current_x, current_y = target_x, target_y
            
        # Move in steps
        for i in range(steps + 1):
            progress = i / steps
            x = int(current_x + (target_x - current_x) * progress)
            y = int(current_y + (target_y - current_y) * progress)
            subprocess.run(['cliclick', f'm:{x},{y}'])
            time.sleep(0.02)
    
    def run_complete_automation(self):
        """Run the complete automation sequence"""
        print("\n🚀 Starting Universal AirPlay Automation")
        print("=" * 60)
        
        # Step 1: Find QuickTime window
        window = self.find_quicktime_window()
        if not window:
            print("\n❌ Automation failed: QuickTime window not found")
            print("Please open QuickTime Player with a video loaded")
            return False
            
        # Step 2: Show control bar
        if not self.show_control_bar(window):
            print("\n⚠️  Warning: Control bar might not be visible")
            
        # Step 3: Find AirPlay icon
        airplay_coords = self.find_airplay_icon(window, ensure_controls=True)
        if not airplay_coords:
            print("\n❌ Automation failed: Could not find AirPlay icon")
            print("Make sure the AirPlay icon template is available")
            return False
            
        # Step 4: Click AirPlay and find Apple TV
        appletv_coords = self.click_airplay_and_find_appletv(airplay_coords, window)
        
        # Step 5: Click Apple TV
        self.click_apple_tv(appletv_coords, airplay_coords, window)
        
        print("\n✅ Automation complete!")
        print(f"📁 Debug images saved to: {self.debug_dir}")
        
        # Save discovered coordinates
        self.save_coordinates(airplay_coords, appletv_coords)
        
        return True
    
    def save_coordinates(self, airplay_coords, appletv_coords):
        """Save discovered coordinates to settings files"""
        settings = {
            'airplay_icon_coords': airplay_coords,
            'apple_tv_coords': appletv_coords,
            'airplay_enabled': True,
            'auto_detected': True,
            'detection_time': datetime.now().isoformat(),
            'scale_factor': self.converter.scale_factor
        }
        
        # Save to both settings files
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            
            # Load existing settings
            existing = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        existing = json.load(f)
                except:
                    pass
                    
            # Update with new coordinates
            existing.update(settings)
            
            # Save
            with open(settings_file, 'w') as f:
                json.dump(existing, f, indent=2)
                
        print(f"\n💾 Coordinates saved to settings files")


def main():
    """Main function with interactive options"""
    print("🎯 Universal AirPlay Automation System")
    print("This system works with any QuickTime window position")
    print("\nOptions:")
    print("1. Run complete automation")
    print("2. Test step by step")
    print("3. Create missing templates")
    
    choice = input("\nSelect option (1-3): ")
    
    automation = UniversalAirPlayAutomation()
    
    if choice == "1":
        print("\n⚠️  Requirements:")
        print("- QuickTime Player is open")
        print("- A video is loaded")
        print("- AirPlay icon template exists")
        
        input("\nPress Enter to start automation...")
        automation.run_complete_automation()
        
    elif choice == "2":
        print("\n🧪 Step-by-step testing")
        
        # Test each step
        window = automation.find_quicktime_window()
        if window:
            input("\nPress Enter to show control bar...")
            automation.show_control_bar(window)
            
            input("\nPress Enter to find AirPlay icon...")
            # Pass window to ensure controls are re-shown after terminal focus
            airplay = automation.find_airplay_icon(window, ensure_controls=True)
            
            if airplay:
                input("\nPress Enter to click AirPlay...")
                appletv = automation.click_airplay_and_find_appletv(airplay, window)
                
                if appletv:
                    input("\nPress Enter to click Apple TV...")
                    automation.click_apple_tv(appletv, airplay, window)
                
    elif choice == "3":
        print("\n📸 Template Creation Helper")
        print("This will help you create the necessary templates")
        print("\n1. Open QuickTime with a video")
        print("2. Show the control bar")
        print("3. Take screenshots of:")
        print("   - AirPlay icon")
        print("   - Apple TV checkbox (when menu is open)")
        print(f"\n4. Save them to: {automation.template_dir}")
        print("\nTemplate names:")
        for name, path in automation.templates.items():
            exists = "✅" if path.exists() else "❌"
            print(f"   {exists} {path.name}")


if __name__ == "__main__":
    main()