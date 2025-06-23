#!/usr/bin/env python3
"""
Audio AirPlay Template Detector - Robust template matching
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import time
import json
from pathlib import Path


class AudioAirPlayTemplateDetector:
    def __init__(self):
        self.scale_factor = self._get_scale_factor()
        self.debug_dir = Path("audio_template_debug")
        self.debug_dir.mkdir(exist_ok=True)
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
    def _get_scale_factor(self):
        """Get display scale factor"""
        try:
            logical_width, _ = pyautogui.size()
            screenshot = pyautogui.screenshot()
            physical_width = screenshot.width
            return physical_width / logical_width
        except:
            return 2.0
    
    def capture_templates(self):
        """Capture and save template images"""
        print("\n📸 Template Capture Mode")
        print("=" * 50)
        print("\nWe'll capture templates for:")
        print("1. AirPlay button")
        print("2. Apple TV icon/text in the popup")
        
        # Step 1: Capture AirPlay button
        print("\n📍 Step 1: Capture AirPlay Button")
        print("Make sure QuickTime is playing audio and controls are visible")
        input("Press Enter when ready...")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        print("\n👆 Click and drag to select the AirPlay button")
        airplay_template = self._select_roi(screenshot_cv2, "Select AirPlay Button")
        
        if airplay_template is not None:
            cv2.imwrite(str(self.templates_dir / "audio_airplay_button.png"), airplay_template)
            print("✅ AirPlay button template saved")
        
        # Step 2: Capture Apple TV in popup
        print("\n📍 Step 2: Capture Apple TV Option")
        print("I will click the AirPlay button to open the popup")
        
        # Get AirPlay position for clicking
        airplay_pos = self._find_template_in_screenshot(
            screenshot_cv2, 
            airplay_template,
            "Finding AirPlay for clicking"
        )
        
        if airplay_pos:
            print(f"Clicking AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})...")
            pyautogui.click(airplay_pos['x'], airplay_pos['y'])
            time.sleep(2)
            
            # Capture popup
            popup_screenshot = pyautogui.screenshot()
            popup_np = np.array(popup_screenshot)
            popup_cv2 = cv2.cvtColor(popup_np, cv2.COLOR_RGB2BGR)
            
            print("\n👆 Click and drag to select the Apple TV text/icon")
            apple_tv_template = self._select_roi(popup_cv2, "Select Apple TV")
            
            if apple_tv_template is not None:
                cv2.imwrite(str(self.templates_dir / "audio_apple_tv.png"), apple_tv_template)
                print("✅ Apple TV template saved")
            
            # Close popup
            pyautogui.click(100, 100)
        
        print("\n✅ Template capture complete!")
    
    def detect_with_templates(self):
        """Detect using saved templates"""
        print("\n🔍 Template-based Detection")
        print("=" * 50)
        
        # Load templates
        airplay_template_path = self.templates_dir / "audio_airplay_button.png"
        apple_tv_template_path = self.templates_dir / "audio_apple_tv.png"
        
        if not airplay_template_path.exists():
            print("❌ No AirPlay template found. Run capture mode first.")
            return None
        
        airplay_template = cv2.imread(str(airplay_template_path))
        
        # Step 1: Find AirPlay button
        print("\n🔍 Finding AirPlay button...")
        input("Make sure QuickTime audio player is visible. Press Enter...")
        
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        airplay_pos = self._find_template_multi_scale(
            screenshot_cv2,
            airplay_template,
            "AirPlay button"
        )
        
        if not airplay_pos:
            print("❌ Could not find AirPlay button")
            return None
        
        print(f"✅ Found AirPlay at ({airplay_pos['x']}, {airplay_pos['y']}) with {airplay_pos['confidence']:.1%} confidence")
        
        # Step 2: Find Apple TV in popup
        if not apple_tv_template_path.exists():
            print("⚠️  No Apple TV template. Using estimated position.")
            apple_tv_pos = {
                'x': airplay_pos['x'] + 50,
                'y': airplay_pos['y'] + 70
            }
        else:
            print("\n🔍 Finding Apple TV option...")
            print("Clicking AirPlay button...")
            pyautogui.click(airplay_pos['x'], airplay_pos['y'])
            time.sleep(2)
            
            popup_screenshot = pyautogui.screenshot()
            popup_np = np.array(popup_screenshot)
            popup_cv2 = cv2.cvtColor(popup_np, cv2.COLOR_RGB2BGR)
            
            apple_tv_template = cv2.imread(str(apple_tv_template_path))
            apple_tv_result = self._find_template_multi_scale(
                popup_cv2,
                apple_tv_template,
                "Apple TV"
            )
            
            if apple_tv_result:
                # Find the checkbox to the right of the text/icon
                apple_tv_pos = {
                    'x': apple_tv_result['x'] + 150,  # Checkbox is to the right
                    'y': apple_tv_result['y']
                }
                print(f"✅ Found Apple TV, checkbox at ({apple_tv_pos['x']}, {apple_tv_pos['y']})")
            else:
                print("⚠️  Could not find Apple TV. Using estimated position.")
                apple_tv_pos = {
                    'x': airplay_pos['x'] + 50,
                    'y': airplay_pos['y'] + 70
                }
            
            # Close popup
            pyautogui.click(100, 100)
        
        # Save results
        results = {
            'airplay_icon_coords': {'x': airplay_pos['x'], 'y': airplay_pos['y']},
            'apple_tv_coords': apple_tv_pos,
            'detection_method': 'template_matching',
            'confidence': airplay_pos['confidence']
        }
        
        self._save_results(results)
        return results
    
    def _find_template_multi_scale(self, image, template, name):
        """Find template with multiple scales and preprocessing"""
        best_match = None
        best_val = 0
        
        # Try different scales
        scales = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
        
        # Try different preprocessing methods
        methods = [
            ("original", lambda img: img),
            ("grayscale", lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img),
            ("edge", lambda img: cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img, 50, 150)),
            ("blurred", lambda img: cv2.GaussianBlur(img, (5, 5), 0))
        ]
        
        debug_results = []
        
        for method_name, preprocess in methods:
            # Preprocess both images
            proc_image = preprocess(image.copy())
            proc_template = preprocess(template.copy())
            
            # Ensure same number of channels
            if len(proc_image.shape) == 2 and len(proc_template.shape) == 3:
                proc_template = cv2.cvtColor(proc_template, cv2.COLOR_BGR2GRAY)
            elif len(proc_image.shape) == 3 and len(proc_template.shape) == 2:
                proc_image = cv2.cvtColor(proc_image, cv2.COLOR_BGR2GRAY)
            
            for scale in scales:
                # Resize template
                scaled_template = cv2.resize(proc_template, None, fx=scale, fy=scale)
                
                # Skip if template is larger than image
                if (scaled_template.shape[0] > proc_image.shape[0] or 
                    scaled_template.shape[1] > proc_image.shape[1]):
                    continue
                
                # Match template
                result = cv2.matchTemplate(proc_image, scaled_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                debug_results.append({
                    'method': method_name,
                    'scale': scale,
                    'confidence': max_val,
                    'location': max_loc
                })
                
                if max_val > best_val:
                    best_val = max_val
                    h, w = scaled_template.shape[:2]
                    
                    # Calculate center in logical coordinates
                    phys_x = max_loc[0] + w // 2
                    phys_y = max_loc[1] + h // 2
                    
                    best_match = {
                        'x': int(phys_x / self.scale_factor),
                        'y': int(phys_y / self.scale_factor),
                        'confidence': max_val,
                        'scale': scale,
                        'method': method_name,
                        'box': (max_loc[0], max_loc[1], w, h)
                    }
        
        # Save debug info
        self._save_debug_matches(image, template, debug_results, name)
        
        # Lower threshold for audio UI (can be more subtle)
        if best_match and best_match['confidence'] > 0.5:
            return best_match
        
        return None
    
    def _save_debug_matches(self, image, template, results, name):
        """Save debug visualization of all matches"""
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Show top 5 results
        debug_img = image.copy()
        for i, res in enumerate(results[:5]):
            conf = res['confidence']
            color = (0, int(255 * conf), int(255 * (1-conf)))  # Green to red gradient
            
            x, y = res['location']
            cv2.circle(debug_img, (x, y), 20, color, 2)
            cv2.putText(debug_img, f"{i+1}: {conf:.2f}", (x+25, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Add legend
        cv2.putText(debug_img, f"Top matches for {name}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        filename = f"debug_{name.replace(' ', '_').lower()}_matches.png"
        cv2.imwrite(str(self.debug_dir / filename), debug_img)
        
        # Also save best match details
        if results:
            best = results[0]
            print(f"   Best match: {best['method']} @ {best['scale']}x = {best['confidence']:.1%}")
    
    def _find_template_in_screenshot(self, screenshot, template, description):
        """Simple template finding for immediate use"""
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.6:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            return {
                'x': int(center_x / self.scale_factor),
                'y': int(center_y / self.scale_factor)
            }
        return None
    
    def _select_roi(self, image, window_name):
        """Let user select ROI"""
        # Create window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1200, 800)
        
        # Variables for ROI selection
        selecting = False
        start_x, start_y = 0, 0
        end_x, end_y = 0, 0
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal selecting, start_x, start_y, end_x, end_y
            
            if event == cv2.EVENT_LBUTTONDOWN:
                selecting = True
                start_x, start_y = x, y
                end_x, end_y = x, y
                
            elif event == cv2.EVENT_MOUSEMOVE:
                if selecting:
                    end_x, end_y = x, y
                    
            elif event == cv2.EVENT_LBUTTONUP:
                selecting = False
                end_x, end_y = x, y
        
        cv2.setMouseCallback(window_name, mouse_callback)
        
        print("Click and drag to select region. Press SPACE to confirm, ESC to cancel.")
        
        while True:
            display_img = image.copy()
            
            # Draw selection rectangle
            if start_x != end_x and start_y != end_y:
                cv2.rectangle(display_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            
            cv2.imshow(window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Space - confirm selection
                if start_x != end_x and start_y != end_y:
                    # Extract ROI
                    x1, x2 = min(start_x, end_x), max(start_x, end_x)
                    y1, y2 = min(start_y, end_y), max(start_y, end_y)
                    roi = image[y1:y2, x1:x2]
                    cv2.destroyWindow(window_name)
                    return roi
            elif key == 27:  # ESC - cancel
                cv2.destroyWindow(window_name)
                return None
    
    def _save_results(self, results):
        """Save detection results"""
        settings_file = Path.home() / '.audio_template_airplay_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Settings saved to: {settings_file}")


def main():
    print("🎯 Audio AirPlay Template Detector")
    print("Robust template matching for audio playback")
    
    detector = AudioAirPlayTemplateDetector()
    
    print("\nOptions:")
    print("1. Capture new templates")
    print("2. Detect using existing templates")
    print("3. Test saved settings")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == '1':
        detector.capture_templates()
        
        # Ask if user wants to detect now
        detect = input("\nDo you want to detect AirPlay now? (y/n): ")
        if detect.lower() == 'y':
            result = detector.detect_with_templates()
        else:
            result = None
            
    elif choice == '2':
        result = detector.detect_with_templates()
        
    elif choice == '3':
        # Load and test saved settings
        settings_file = Path.home() / '.audio_template_airplay_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                result = json.load(f)
            print(f"\nLoaded settings: {result}")
        else:
            print("❌ No saved settings found")
            result = None
    else:
        print("Invalid choice")
        result = None
    
    # Test if we have results
    if result and choice != '3':
        test = input("\n🧪 Test the detection? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting in 3 seconds...")
            time.sleep(3)
            
            # Click AirPlay
            pyautogui.click(
                result['airplay_icon_coords']['x'],
                result['airplay_icon_coords']['y']
            )
            time.sleep(1.5)
            
            # Click Apple TV
            pyautogui.click(
                result['apple_tv_coords']['x'],
                result['apple_tv_coords']['y']
            )
            
            print("✅ Test complete!")


if __name__ == "__main__":
    main()