#!/usr/bin/env python3
"""
Test AirPlay detection with visualization
"""

import subprocess
import time
from airplay_icon_detector import AirPlayIconDetector

def test_detection():
    print("AirPlay Detection Test")
    print("=" * 50)
    
    # Ensure QuickTime is open
    print("Opening QuickTime Player...")
    subprocess.run(['open', '-a', 'QuickTime Player'])
    time.sleep(2)
    
    print("\nPlease load a video in QuickTime Player")
    print("Press Enter when ready...")
    input()
    
    # Create detector
    detector = AirPlayIconDetector()
    
    # Test basic detection
    print("\n1. Testing AirPlay icon detection...")
    airplay = detector.detect_airplay_icon()
    
    if airplay:
        print(f"✓ Found AirPlay icon at ({airplay['x']}, {airplay['y']}) with {airplay['confidence']:.1%} confidence")
    else:
        print("✗ Could not find AirPlay icon")
        return
    
    # Test full detection with menu
    print("\n2. Testing full detection (icon + Apple TV)...")
    result = detector.detect_and_click()
    
    if result:
        print(f"✓ AirPlay icon: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"✓ Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
    else:
        print("✗ Detection failed")
        return
    
    # Create visualization
    print("\n3. Creating visualization...")
    detector.visualize_detection("airplay_detection_test.png")
    print("✓ Visualization saved to 'airplay_detection_test.png'")
    
    # Test clicking
    print("\n4. Testing actual clicking...")
    print("The app will now:")
    print("  - Click the AirPlay icon")
    print("  - Wait 1 second")
    print("  - Click the Apple TV option")
    print("  - Close the menu")
    
    proceed = input("\nProceed with test? (y/n): ")
    if proceed.lower() == 'y':
        # Click AirPlay
        subprocess.run(['cliclick', f"c:{result['airplay_icon_coords']['x']},{result['airplay_icon_coords']['y']}"])
        time.sleep(1)
        
        # Click Apple TV
        subprocess.run(['cliclick', f"c:{result['apple_tv_coords']['x']},{result['apple_tv_coords']['y']}"])
        time.sleep(0.5)
        
        print("✓ Test completed!")
    
    print("\n" + "=" * 50)
    print("Detection Summary:")
    print(f"AirPlay Icon: X={result['airplay_icon_coords']['x']}, Y={result['airplay_icon_coords']['y']}")
    print(f"Apple TV:     X={result['apple_tv_coords']['x']}, Y={result['apple_tv_coords']['y']}")
    print("\nThese coordinates have been saved and can be used in the main app.")

if __name__ == "__main__":
    test_detection()