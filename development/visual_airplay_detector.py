#!/usr/bin/env python3
"""
Visual AirPlay detector with clear feedback
"""

import cv2
import subprocess
import time
from pathlib import Path
import json
import numpy as np

class VisualAirPlayDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path(__file__).parent / "debug_output"
        self.debug_dir.mkdir(exist_ok=True)
        
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def show_visual_feedback(self, message, duration=2):
        """Show visual feedback using macOS notification"""
        script = f'''
        display notification "{message}" with title "AirPlay Detector" sound name "Tink"
        '''
        subprocess.run(['osascript', '-e', script])
        time.sleep(duration)
    
    def visualize_area(self, x, y, width, height, color="red"):
        """Draw a rectangle on screen to show where we're looking"""
        # This would require a GUI window, so for now we'll just log it
        print(f"🔍 Looking at area: ({x}, {y}) - {width}x{height} pixels")
    
    def interactive_detection(self):
        """Interactive detection with clear visual feedback"""
        print("\n🎯 Interactive AirPlay Detection")
        print("=" * 60)
        
        # Step 0: Prepare
        print("\n📋 Preparation:")
        print("1. Make sure QuickTime Player is open")
        print("2. Load a video (drag & drop any video file)")
        print("3. Play the video (press space bar)")
        print("4. Make sure you can see the QuickTime window")
        
        input("\nPress Enter when ready...")
        
        # Step 1: Find QuickTime window
        print("\n🔍 Step 1: Finding QuickTime Window")
        qt_window = self.find_quicktime_window_with_feedback()
        if not qt_window:
            return None
            
        # Step 2: Show controls
        print("\n🎮 Step 2: Showing Controls")
        self.show_controls_with_feedback(qt_window)
        
        # Step 3: Find AirPlay using your template
        print("\n🔍 Step 3: Finding AirPlay Icon")
        airplay_pos = self.find_airplay_with_template()
        if not airplay_pos:
            print("❌ Could not find AirPlay icon with template")
            print("\n🤔 Let's try manual selection...")
            airplay_pos = self.manual_airplay_selection(qt_window)
            
        if not airplay_pos:
            return None
            
        # Step 4: Click AirPlay and find Apple TV
        print("\n📺 Step 4: Finding Apple TV Option")
        appletv_pos = self.find_apple_tv_with_feedback(airplay_pos)
        
        return {
            'airplay_icon_coords': {'x': airplay_pos['x'], 'y': airplay_pos['y']},
            'apple_tv_coords': {'x': appletv_pos['x'], 'y': appletv_pos['y']}
        }
    
    def find_quicktime_window_with_feedback(self):
        """Find QuickTime with visual feedback"""
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
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            window = {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
            print(f"✅ Found QuickTime window:")
            print(f"   Position: ({window['x']}, {window['y']})")
            print(f"   Size: {window['width']} x {window['height']}")
            
            # Flash the window to show we found it
            self.flash_quicktime_window()
            
            return window
        else:
            print("❌ QuickTime window not found!")
            print("   Make sure QuickTime Player is open")
            return None
    
    def flash_quicktime_window(self):
        """Flash QuickTime window to show we found it"""
        script = '''
        tell application "QuickTime Player"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        time.sleep(0.5)
    
    def show_controls_with_feedback(self, qt_window):
        """Show controls with clear feedback"""
        center_x = qt_window['x'] + qt_window['width'] // 2
        bottom_y = qt_window['y'] + qt_window['height'] - 30
        
        print(f"🖱️  Moving mouse to bottom of window...")
        print(f"   Target: ({center_x}, {bottom_y})")
        
        # Move slowly so user can see
        current_pos = self.get_mouse_position()
        if current_pos:
            steps = 10
            for i in range(steps + 1):
                progress = i / steps
                x = int(current_pos[0] + (center_x - current_pos[0]) * progress)
                y = int(current_pos[1] + (bottom_y - current_pos[1]) * progress)
                subprocess.run(['cliclick', f'm:{x},{y}'])
                time.sleep(0.05)
        else:
            subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        
        print("⏳ Waiting for controls to appear...")
        time.sleep(1.5)
        
        # Small movement to keep controls visible
        subprocess.run(['cliclick', f'm:{center_x + 5},{bottom_y}'])
        time.sleep(0.5)
        
        print("✅ Controls should now be visible")
    
    def get_mouse_position(self):
        """Get current mouse position"""
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        if result.stdout:
            coords = result.stdout.strip().split(',')
            return (int(coords[0]), int(coords[1]))
        return None
    
    def find_airplay_with_template(self):
        """Find AirPlay using template with visual feedback"""
        airplay_template = self.template_dir / "airplay_icon.png"
        
        if not airplay_template.exists():
            print(f"❌ Template not found: {airplay_template}")
            return None
            
        print("📸 Capturing screen...")
        screenshot = self.capture_screen()
        
        print("🔍 Looking for AirPlay icon using template...")
        
        from template_based_detector import TemplateBasedDetector
        detector = TemplateBasedDetector()
        result = detector.find_with_multiple_scales(airplay_template, screenshot)
        
        if result and result['confidence'] > 0.5:
            print(f"✅ Found AirPlay icon!")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"   Position: ({result['x']}, {result['y']})")
            print(f"   Scale: {result.get('scale', 1.0)}")
            
            # Save debug image
            debug_img = screenshot.copy()
            cv2.rectangle(debug_img, result['top_left'], result['bottom_right'], (0, 255, 0), 3)
            cv2.putText(debug_img, f"AirPlay {result['confidence']:.1%}", 
                       (result['top_left'][0], result['top_left'][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite(str(self.debug_dir / "found_airplay.png"), debug_img)
            print(f"   Debug image saved to: {self.debug_dir / 'found_airplay.png'}")
            
            # Move mouse to show where we found it
            subprocess.run(['cliclick', f"m:{result['x']},{result['y']}"])
            time.sleep(1)
            
            return {'x': result['x'], 'y': result['y']}
        else:
            print(f"❌ Template matching failed")
            return None
    
    def manual_airplay_selection(self, qt_window):
        """Manual selection when template fails"""
        print("\n🎯 Manual AirPlay Selection")
        print("Since template matching failed, let's try manually.")
        print("\nAirPlay icon is usually:")
        print("- In the control bar at the bottom")
        print("- On the right side")
        print("- Triangle with rectangle shape")
        
        # Common positions to try
        positions = [
            # (offset from right, offset from bottom)
            (150, 50),  # Standard position
            (120, 50),  # Smaller window
            (180, 50),  # Larger window
            (150, 40),  # Different UI scale
            (150, 60),  # Different UI scale
        ]
        
        print("\nI'll move the mouse to likely positions.")
        print("Tell me when the mouse is on the AirPlay icon.")
        
        for i, (offset_x, offset_y) in enumerate(positions):
            x = qt_window['x'] + qt_window['width'] - offset_x
            y = qt_window['y'] + qt_window['height'] - offset_y
            
            print(f"\n🎯 Position {i+1}/5: ({x}, {y})")
            subprocess.run(['cliclick', f'm:{x},{y}'])
            
            response = input("Is the mouse on the AirPlay icon? (y/n/skip): ")
            if response.lower() == 'y':
                return {'x': x, 'y': y}
            elif response.lower() == 'skip':
                break
        
        # Last resort: ask user to click
        print("\n🖱️  Manual clicking mode")
        print("Please click on the AirPlay icon yourself.")
        print("I'll detect where you clicked.")
        
        input("Position your mouse on the AirPlay icon and press Enter...")
        
        pos = self.get_mouse_position()
        if pos:
            print(f"✅ Recorded position: ({pos[0]}, {pos[1]})")
            return {'x': pos[0], 'y': pos[1]}
        
        return None
    
    def find_apple_tv_with_feedback(self, airplay_pos):
        """Find Apple TV with visual feedback"""
        print(f"\n🖱️  Clicking AirPlay icon at ({airplay_pos['x']}, {airplay_pos['y']})...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        
        print("⏳ Waiting for menu to appear...")
        time.sleep(1.5)
        
        print("📸 Capturing menu...")
        menu_screenshot = self.capture_screen()
        cv2.imwrite(str(self.debug_dir / "airplay_menu.png"), menu_screenshot)
        
        # Try template first
        appletv_template = self.template_dir / "apple_tv_checkbox.png"
        if appletv_template.exists():
            print("🔍 Looking for Apple TV using template...")
            from template_based_detector import TemplateBasedDetector
            detector = TemplateBasedDetector()
            result = detector.find_with_multiple_scales(appletv_template, menu_screenshot)
            
            if result and result['confidence'] > 0.5:
                print(f"✅ Found Apple TV option!")
                subprocess.run(['cliclick', f"m:{result['x']},{result['y']}"])
                time.sleep(1)
                return {'x': result['x'], 'y': result['y']}
        
        # Manual fallback
        print("\n🎯 Manual Apple TV selection")
        print("The Apple TV option is usually:")
        print("- Below the AirPlay icon")
        print("- Has a checkbox on the left")
        print("- Says 'Apple TV' or your device name")
        
        # Try common offsets
        offsets = [
            (50, 70),   # Standard
            (0, 70),    # Direct below
            (30, 50),   # Closer
            (70, 90),   # Further
        ]
        
        for i, (dx, dy) in enumerate(offsets):
            x = airplay_pos['x'] + dx
            y = airplay_pos['y'] + dy
            
            print(f"\n🎯 Trying position {i+1}/4: ({x}, {y})")
            subprocess.run(['cliclick', f'm:{x},{y}'])
            
            response = input("Is this the Apple TV checkbox? (y/n): ")
            if response.lower() == 'y':
                return {'x': x, 'y': y}
        
        # Close menu
        subprocess.run(['cliclick', 'c:100,100'])
        
        # Use default offset
        print("\n⚠️  Using default offset")
        return {
            'x': airplay_pos['x'] + 50,
            'y': airplay_pos['y'] + 70
        }


def main():
    print("🎨 Visual AirPlay Detector")
    print("This version provides clear visual feedback")
    print("=" * 60)
    
    detector = VisualAirPlayDetector()
    
    result = detector.interactive_detection()
    
    if result:
        print("\n✅ Detection successful!")
        print(f"AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        
        # Test it
        test = input("\n🧪 Test these positions? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting in 3 seconds...")
            time.sleep(3)
            
            # Show controls
            qt_window = detector.find_quicktime_window_with_feedback()
            if qt_window:
                detector.show_controls_with_feedback(qt_window)
            
            # Click AirPlay
            print("Clicking AirPlay...")
            subprocess.run(['cliclick', f"c:{result['airplay_icon_coords']['x']},{result['airplay_icon_coords']['y']}"])
            time.sleep(1.5)
            
            # Click Apple TV  
            print("Clicking Apple TV...")
            subprocess.run(['cliclick', f"c:{result['apple_tv_coords']['x']},{result['apple_tv_coords']['y']}"])
            
            print("\n✅ Test complete!")
        
        # Save
        save = input("\n💾 Save these settings? (y/n): ")
        if save.lower() == 'y':
            settings = result.copy()
            settings['airplay_configured'] = True
            settings['detection_method'] = 'visual'
            
            for filename in ['.quickdrop_settings.json', '.quicktime_converter_settings.json']:
                settings_file = Path.home() / filename
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                print(f"✅ Saved to {settings_file}")
    else:
        print("\n❌ Detection failed")


if __name__ == "__main__":
    main()