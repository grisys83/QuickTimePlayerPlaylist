#!/usr/bin/env python3
"""Quick test of template detection"""

from template_based_detector import TemplateBasedDetector
import time

print("Testing AirPlay detection...")
print("Make sure QuickTime is open with a video loaded")
time.sleep(2)

detector = TemplateBasedDetector()
result = detector.detect_airplay_setup()

if result:
    print("\n✅ Detection successful!")
    print(f"AirPlay icon: X={result['airplay_icon_coords']['x']}, Y={result['airplay_icon_coords']['y']}")
    print(f"Apple TV: X={result['apple_tv_coords']['x']}, Y={result['apple_tv_coords']['y']}")
    
    # Visualize
    print("\nCreating visualization...")
    detector.visualize_detection("detection_test_result.png")
    print("Check detection_test_result.png to see the results")
else:
    print("\n❌ Detection failed")
    print("Make sure:")
    print("1. QuickTime is open with a video")
    print("2. Templates exist in the templates folder")
    print("3. The UI matches the captured templates")