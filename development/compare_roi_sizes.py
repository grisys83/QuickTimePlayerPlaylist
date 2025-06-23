#!/usr/bin/env python3
"""
Compare different ROI sizes to find the best fit
"""

import cv2
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

def compare_roi_sizes():
    converter = CoordinateConverter()
    
    print("🔍 ROI Size Comparison")
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
    
    print(f"✅ Window: {window['width']}x{window['height']}")
    
    # Show controls
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(0.5)
    
    center_x = window['x'] + window['width'] // 2
    control_y = window['y'] + int(window['height'] * 0.65)
    
    subprocess.run(['cliclick', f'm:{center_x},{control_y}'])
    time.sleep(1)
    
    # Capture
    screenshot_path = "/tmp/roi_compare.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    screenshot = cv2.imread(screenshot_path)
    
    # Convert to CV2
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
    
    # Different ROI configurations to test
    roi_configs = [
        # (name, top_percent, bottom_percent, color)
        ("Old (60%-20%)", 0.6, 0.2, (0, 0, 255)),      # Red - old config
        ("New (80%-5%)", 0.8, 0.05, (0, 255, 0)),      # Green - new config
        ("Alt1 (90%-5%)", 0.9, 0.05, (255, 255, 0)),   # Yellow - even bigger
        ("Alt2 (75%-10%)", 0.75, 0.1, (255, 0, 255)),  # Magenta - middle ground
    ]
    
    height = window['height']
    
    for i, (name, top_pct, bottom_pct, color) in enumerate(roi_configs):
        roi_top = int(win_cv2_y2 - height * top_pct)
        roi_bottom = int(win_cv2_y2 - height * bottom_pct)
        
        # Draw ROI
        cv2.rectangle(vis, (int(win_cv2_x1 + i * 5), roi_top), 
                     (int(win_cv2_x2 - i * 5), roi_bottom), color, 2)
        
        # Label
        roi_height = roi_bottom - roi_top
        label = f"{name}: {roi_height}px"
        cv2.putText(vis, label, 
                   (int(win_cv2_x1 + 10 + i * 150), roi_top - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        print(f"\n{name}:")
        print(f"  ROI height: {roi_height}px")
        print(f"  Coverage: {(roi_height/height*100):.1f}% of window")
    
    # Save
    output_dir = Path.home() / "roi_comparison"
    output_dir.mkdir(exist_ok=True)
    cv2.imwrite(str(output_dir / "roi_comparison.png"), vis)
    
    print(f"\n💾 Comparison saved to: {output_dir / 'roi_comparison.png'}")
    print("\n📊 Analysis:")
    print("- Red: Old config (too small)")
    print("- Green: New config (3x larger)")
    print("- Yellow: Alternative 1 (even bigger)")
    print("- Magenta: Alternative 2 (middle ground)")
    
    # Also save individual ROIs
    for name, top_pct, bottom_pct, _ in roi_configs:
        roi_top = int(win_cv2_y2 - height * top_pct)
        roi_bottom = int(win_cv2_y2 - height * bottom_pct)
        
        if roi_top < roi_bottom:
            roi = screenshot[roi_top:roi_bottom, int(win_cv2_x1):int(win_cv2_x2)]
            filename = name.replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")
            cv2.imwrite(str(output_dir / f"roi_{filename}.png"), roi)


if __name__ == "__main__":
    print("Make sure QuickTime is open with a video")
    input("Press Enter to compare ROI sizes...")
    compare_roi_sizes()