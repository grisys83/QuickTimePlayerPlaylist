#!/usr/bin/env python3
"""
Test QuickDrop settings and AirPlay functionality
"""

import json
from pathlib import Path
import subprocess
import time

def test_settings():
    """Test loading settings"""
    print("🧪 Testing QuickDrop Settings")
    print("=" * 50)
    
    # Check .airplay_templates.json
    templates_file = Path.home() / '.airplay_templates.json'
    if templates_file.exists():
        print("✅ Found .airplay_templates.json")
        with open(templates_file, 'r') as f:
            templates = json.load(f)
            
        if 'airplay_button' in templates:
            pos = templates['airplay_button']['captured_at']
            print(f"  AirPlay button: ({pos['x']}, {pos['y']})")
            
        if 'apple_tv_icon' in templates:
            if 'offsets' in templates['apple_tv_icon'] and 'checkbox' in templates['apple_tv_icon']['offsets']:
                pos = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                print(f"  Checkbox: ({pos['x']}, {pos['y']})")
    else:
        print("❌ No .airplay_templates.json found")
        print("   Run: python3 template_creator_slow.py")
        
    # Check .quickdrop_settings.json
    quickdrop_file = Path.home() / '.quickdrop_settings.json'
    if quickdrop_file.exists():
        print("\n✅ Found .quickdrop_settings.json")
        with open(quickdrop_file, 'r') as f:
            settings = json.load(f)
            print(f"  Settings: {json.dumps(settings, indent=2)}")
    else:
        print("\n⚠️ No .quickdrop_settings.json found")

def test_airplay_simple():
    """Test simple AirPlay activation"""
    print("\n\n🧪 Testing Simple AirPlay")
    print("=" * 50)
    
    # Load coordinates
    templates_file = Path.home() / '.airplay_templates.json'
    if not templates_file.exists():
        print("❌ No templates found")
        return
        
    with open(templates_file, 'r') as f:
        templates = json.load(f)
    
    # Get coordinates
    airplay_pos = None
    checkbox_pos = None
    
    if 'airplay_button' in templates:
        airplay_pos = templates['airplay_button']['captured_at']
        
    if 'apple_tv_icon' in templates and 'offsets' in templates['apple_tv_icon']:
        if 'checkbox' in templates['apple_tv_icon']['offsets']:
            checkbox_pos = templates['apple_tv_icon']['offsets']['checkbox']['absolute']
    
    if not airplay_pos or not checkbox_pos:
        print("❌ Missing coordinates")
        return
    
    print(f"📍 AirPlay: ({airplay_pos['x']}, {airplay_pos['y']})")
    print(f"📍 Checkbox: ({checkbox_pos['x']}, {checkbox_pos['y']})")
    
    # Test with cliclick
    import shutil
    if shutil.which('cliclick'):
        print("\n✅ Using cliclick")
        
        # Activate QuickTime
        print("  Activating QuickTime...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # Show controls
        print("  Showing controls...")
        subprocess.run(['cliclick', f"m:{airplay_pos['x']},{airplay_pos['y'] - 50}"])
        time.sleep(0.5)
        
        # Click AirPlay
        print("  Clicking AirPlay...")
        subprocess.run(['cliclick', f"c:{airplay_pos['x']},{airplay_pos['y']}"])
        time.sleep(1)
        
        # Click checkbox
        print("  Clicking checkbox...")
        subprocess.run(['cliclick', f"c:{checkbox_pos['x']},{checkbox_pos['y']}"])
        
        print("\n✅ Test completed!")
    else:
        print("\n❌ cliclick not found")
        print("   Install: brew install cliclick")

def check_dependencies():
    """Check all dependencies"""
    print("\n\n🧪 Checking Dependencies")
    print("=" * 50)
    
    deps = {
        'PyQt5': False,
        'pyautogui': False,
        'cv2': False,
        'numpy': False,
        'PIL': False
    }
    
    for module in deps:
        try:
            __import__(module)
            deps[module] = True
        except:
            pass
    
    for module, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"{status} {module}")
    
    # Check cliclick
    import shutil
    if shutil.which('cliclick'):
        print("✅ cliclick")
    else:
        print("❌ cliclick (brew install cliclick)")

def main():
    print("🔧 QuickDrop Diagnostic Tool")
    
    check_dependencies()
    test_settings()
    
    print("\n\nTest AirPlay activation? (y/n): ", end='')
    # Auto yes for testing
    print("y")
    test_airplay_simple()

if __name__ == "__main__":
    main()