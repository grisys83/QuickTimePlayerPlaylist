#!/usr/bin/env python3
"""Update QuickDrop coordinates manually"""

import json
from pathlib import Path

# Current detected coordinates
current = {
    'airplay_icon_coords': {'x': 155, 'y': 686},
    'apple_tv_coords': {'x': 205, 'y': 756}  # Estimated: +50, +70
}

print("Current coordinates:")
print(f"AirPlay: ({current['airplay_icon_coords']['x']}, {current['airplay_icon_coords']['y']})")
print(f"Apple TV: ({current['apple_tv_coords']['x']}, {current['apple_tv_coords']['y']})")

print("\nIf Apple TV position is wrong, you can adjust it.")
print("The Apple TV checkbox is usually:")
print("- 50-100 pixels to the right of AirPlay icon")
print("- 50-100 pixels below AirPlay icon")

adjust = input("\nAdjust coordinates? (y/n): ")

if adjust.lower() == 'y':
    try:
        x_offset = int(input("X offset from AirPlay (default 50): ") or "50")
        y_offset = int(input("Y offset from AirPlay (default 70): ") or "70")
        
        current['apple_tv_coords']['x'] = current['airplay_icon_coords']['x'] + x_offset
        current['apple_tv_coords']['y'] = current['airplay_icon_coords']['y'] + y_offset
        
        print(f"\nNew Apple TV position: ({current['apple_tv_coords']['x']}, {current['apple_tv_coords']['y']})")
    except:
        print("Invalid input, using defaults")

# Save settings
current['airplay_configured'] = True
settings_file = Path.home() / '.quickdrop_settings.json'

save = input("\nSave these settings? (y/n): ")
if save.lower() == 'y':
    with open(settings_file, 'w') as f:
        json.dump(current, f, indent=2)
    print(f"Settings saved to: {settings_file}")
else:
    print("Settings not saved")