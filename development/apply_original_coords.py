#!/usr/bin/env python3
"""Apply original template coordinates to QuickDrop"""

import json
from pathlib import Path

# Original coordinates from QuickTimeConverterQt
original_coords = {
    'airplay_icon_coords': {'x': 844, 'y': 714},
    'apple_tv_coords': {'x': 970, 'y': 784},
    'airplay_configured': True
}

# Also check if we have settings from the converter
converter_settings = Path.home() / '.quicktime_converter_settings.json'
if converter_settings.exists():
    print("Found QuickTimeConverter settings!")
    with open(converter_settings, 'r') as f:
        saved = json.load(f)
        if 'airplay_icon_coords' in saved:
            original_coords.update(saved)
            print(f"Using saved coordinates: {saved}")

print("\nCoordinates to apply:")
print(f"AirPlay: ({original_coords['airplay_icon_coords']['x']}, {original_coords['airplay_icon_coords']['y']})")
print(f"Apple TV: ({original_coords['apple_tv_coords']['x']}, {original_coords['apple_tv_coords']['y']})")

# Save to QuickDrop settings
quickdrop_settings = Path.home() / '.quickdrop_settings.json'

confirm = input("\nApply these coordinates to QuickDrop? (y/n): ")
if confirm.lower() == 'y':
    with open(quickdrop_settings, 'w') as f:
        json.dump(original_coords, f, indent=2)
    print(f"\n✓ Settings saved to: {quickdrop_settings}")
    print("QuickDrop will now use these coordinates!")
else:
    print("Cancelled")