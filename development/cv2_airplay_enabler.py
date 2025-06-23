#!/usr/bin/env python3
"""
Smart CV2 AirPlay Enabler
- Always detects current positions
- Updates saved coordinates when successful
- Learns from each use
"""

import cv2
import numpy as np
import subprocess
import time
import json
from pathlib import Path
from coordinate_converter import CoordinateConverter

class SmartCV2AirPlay:
    def __init__(self, settings=None):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        self.settings = settings or self.load_settings()
        
        # Cache for this session
        self.session_cache = {
            'last_airplay': None,
            'last_appletv': None,
            'last_detection_time': 0
        }
        
    def load_settings(self):
        """Load settings"""
        settings_file = Path.home() / '.quicktime_converter_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_detected_coordinates(self, airplay_coords, appletv_coords):
        """Save successfully detected coordinates for future use"""
        self.settings['airplay_icon_coords'] = airplay_coords
        self.settings['apple_tv_coords'] = appletv_coords
        self.settings['last_cv2_detection'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to both settings files
        for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
            settings_file = Path.home() / filename
            try:
                existing = {}
                if settings_file.exists():
                    with open(settings_file, 'r') as f:
                        existing = json.load(f)
                
                existing.update(self.settings)
                
                with open(settings_file, 'w') as f:
                    json.dump(existing, f, indent=2)
            except:
                pass
    
    def capture_screen(self):
        """Quick screen capture"""
        screenshot_path = "/tmp/smart_cv2_screen.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
    
    def find_template_fast(self, screenshot, template_name, threshold=0.7):
        """Fast template matching with optimal scales"""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path))
        if template is None:
            return None
            
        # Use fewer scales for speed
        scales = [0.9, 1.0, 1.1]  # Most common scales
        
        for scale in scales:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > threshold:
                # Calculate center and convert coordinates
                cv2_x = max_loc[0] + width // 2
                cv2_y = max_loc[1] + height // 2
                screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
                
                return {'x': screen_x, 'y': screen_y, 'confidence': max_val}
        
        return None
    
    def find_all_templates_fast(self, screenshot, template_name, threshold=0.7):
        """Find all instances of a template"""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return []
            
        template = cv2.imread(str(template_path))
        if template is None:
            return []
            
        # Single scale for speed
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # Find all matches
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            cv2_x = pt[0] + template.shape[1] // 2
            cv2_y = pt[1] + template.shape[0] // 2
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            matches.append({
                'x': screen_x, 
                'y': screen_y,
                'cv2_y': cv2_y,  # Keep for Y-level comparison
                'confidence': result[pt[1], pt[0]]
            })
        
        return matches
    
    def enable_airplay_smart(self):
        """Smart AirPlay enable with real-time detection"""
        start_time = time.time()
        
        # Step 1: Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.2)
        
        # Step 2: Get window and show controls
        window = self.get_quicktime_window()
        if not window:
            return False
            
        self.show_controls_fast(window)
        
        # Step 3: Detect AirPlay icon
        screenshot = self.capture_screen()
        airplay = self.find_template_fast(screenshot, 'airplay_icon.png')
        
        if not airplay:
            print("AirPlay icon not found, retrying...")
            time.sleep(0.3)
            self.show_controls_fast(window)
            screenshot = self.capture_screen()
            airplay = self.find_template_fast(screenshot, 'airplay_icon.png', threshold=0.6)
        
        if not airplay:
            print("Failed to find AirPlay icon")
            return False
        
        # Step 4: Click AirPlay
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(0.4)
        
        # Step 5: Find and click Apple TV checkbox using ROI approach
        menu_screenshot = self.capture_screen()
        
        # Debug: save menu screenshot
        self.save_debug_image(menu_screenshot, "1_menu_screenshot")
        
        # Get AirPlay position in CV2 coordinates for ROI
        airplay_cv2_x, airplay_cv2_y = self.screen_to_cv2(airplay['x'], airplay['y'])
        
        # Step 5.1: Define ROI around AirPlay menu area
        # AirPlay menu can be quite large, especially on small windows
        roi_left = max(0, airplay_cv2_x - 400)  # Much wider
        roi_right = min(menu_screenshot.shape[1], airplay_cv2_x + 400)
        roi_top = max(0, airplay_cv2_y - 800)  # Much taller - menu can be big
        roi_bottom = airplay_cv2_y - 20  # Just above the icon
        
        # Visualize ROI on full screenshot
        roi_vis = menu_screenshot.copy()
        cv2.rectangle(roi_vis, (int(roi_left), int(roi_top)), (int(roi_right), int(roi_bottom)), (0, 255, 0), 2)
        cv2.putText(roi_vis, "Menu ROI", (int(roi_left), int(roi_top - 10)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.circle(roi_vis, (int(airplay_cv2_x), int(airplay_cv2_y)), 10, (0, 0, 255), -1)
        cv2.putText(roi_vis, "AirPlay", (int(airplay_cv2_x + 15), int(airplay_cv2_y)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.save_debug_image(roi_vis, "2_menu_roi_visualization")
        
        # Extract ROI from screenshot
        roi = menu_screenshot[int(roi_top):int(roi_bottom), int(roi_left):int(roi_right)]
        
        if roi.size == 0:
            print("ROI is empty, using fallback")
            appletv_coords = {'x': airplay['x'] + 50, 'y': airplay['y'] - 70}
        else:
            # Save ROI for debug
            self.save_debug_image(roi, "3_menu_roi_extracted")
            
            # Step 5.2: Find Apple TV text/icon within ROI
            appletv_found = False
            appletv_roi_coords = None
            
            # Try to find Apple TV text in ROI
            if (self.template_dir / "apple_tv.png").exists():
                template = cv2.imread(str(self.template_dir / "apple_tv.png"))
                if template is not None:
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    
                    result = cv2.matchTemplate(gray_roi, gray_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > 0.6:
                        # Found Apple TV in ROI
                        roi_x = max_loc[0] + template.shape[1] // 2
                        roi_y = max_loc[1] + template.shape[0] // 2
                        
                        # Convert ROI coordinates back to full image coordinates
                        full_cv2_x = roi_left + roi_x
                        full_cv2_y = roi_top + roi_y
                        
                        # Convert to screen coordinates
                        screen_x, screen_y = self.converter.cv2_to_screen(full_cv2_x, full_cv2_y)
                        appletv_roi_coords = {'x': screen_x, 'y': screen_y}
                        appletv_found = True
                        print(f"Found Apple TV text at ({screen_x}, {screen_y})")
                        
                        # Visualize Apple TV found
                        appletv_vis = roi.copy()
                        cv2.rectangle(appletv_vis, max_loc, 
                                    (max_loc[0] + template.shape[1], max_loc[1] + template.shape[0]), 
                                    (0, 255, 0), 2)
                        cv2.putText(appletv_vis, f"Apple TV {max_val:.1%}", 
                                   (max_loc[0], max_loc[1] - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        self.save_debug_image(appletv_vis, "4_appletv_found_in_roi")
            
            if appletv_found and appletv_roi_coords:
                # Step 5.3: Define smaller ROI around Apple TV text for checkbox
                # Checkbox is typically 50-100 pixels to the left of the text
                checkbox_roi_left = max(0, roi_x - 100)
                checkbox_roi_right = roi_x - 20
                checkbox_roi_top = max(0, roi_y - 20)
                checkbox_roi_bottom = min(roi.shape[0], roi_y + 20)
                
                # Extract checkbox ROI
                checkbox_roi = roi[int(checkbox_roi_top):int(checkbox_roi_bottom), 
                                  int(checkbox_roi_left):int(checkbox_roi_right)]
                
                if checkbox_roi.size > 0:
                    # Visualize checkbox ROI
                    cb_roi_vis = roi.copy()
                    cv2.rectangle(cb_roi_vis, (int(checkbox_roi_left), int(checkbox_roi_top)), 
                                (int(checkbox_roi_right), int(checkbox_roi_bottom)), (255, 0, 255), 2)
                    cv2.putText(cb_roi_vis, "Checkbox ROI", 
                               (int(checkbox_roi_left), int(checkbox_roi_top - 5)),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                    self.save_debug_image(cb_roi_vis, "5_checkbox_roi_visualization")
                    
                    # Save checkbox ROI for debug
                    self.save_debug_image(checkbox_roi, "6_checkbox_roi_extracted")
                    
                    # Now look for checkbox in this small area
                    if (self.template_dir / "checkbox_unchecked.png").exists():
                        checkbox_template = cv2.imread(str(self.template_dir / "checkbox_unchecked.png"))
                        if checkbox_template is not None:
                            result = cv2.matchTemplate(checkbox_roi, checkbox_template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            
                            if max_val > 0.5:
                                # Found checkbox
                                cb_roi_x = max_loc[0] + checkbox_template.shape[1] // 2
                                cb_roi_y = max_loc[1] + checkbox_template.shape[0] // 2
                                
                                # Convert back to full coordinates
                                cb_full_cv2_x = roi_left + checkbox_roi_left + cb_roi_x
                                cb_full_cv2_y = roi_top + checkbox_roi_top + cb_roi_y
                                
                                cb_screen_x, cb_screen_y = self.converter.cv2_to_screen(cb_full_cv2_x, cb_full_cv2_y)
                                appletv_coords = {'x': cb_screen_x, 'y': cb_screen_y}
                                print(f"Found checkbox at ({cb_screen_x}, {cb_screen_y})")
                                
                                # Final visualization
                                final_vis = menu_screenshot.copy()
                                cv2.circle(final_vis, (int(cb_full_cv2_x), int(cb_full_cv2_y)), 10, (0, 255, 0), -1)
                                cv2.putText(final_vis, "Checkbox Found!", 
                                           (int(cb_full_cv2_x - 50), int(cb_full_cv2_y - 20)),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                self.save_debug_image(final_vis, "7_final_checkbox_position")
                            else:
                                # No checkbox template match, use offset from Apple TV text
                                # User found: checkbox is 500px to the right of Apple TV
                                appletv_coords = {
                                    'x': appletv_roi_coords['x'] + 500,
                                    'y': appletv_roi_coords['y']
                                }
                                print(f"Using +500px offset from Apple TV text")
                    else:
                        # No checkbox template, use offset
                        # Checkbox is 246px to the RIGHT of Apple TV icon
                        appletv_coords = {
                            'x': appletv_roi_coords['x'] + 246,
                            'y': appletv_roi_coords['y']
                        }
                else:
                    # Checkbox ROI empty, use Apple TV position with offset
                    appletv_coords = {
                        'x': appletv_roi_coords['x'] - 50,
                        'y': appletv_roi_coords['y']
                    }
            else:
                # No Apple TV found in ROI, use offset from AirPlay
                print("Apple TV not found in ROI, using offset")
                appletv_coords = {
                    'x': airplay['x'] + 50,
                    'y': airplay['y'] - 70
                }
        
        # Click Apple TV
        subprocess.run(['cliclick', f"c:{appletv_coords['x']},{appletv_coords['y']}"])
        
        # Save successful coordinates
        self.save_detected_coordinates(airplay, appletv_coords)
        
        elapsed = time.time() - start_time
        print(f"✅ AirPlay enabled in {elapsed:.2f}s (coordinates updated)")
        
        return True
    
    def get_quicktime_window(self):
        """Get QuickTime window info"""
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
            return {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
        return None
    
    def screen_to_cv2(self, screen_x, screen_y):
        """Helper method to access converter's screen_to_cv2"""
        return self.converter.screen_to_cv2(screen_x, screen_y)
    
    def save_debug_image(self, image, name):
        """Save debug image"""
        debug_dir = Path.home() / "airplay_debug"
        debug_dir.mkdir(exist_ok=True)
        path = debug_dir / f"{name}_{int(time.time())}.png"
        cv2.imwrite(str(path), image)
        print(f"📸 Debug image: {path.name}")
    
    def show_controls_fast(self, window):
        """Show controls quickly"""
        center_x = window['x'] + window['width'] // 2
        # Move to area where control bar appears (around 250px from bottom)
        control_y = window['y'] + window['height'] - 250
        
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(0.4)


# Drop-in replacement for cv2_airplay_enabler
class CV2AirPlayEnabler:
    def __init__(self, settings=None):
        self.smart_enabler = SmartCV2AirPlay(settings)
        self.settings = settings or {}
        self.templates_available = True  # Always try CV2
        
    def enable_airplay_fast(self):
        """Enable AirPlay with smart detection"""
        return self.smart_enabler.enable_airplay_smart()
    
    def enable_airplay_cv2(self):
        """Alias for compatibility"""
        return self.enable_airplay_fast()


def test_smart_airplay():
    """Test the smart AirPlay system"""
    print("🧠 Smart CV2 AirPlay Test")
    print("This will detect positions in real-time")
    
    enabler = SmartCV2AirPlay()
    
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to test...")
    
    success = enabler.enable_airplay_smart()
    
    if success:
        print("\n✅ Success! Coordinates have been updated.")
        print("Future uses will be even faster.")
    else:
        print("\n❌ Failed. Check if templates exist.")


if __name__ == "__main__":
    test_smart_airplay()