#!/usr/bin/env python3
"""
Test coordinate fix for QuickTimeConverterQt
"""

import subprocess
import time
import json
from pathlib import Path

def test_saved_coordinates():
    """Test saved coordinates"""
    print("🔍 Testing Saved Coordinates")
    
    # Load settings
    settings_file = Path.home() / '.quicktime_converter_settings.json'
    if not settings_file.exists():
        print("❌ No saved settings found")
        return
        
    with open(settings_file, 'r') as f:
        settings = json.load(f)
        
    airplay = settings.get('airplay_icon_coords', {})
    appletv = settings.get('apple_tv_coords', {})
    
    print(f"\n📍 Saved coordinates:")
    print(f"   AirPlay: {airplay}")
    print(f"   Apple TV: {appletv}")
    
    # Test AirPlay position
    if airplay and 'x' in airplay and 'y' in airplay:
        print(f"\n🖱️  Moving to AirPlay position ({airplay['x']}, {airplay['y']})...")
        subprocess.run(['cliclick', f"m:{airplay['x']},{airplay['y']}"])
        
        response = input("Is the mouse on the AirPlay icon? (y/n): ")
        if response.lower() != 'y':
            print("❌ AirPlay position is incorrect!")
            
            # Try to find correct position
            print("\n🔧 Let's fix it...")
            from fixed_template_detector import FixedTemplateDetector
            detector = FixedTemplateDetector()
            
            # Activate QuickTime
            detector.activate_quicktime()
            window = detector.get_quicktime_window()
            
            if window:
                detector.show_controls(window)
                result = detector.test_airplay_detection()
                
                if result:
                    # Update settings
                    settings['airplay_icon_coords'] = result
                    settings['apple_tv_coords'] = {
                        'x': result['x'] + 50,
                        'y': result['y'] + 70
                    }
                    
                    with open(settings_file, 'w') as f:
                        json.dump(settings, f, indent=2)
                        
                    print("✅ Settings updated!")
        else:
            print("✅ AirPlay position is correct!")

def test_direct_coordinates():
    """Test coordinate conversion directly"""
    print("\n🔍 Testing Coordinate Conversion")
    
    try:
        from coordinate_converter import CoordinateConverter
        from fixed_template_detector import FixedTemplateDetector
        
        converter = CoordinateConverter()
        print(f"Scale factor: {converter.scale_factor}")
        
        detector = FixedTemplateDetector()
        
        # Make sure QuickTime is ready
        print("\nMake sure QuickTime is open with a video")
        input("Press Enter to continue...")
        
        detector.activate_quicktime()
        window = detector.get_quicktime_window()
        
        if window:
            print(f"Window: {window}")
            
            # Test control position
            print("\n📍 Testing control bar position...")
            detector.show_controls(window)
            
            # Try to find AirPlay
            template = detector.template_dir / "airplay_icon.png"
            if template.exists():
                screenshot = detector.capture_screen()
                result = detector.find_with_correct_coordinates(template, screenshot)
                
                if result:
                    print(f"\n✅ Found AirPlay icon!")
                    print(f"   CV2 coords: {result['cv2_coords']}")
                    print(f"   Screen coords: {result['screen_coords']}")
                    print(f"   Scale used: {result['scale']}")
                    
                    # Move mouse
                    subprocess.run(['cliclick', f"m:{result['screen_coords']['x']},{result['screen_coords']['y']}"])
                    
                    confirm = input("Is the mouse on the AirPlay icon? (y/n): ")
                    if confirm.lower() == 'y':
                        print("✅ Coordinate conversion is working!")
                        return result['screen_coords']
                    else:
                        print("❌ Coordinate conversion still has issues")
                else:
                    print("❌ Could not find AirPlay icon")
            else:
                print(f"❌ Template not found: {template}")
                
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🧪 QuickTime Coordinate Fix Tester")
    print("=" * 50)
    
    print("\n1. Test saved coordinates")
    print("2. Test coordinate conversion")
    print("3. Both tests")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        test_saved_coordinates()
    elif choice == "2":
        test_direct_coordinates()
    elif choice == "3":
        test_saved_coordinates()
        test_direct_coordinates()

if __name__ == "__main__":
    main()