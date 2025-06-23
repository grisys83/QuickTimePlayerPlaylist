#!/usr/bin/env python3
"""
Improved AirPlay Icon Detector
Uses multiple detection methods for better accuracy
"""

import cv2
import numpy as np
import subprocess
import os
import time
from pathlib import Path

class AirPlayIconDetector:
    def __init__(self):
        self.quicktime_control_height = 100  # QuickTime control bar is usually at bottom
        
    def capture_screen(self):
        """Capture screen using macOS screencapture"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        os.remove(screenshot_path)
        return screenshot
    
    def find_quicktime_window(self):
        """Find QuickTime window position using AppleScript"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    return (item 1 of windowPos as string) & "," & (item 2 of windowPos as string) & "," & (item 1 of windowSize as string) & "," & (item 2 of windowSize as string)
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
    
    def detect_airplay_icon(self):
        """Main detection method"""
        # Get QuickTime window position
        qt_window = self.find_quicktime_window()
        if not qt_window:
            print("QuickTime window not found")
            return None
            
        # Capture screen
        screenshot = self.capture_screen()
        
        # Focus on control bar area (bottom of QuickTime window)
        control_bar_y = qt_window['y'] + qt_window['height'] - self.quicktime_control_height
        control_bar = screenshot[
            control_bar_y:qt_window['y'] + qt_window['height'],
            qt_window['x']:qt_window['x'] + qt_window['width']
        ]
        
        # Method 1: Color-based detection (AirPlay icon is usually white/light gray)
        airplay_coords = self._detect_by_color(control_bar, qt_window['x'], control_bar_y)
        if airplay_coords:
            return airplay_coords
            
        # Method 2: Shape detection
        airplay_coords = self._detect_by_shape(control_bar, qt_window['x'], control_bar_y)
        if airplay_coords:
            return airplay_coords
            
        # Method 3: Feature matching (if we have a template)
        airplay_coords = self._detect_by_template(control_bar, qt_window['x'], control_bar_y)
        return airplay_coords
    
    def _detect_by_color(self, control_bar, offset_x, offset_y):
        """Detect AirPlay icon by its color (usually white/light gray)"""
        # Convert to grayscale
        gray = cv2.cvtColor(control_bar, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find bright areas (icons are usually bright)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for AirPlay-like shapes
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # AirPlay icon size constraints
            if 15 < w < 40 and 15 < h < 40:
                # Check if it's roughly square (AirPlay icon bounding box)
                aspect_ratio = w / h
                if 0.7 < aspect_ratio < 1.3:
                    # Check position (usually in right side of control bar)
                    if x > control_bar.shape[1] * 0.6:  # Right 40% of control bar
                        return {
                            'x': offset_x + x + w // 2,
                            'y': offset_y + y + h // 2,
                            'confidence': 0.7
                        }
        return None
    
    def _detect_by_shape(self, control_bar, offset_x, offset_y):
        """Detect by shape characteristics"""
        gray = cv2.cvtColor(control_bar, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Approximate polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # AirPlay icon has triangle + rectangle shape
            if 3 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(contour)
                if 15 < w < 40 and 15 < h < 40 and x > control_bar.shape[1] * 0.6:
                    return {
                        'x': offset_x + x + w // 2,
                        'y': offset_y + y + h // 2,
                        'confidence': 0.6
                    }
        return None
    
    def _detect_by_template(self, control_bar, offset_x, offset_y):
        """Template matching (requires saved template)"""
        template_path = Path(__file__).parent / "airplay_template.png"
        if not template_path.exists():
            return None
            
        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
        gray = cv2.cvtColor(control_bar, cv2.COLOR_BGR2GRAY)
        
        # Try different scales
        best_match = None
        best_val = 0
        
        for scale in [0.8, 1.0, 1.2]:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val and max_val > 0.7:
                best_val = max_val
                best_match = {
                    'x': offset_x + max_loc[0] + width // 2,
                    'y': offset_y + max_loc[1] + height // 2,
                    'confidence': max_val
                }
        
        return best_match
    
    def save_template(self):
        """Helper to save AirPlay icon template"""
        print("Opening QuickTime to capture AirPlay icon template...")
        
        # Ensure QuickTime is open
        subprocess.run(['open', '-a', 'QuickTime Player'])
        time.sleep(2)
        
        print("Please:")
        print("1. Load any video in QuickTime")
        print("2. Make sure the AirPlay icon is visible")
        print("3. Press Enter when ready...")
        input()
        
        # Capture and find icon
        result = self.detect_airplay_icon()
        if result:
            # Capture area around detected icon
            screenshot = self.capture_screen()
            x, y = result['x'], result['y']
            
            # Extract 30x30 area around icon
            icon_area = screenshot[y-15:y+15, x-15:x+15]
            cv2.imwrite("airplay_template.png", icon_area)
            print(f"Template saved! Icon detected at ({x}, {y})")
            
            # Show what was captured
            cv2.imshow("Captured AirPlay Icon", icon_area)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
        else:
            print("Could not detect AirPlay icon automatically")
    
    def detect_and_click(self):
        """Detect AirPlay icon and menu items"""
        # First, find AirPlay icon
        airplay = self.detect_airplay_icon()
        if not airplay:
            return None
            
        results = {
            'airplay_icon_coords': {
                'x': airplay['x'],
                'y': airplay['y']
            }
        }
        
        # Click AirPlay icon to open menu
        subprocess.run(['cliclick', f"c:{airplay['x']},{airplay['y']}"])
        time.sleep(0.7)  # Give menu time to appear
        
        # Capture screen with menu open
        screenshot = self.capture_screen()
        
        # Detect Apple TV in the menu
        apple_tv_coords = self._detect_apple_tv_in_menu(screenshot, airplay)
        
        if apple_tv_coords:
            results['apple_tv_coords'] = apple_tv_coords
        else:
            # Fallback to estimation
            results['apple_tv_coords'] = {
                'x': airplay['x'] + 50,
                'y': airplay['y'] + 70
            }
        
        # Close menu by clicking elsewhere
        subprocess.run(['cliclick', 'c:100,100'])
        
        return results
    
    def _detect_apple_tv_in_menu(self, screenshot, airplay_pos):
        """Detect Apple TV item in AirPlay menu"""
        # Define search area (menu appears near AirPlay icon)
        search_x = max(0, airplay_pos['x'] - 150)
        search_y = airplay_pos['y'] + 20  # Menu appears below
        search_width = 300
        search_height = 200
        
        # Extract menu area
        menu_area = screenshot[
            search_y:search_y + search_height,
            search_x:search_x + search_width
        ]
        
        # Method 1: Look for checkbox pattern
        checkbox_pos = self._find_checkbox(menu_area, search_x, search_y)
        if checkbox_pos:
            return checkbox_pos
            
        # Method 2: Look for text "Apple TV" using OCR
        try:
            import pytesseract
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(menu_area, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # OCR to find text
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            
            # Look for "Apple TV" or similar text
            for i, word in enumerate(data['text']):
                if word and ('Apple' in word or 'TV' in word or 'HomePod' in word):
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Return position to the left of text (where checkbox would be)
                    return {
                        'x': search_x + x - 20,  # Checkbox is usually left of text
                        'y': search_y + y + h // 2
                    }
        except ImportError:
            print("pytesseract not installed, skipping OCR detection")
        except Exception as e:
            print(f"OCR error: {e}")
            
        # Method 3: Pattern matching for menu items
        return self._find_menu_item_pattern(menu_area, search_x, search_y)
    
    def _find_checkbox(self, menu_area, offset_x, offset_y):
        """Find checkbox pattern in menu"""
        gray = cv2.cvtColor(menu_area, cv2.COLOR_BGR2GRAY)
        
        # Look for square shapes (checkboxes)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Approximate to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Checkbox is usually a square
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it's square-ish and right size
                if 10 < w < 25 and 10 < h < 25 and 0.8 < w/h < 1.2:
                    # Checkboxes are usually on the left side of menu
                    if x < menu_area.shape[1] * 0.3:
                        return {
                            'x': offset_x + x + w // 2,
                            'y': offset_y + y + h // 2
                        }
        return None
    
    def _find_menu_item_pattern(self, menu_area, offset_x, offset_y):
        """Find menu item by typical pattern"""
        gray = cv2.cvtColor(menu_area, cv2.COLOR_BGR2GRAY)
        
        # Menu items often have consistent height and spacing
        # Look for horizontal lines (menu separators)
        edges = cv2.Canny(gray, 30, 100)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            # Sort lines by y-coordinate
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 5:  # Horizontal line
                    horizontal_lines.append(y1)
            
            horizontal_lines = sorted(set(horizontal_lines))
            
            # Apple TV is usually the second or third item
            if len(horizontal_lines) >= 2:
                # Position between first and second separator
                item_y = horizontal_lines[0] + 20
                return {
                    'x': offset_x + 30,  # Typical checkbox position
                    'y': offset_y + item_y
                }
        
        return None
    
    def visualize_detection(self, save_path="detection_result.png"):
        """Visualize the detection process for debugging"""
        screenshot = self.capture_screen()
        result = self.detect_airplay_icon()
        
        if result:
            # Draw circle on AirPlay icon
            cv2.circle(screenshot, (result['x'], result['y']), 20, (0, 255, 0), 2)
            cv2.putText(screenshot, "AirPlay", (result['x'] - 30, result['y'] - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Click and detect menu
            subprocess.run(['cliclick', f"c:{result['x']},{result['y']}"])
            time.sleep(0.7)
            
            menu_screenshot = self.capture_screen()
            apple_tv = self._detect_apple_tv_in_menu(menu_screenshot, result)
            
            if apple_tv:
                cv2.circle(menu_screenshot, (apple_tv['x'], apple_tv['y']), 15, (255, 0, 0), 2)
                cv2.putText(menu_screenshot, "Apple TV", (apple_tv['x'] - 35, apple_tv['y'] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            cv2.imwrite(save_path, menu_screenshot)
            print(f"Detection visualization saved to {save_path}")
            
            # Close menu
            subprocess.run(['cliclick', 'c:100,100'])
        
        return result


def main():
    detector = AirPlayIconDetector()
    
    print("AirPlay Icon Auto-Detector")
    print("1. Detect AirPlay coordinates")
    print("2. Save icon template for better detection")
    
    choice = input("Choose (1 or 2): ")
    
    if choice == "1":
        print("\nDetecting AirPlay icon...")
        result = detector.detect_and_click()
        
        if result:
            print(f"\nSuccess!")
            print(f"AirPlay Icon: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
            print(f"Apple TV (estimated): ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        else:
            print("Could not detect AirPlay icon")
            
    elif choice == "2":
        detector.save_template()

if __name__ == "__main__":
    main()