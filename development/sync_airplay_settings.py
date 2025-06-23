#!/usr/bin/env python3
"""
Synchronize AirPlay settings between QuickTimeConverter and QuickDrop
"""

import json
from pathlib import Path

def sync_settings():
    """Sync AirPlay coordinates between apps"""
    print("🔄 Synchronizing AirPlay Settings")
    print("=" * 50)
    
    # File paths
    qt_settings_file = Path.home() / '.quicktime_converter_settings.json'
    qd_settings_file = Path.home() / '.quickdrop_settings.json'
    
    # Load QuickTimeConverter settings
    qt_settings = {}
    if qt_settings_file.exists():
        with open(qt_settings_file, 'r') as f:
            qt_settings = json.load(f)
            print(f"\n✅ Loaded QuickTimeConverter settings:")
            print(f"   AirPlay: {qt_settings.get('airplay_icon_coords', 'Not set')}")
            print(f"   Apple TV: {qt_settings.get('apple_tv_coords', 'Not set')}")
    else:
        print("❌ QuickTimeConverter settings not found")
        
    # Load QuickDrop settings
    qd_settings = {}
    if qd_settings_file.exists():
        with open(qd_settings_file, 'r') as f:
            qd_settings = json.load(f)
            print(f"\n✅ Loaded QuickDrop settings:")
            print(f"   AirPlay: {qd_settings.get('airplay_icon_coords', 'Not set')}")
            print(f"   Apple TV: {qd_settings.get('apple_tv_coords', 'Not set')}")
    else:
        print("\n⚠️  QuickDrop settings not found")
        
    # Find the most recent valid coordinates
    valid_coords = None
    source = None
    
    # Check if QuickTimeConverter has manually configured coordinates
    if qt_settings.get('manually_configured') and qt_settings.get('airplay_icon_coords'):
        valid_coords = {
            'airplay_icon_coords': qt_settings['airplay_icon_coords'],
            'apple_tv_coords': qt_settings['apple_tv_coords']
        }
        source = "QuickTimeConverter (manually configured)"
    # Otherwise check for any valid coordinates
    elif qt_settings.get('airplay_icon_coords'):
        valid_coords = {
            'airplay_icon_coords': qt_settings['airplay_icon_coords'],
            'apple_tv_coords': qt_settings['apple_tv_coords']
        }
        source = "QuickTimeConverter"
    elif qd_settings.get('airplay_icon_coords') and qd_settings.get('airplay_configured'):
        valid_coords = {
            'airplay_icon_coords': qd_settings['airplay_icon_coords'],
            'apple_tv_coords': qd_settings['apple_tv_coords']
        }
        source = "QuickDrop"
        
    if not valid_coords:
        print("\n❌ No valid coordinates found in either app")
        print("Please run the reset_airplay_coordinates.py script first")
        return
        
    print(f"\n📍 Using coordinates from: {source}")
    print(f"   AirPlay: {valid_coords['airplay_icon_coords']}")
    print(f"   Apple TV: {valid_coords['apple_tv_coords']}")
    
    # Update both settings files
    print("\n🔄 Synchronizing settings...")
    
    # Update QuickTimeConverter
    qt_settings.update(valid_coords)
    with open(qt_settings_file, 'w') as f:
        json.dump(qt_settings, f, indent=2)
    print("✅ Updated QuickTimeConverter settings")
    
    # Update QuickDrop
    qd_settings.update(valid_coords)
    qd_settings['airplay_configured'] = True
    with open(qd_settings_file, 'w') as f:
        json.dump(qd_settings, f, indent=2)
    print("✅ Updated QuickDrop settings")
    
    print("\n✅ Synchronization complete!")
    print("Both apps now use the same AirPlay coordinates")

if __name__ == "__main__":
    sync_settings()