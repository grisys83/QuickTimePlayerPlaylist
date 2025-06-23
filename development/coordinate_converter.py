#!/usr/bin/env python3
"""
Convert between CV2 coordinates and macOS screen coordinates
"""

import subprocess
import cv2
import Quartz
from AppKit import NSScreen

class CoordinateConverter:
    def __init__(self):
        self.scale_factor = self.get_scale_factor()
        self.screen_info = self.get_screen_info()
        print(f"🖥️  Display scale factor: {self.scale_factor}")
        print(f"📐 Screen resolution: {self.screen_info['logical_width']}x{self.screen_info['logical_height']} (logical)")
        print(f"📸 Screenshot resolution: {self.screen_info['physical_width']}x{self.screen_info['physical_height']} (physical)")
        
    def get_scale_factor(self):
        """Get the display scale factor (1x, 2x, 3x for Retina)"""
        main_screen = NSScreen.mainScreen()
        if main_screen:
            return main_screen.backingScaleFactor()
        return 1.0
    
    def get_screen_info(self):
        """Get screen dimensions"""
        # Logical resolution (what macOS uses for coordinates)
        logical_width = Quartz.CGDisplayPixelsWide(0)
        logical_height = Quartz.CGDisplayPixelsHigh(0)
        
        # Physical resolution (what screenshots capture)
        main_screen = NSScreen.mainScreen()
        if main_screen:
            frame = main_screen.frame()
            physical_width = frame.size.width * self.scale_factor
            physical_height = frame.size.height * self.scale_factor
        else:
            physical_width = logical_width
            physical_height = logical_height
            
        return {
            'logical_width': logical_width,
            'logical_height': logical_height,
            'physical_width': int(physical_width),
            'physical_height': int(physical_height),
            'scale': self.scale_factor
        }
    
    def cv2_to_screen(self, cv2_x, cv2_y):
        """Convert CV2 coordinates to screen coordinates for cliclick"""
        # CV2 uses physical pixels, cliclick uses logical pixels
        screen_x = cv2_x / self.scale_factor
        screen_y = cv2_y / self.scale_factor
        
        return int(screen_x), int(screen_y)
    
    def screen_to_cv2(self, screen_x, screen_y):
        """Convert screen coordinates to CV2 coordinates"""
        cv2_x = screen_x * self.scale_factor
        cv2_y = screen_y * self.scale_factor
        
        return int(cv2_x), int(cv2_y)
    
    def test_coordinate_mapping(self):
        """Test the coordinate mapping"""
        print("\n🧪 Testing coordinate conversion...")
        
        # Take a screenshot
        screenshot_path = "/tmp/coord_test.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        
        print(f"📸 Screenshot size (CV2): {screenshot.shape[1]}x{screenshot.shape[0]}")
        print(f"🖥️  Screen size (logical): {self.screen_info['logical_width']}x{self.screen_info['logical_height']}")
        print(f"📏 Scale factor: {self.scale_factor}")
        
        # Test conversions
        test_points = [
            (100, 100, "Top-left area"),
            (screenshot.shape[1]//2, screenshot.shape[0]//2, "Center"),
            (screenshot.shape[1]-100, screenshot.shape[0]-100, "Bottom-right area")
        ]
        
        for cv2_x, cv2_y, name in test_points:
            screen_x, screen_y = self.cv2_to_screen(cv2_x, cv2_y)
            print(f"\n📍 {name}:")
            print(f"   CV2: ({cv2_x}, {cv2_y})")
            print(f"   Screen: ({screen_x}, {screen_y})")
            
            # Move mouse to show the position
            print(f"   Moving mouse to screen position...")
            subprocess.run(['cliclick', f'm:{screen_x},{screen_y}'])
            
            response = input("   Is the mouse in the correct position? (y/n): ")
            if response.lower() != 'y':
                print("   ❌ Coordinate conversion may need adjustment")
    
    def debug_quicktime_coordinates(self):
        """Debug QuickTime specific coordinates"""
        print("\n🎯 QuickTime Coordinate Debug")
        
        # Get QuickTime window
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    return (item 1 of windowPos as string) & "," & ¬
                           (item 2 of windowPos as string) & "," & ¬
                           (item 1 of windowSize as string) & "," & ¬
                           (item 2 of windowSize as string)
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if not result.stdout.strip():
            print("QuickTime not found")
            return
            
        coords = result.stdout.strip().split(',')
        window = {
            'x': int(coords[0]),
            'y': int(coords[1]),
            'width': int(coords[2]),
            'height': int(coords[3])
        }
        
        print(f"📺 QuickTime window (logical): {window}")
        
        # Take screenshot and find window in CV2 coordinates
        screenshot_path = "/tmp/qt_debug.png"
        subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        
        # Convert window coords to CV2
        cv2_x, cv2_y = self.screen_to_cv2(window['x'], window['y'])
        cv2_w, cv2_h = self.screen_to_cv2(window['width'], window['height'])
        
        print(f"📸 QuickTime in CV2 coords: x={cv2_x}, y={cv2_y}, w={cv2_w}, h={cv2_h}")
        
        # Draw rectangle on screenshot
        cv2.rectangle(screenshot, (cv2_x, cv2_y), (cv2_x + cv2_w, cv2_y + cv2_h), (0, 255, 0), 3)
        cv2.imwrite("/tmp/qt_window_marked.png", screenshot)
        print("✅ Saved marked screenshot to /tmp/qt_window_marked.png")
        
        subprocess.run(["rm", screenshot_path])


# Updated template detector with coordinate conversion
class CorrectedTemplateDetector:
    def __init__(self):
        self.converter = CoordinateConverter()
        
    def find_and_click(self, template_path, screenshot=None):
        """Find template and click with correct coordinates"""
        if screenshot is None:
            screenshot_path = "/tmp/screenshot.png"
            subprocess.run(["screencapture", "-x", screenshot_path], capture_output=True)
            screenshot = cv2.imread(screenshot_path)
            subprocess.run(["rm", screenshot_path])
        
        # Find template in CV2 coordinates
        template = cv2.imread(str(template_path))
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.7:
            # Calculate center in CV2 coordinates
            cv2_x = max_loc[0] + template.shape[1] // 2
            cv2_y = max_loc[1] + template.shape[0] // 2
            
            # Convert to screen coordinates
            screen_x, screen_y = self.converter.cv2_to_screen(cv2_x, cv2_y)
            
            print(f"✅ Found template:")
            print(f"   CV2 coords: ({cv2_x}, {cv2_y})")
            print(f"   Screen coords: ({screen_x}, {screen_y})")
            
            # Click using screen coordinates
            subprocess.run(['cliclick', f'c:{screen_x},{screen_y}'])
            return True
            
        return False


def main():
    print("🔧 Coordinate System Debugger")
    print("This will help identify coordinate conversion issues")
    
    converter = CoordinateConverter()
    
    print("\n1. Test basic coordinate mapping")
    print("2. Debug QuickTime coordinates")
    print("3. Test with actual template")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        converter.test_coordinate_mapping()
    elif choice == "2":
        converter.debug_quicktime_coordinates()
    elif choice == "3":
        detector = CorrectedTemplateDetector()
        template_path = input("Enter template path: ")
        if detector.find_and_click(template_path):
            print("✅ Successfully found and clicked!")
        else:
            print("❌ Template not found")


if __name__ == "__main__":
    main()