#!/usr/bin/env python3
"""
Interactive AirPlay detector with extensive debugging
"""

import cv2
import numpy as np
import subprocess
import time
from pathlib import Path
import json
from datetime import datetime

class InteractiveAirPlayDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path(__file__).parent / "debug_output" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Debug images will be saved to: {self.debug_dir}")
        
    def capture_screen(self, name="screenshot"):
        """Capture screen and save debug copy"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        # Save debug copy
        debug_path = self.debug_dir / f"{name}.png"
        cv2.imwrite(str(debug_path), screenshot)
        print(f"   📸 Saved: {debug_path.name}")
        
        return screenshot
    
    def get_mouse_position(self):
        """Get current mouse position"""
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            return (int(coords[0]), int(coords[1]))
        return None
    
    def move_mouse_slowly(self, target_x, target_y, steps=20):
        """Move mouse slowly so user can see"""
        current = self.get_mouse_position()
        if not current:
            subprocess.run(['cliclick', f'm:{target_x},{target_y}'])
            return
            
        for i in range(steps + 1):
            progress = i / steps
            x = int(current[0] + (target_x - current[0]) * progress)
            y = int(current[1] + (target_y - current[1]) * progress)
            subprocess.run(['cliclick', f'm:{x},{y}'])
            time.sleep(0.02)
    
    def interactive_position_finder(self, initial_x, initial_y, name="position"):
        """Interactive position adjustment with visual feedback"""
        print(f"\n🎯 Finding {name}")
        print("I'll move the mouse to where I think it should be.")
        print("You can adjust using the keyboard:")
        print("  ↑ w = up     ↓ s = down")
        print("  ← a = left   → d = right")
        print("  + = bigger steps (10px)   - = smaller steps (1px)")
        print("  c = confirm position")
        print("  r = reset to initial position")
        print("  q = quit/skip")
        
        x, y = initial_x, initial_y
        step_size = 5
        
        # Move to initial position
        self.move_mouse_slowly(x, y)
        print(f"\n📍 Initial position: ({x}, {y})")
        
        while True:
            cmd = input(f"Step size: {step_size}px | Position: ({x}, {y}) | Command: ").lower().strip()
            
            if cmd == 'c':
                print(f"✅ Confirmed: ({x}, {y})")
                return {'x': x, 'y': y}
            elif cmd == 'q':
                print("⏭️  Skipped")
                return None
            elif cmd == 'r':
                x, y = initial_x, initial_y
                self.move_mouse_slowly(x, y)
            elif cmd == 'w':
                y -= step_size
                subprocess.run(['cliclick', f'm:{x},{y}'])
            elif cmd == 's':
                y += step_size
                subprocess.run(['cliclick', f'm:{x},{y}'])
            elif cmd == 'a':
                x -= step_size
                subprocess.run(['cliclick', f'm:{x},{y}'])
            elif cmd == 'd':
                x += step_size
                subprocess.run(['cliclick', f'm:{x},{y}'])
            elif cmd == '+':
                step_size = min(50, step_size + 5)
                print(f"Step size: {step_size}px")
            elif cmd == '-':
                step_size = max(1, step_size - 1)
                print(f"Step size: {step_size}px")
            else:
                print("Unknown command. Use w/a/s/d to move, c to confirm, q to quit")
    
    def find_quicktime_window(self):
        """Find QuickTime window with visual confirmation"""
        print("\n🔍 Step 1: Finding QuickTime Window")
        
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    return (item 1 of windowPos as string) & "," & ¬
                           (item 2 of windowPos as string) & "," & ¬
                           (item 1 of windowSize as string) & "," & ¬
                           (item 2 of windowSize as string)
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if not result.stdout.strip():
            print("❌ QuickTime window not found!")
            return None
            
        coords = result.stdout.strip().split(',')
        window = {
            'x': int(coords[0]),
            'y': int(coords[1]),
            'width': int(coords[2]),
            'height': int(coords[3])
        }
        
        print(f"✅ Found window: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
        
        # Draw window outline
        print("\n🖼️  I'll outline the QuickTime window corners...")
        
        # Move to each corner
        corners = [
            (window['x'], window['y'], "Top-Left"),
            (window['x'] + window['width'], window['y'], "Top-Right"),
            (window['x'] + window['width'], window['y'] + window['height'], "Bottom-Right"),
            (window['x'], window['y'] + window['height'], "Bottom-Left"),
        ]
        
        for x, y, name in corners:
            print(f"   📍 {name}: ({x}, {y})")
            self.move_mouse_slowly(x, y, steps=10)
            time.sleep(0.5)
        
        confirm = input("\nIs this the correct QuickTime window? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Please position QuickTime window and try again")
            return None
            
        return window
    
    def show_controls_step(self, window):
        """Show controls with extensive feedback"""
        print("\n🎮 Step 2: Showing Controls")
        
        # Capture before
        self.capture_screen("1_before_controls")
        
        center_x = window['x'] + window['width'] // 2
        
        print("🔍 Finding where controls appear...")
        print("I'll move the mouse to different positions.")
        print("Tell me when you see the control bar appear.")
        
        # Try different positions from bottom
        offsets = [100, 150, 200, 250, 300, 340, 380, 420, 460, 500]
        control_y = None
        
        for offset in offsets:
            test_y = window['y'] + window['height'] - offset
            print(f"\n📍 Testing offset {offset}px from bottom...")
            self.move_mouse_slowly(center_x, test_y, steps=15)
            time.sleep(1)
            
            response = input("Do you see the control bar? (y/n/adjust): ").lower()
            if response == 'y':
                control_y = test_y
                print(f"✅ Controls found at offset {offset}px")
                break
            elif response == 'adjust':
                # Fine-tune position
                print("\nFine-tuning position...")
                result = self.interactive_position_finder(center_x, test_y, "Control Bar Position")
                if result:
                    control_y = result['y']
                    break
        
        if not control_y:
            print("\n⚠️  Using manual positioning...")
            result = self.interactive_position_finder(center_x, window['y'] + window['height'] - 300, "Control Bar")
            if result:
                control_y = result['y']
            else:
                control_y = window['y'] + window['height'] - 340  # Last resort fallback
        
        bottom_y = control_y
        self.last_control_y = control_y  # Save for later
        
        print(f"\n✅ Using control position: ({center_x}, {bottom_y})")
        self.move_mouse_slowly(center_x, bottom_y, steps=10)
        
        print("⏳ Waiting for controls to appear...")
        for i in range(3):
            print(f"   {3-i}...")
            time.sleep(1)
        
        # Capture after
        self.capture_screen("2_after_controls")
        
        # Keep controls visible
        print("🖱️  Moving mouse slightly to keep controls visible...")
        self.move_mouse_slowly(center_x + 10, bottom_y, steps=5)
        time.sleep(0.5)
        
        # Capture with controls stable
        self.capture_screen("3_controls_visible")
        
        confirm = input("\nCan you see the QuickTime controls at the bottom? (y/n): ")
        return confirm.lower() == 'y'
    
    def find_airplay_icon(self, window):
        """Find AirPlay icon with multiple methods"""
        print("\n🔍 Step 3: Finding AirPlay Icon")
        
        # Method 1: Template matching
        if self.try_template_matching():
            return self.last_found_position
        
        # Method 2: Interactive search
        print("\n📍 Template matching failed. Let's find it manually.")
        print("The AirPlay icon looks like: ▲ with a rectangle")
        print("It's usually on the right side of the control bar")
        
        # Start from typical position
        initial_x = window['x'] + window['width'] - 150
        initial_y = window['y'] + window['height'] - 50
        
        result = self.interactive_position_finder(initial_x, initial_y, "AirPlay Icon")
        
        if result:
            # Capture with mouse on AirPlay
            self.capture_screen("4_airplay_position")
            return result
            
        return None
    
    def try_template_matching(self):
        """Try template matching with extensive debugging"""
        airplay_template = self.template_dir / "airplay_icon.png"
        
        if not airplay_template.exists():
            print(f"⚠️  No template at: {airplay_template}")
            return False
            
        print("🔍 Trying template matching...")
        screenshot = self.capture_screen("template_matching_source")
        
        # Load template
        template = cv2.imread(str(airplay_template))
        print(f"   Template size: {template.shape[:2]}")
        
        # Try different scales
        from template_based_detector import TemplateBasedDetector
        detector = TemplateBasedDetector()
        
        best_result = None
        best_confidence = 0
        
        scales = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]
        
        for scale in scales:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # Match
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_result = {
                    'x': max_loc[0] + width // 2,
                    'y': max_loc[1] + height // 2,
                    'confidence': max_val,
                    'scale': scale,
                    'top_left': max_loc,
                    'size': (width, height)
                }
            
            # Save debug image for each scale
            if max_val > 0.3:  # Only save promising matches
                debug_img = screenshot.copy()
                cv2.rectangle(debug_img, max_loc, (max_loc[0] + width, max_loc[1] + height), (0, 255, 0), 2)
                cv2.putText(debug_img, f"Scale: {scale:.1f}, Conf: {max_val:.2f}", 
                           (max_loc[0], max_loc[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.imwrite(str(self.debug_dir / f"template_scale_{scale:.1f}.png"), debug_img)
        
        print(f"   Best match: {best_confidence:.2f} at scale {best_result['scale'] if best_result else 'N/A'}")
        
        if best_result and best_confidence > 0.5:
            print(f"✅ Found with {best_confidence:.1%} confidence at scale {best_result['scale']}")
            
            # Move mouse to show
            self.move_mouse_slowly(best_result['x'], best_result['y'])
            
            confirm = input("Is the mouse on the AirPlay icon? (y/n): ")
            if confirm.lower() == 'y':
                self.last_found_position = {'x': best_result['x'], 'y': best_result['y']}
                return True
        
        return False
    
    def find_apple_tv_option(self, airplay_pos):
        """Find Apple TV in menu"""
        print("\n📺 Step 4: Finding Apple TV Option")
        
        # Click AirPlay
        print(f"🖱️  Clicking AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        
        # Wait and capture
        print("⏳ Waiting for menu...")
        for i in range(2):
            time.sleep(1)
            self.capture_screen(f"5_menu_wait_{i}")
        
        # Final capture
        menu_screenshot = self.capture_screen("6_menu_open")
        
        print("\n🔍 Looking for Apple TV option...")
        print("It should have:")
        print("  □ A checkbox on the left")
        print("  'Apple TV' or your device name")
        print("  Usually the first or second item")
        
        # Start from below AirPlay icon
        initial_x = airplay_pos['x'] + 50
        initial_y = airplay_pos['y'] + 70
        
        result = self.interactive_position_finder(initial_x, initial_y, "Apple TV Checkbox")
        
        if result:
            self.capture_screen("7_apple_tv_position")
            return result
            
        # Close menu if we failed
        subprocess.run(['cliclick', 'c:100,100'])
        return None
    
    def run_complete_detection(self):
        """Run the complete detection process"""
        print("\n🚀 Interactive AirPlay Detection")
        print("=" * 60)
        print("This process will help you find the exact positions")
        print("for AirPlay automation, with your guidance.")
        
        # Find window
        window = self.find_quicktime_window()
        if not window:
            return None
            
        # Show controls
        if not self.show_controls_step(window):
            print("❌ Could not show controls")
            return None
            
        # Find AirPlay
        airplay_pos = self.find_airplay_icon(window)
        if not airplay_pos:
            print("❌ Could not find AirPlay icon")
            return None
            
        # Find Apple TV
        appletv_pos = self.find_apple_tv_option(airplay_pos)
        if not appletv_pos:
            print("❌ Could not find Apple TV option")
            # Use estimate
            appletv_pos = {
                'x': airplay_pos['x'] + 50,
                'y': airplay_pos['y'] + 70
            }
            print(f"⚠️  Using estimated position: ({appletv_pos['x']}, {appletv_pos['y']})")
        
        # Save the control offset we found
        control_offset = None
        if hasattr(self, 'last_control_y') and window:
            control_offset = window['y'] + window['height'] - self.last_control_y
            
        return {
            'airplay_icon_coords': airplay_pos,
            'apple_tv_coords': appletv_pos,
            'control_offset': control_offset,
            'debug_folder': str(self.debug_dir)
        }
    
    def test_positions(self, coords):
        """Test the detected positions"""
        print("\n🧪 Testing Positions")
        print("I'll click through the sequence...")
        
        # Get window
        window = self.find_quicktime_window()
        if not window:
            return
            
        # Show controls - ask user for best position
        print("1️⃣ Showing controls...")
        center_x = window['x'] + window['width'] // 2
        
        print("Where should I move the mouse to show controls?")
        offset = input("Offset from bottom (default 340): ").strip()
        offset = int(offset) if offset else 340
        
        bottom_y = window['y'] + window['height'] - offset
        self.move_mouse_slowly(center_x, bottom_y)
        time.sleep(1.5)
        
        # Click AirPlay
        print("2️⃣ Clicking AirPlay...")
        self.move_mouse_slowly(coords['airplay_icon_coords']['x'], 
                              coords['airplay_icon_coords']['y'])
        time.sleep(0.5)
        subprocess.run(['cliclick', f"c:{coords['airplay_icon_coords']['x']},{coords['airplay_icon_coords']['y']}"])
        time.sleep(1.5)
        
        # Click Apple TV
        print("3️⃣ Clicking Apple TV...")
        self.move_mouse_slowly(coords['apple_tv_coords']['x'], 
                              coords['apple_tv_coords']['y'])
        time.sleep(0.5)
        subprocess.run(['cliclick', f"c:{coords['apple_tv_coords']['x']},{coords['apple_tv_coords']['y']}"])
        
        print("\n✅ Test complete!")


def main():
    detector = InteractiveAirPlayDetector()
    
    print("🎯 Interactive AirPlay Position Detector")
    print("This tool will help you find the exact positions")
    print("for AirPlay automation with your guidance.")
    print("\n⚠️  Requirements:")
    print("1. QuickTime Player is open")
    print("2. A video is loaded and playing")
    print("3. You can see the QuickTime window")
    
    input("\nPress Enter when ready...")
    
    # Run detection
    result = detector.run_complete_detection()
    
    if result:
        print("\n✅ Detection Complete!")
        print(f"AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        print(f"Debug images: {result['debug_folder']}")
        
        # Test
        test = input("\n🧪 Test these positions? (y/n): ")
        if test.lower() == 'y':
            detector.test_positions(result)
        
        # Save
        save = input("\n💾 Save these settings? (y/n): ")
        if save.lower() == 'y':
            settings = {
                'airplay_icon_coords': result['airplay_icon_coords'],
                'apple_tv_coords': result['apple_tv_coords'],
                'airplay_configured': True,
                'detection_method': 'interactive'
            }
            
            # Add control offset if we found it
            if result.get('control_offset'):
                settings['control_offset'] = result['control_offset']
                print(f"📏 Also saving control offset: {result['control_offset']}px")
            
            for filename in ['.quickdrop_settings.json', '.quicktime_converter_settings.json']:
                settings_file = Path.home() / filename
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                print(f"✅ Saved to {settings_file}")
    else:
        print("\n❌ Detection failed")
        print(f"Check debug images in: {detector.debug_dir}")


if __name__ == "__main__":
    main()