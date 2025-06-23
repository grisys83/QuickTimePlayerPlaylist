#!/usr/bin/env python3
"""
Test coordinate system differences
"""

import subprocess
import time
import pyautogui
import cv2
import numpy as np
from pathlib import Path

def test_coordinate_systems():
    """Test different coordinate systems"""
    print("🧪 Coordinate System Test")
    print("=" * 50)
    
    # 1. PyAutoGUI coordinates
    logical_width, logical_height = pyautogui.size()
    print(f"\n📐 PyAutoGUI logical size: {logical_width}x{logical_height}")
    
    # 2. Screenshot physical size
    screenshot = pyautogui.screenshot()
    physical_width = screenshot.width
    physical_height = screenshot.height
    print(f"📐 Screenshot physical size: {physical_width}x{physical_height}")
    
    # 3. Scale factor
    scale_factor = physical_width / logical_width
    print(f"📐 Scale factor: {scale_factor}")
    
    # 4. Current mouse position
    mouse_x, mouse_y = pyautogui.position()
    print(f"\n🖱️ PyAutoGUI mouse position: ({mouse_x}, {mouse_y})")
    
    # 5. Test with cliclick
    import shutil
    if shutil.which('cliclick'):
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
        print(f"🖱️ cliclick position: {result.stdout.strip()}")
    
    # 6. Test clicking
    print("\n\n🎯 Click Test")
    print("Move your mouse to a specific location and note the position")
    print("Waiting 5 seconds...")
    
    for i in range(5, 0, -1):
        x, y = pyautogui.position()
        print(f"\r{i}... PyAutoGUI: ({x}, {y})  ", end='', flush=True)
        time.sleep(1)
    
    print(f"\n\nClicking at ({x}, {y}) with different methods:")
    
    # Method 1: PyAutoGUI click
    print("\n1. PyAutoGUI click...")
    pyautogui.click(x, y)
    time.sleep(1)
    
    # Method 2: cliclick with logical coordinates
    if shutil.which('cliclick'):
        print(f"2. cliclick with logical coords ({x}, {y})...")
        subprocess.run(['cliclick', f'c:{x},{y}'])
        time.sleep(1)
        
        # Method 3: cliclick with physical coordinates (wrong!)
        phys_x = int(x * scale_factor)
        phys_y = int(y * scale_factor)
        print(f"3. cliclick with physical coords ({phys_x}, {phys_y}) - This should be wrong!")
        subprocess.run(['cliclick', f'c:{phys_x},{phys_y}'])

def test_template_matching():
    """Test template matching coordinate conversion"""
    print("\n\n🧪 Template Matching Test")
    print("=" * 50)
    
    # Load a template if it exists
    template_path = Path(__file__).parent / "templates" / "airplay_icon.png"
    if not template_path.exists():
        print("❌ No template found")
        return
    
    print(f"✅ Using template: {template_path}")
    
    # Take screenshot
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Load template
    template = cv2.imread(str(template_path))
    
    # Match template
    result = cv2.matchTemplate(screenshot_cv2, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > 0.7:
        h, w = template.shape[:2]
        
        # Physical pixel coordinates from CV2
        phys_x = max_loc[0] + w // 2
        phys_y = max_loc[1] + h // 2
        
        # Logical coordinates for cliclick/pyautogui
        logical_width, _ = pyautogui.size()
        scale_factor = screenshot.width / logical_width
        
        logical_x = phys_x / scale_factor
        logical_y = phys_y / scale_factor
        
        print(f"\n✅ Template found!")
        print(f"   Physical coords (CV2): ({phys_x}, {phys_y})")
        print(f"   Logical coords (cliclick): ({logical_x:.0f}, {logical_y:.0f})")
        print(f"   Scale factor: {scale_factor}")
        
        # Visual feedback
        print("\n📍 Moving mouse to show difference...")
        print("   First to wrong (physical) position...")
        pyautogui.moveTo(phys_x, phys_y, duration=1)
        time.sleep(1)
        
        print("   Now to correct (logical) position...")
        pyautogui.moveTo(logical_x, logical_y, duration=1)
        time.sleep(1)
        
        return {
            'physical': (phys_x, phys_y),
            'logical': (logical_x, logical_y),
            'scale': scale_factor
        }
    else:
        print(f"❌ Template not found (max confidence: {max_val:.2f})")

def main():
    test_coordinate_systems()
    test_template_matching()
    
    print("\n\n📊 Summary:")
    print("- PyAutoGUI uses LOGICAL pixels for mouse position/clicks")
    print("- PyAutoGUI screenshots are in PHYSICAL pixels")
    print("- CV2 template matching returns PHYSICAL pixel coordinates")
    print("- cliclick expects LOGICAL pixel coordinates")
    print("\n✅ Always convert CV2/screenshot coordinates by dividing by scale factor!")

if __name__ == "__main__":
    main()