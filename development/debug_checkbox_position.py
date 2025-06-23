#!/usr/bin/env python3
"""
Debug checkbox positioning in AirPlay menu
"""

import cv2
import numpy as np
import subprocess
import time
from pathlib import Path
from coordinate_converter import CoordinateConverter

def debug_checkbox_position():
    """Help understand checkbox positioning"""
    print("🔍 Checkbox Position Debugger")
    print("=" * 50)
    
    converter = CoordinateConverter()
    print(f"Scale factor: {converter.scale_factor}")
    
    # Ensure AirPlay menu is open
    print("\n1. Open QuickTime with a video")
    print("2. Show controls")
    print("3. Click AirPlay to open menu")
    input("\nPress Enter when AirPlay menu is visible...")
    
    # Take screenshot
    print("\n📸 Capturing menu...")
    screenshot_path = "/tmp/airplay_menu_debug.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    screenshot = cv2.imread(screenshot_path)
    
    # Get current mouse position (should be on Apple TV text)
    print("\nMove mouse to the Apple TV text/icon")
    input("Press Enter when mouse is on Apple TV text...")
    
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        appletv_screen_x, appletv_screen_y = int(coords[0]), int(coords[1])
        print(f"Apple TV position (screen): ({appletv_screen_x}, {appletv_screen_y})")
        
        # Convert to CV2
        appletv_cv2_x, appletv_cv2_y = converter.screen_to_cv2(appletv_screen_x, appletv_screen_y)
        print(f"Apple TV position (CV2): ({appletv_cv2_x}, {appletv_cv2_y})")
    
    # Now get checkbox position
    print("\nMove mouse to the CHECKBOX for Apple TV")
    input("Press Enter when mouse is on the checkbox...")
    
    result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    if result.stdout:
        coords = result.stdout.strip().split(',')
        checkbox_screen_x, checkbox_screen_y = int(coords[0]), int(coords[1])
        print(f"Checkbox position (screen): ({checkbox_screen_x}, {checkbox_screen_y})")
        
        # Convert to CV2
        checkbox_cv2_x, checkbox_cv2_y = converter.screen_to_cv2(checkbox_screen_x, checkbox_screen_y)
        print(f"Checkbox position (CV2): ({checkbox_cv2_x}, {checkbox_cv2_y})")
        
        # Calculate offset
        offset_screen_x = checkbox_screen_x - appletv_screen_x
        offset_screen_y = checkbox_screen_y - appletv_screen_y
        
        offset_cv2_x = checkbox_cv2_x - appletv_cv2_x
        offset_cv2_y = checkbox_cv2_y - appletv_cv2_y
        
        print(f"\n📏 Offset from Apple TV to Checkbox:")
        print(f"   Screen coordinates: ({offset_screen_x}, {offset_screen_y})")
        print(f"   CV2 coordinates: ({offset_cv2_x}, {offset_cv2_y})")
        
        # Draw on screenshot
        # Mark Apple TV position
        cv2.circle(screenshot, (int(appletv_cv2_x), int(appletv_cv2_y)), 5, (0, 255, 0), -1)
        cv2.putText(screenshot, "Apple TV", (int(appletv_cv2_x) + 10, int(appletv_cv2_y) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Mark checkbox position
        cv2.circle(screenshot, (int(checkbox_cv2_x), int(checkbox_cv2_y)), 5, (255, 0, 0), -1)
        cv2.putText(screenshot, "Checkbox", (int(checkbox_cv2_x) + 10, int(checkbox_cv2_y) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw line between them
        cv2.line(screenshot, (int(appletv_cv2_x), int(appletv_cv2_y)), 
                (int(checkbox_cv2_x), int(checkbox_cv2_y)), (255, 255, 0), 2)
        
        # Save debug image
        debug_path = "/tmp/checkbox_debug.png"
        cv2.imwrite(debug_path, screenshot)
        print(f"\n💾 Debug image saved to: {debug_path}")
        
        # Recommendation
        print("\n💡 Recommendation for code:")
        print(f"If Apple TV is found, checkbox offset should be:")
        print(f"   offset_pixels = {offset_screen_x}  # In screen coordinates")
        print(f"   checkbox_x = appletv_x + offset_pixels")
        print(f"   checkbox_y = appletv_y  # Same Y level")

if __name__ == "__main__":
    debug_checkbox_position()