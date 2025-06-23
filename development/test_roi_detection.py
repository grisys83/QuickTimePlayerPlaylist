#!/usr/bin/env python3
"""
Test the ROI-based detection approach
"""

import subprocess
import time
from pathlib import Path

def test_roi_detection():
    print("🧪 Testing ROI-based AirPlay Detection")
    print("=" * 60)
    
    print("\n📋 Prerequisites:")
    print("1. QuickTime Player should be open")
    print("2. A video should be loaded and playing")
    print("3. Debug images will be saved to ~/airplay_debug/")
    
    input("\nPress Enter to start test...")
    
    # Import the enabler
    from cv2_airplay_enabler import CV2AirPlayEnabler
    
    # Create enabler
    enabler = CV2AirPlayEnabler()
    
    print("\n🚀 Running AirPlay enable with ROI detection...")
    start_time = time.time()
    
    # Run the enable function
    success = enabler.enable_airplay_fast()
    
    elapsed = time.time() - start_time
    
    if success:
        print(f"\n✅ Success! AirPlay enabled in {elapsed:.2f} seconds")
    else:
        print(f"\n❌ Failed to enable AirPlay")
    
    print(f"\n📁 Debug images saved to: {Path.home() / 'airplay_debug'}")
    print("\nPlease check the debug images to see the ROI detection process:")
    print("1. 1_menu_screenshot.png - Full menu capture")
    print("2. 2_menu_roi_visualization.png - Shows the ROI area")
    print("3. 3_menu_roi_extracted.png - The extracted ROI")
    print("4. 4_appletv_found_in_roi.png - Apple TV text detection")
    print("5. 5_checkbox_roi_visualization.png - Checkbox search area")
    print("6. 6_checkbox_roi_extracted.png - Extracted checkbox area")
    print("7. 7_final_checkbox_position.png - Final result")
    
    # List debug images
    debug_dir = Path.home() / "airplay_debug"
    if debug_dir.exists():
        images = sorted(debug_dir.glob("*.png"))
        if images:
            print(f"\n📸 Found {len(images)} debug images:")
            for img in images[-7:]:  # Show last 7 images
                print(f"   - {img.name}")


if __name__ == "__main__":
    test_roi_detection()