#!/usr/bin/env python3
"""
Debug script to visualize control bar ROI
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter
import numpy as np

def debug_control_bar():
    converter = CoordinateConverter()
    
    print("🔍 Control Bar ROI Debugger")
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
        print("❌ QuickTime window not found!")
        return
        
    coords = result.stdout.strip().split(',')
    window = {
        'x': int(coords[0]),
        'y': int(coords[1]),
        'width': int(coords[2]),
        'height': int(coords[3])
    }
    
    print(f"✅ QuickTime window: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
    
    # Activate and show controls
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    # Move mouse to show controls
    center_x = window['x'] + window['width'] // 2
    # Position mouse where control bar should be (around 250px from bottom)
    control_y = window['y'] + window['height'] - 250
    
    print(f"\n🖱️  Moving mouse to ({center_x}, {control_y}) to show controls...")
    print(f"   (This is {window['y'] + window['height'] - control_y}px from bottom of window)")
    subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
    time.sleep(1)
    
    # Capture screen
    screenshot_path = "/tmp/qt_debug.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    screenshot = cv2.imread(screenshot_path)
    
    # Convert window coordinates to CV2
    win_cv2_x1, win_cv2_y1 = converter.screen_to_cv2(window['x'], window['y'])
    win_cv2_x2, win_cv2_y2 = converter.screen_to_cv2(
        window['x'] + window['width'], 
        window['y'] + window['height']
    )
    
    print(f"\n📐 Window in CV2 coords:")
    print(f"   Top-left: ({int(win_cv2_x1)}, {int(win_cv2_y1)})")
    print(f"   Bottom-right: ({int(win_cv2_x2)}, {int(win_cv2_y2)})")
    
    # Create visualization
    vis = screenshot.copy()
    
    # Draw window boundary
    cv2.rectangle(vis, (int(win_cv2_x1), int(win_cv2_y1)), 
                 (int(win_cv2_x2), int(win_cv2_y2)), (255, 0, 0), 2)
    cv2.putText(vis, "QuickTime Window", (int(win_cv2_x1), int(win_cv2_y1 - 10)), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Try different ROI sizes
    roi_sizes = [100, 120, 150, 180, 200]
    colors = [(0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 165, 255)]
    
    for i, (size, color) in enumerate(zip(roi_sizes, colors)):
        roi_top = int(win_cv2_y2 - size)
        cv2.rectangle(vis, (int(win_cv2_x1), roi_top), 
                     (int(win_cv2_x2), int(win_cv2_y2)), color, 2)
        cv2.putText(vis, f"ROI {size}px", (int(win_cv2_x1), roi_top - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # Save visualization
    debug_dir = Path.home() / "control_bar_debug"
    debug_dir.mkdir(exist_ok=True)
    
    vis_path = debug_dir / "control_bar_roi_test.png"
    cv2.imwrite(str(vis_path), vis)
    print(f"\n💾 Saved visualization to: {vis_path}")
    
    # Also save individual ROI extracts
    for size in roi_sizes:
        roi_top = int(win_cv2_y2 - size)
        roi = screenshot[roi_top:int(win_cv2_y2), int(win_cv2_x1):int(win_cv2_x2)]
        
        roi_path = debug_dir / f"roi_{size}px.png"
        cv2.imwrite(str(roi_path), roi)
        print(f"   Saved ROI {size}px to: {roi_path.name}")
    
    # Analyze control bar position
    print("\n📊 Analysis:")
    print("The control bar appears at the bottom of the QuickTime window")
    print("Based on the visualization, check which ROI size best captures it")
    print("\nRecommended: Use the ROI that includes the entire control bar")
    print("without too much empty space above it")


if __name__ == "__main__":
    debug_control_bar()