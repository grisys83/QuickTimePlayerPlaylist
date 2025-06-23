#!/usr/bin/env python3
"""
Dynamically find control bar by searching from bottom up
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import numpy as np

class DynamicControlBarFinder:
    def __init__(self):
        self.converter = CoordinateConverter()
        self.template_dir = Path(__file__).parent / "templates"
        
    def find_control_bar(self):
        """Find control bar dynamically"""
        print("🔍 Dynamic Control Bar Finder")
        print("=" * 50)
        
        # Get window
        window = self.get_quicktime_window()
        if not window:
            return None
            
        # Show controls
        self.show_controls(window)
        
        # Capture screen
        screenshot = self.capture_screen()
        
        # Convert window to CV2 coords
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Search for control bar from bottom up
        print("\n🔍 Searching for control bar from bottom up...")
        
        # Extract window area
        window_roi = screenshot[int(win_cv2_y1):int(win_cv2_y2), 
                               int(win_cv2_x1):int(win_cv2_x2)]
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(window_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection to find control bar boundary
        edges = cv2.Canny(gray, 50, 150)
        
        # Find horizontal lines (control bar typically has strong horizontal edge)
        height, width = edges.shape
        control_bar_top = None
        
        # Search from bottom up for strong horizontal edge
        for y in range(height - 1, height // 2, -1):  # Search bottom half
            edge_sum = np.sum(edges[y, :])
            if edge_sum > width * 0.3:  # If more than 30% of width has edges
                control_bar_top = y
                break
        
        if control_bar_top:
            print(f"✅ Found control bar edge at Y={control_bar_top} (from bottom: {height - control_bar_top}px)")
            
            # Create visualization
            vis = screenshot.copy()
            
            # Draw window
            cv2.rectangle(vis, (int(win_cv2_x1), int(win_cv2_y1)), 
                         (int(win_cv2_x2), int(win_cv2_y2)), (255, 0, 0), 2)
            
            # Draw detected control bar area
            control_cv2_y = int(win_cv2_y1 + control_bar_top)
            cv2.rectangle(vis, (int(win_cv2_x1), control_cv2_y), 
                         (int(win_cv2_x2), int(win_cv2_y2)), (0, 255, 0), 2)
            cv2.putText(vis, "Detected Control Bar", 
                       (int(win_cv2_x1), control_cv2_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Save results
            debug_dir = Path.home() / "control_bar_debug"
            debug_dir.mkdir(exist_ok=True)
            
            cv2.imwrite(str(debug_dir / "edges.png"), edges)
            cv2.imwrite(str(debug_dir / "detected_control_bar.png"), vis)
            
            control_bar_roi = window_roi[control_bar_top:, :]
            cv2.imwrite(str(debug_dir / "control_bar_extracted.png"), control_bar_roi)
            
            print(f"\n📁 Debug images saved to: {debug_dir}")
            
            return {
                'control_bar_height': height - control_bar_top,
                'recommended_roi_height': (height - control_bar_top) + 20  # Add some padding
            }
        else:
            print("❌ Could not detect control bar edge")
            
            # Try template matching as fallback
            return self.find_by_template(window_roi, screenshot, win_cv2_x1, win_cv2_y1)
    
    def find_by_template(self, window_roi, screenshot, win_x1, win_y1):
        """Fallback: find control bar using play button template"""
        print("\n🔍 Trying template matching for play button...")
        
        play_template_path = self.template_dir / "play_button.png"
        if not play_template_path.exists():
            print(f"❌ Template not found: {play_template_path}")
            return None
            
        template = cv2.imread(str(play_template_path))
        if template is None:
            return None
            
        # Search in bottom half of window
        height, width = window_roi.shape[:2]
        bottom_half = window_roi[height//2:, :]
        
        result = cv2.matchTemplate(bottom_half, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.7:
            # Found play button
            button_y = height//2 + max_loc[1]
            control_bar_top = button_y - 30  # Control bar extends above button
            control_bar_height = height - control_bar_top
            
            print(f"✅ Found play button, estimated control bar height: {control_bar_height}px")
            
            # Visualize
            vis = screenshot.copy()
            control_cv2_y = int(win_y1 + control_bar_top)
            cv2.rectangle(vis, (int(win_x1), control_cv2_y), 
                         (int(win_x1 + width), int(win_y1 + height)), 
                         (0, 255, 255), 2)
            cv2.putText(vis, "Control Bar (by template)", 
                       (int(win_x1), control_cv2_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            debug_dir = Path.home() / "control_bar_debug"
            cv2.imwrite(str(debug_dir / "control_bar_by_template.png"), vis)
            
            return {
                'control_bar_height': control_bar_height,
                'recommended_roi_height': control_bar_height + 20
            }
        
        return None
    
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
    
    def show_controls(self, window):
        """Show controls"""
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        center_x = window['x'] + window['width'] // 2
        control_y = window['y'] + int(window['height'] * 0.85)
        
        subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
        time.sleep(1)
        subprocess.run(['cliclick', f'm:{center_x + 5},{control_y}'])
        time.sleep(0.5)
    
    def capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/qt_screen.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot


def main():
    print("🎯 Finding optimal control bar ROI size")
    print("\nMake sure QuickTime is open with a video")
    input("Press Enter to start...")
    
    finder = DynamicControlBarFinder()
    result = finder.find_control_bar()
    
    if result:
        print(f"\n✅ Recommendation:")
        print(f"   Control bar height: ~{result['control_bar_height']}px")
        print(f"   Recommended ROI height: {result['recommended_roi_height']}px")
        print(f"\n💡 Update your code to use ROI height of {result['recommended_roi_height']}px")
    else:
        print("\n❌ Could not determine control bar size")
        print("   Using default ROI height of 150px")


if __name__ == "__main__":
    main()