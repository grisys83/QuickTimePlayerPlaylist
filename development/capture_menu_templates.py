#!/usr/bin/env python3
"""
Capture templates from the current AirPlay menu
"""

import cv2
import subprocess
import time
from pathlib import Path

def capture_menu_templates():
    print("📸 AirPlay Menu Template Capture")
    print("=" * 50)
    
    print("\n📋 Instructions:")
    print("1. Open QuickTime with a video")
    print("2. Show controls and click AirPlay to open menu")
    print("3. Make sure 'living' (Apple TV) is visible")
    
    input("\nPress Enter when the AirPlay menu is open...")
    
    # Capture screen
    screenshot_path = "/tmp/menu_capture.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    screenshot = cv2.imread(screenshot_path)
    
    if screenshot is None:
        print("❌ Failed to capture screen")
        return
        
    # Save full menu
    output_dir = Path.home() / "menu_templates"
    output_dir.mkdir(exist_ok=True)
    
    cv2.imwrite(str(output_dir / "full_menu.png"), screenshot)
    print(f"\n💾 Saved full menu to: {output_dir / 'full_menu.png'}")
    
    # Show instructions for manual cropping
    print("\n✂️  Manual Template Creation:")
    print("1. Open the full_menu.png in Preview")
    print("2. Select and crop just the 'living' text")
    print("3. Save as 'living_text.png' in templates/")
    print("4. Also crop the checkbox area (if visible)")
    print("5. Save as 'checkbox_empty.png' in templates/")
    
    print("\n💡 Tips:")
    print("- Crop tightly around the text")
    print("- Include a few pixels of padding")
    print("- Save in PNG format")
    
    print(f"\n📁 Save templates to: {Path(__file__).parent / 'templates'}")


if __name__ == "__main__":
    capture_menu_templates()