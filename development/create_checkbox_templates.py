#!/usr/bin/env python3
"""
Helper to create checkbox templates for AirPlay menu
"""

import subprocess
import time
from pathlib import Path

def create_checkbox_templates():
    """Guide user to create checkbox templates"""
    print("📸 Checkbox Template Creator")
    print("=" * 50)
    
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    
    print("\nThis will help you create checkbox templates for the AirPlay menu.")
    print("\nRequired templates:")
    print("1. checkbox_unchecked.png - Empty checkbox □")
    print("2. checkbox_checked.png - Checked checkbox ☑")
    print("3. apple_tv.png - Apple TV text/icon (without checkbox)")
    
    print("\n⚠️  Important: The checkbox is SEPARATE from the Apple TV text!")
    print("The checkbox is typically to the LEFT of the device name.")
    
    print("\nSteps:")
    print("1. Open QuickTime Player with a video")
    print("2. Show controls (move mouse to bottom)")
    print("3. Click the AirPlay icon to open the menu")
    print("4. You should see devices with checkboxes")
    
    input("\nPress Enter when the AirPlay menu is open...")
    
    # Take screenshot
    print("\n📸 Taking screenshot of AirPlay menu...")
    screenshot_path = "/tmp/airplay_menu_full.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    print(f"Screenshot saved to: {screenshot_path}")
    
    print("\nNow use an image editor to:")
    print("1. Crop just the CHECKBOX (not the text) - save as 'checkbox_unchecked.png'")
    print("2. If there's a checked checkbox, crop that too - save as 'checkbox_checked.png'")
    print("3. Crop just the 'Apple TV' text/icon (no checkbox) - save as 'apple_tv.png'")
    print(f"\nSave all templates to: {template_dir}")
    
    print("\n💡 Tips:")
    print("- Make tight crops around each element")
    print("- Include a few pixels of padding")
    print("- Save as PNG with transparency if possible")
    print("- The checkbox is usually a small square to the left of the device name")
    
    # Check which templates exist
    print("\n📁 Current template status:")
    templates = [
        "airplay_icon.png",
        "apple_tv.png", 
        "checkbox_unchecked.png",
        "checkbox_checked.png"
    ]
    
    for template in templates:
        path = template_dir / template
        status = "✅ Exists" if path.exists() else "❌ Missing"
        print(f"   {template}: {status}")

if __name__ == "__main__":
    create_checkbox_templates()