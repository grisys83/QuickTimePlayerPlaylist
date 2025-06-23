#!/usr/bin/env python3
"""Debug template detection"""

import cv2
from template_based_detector import TemplateBasedDetector
from pathlib import Path

detector = TemplateBasedDetector()

# Check templates
print("Checking templates...")
airplay_template = detector.template_dir / "airplay_icon.png"
apple_tv_template = detector.template_dir / "apple_tv_checkbox.png"

if airplay_template.exists():
    template = cv2.imread(str(airplay_template))
    print(f"✓ AirPlay template: {template.shape if template is not None else 'Failed to load'}")
else:
    print("✗ AirPlay template not found")

if apple_tv_template.exists():
    template = cv2.imread(str(apple_tv_template))
    print(f"✓ Apple TV template: {template.shape if template is not None else 'Failed to load'}")
else:
    print("✗ Apple TV template not found")

# Capture current screen
print("\nCapturing screen...")
screenshot = detector.capture_screen()
print(f"Screenshot size: {screenshot.shape}")

# Try detection with different thresholds
print("\nTrying detection with different thresholds...")
for threshold in [0.9, 0.8, 0.7, 0.6, 0.5]:
    result = detector.find_template(airplay_template, screenshot, threshold)
    if result:
        print(f"✓ Found at threshold {threshold}: confidence={result['confidence']:.2f}, position=({result['x']}, {result['y']})")
        break
    else:
        print(f"✗ Not found at threshold {threshold}")

# Try with multiple scales
print("\nTrying with multiple scales...")
result = detector.find_with_multiple_scales(airplay_template, screenshot)
if result:
    print(f"✓ Found with scale {result['scale']}: confidence={result['confidence']:.2f}, position=({result['x']}, {result['y']})")
    
    # Create visualization
    cv2.rectangle(screenshot, result['top_left'], result['bottom_right'], (0, 255, 0), 2)
    cv2.imwrite("debug_result.png", screenshot)
    print("Saved visualization to debug_result.png")
else:
    print("✗ Not found at any scale")
    
# Save current screenshot for inspection
cv2.imwrite("current_screen.png", screenshot)
print("\nSaved current screenshot to current_screen.png for inspection")