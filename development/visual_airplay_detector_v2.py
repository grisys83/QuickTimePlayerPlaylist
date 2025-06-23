#!/usr/bin/env python3
"""
Visual AirPlay Detector V2
- ROI-based detection approach
- More debug images at each step
- User confirmation at each stage
"""

import cv2
import subprocess
import time
from pathlib import Path
import json
import numpy as np
from coordinate_converter import CoordinateConverter

class VisualAirPlayDetectorV2:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.debug_dir = Path(__file__).parent / "debug_output_v2"
        self.debug_dir.mkdir(exist_ok=True)
        
        # Clear previous debug images
        for img in self.debug_dir.glob("*.png"):
            img.unlink()
            
    def capture_screen(self, name="screen"):
        """Capture screen and save debug copy"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        # Save debug copy
        debug_path = self.debug_dir / f"{name}_{int(time.time())}.png"
        cv2.imwrite(str(debug_path), screenshot)
        print(f"📸 Saved: {debug_path.name}")
        
        return screenshot
    
    def draw_roi(self, image, roi_rect, label, color=(0, 255, 0)):
        """Draw ROI on image with label"""
        x1, y1, x2, y2 = roi_rect
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return image
    
    def show_coordinates_info(self):
        """Show coordinate system information"""
        print("\n📐 Coordinate Systems:")
        print("┌─────────────────────────────────────────┐")
        print("│ CV2 Coordinates:                        │")
        print("│ - Y=0 at TOP of screen                  │")
        print("│ - Y increases DOWNWARD                  │")
        print("│                                         │")
        print("│ Screen/Click Coordinates:               │")
        print("│ - Different due to Retina display (2x)  │")
        print("│ - We handle conversion automatically    │")
        print("└─────────────────────────────────────────┘")
    
    def find_quicktime_window(self):
        """Find QuickTime window with visual feedback"""
        print("\n🪟 Finding QuickTime Window...")
        
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
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        return window
    
    def show_controls(self, window):
        """Show controls with animation"""
        print("\n🎮 Showing controls...")
        
        center_x = window['x'] + window['width'] // 2
        
        # Adaptive positioning based on window size
        if window['height'] < 400:
            # Small window - control bar at ~65% from top
            bottom_y = window['y'] + int(window['height'] * 0.65)
        elif window['height'] < 600:
            # Medium window - control bar at ~70% from top  
            bottom_y = window['y'] + int(window['height'] * 0.70)
        else:
            # Large window - fixed offset from bottom
            bottom_y = window['y'] + window['height'] - 250
        
        print(f"   Window height: {window['height']}px")
        print(f"   Mouse Y position: {bottom_y} ({window['y'] + window['height'] - bottom_y}px from bottom)")
        
        # Move to bottom center
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        time.sleep(0.8)
        
        # Small movement to keep visible
        subprocess.run(['cliclick', f'm:{center_x + 5},{bottom_y}'])
        time.sleep(0.5)
        
        print("✅ Controls should be visible")
    
    def find_airplay_icon_roi(self, screenshot, window):
        """Find AirPlay icon using ROI approach"""
        print("\n🔍 Step 1: Finding AirPlay Icon")
        
        # Convert window coordinates to CV2
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Define control bar ROI adaptively based on window size
        window_height = window['height']
        
        if window_height < 400:
            # Small window - control bar takes larger proportion
            # Need much bigger ROI for small windows
            roi_top_offset = int(window_height * 0.8)  # 80% from bottom
            roi_bottom_offset = int(window_height * 0.05)  # 5% from bottom
        elif window_height < 600:
            # Medium window - mix of proportional and fixed
            roi_top_offset = min(300, int(window_height * 0.5))
            roi_bottom_offset = 100
        else:
            # Large window - use fixed offsets (150-450px from bottom)
            roi_top_offset = 450
            roi_bottom_offset = 150
            
        control_roi = (
            int(win_cv2_x1),
            int(win_cv2_y2 - roi_top_offset),
            int(win_cv2_x2),
            int(win_cv2_y2 - roi_bottom_offset)
        )
        
        print(f"   Window height: {window_height}px")
        print(f"   ROI offsets: {roi_top_offset}px to {roi_bottom_offset}px from bottom")
        
        # Draw and save control bar ROI
        vis = screenshot.copy()
        self.draw_roi(vis, control_roi, "Control Bar ROI", (0, 255, 0))
        cv2.imwrite(str(self.debug_dir / "1_control_bar_roi.png"), vis)
        
        # Extract control bar ROI
        x1, y1, x2, y2 = control_roi
        control_bar = screenshot[y1:y2, x1:x2]
        cv2.imwrite(str(self.debug_dir / "2_control_bar_extracted.png"), control_bar)
        
        # Load AirPlay template
        airplay_template = self.template_dir / "airplay_icon.png"
        if not airplay_template.exists():
            print(f"❌ Template not found: {airplay_template}")
            return None
            
        template = cv2.imread(str(airplay_template))
        
        # Try multiple scales
        print("🔍 Searching for AirPlay icon...")
        best_match = None
        best_val = 0
        
        for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            result = cv2.matchTemplate(control_bar, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_match = {
                    'loc': max_loc,
                    'size': (width, height),
                    'scale': scale,
                    'confidence': max_val
                }
        
        if best_match and best_match['confidence'] > 0.5:
            # Convert back to full image coordinates
            roi_x = best_match['loc'][0] + best_match['size'][0] // 2
            roi_y = best_match['loc'][1] + best_match['size'][1] // 2
            
            cv2_x = x1 + roi_x
            cv2_y = y1 + roi_y
            
            # Draw found position
            found_vis = screenshot.copy()
            cv2.circle(found_vis, (int(cv2_x), int(cv2_y)), 10, (0, 255, 0), -1)
            cv2.putText(found_vis, f"AirPlay {best_match['confidence']:.1%}", 
                       (int(cv2_x - 50), int(cv2_y - 20)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imwrite(str(self.debug_dir / "3_airplay_found.png"), found_vis)
            
            # Convert to screen coordinates
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            print(f"✅ Found AirPlay icon!")
            print(f"   Confidence: {best_match['confidence']:.1%}")
            print(f"   CV2 coords: ({int(cv2_x)}, {int(cv2_y)})")
            print(f"   Screen coords: ({screen_x}, {screen_y})")
            
            return {'x': screen_x, 'y': screen_y, 'cv2_x': cv2_x, 'cv2_y': cv2_y}
        
        print(f"❌ AirPlay icon not found (best: {best_val:.1%})")
        return None
    
    def find_checkbox_in_menu_roi(self, menu_screenshot, airplay_cv2_pos):
        """Find checkbox using hierarchical ROI approach"""
        print("\n🔍 Step 2: Finding Apple TV Checkbox (ROI approach)")
        
        height, width = menu_screenshot.shape[:2]
        airplay_cv2_x, airplay_cv2_y = airplay_cv2_pos
        
        # Step 2.1: Define menu ROI (above AirPlay icon)
        print("📍 Defining menu ROI...")
        # Much larger ROI for menus (especially on small windows)
        menu_roi = (
            max(0, int(airplay_cv2_x - 400)),      # left (wider)
            max(0, int(airplay_cv2_y - 800)),      # top (much taller)
            min(width, int(airplay_cv2_x + 400)),  # right (wider)
            int(airplay_cv2_y - 20)                # bottom (just above icon)
        )
        
        # Visualize menu ROI
        vis = menu_screenshot.copy()
        self.draw_roi(vis, menu_roi, "Menu ROI", (255, 255, 0))
        cv2.circle(vis, (int(airplay_cv2_x), int(airplay_cv2_y)), 5, (0, 0, 255), -1)
        cv2.putText(vis, "AirPlay Icon", (int(airplay_cv2_x + 10), int(airplay_cv2_y)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite(str(self.debug_dir / "4_menu_roi.png"), vis)
        
        # Extract menu ROI
        x1, y1, x2, y2 = menu_roi
        menu_roi_img = menu_screenshot[y1:y2, x1:x2]
        cv2.imwrite(str(self.debug_dir / "5_menu_roi_extracted.png"), menu_roi_img)
        
        if menu_roi_img.size == 0:
            print("❌ Menu ROI is empty!")
            return None
        
        # Step 2.2: Find Apple TV text in menu ROI
        print("📍 Looking for Apple TV text...")
        appletv_template_path = self.template_dir / "apple_tv.png"
        appletv_found = False
        appletv_roi_pos = None
        
        if appletv_template_path.exists():
            appletv_template = cv2.imread(str(appletv_template_path))
            if appletv_template is not None:
                result = cv2.matchTemplate(menu_roi_img, appletv_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > 0.6:
                    appletv_roi_x = max_loc[0] + appletv_template.shape[1] // 2
                    appletv_roi_y = max_loc[1] + appletv_template.shape[0] // 2
                    appletv_found = True
                    appletv_roi_pos = (appletv_roi_x, appletv_roi_y)
                    
                    # Visualize Apple TV found
                    appletv_vis = menu_roi_img.copy()
                    cv2.circle(appletv_vis, (appletv_roi_x, appletv_roi_y), 8, (0, 255, 0), 2)
                    cv2.putText(appletv_vis, f"Apple TV {max_val:.1%}", 
                               (appletv_roi_x - 40, appletv_roi_y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.imwrite(str(self.debug_dir / "6_appletv_found.png"), appletv_vis)
                    
                    print(f"✅ Found Apple TV text (confidence: {max_val:.1%})")
        
        # Step 2.3: Define checkbox ROI
        if appletv_found and appletv_roi_pos:
            print("📍 Defining checkbox ROI around Apple TV text...")
            # Checkbox is typically 50-100 pixels to the left of text
            cb_roi = (
                max(0, appletv_roi_pos[0] - 100),           # left
                max(0, appletv_roi_pos[1] - 20),            # top
                appletv_roi_pos[0] - 20,                    # right (left of text)
                min(menu_roi_img.shape[0], appletv_roi_pos[1] + 20)  # bottom
            )
            
            # Visualize checkbox ROI
            cb_vis = menu_roi_img.copy()
            self.draw_roi(cb_vis, cb_roi, "Checkbox ROI", (255, 0, 255))
            cv2.imwrite(str(self.debug_dir / "7_checkbox_roi.png"), cb_vis)
            
            # Extract checkbox ROI
            cb_x1, cb_y1, cb_x2, cb_y2 = cb_roi
            checkbox_roi_img = menu_roi_img[cb_y1:cb_y2, cb_x1:cb_x2]
            
            if checkbox_roi_img.size > 0:
                cv2.imwrite(str(self.debug_dir / "8_checkbox_roi_extracted.png"), checkbox_roi_img)
                
                # Look for checkbox in this small area
                checkbox_template_path = self.template_dir / "checkbox_unchecked.png"
                if checkbox_template_path.exists():
                    checkbox_template = cv2.imread(str(checkbox_template_path))
                    if checkbox_template is not None:
                        result = cv2.matchTemplate(checkbox_roi_img, checkbox_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        
                        if max_val > 0.5:
                            # Found checkbox!
                            cb_roi_x = max_loc[0] + checkbox_template.shape[1] // 2
                            cb_roi_y = max_loc[1] + checkbox_template.shape[0] // 2
                            
                            # Convert back to full image coordinates
                            full_cv2_x = x1 + cb_x1 + cb_roi_x
                            full_cv2_y = y1 + cb_y1 + cb_roi_y
                            
                            # Convert to screen coordinates
                            screen_x, screen_y = self.converter.cv2_to_screen(full_cv2_x, full_cv2_y)
                            
                            print(f"✅ Found checkbox! (confidence: {max_val:.1%})")
                            print(f"   CV2 coords: ({int(full_cv2_x)}, {int(full_cv2_y)})")
                            print(f"   Screen coords: ({screen_x}, {screen_y})")
                            
                            # Final visualization
                            final_vis = menu_screenshot.copy()
                            cv2.circle(final_vis, (int(full_cv2_x), int(full_cv2_y)), 10, (0, 255, 0), -1)
                            cv2.putText(final_vis, "Checkbox", 
                                       (int(full_cv2_x - 30), int(full_cv2_y - 15)),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imwrite(str(self.debug_dir / "9_checkbox_found_final.png"), final_vis)
                            
                            return {'x': screen_x, 'y': screen_y}
        
        # Fallback: use offset from Apple TV text
        if appletv_found and appletv_roi_pos:
            print("⚠️ Checkbox template not found, using offset from Apple TV text")
            # User found: checkbox is at specific offset from Apple TV icon
            # First get screen coordinates of Apple TV
            appletv_screen_x, appletv_screen_y = self.converter.cv2_to_screen(
                x1 + appletv_roi_pos[0], 
                y1 + appletv_roi_pos[1]
            )
            # Checkbox is to the left of Apple TV text (negative offset)
            screen_x = appletv_screen_x - 50  # Adjust this value based on actual menu
            screen_y = appletv_screen_y
            
            # Visualize offset method
            # Convert screen coords back to CV2 for visualization
            checkbox_cv2_x, checkbox_cv2_y = self.converter.screen_to_cv2(screen_x, screen_y)
            offset_vis = menu_screenshot.copy()
            cv2.circle(offset_vis, (int(checkbox_cv2_x), int(checkbox_cv2_y)), 10, (255, 255, 0), -1)
            cv2.putText(offset_vis, "Checkbox (+500px)", 
                       (int(checkbox_cv2_x - 50), int(checkbox_cv2_y - 15)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imwrite(str(self.debug_dir / "9_checkbox_offset_method.png"), offset_vis)
            
            print(f"📍 Using +500px offset from Apple TV")
            print(f"   Checkbox position: ({screen_x}, {screen_y})")
            
            return {'x': screen_x, 'y': screen_y}
        
        # Last resort: offset from AirPlay
        print("⚠️ Using default offset from AirPlay icon")
        # Based on the screenshot, "living" appears to be:
        # - Slightly to the left of AirPlay (about 20px)
        # - About 160px above AirPlay
        offset_cv2_x = airplay_cv2_x - 20
        offset_cv2_y = airplay_cv2_y - 160  # Above in CV2 = lower Y
        screen_x, screen_y = self.converter.cv2_to_screen(offset_cv2_x, offset_cv2_y)
        
        # Visualize
        fallback_vis = menu_screenshot.copy()
        cv2.circle(fallback_vis, (int(offset_cv2_x), int(offset_cv2_y)), 10, (255, 0, 255), -1)
        cv2.putText(fallback_vis, "Checkbox (fallback)", 
                   (int(offset_cv2_x - 60), int(offset_cv2_y - 15)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        cv2.imwrite(str(self.debug_dir / "9_checkbox_fallback.png"), fallback_vis)
        
        return {'x': screen_x, 'y': screen_y}
    
    def interactive_detection(self):
        """Main detection flow with user confirmation"""
        print("\n🎯 Visual AirPlay Detector V2")
        print("=" * 60)
        
        self.show_coordinates_info()
        
        # Preparation
        print("\n📋 Preparation:")
        print("1. Open QuickTime Player")
        print("2. Load a video")
        print("3. Start playing the video")
        input("\nPress Enter when ready...")
        
        # Step 1: Find window
        window = self.find_quicktime_window()
        if not window:
            return None
        
        # Step 2: Show controls
        self.show_controls(window)
        
        # Step 3: Capture and find AirPlay
        print("\n📸 Capturing screen with controls...")
        screenshot = self.capture_screen("controls_visible")
        
        airplay_pos = self.find_airplay_icon_roi(screenshot, window)
        
        if not airplay_pos:
            print("\n❌ Failed to find AirPlay icon")
            return None
        
        # Confirm AirPlay position
        print("\n🎯 Moving mouse to AirPlay icon...")
        subprocess.run(['cliclick', f"m:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1)
        
        confirm = input("Is the mouse on the AirPlay icon? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ AirPlay position incorrect")
            return None
        
        # Step 4: Click AirPlay and capture menu
        print("\n📺 Opening AirPlay menu...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1.5)
        
        print("📸 Capturing menu...")
        menu_screenshot = self.capture_screen("airplay_menu_open")
        
        # Step 5: Find checkbox
        checkbox_pos = self.find_checkbox_in_menu_roi(
            menu_screenshot, 
            (airplay_pos['cv2_x'], airplay_pos['cv2_y'])
        )
        
        if not checkbox_pos:
            print("\n❌ Failed to find checkbox")
            return None
        
        # Confirm checkbox position
        print("\n🎯 Moving mouse to checkbox...")
        subprocess.run(['cliclick', f"m:{checkbox_pos['x']},{checkbox_pos['y']}"])
        time.sleep(1)
        
        confirm = input("Is the mouse on the Apple TV checkbox? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Checkbox position incorrect")
            # Close menu
            subprocess.run(['cliclick', 'c:100,100'])
            return None
        
        # Close menu for now
        subprocess.run(['cliclick', 'c:100,100'])
        
        print("\n✅ Detection successful!")
        print(f"\n📊 Results:")
        print(f"   AirPlay icon: ({airplay_pos['x']}, {airplay_pos['y']})")
        print(f"   Apple TV checkbox: ({checkbox_pos['x']}, {checkbox_pos['y']})")
        print(f"\n📁 Debug images saved to: {self.debug_dir}")
        
        return {
            'airplay_icon_coords': {'x': airplay_pos['x'], 'y': airplay_pos['y']},
            'apple_tv_coords': {'x': checkbox_pos['x'], 'y': checkbox_pos['y']}
        }
    
    def test_positions(self, positions):
        """Test the detected positions"""
        print("\n🧪 Testing positions...")
        
        # Find window and show controls
        window = self.find_quicktime_window()
        if not window:
            return False
        
        self.show_controls(window)
        time.sleep(0.5)
        
        # Click AirPlay
        print("Clicking AirPlay icon...")
        airplay = positions['airplay_icon_coords']
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(1.5)
        
        # Click checkbox
        print("Clicking Apple TV checkbox...")
        appletv = positions['apple_tv_coords']
        subprocess.run(['cliclick', f"c:{appletv['x']},{appletv['y']}"])
        time.sleep(0.5)
        
        success = input("\n✅ Did AirPlay enable successfully? (y/n): ")
        return success.lower() == 'y'


def main():
    detector = VisualAirPlayDetectorV2()
    
    # Run detection
    result = detector.interactive_detection()
    
    if result:
        # Offer to test
        test = input("\n🧪 Test these positions? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting in 3 seconds...")
            time.sleep(3)
            
            success = detector.test_positions(result)
            
            if success:
                # Save settings
                save = input("\n💾 Save these settings? (y/n): ")
                if save.lower() == 'y':
                    settings = result.copy()
                    settings['airplay_configured'] = True
                    settings['detection_method'] = 'visual_v2_roi'
                    settings['last_detection'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    for filename in ['.quickdrop_settings.json', '.quicktime_converter_settings.json']:
                        settings_file = Path.home() / filename
                        
                        # Load existing settings
                        existing = {}
                        if settings_file.exists():
                            with open(settings_file, 'r') as f:
                                existing = json.load(f)
                        
                        # Update with new settings
                        existing.update(settings)
                        
                        # Save
                        with open(settings_file, 'w') as f:
                            json.dump(existing, f, indent=2)
                        print(f"✅ Saved to {settings_file}")
            else:
                print("\n❌ Test failed, positions may need adjustment")
    else:
        print("\n❌ Detection failed")
        print("Check the debug images in:", detector.debug_dir)


if __name__ == "__main__":
    main()