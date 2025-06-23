#!/usr/bin/env python3
"""
Test different AirPlay detection approaches
"""

import sys
import time
from pathlib import Path

def test_visual_detector_v2():
    """Test the new visual detector with ROI approach"""
    print("\n🎯 Testing Visual AirPlay Detector V2 (ROI-based)")
    print("This will guide you through interactive detection")
    print("Debug images will be saved for analysis")
    
    from visual_airplay_detector_v2 import main as run_visual_v2
    run_visual_v2()

def test_cv2_enabler():
    """Test the CV2 enabler with ROI approach"""
    print("\n🚀 Testing CV2 AirPlay Enabler (Smart ROI)")
    
    from cv2_airplay_enabler import CV2AirPlayEnabler
    
    print("\nMake sure QuickTime is open with a video playing")
    input("Press Enter to test...")
    
    enabler = CV2AirPlayEnabler()
    start_time = time.time()
    
    success = enabler.enable_airplay_fast()
    elapsed = time.time() - start_time
    
    if success:
        print(f"\n✅ Success! AirPlay enabled in {elapsed:.2f} seconds")
    else:
        print(f"\n❌ Failed to enable AirPlay")
    
    print(f"\n📁 Debug images in: {Path.home() / 'airplay_debug'}")

def test_original_visual():
    """Test the original visual detector"""
    print("\n🎨 Testing Original Visual Detector")
    
    from visual_airplay_detector import main as run_visual_v1
    run_visual_v1()

def check_settings():
    """Check current settings"""
    print("\n🔍 Checking Current Settings")
    
    from check_airplay_settings import check_settings as run_check
    run_check()

def main():
    print("🧪 AirPlay Detection Test Suite")
    print("=" * 60)
    
    print("\nChoose a test:")
    print("1. Visual Detector V2 (ROI-based) - Most thorough")
    print("2. CV2 Enabler (Smart ROI) - Fast automatic")
    print("3. Original Visual Detector - Interactive")
    print("4. Check Current Settings")
    print("5. Exit")
    
    choice = input("\nSelect (1-5): ")
    
    if choice == '1':
        test_visual_detector_v2()
    elif choice == '2':
        test_cv2_enabler()
    elif choice == '3':
        test_original_visual()
    elif choice == '4':
        check_settings()
    elif choice == '5':
        print("\nExiting...")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")
        
    # Ask if user wants to run another test
    again = input("\n🔄 Run another test? (y/n): ")
    if again.lower() == 'y':
        print("\n" + "=" * 60)
        main()

if __name__ == "__main__":
    main()