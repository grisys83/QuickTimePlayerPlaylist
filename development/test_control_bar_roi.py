#!/usr/bin/env python3
"""
Test the new control bar ROI (150-450px from bottom)
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

def test_new_roi():
    converter = CoordinateConverter()
    
    print("🧪 Testing Control Bar ROI (150-450px)")
    print("=" * 50)
    
    # Get QuickTime window
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
        print("❌ QuickTime not found")
        return
        
    coords = result.stdout.strip().split(',')
    window = {
        'x': int(coords[0]),
        'y': int(coords[1]),
        'width': int(coords[2]),
        'height': int(coords[3])
    }
    
    print(f"✅ Window: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
    
    # Activate and show controls
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    # Move mouse to control bar area (250px from bottom)
    center_x = window['x'] + window['width'] // 2
    control_y = window['y'] + window['height'] - 250
    
    print(f"\n🖱️  Moving to control area ({center_x}, {control_y})...")
    subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
    time.sleep(1)
    
    # Capture
    screenshot_path = "/tmp/qt_roi_test.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    screenshot = cv2.imread(screenshot_path)
    
    # Convert to CV2 coords
    win_cv2_x1, win_cv2_y1 = converter.screen_to_cv2(window['x'], window['y'])
    win_cv2_x2, win_cv2_y2 = converter.screen_to_cv2(
        window['x'] + window['width'], 
        window['y'] + window['height']
    )
    
    # Create visualization
    vis = screenshot.copy()
    
    # Draw window
    cv2.rectangle(vis, (int(win_cv2_x1), int(win_cv2_y1)), 
                 (int(win_cv2_x2), int(win_cv2_y2)), (255, 0, 0), 2)
    cv2.putText(vis, "QuickTime Window", (int(win_cv2_x1), int(win_cv2_y1 - 10)), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Draw new ROI (150-450px from bottom)
    roi_top = int(win_cv2_y2 - 450)
    roi_bottom = int(win_cv2_y2 - 150)
    cv2.rectangle(vis, (int(win_cv2_x1), roi_top), 
                 (int(win_cv2_x2), roi_bottom), (0, 255, 0), 3)
    cv2.putText(vis, "Control Bar ROI (150-450px)", 
               (int(win_cv2_x1), roi_top - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Draw expected control bar area
    expected_top = int(win_cv2_y2 - 350)
    expected_bottom = int(win_cv2_y2 - 200)
    cv2.rectangle(vis, (int(win_cv2_x1), expected_top), 
                 (int(win_cv2_x2), expected_bottom), (255, 255, 0), 2)
    cv2.putText(vis, "Expected Control Bar (200-350px)", 
               (int(win_cv2_x1 + 200), expected_top + 75), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    # Extract and save ROI
    roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
    
    # Save
    output_dir = Path.home() / "control_bar_test"
    output_dir.mkdir(exist_ok=True)
    
    cv2.imwrite(str(output_dir / "roi_visualization.png"), vis)
    cv2.imwrite(str(output_dir / "roi_extracted.png"), roi)
    
    print(f"\n📁 Results saved to: {output_dir}")
    print("\n📊 Analysis:")
    print("- Green box: New ROI (150-450px from bottom)")
    print("- Yellow box: Expected control bar location (200-350px)")
    print("- The ROI should comfortably contain the control bar")
    
    # Try to find AirPlay icon in ROI
    template_dir = Path(__file__).parent / "templates"
    airplay_template = template_dir / "airplay_icon.png"
    
    if airplay_template.exists():
        print("\n🔍 Looking for AirPlay icon in ROI...")
        template = cv2.imread(str(airplay_template))
        
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:
            print(f"✅ Found AirPlay icon! Confidence: {max_val:.1%}")
            
            # Mark on ROI
            icon_vis = roi.copy()
            cv2.rectangle(icon_vis, max_loc, 
                         (max_loc[0] + template.shape[1], max_loc[1] + template.shape[0]),
                         (0, 255, 0), 2)
            cv2.imwrite(str(output_dir / "airplay_found_in_roi.png"), icon_vis)
        else:
            print(f"❌ AirPlay icon not found (best match: {max_val:.1%})")


if __name__ == "__main__":
    print("Make sure QuickTime is open with a video")
    input("Press Enter to test...")
    test_new_roi()