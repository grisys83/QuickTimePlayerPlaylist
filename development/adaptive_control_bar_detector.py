#!/usr/bin/env python3
"""
Adaptive control bar detection that adjusts based on window size
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import numpy as np

class AdaptiveControlBarDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        
    def get_adaptive_roi(self, window_height):
        """
        Get ROI bounds based on window size
        
        For smaller windows, the control bar takes up a larger proportion
        For larger windows, it's more consistent in absolute pixels
        """
        if window_height < 400:
            # Small window - control bar is proportionally MUCH larger
            # Use 20-95% from top (80-5% from bottom) 
            roi_top_offset = int(window_height * 0.8)  # 80% from bottom
            roi_bottom_offset = int(window_height * 0.05)  # 5% from bottom
        elif window_height < 600:
            # Medium window
            roi_top_offset = min(300, int(window_height * 0.5))
            roi_bottom_offset = 100
        else:
            # Large window - use fixed pixel offsets
            roi_top_offset = 450
            roi_bottom_offset = 150
            
        return roi_top_offset, roi_bottom_offset
    
    def get_mouse_position_for_controls(self, window):
        """
        Get adaptive mouse position based on window size
        """
        if window['height'] < 400:
            # Small window - hover at 65% from top
            y_offset = int(window['height'] * 0.65)
        elif window['height'] < 600:
            # Medium window - hover at 70% from top
            y_offset = int(window['height'] * 0.70)
        else:
            # Large window - hover at fixed offset from bottom
            y_offset = window['height'] - 250
            
        return window['x'] + window['width'] // 2, window['y'] + y_offset
    
    def detect_control_bar(self):
        """Main detection with adaptive approach"""
        print("🎯 Adaptive Control Bar Detection")
        print("=" * 50)
        
        # Get window
        window = self.get_quicktime_window()
        if not window:
            return
            
        print(f"\n📐 Window Analysis:")
        print(f"   Size: {window['width']}x{window['height']}")
        
        if window['height'] < 400:
            print("   Category: Small window")
        elif window['height'] < 600:
            print("   Category: Medium window")
        else:
            print("   Category: Large window")
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Get adaptive mouse position
        mouse_x, mouse_y = self.get_mouse_position_for_controls(window)
        offset_from_bottom = window['y'] + window['height'] - mouse_y
        
        print(f"\n🖱️  Adaptive mouse position:")
        print(f"   Position: ({mouse_x}, {mouse_y})")
        print(f"   Offset from bottom: {offset_from_bottom}px")
        print(f"   Percentage from top: {((mouse_y - window['y']) / window['height'] * 100):.0f}%")
        
        subprocess.run(['cliclick', f'm:{mouse_x},{mouse_y}'])
        time.sleep(1)
        
        # Capture
        screenshot_path = "/tmp/adaptive_test.png"
        subprocess.run(["screencapture", "-x", screenshot_path])
        screenshot = cv2.imread(screenshot_path)
        
        # Convert to CV2
        win_cv2_x1, win_cv2_y1 = self.converter.screen_to_cv2(window['x'], window['y'])
        win_cv2_x2, win_cv2_y2 = self.converter.screen_to_cv2(
            window['x'] + window['width'], 
            window['y'] + window['height']
        )
        
        # Get adaptive ROI
        roi_top_offset, roi_bottom_offset = self.get_adaptive_roi(window['height'])
        
        print(f"\n📊 Adaptive ROI:")
        print(f"   Top offset: {roi_top_offset}px from bottom")
        print(f"   Bottom offset: {roi_bottom_offset}px from bottom")
        
        # Create visualization
        vis = screenshot.copy()
        
        # Draw window
        cv2.rectangle(vis, (int(win_cv2_x1), int(win_cv2_y1)), 
                     (int(win_cv2_x2), int(win_cv2_y2)), (255, 0, 0), 2)
        cv2.putText(vis, f"Window {window['width']}x{window['height']}", 
                   (int(win_cv2_x1), int(win_cv2_y1 - 10)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Draw adaptive ROI
        roi_top = int(win_cv2_y2 - roi_top_offset)
        roi_bottom = int(win_cv2_y2 - roi_bottom_offset)
        cv2.rectangle(vis, (int(win_cv2_x1), roi_top), 
                     (int(win_cv2_x2), roi_bottom), (0, 255, 0), 3)
        cv2.putText(vis, f"Adaptive ROI ({roi_top_offset}-{roi_bottom_offset}px)", 
                   (int(win_cv2_x1), roi_top - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw mouse position
        mouse_cv2_x, mouse_cv2_y = self.converter.screen_to_cv2(mouse_x, mouse_y)
        cv2.circle(vis, (int(mouse_cv2_x), int(mouse_cv2_y)), 10, (255, 0, 255), -1)
        cv2.putText(vis, "Mouse", (int(mouse_cv2_x + 15), int(mouse_cv2_y)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # Extract ROI
        roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
        
        # Save
        output_dir = Path.home() / "adaptive_control_bar"
        output_dir.mkdir(exist_ok=True)
        
        cv2.imwrite(str(output_dir / "adaptive_visualization.png"), vis)
        cv2.imwrite(str(output_dir / "adaptive_roi.png"), roi)
        
        print(f"\n💾 Results saved to: {output_dir}")
        
        # Try to find control elements
        self.analyze_control_bar(roi, output_dir)
    
    def analyze_control_bar(self, roi, output_dir):
        """Analyze the ROI for control bar elements"""
        if roi.size == 0:
            print("\n❌ ROI is empty")
            return
            
        print("\n🔍 Analyzing control bar...")
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Find edges
        edges = cv2.Canny(gray, 50, 150)
        cv2.imwrite(str(output_dir / "edges.png"), edges)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours
        contour_vis = roi.copy()
        cv2.drawContours(contour_vis, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(str(output_dir / "contours.png"), contour_vis)
        
        print(f"   Found {len(contours)} contours")
        
        # Look for rectangular shapes (buttons)
        button_candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Buttons are typically square-ish or slightly wide
            if 0.5 < aspect_ratio < 2.0 and 20 < w < 100 and 20 < h < 100:
                button_candidates.append((x, y, w, h))
        
        print(f"   Found {len(button_candidates)} potential buttons")
        
        if button_candidates:
            button_vis = roi.copy()
            for x, y, w, h in button_candidates:
                cv2.rectangle(button_vis, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.imwrite(str(output_dir / "button_candidates.png"), button_vis)
    
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


def main():
    print("Make sure QuickTime is open with a video")
    input("Press Enter to start adaptive detection...")
    
    detector = AdaptiveControlBarDetector()
    detector.detect_control_bar()


if __name__ == "__main__":
    main()