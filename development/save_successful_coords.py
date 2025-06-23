#!/usr/bin/env python3
"""
Save the successful coordinates from the working detection
"""

import json
from pathlib import Path

def save_successful_coordinates():
    """Save the coordinates that worked"""
    
    # The successful checkbox click was at (759, 639)
    # We need to reverse-engineer the AirPlay position
    # checkbox_x = airplay_x - 80
    # checkbox_y = airplay_y - 160
    
    checkbox_x = 759
    checkbox_y = 639
    
    # Calculate AirPlay position
    airplay_x = checkbox_x + 80  # 839
    airplay_y = checkbox_y + 160  # 799
    
    settings = {
        'airplay_icon_coords': {
            'x': airplay_x,
            'y': airplay_y
        },
        'apple_tv_coords': {
            'x': checkbox_x,
            'y': checkbox_y
        },
        'checkbox_offset': {
            'x': -80,
            'y': -160
        },
        'airplay_configured': True,
        'detection_method': 'maintain_focus',
        'last_successful_click': '(759, 639)'
    }
    
    print("💾 Saving successful coordinates...")
    print(f"   AirPlay icon: ({airplay_x}, {airplay_y})")
    print(f"   Checkbox: ({checkbox_x}, {checkbox_y})")
    print(f"   Offset: (-80, -160)")
    
    # Save to both settings files
    for filename in ['.quicktime_converter_settings.json', '.quickdrop_settings.json']:
        settings_file = Path.home() / filename
        
        # Load existing settings
        existing = {}
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                try:
                    existing = json.load(f)
                except:
                    existing = {}
        
        # Update with new coordinates
        existing.update(settings)
        
        # Save
        with open(settings_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"✅ Saved to {settings_file}")
    
    print("\n✅ Coordinates saved successfully!")
    print("All scripts should now use these working coordinates.")


if __name__ == "__main__":
    save_successful_coordinates()