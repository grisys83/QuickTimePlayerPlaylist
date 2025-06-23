#!/usr/bin/env python3
"""
Save the correct Apple TV icon to checkbox offset
"""

import json
from pathlib import Path

def save_appletv_offset():
    """Save the verified offset"""
    
    # The verified offset from Apple TV icon to checkbox
    offset = {
        'x': 246,  # 246 pixels to the RIGHT
        'y': 0     # Same Y level
    }
    
    settings = {
        'appletv_icon_to_checkbox_offset': offset,
        'checkbox_position': 'right_of_icon',  # Not left as commonly assumed
        'offset_verified': True,
        'offset_description': 'Checkbox is 246 pixels to the right of Apple TV icon'
    }
    
    print("💾 Saving Apple TV icon to checkbox offset...")
    print(f"   Offset: X=+{offset['x']}, Y={offset['y']}")
    print("   Position: Checkbox is to the RIGHT of the icon")
    
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
        
        # Update with new offset
        existing.update(settings)
        
        # Save
        with open(settings_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"✅ Saved to {settings_file}")
    
    print("\n✅ Offset saved successfully!")
    print("\n📋 Usage in scripts:")
    print("   checkbox_x = appletv_icon_x + 246")
    print("   checkbox_y = appletv_icon_y")


if __name__ == "__main__":
    save_appletv_offset()