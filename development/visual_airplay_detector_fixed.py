#!/usr/bin/env python3
"""
Fixed Visual AirPlay Detector - Properly detects Apple TV after AirPlay click
"""

import cv2
import numpy as np
import pyautogui
import time
import json
from pathlib import Path
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class FixedVisualAirPlayDetector:
    def __init__(self):
        self.debug_dir = Path("airplay_debug_fixed")
        self.debug_dir.mkdir(exist_ok=True)
        self.scale_factor = self._get_scale_factor()
        self.templates_dir = Path("templates")
        self.results = {}
        
    def _get_scale_factor(self):
        """Get display scale factor (for Retina displays)"""
        try:
            logical_width, _ = pyautogui.size()
            screenshot = pyautogui.screenshot()
            physical_width = screenshot.width
            return physical_width / logical_width
        except:
            return 2.0  # Default for Retina
    
    def save_debug_image(self, image, name, annotations=None, description=""):
        """Save debug image with annotations"""
        debug_img = image.copy()
        
        # Add timestamp and description
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(debug_img, f"{name} - {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        if description:
            cv2.putText(debug_img, description, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        if annotations:
            for ann in annotations:
                if ann['type'] == 'rectangle':
                    cv2.rectangle(debug_img, ann['pt1'], ann['pt2'], ann['color'], ann['thickness'])
                elif ann['type'] == 'text':
                    cv2.putText(debug_img, ann['text'], ann['org'], 
                              cv2.FONT_HERSHEY_SIMPLEX, ann.get('fontScale', 0.8), 
                              ann['color'], ann.get('thickness', 2))
                elif ann['type'] == 'circle':
                    cv2.circle(debug_img, ann['center'], ann['radius'], 
                             ann['color'], ann['thickness'])
                elif ann['type'] == 'crosshair':
                    cv2.drawMarker(debug_img, ann['center'], ann['color'], 
                                 cv2.MARKER_CROSS, ann.get('size', 30), ann.get('thickness', 2))
        
        timestamp_full = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = self.debug_dir / f"{name}_{timestamp_full}.png"
        cv2.imwrite(str(filename), debug_img)
        print(f"📸 Saved: {filename.name}")
        return filename
    
    def step1_find_airplay_button(self):
        """Step 1: Find AirPlay button in QuickTime controls"""
        print("\n🎯 Step 1: Finding AirPlay Button")
        print("=" * 50)
        
        if not self.confirm_ready("Is QuickTime Player open with a video?"):
            return None
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        self.save_debug_image(screenshot_cv2, "01_initial_screenshot",
                            description="Starting point")
        
        # Show controls
        print("📍 Moving mouse to show controls...")
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, screen_height - 100, duration=0.5)
        time.sleep(1)
        
        # Take screenshot with controls
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        self.save_debug_image(screenshot_cv2, "02_controls_visible",
                            description="QuickTime controls should be visible")
        
        # Try template matching for AirPlay
        airplay_pos = self._find_airplay_with_template(screenshot_cv2)
        
        if not airplay_pos:
            print("❌ Template matching failed, trying manual selection...")
            airplay_pos = self._manual_select_airplay(screenshot_cv2)
        
        if airplay_pos:
            # Confirm with user
            if self.confirm_location(screenshot_cv2, airplay_pos, "Is this the AirPlay button?"):
                print(f"✅ AirPlay button confirmed at ({airplay_pos['x']}, {airplay_pos['y']})")
                return airplay_pos
        
        return None
    
    def step2_find_apple_tv_in_menu(self, airplay_pos):
        """Step 2: Click AirPlay and find Apple TV in the popup menu"""
        print("\n📺 Step 2: Finding Apple TV in AirPlay Menu")
        print("=" * 50)
        
        # Take screenshot before clicking
        before_click = pyautogui.screenshot()
        before_np = np.array(before_click)
        before_cv2 = cv2.cvtColor(before_np, cv2.COLOR_RGB2BGR)
        
        # Mark where we'll click
        phys_x = int(airplay_pos['x'] * self.scale_factor)
        phys_y = int(airplay_pos['y'] * self.scale_factor)
        
        annotations = [
            {'type': 'circle', 'center': (phys_x, phys_y), 'radius': 20,
             'color': (0, 0, 255), 'thickness': 3},
            {'type': 'text', 'text': 'Clicking here',
             'org': (phys_x - 50, phys_y - 30),
             'color': (0, 0, 255)}
        ]
        self.save_debug_image(before_cv2, "03_before_airplay_click", annotations,
                            "About to click AirPlay button")
        
        # Click AirPlay
        print(f"🖱️ Clicking AirPlay at ({airplay_pos['x']}, {airplay_pos['y']})...")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        time.sleep(1.5)  # Wait for menu
        
        # Take screenshot after clicking
        after_click = pyautogui.screenshot()
        after_np = np.array(after_click)
        after_cv2 = cv2.cvtColor(after_np, cv2.COLOR_RGB2BGR)
        
        self.save_debug_image(after_cv2, "04_after_airplay_click",
                            description="AirPlay menu should be visible")
        
        # Find the difference (popup area)
        diff = cv2.absdiff(before_cv2, after_cv2)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        self.save_debug_image(thresh, "05_menu_difference",
                            description="Difference shows popup menu area")
        
        # Find popup bounds
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            
            # Highlight popup area
            popup_annotated = after_cv2.copy()
            cv2.rectangle(popup_annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(popup_annotated, "Popup Menu", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            self.save_debug_image(popup_annotated, "06_popup_area_detected",
                                description=f"Popup area: {w}x{h} pixels")
            
            # Focus on popup area
            popup_region = after_cv2[y:y+h, x:x+w]
            self.save_debug_image(popup_region, "07_popup_region_only",
                                description="Isolated popup menu")
            
            # Look for Apple TV option
            apple_tv_pos = self._find_apple_tv_in_region(popup_region, x, y)
            
            if apple_tv_pos:
                # Show full screen with Apple TV location
                full_annotated = after_cv2.copy()
                tv_phys_x = int(apple_tv_pos['x'] * self.scale_factor)
                tv_phys_y = int(apple_tv_pos['y'] * self.scale_factor)
                
                cv2.circle(full_annotated, (tv_phys_x, tv_phys_y), 25, (0, 255, 0), 3)
                cv2.putText(full_annotated, "Apple TV", (tv_phys_x - 40, tv_phys_y - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                self.save_debug_image(full_annotated, "08_apple_tv_found",
                                    description="Apple TV option located")
                
                if self.confirm_location(after_cv2, apple_tv_pos, "Is this the Apple TV checkbox?"):
                    return apple_tv_pos
        
        # Manual selection fallback
        print("\n❌ Could not find Apple TV automatically")
        print("👆 Please click on the Apple TV checkbox in the menu...")
        
        # Let user see the menu
        time.sleep(0.5)
        
        # Manual selection with menu still open
        apple_tv_pos = self._manual_select_apple_tv(after_cv2)
        
        # Close menu
        pyautogui.click(100, 100)
        
        return apple_tv_pos
    
    def _find_airplay_with_template(self, screenshot):
        """Find AirPlay button using template"""
        template_path = self.templates_dir / "airplay_icon.png"
        if not template_path.exists():
            print("❌ No AirPlay template found")
            return None
        
        template = cv2.imread(str(template_path))
        
        # Try multiple scales
        best_match = None
        best_val = 0
        
        for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
            scaled = cv2.resize(template, None, fx=scale, fy=scale)
            result = cv2.matchTemplate(screenshot, scaled, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                h, w = scaled.shape[:2]
                best_match = {
                    'loc': max_loc,
                    'size': (w, h),
                    'confidence': max_val,
                    'scale': scale
                }
        
        if best_match and best_val > 0.6:
            loc = best_match['loc']
            w, h = best_match['size']
            
            # Physical center
            phys_x = loc[0] + w // 2
            phys_y = loc[1] + h // 2
            
            # Logical coordinates
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            print(f"✅ Found AirPlay with {best_val:.1%} confidence")
            return {'x': logical_x, 'y': logical_y}
        
        return None
    
    def _find_apple_tv_in_region(self, popup_region, offset_x, offset_y):
        """Find Apple TV option in the popup region"""
        # Convert to grayscale
        gray = cv2.cvtColor(popup_region, cv2.COLOR_BGR2GRAY)
        
        # Look for checkbox patterns (usually square)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        annotated = popup_region.copy()
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 1000:  # Checkbox size range
                x, y, w, h = cv2.boundingRect(contour)
                aspect = w / h if h > 0 else 0
                
                # Square-ish shape
                if 0.7 < aspect < 1.3:
                    candidates.append({
                        'x': x + w//2,
                        'y': y + h//2,
                        'area': area,
                        'bounds': (x, y, w, h)
                    })
                    
                    cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if candidates:
            self.save_debug_image(annotated, "09_checkbox_candidates",
                                description=f"Found {len(candidates)} checkbox candidates")
            
            # Usually the first or most prominent checkbox
            best = candidates[0]
            
            # Convert to full image coordinates
            full_x = offset_x + best['x']
            full_y = offset_y + best['y']
            
            # Convert to logical
            logical_x = int(full_x / self.scale_factor)
            logical_y = int(full_y / self.scale_factor)
            
            return {'x': logical_x, 'y': logical_y}
        
        # Try default offset from AirPlay button
        # Apple TV is usually below and to the right
        return None
    
    def _manual_select_airplay(self, screenshot):
        """Manual selection for AirPlay button"""
        return self._manual_selection(screenshot, "Select AirPlay Button", 
                                    "Click on the AirPlay button (triangle with rectangle)")
    
    def _manual_select_apple_tv(self, screenshot):
        """Manual selection for Apple TV checkbox"""
        return self._manual_selection(screenshot, "Select Apple TV Checkbox",
                                    "Click on the Apple TV checkbox in the menu")
    
    def _manual_selection(self, screenshot, title, instruction):
        """Generic manual selection interface"""
        print(f"\n👆 Manual selection: {instruction}")
        
        # Create window
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 1200, 800)
        
        # Scale image if needed
        height, width = screenshot.shape[:2]
        max_width, max_height = 1400, 900
        scale = min(max_width/width, max_height/height, 1.0)
        
        if scale < 1.0:
            display = cv2.resize(screenshot, None, fx=scale, fy=scale)
        else:
            display = screenshot.copy()
            scale = 1.0
        
        clicked_pos = None
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal clicked_pos
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convert back to original coordinates
                clicked_pos = (int(x/scale), int(y/scale))
                cv2.destroyAllWindows()
        
        cv2.setMouseCallback(title, mouse_callback)
        
        # Add instructions
        cv2.putText(display, instruction, (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display, "Press ESC to cancel", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        cv2.imshow(title, display)
        
        print("Waiting for click...")
        while clicked_pos is None:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                cv2.destroyAllWindows()
                return None
        
        if clicked_pos:
            phys_x, phys_y = clicked_pos
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            print(f"✅ Selected: ({logical_x}, {logical_y})")
            return {'x': logical_x, 'y': logical_y}
        
        return None
    
    def confirm_ready(self, message):
        """Simple confirmation dialog"""
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno("Ready?", message)
        root.destroy()
        return result
    
    def confirm_location(self, screenshot, coords, message):
        """Show location for confirmation"""
        # Create window
        root = tk.Tk()
        root.title("Confirm Location")
        
        # Get region around coordinates
        phys_x = int(coords['x'] * self.scale_factor)
        phys_y = int(coords['y'] * self.scale_factor)
        
        # Crop region
        size = 200
        x1 = max(0, phys_x - size)
        y1 = max(0, phys_y - size)
        x2 = min(screenshot.shape[1], phys_x + size)
        y2 = min(screenshot.shape[0], phys_y + size)
        
        region = screenshot[y1:y2, x1:x2].copy()
        
        # Mark the center
        center_x = phys_x - x1
        center_y = phys_y - y1
        cv2.circle(region, (center_x, center_y), 20, (0, 255, 0), 3)
        cv2.drawMarker(region, (center_x, center_y), (255, 0, 0), cv2.MARKER_CROSS, 40, 2)
        
        # Convert for display
        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(region_rgb)
        
        # Resize if needed
        if pil_image.width > 400:
            pil_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(pil_image)
        
        # Create GUI
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()
        
        tk.Label(frame, text=message).pack()
        tk.Label(frame, text=f"Location: ({coords['x']}, {coords['y']})").pack()
        tk.Label(frame, image=photo).pack(pady=10)
        
        result = [False]
        
        def on_yes():
            result[0] = True
            root.destroy()
        
        def on_no():
            result[0] = False
            root.destroy()
        
        button_frame = tk.Frame(frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="Yes", command=on_yes, 
                 bg="green", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="No", command=on_no,
                 bg="red", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop()
        return result[0]
    
    def run(self):
        """Run the complete detection process"""
        print("🎯 Fixed Visual AirPlay Detector")
        print("=" * 50)
        print("This version properly detects:")
        print("1. AirPlay button in QuickTime controls")
        print("2. Apple TV checkbox in the AirPlay menu")
        print("=" * 50)
        
        # Step 1: Find AirPlay button
        airplay_pos = self.step1_find_airplay_button()
        if not airplay_pos:
            print("\n❌ Failed to find AirPlay button")
            return False
        
        # Step 2: Find Apple TV in menu
        apple_tv_pos = self.step2_find_apple_tv_in_menu(airplay_pos)
        if not apple_tv_pos:
            print("\n❌ Failed to find Apple TV checkbox")
            return False
        
        # Save results
        self.results = {
            'airplay_button': airplay_pos,
            'apple_tv_checkbox': apple_tv_pos
        }
        
        # Save to files
        results_file = Path("airplay_detection_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
        # Update templates
        templates = {
            'airplay_button': {
                'captured_at': airplay_pos
            },
            'apple_tv_icon': {
                'offsets': {
                    'checkbox': {
                        'absolute': apple_tv_pos
                    }
                }
            }
        }
        
        templates_file = Path.home() / '.airplay_templates.json'
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        print(f"💾 Templates saved to: {templates_file}")
        
        print("\n✅ Detection complete!")
        print(f"AirPlay button: ({airplay_pos['x']}, {airplay_pos['y']})")
        print(f"Apple TV checkbox: ({apple_tv_pos['x']}, {apple_tv_pos['y']})")
        
        # Test option
        test = input("\n🧪 Test these coordinates? (y/n): ")
        if test.lower() == 'y':
            self.test_coordinates(airplay_pos, apple_tv_pos)
        
        return True
    
    def test_coordinates(self, airplay_pos, apple_tv_pos):
        """Test the detected coordinates"""
        print("\n🧪 Testing coordinates...")
        
        # Activate QuickTime
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # Show controls
        print("Showing controls...")
        pyautogui.moveTo(airplay_pos['x'], airplay_pos['y'] - 50, duration=0.5)
        time.sleep(1)
        
        # Click AirPlay
        print("Clicking AirPlay...")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        time.sleep(1.5)
        
        # Click Apple TV
        print("Clicking Apple TV...")
        pyautogui.click(apple_tv_pos['x'], apple_tv_pos['y'])
        
        print("✅ Test complete!")


def main():
    detector = FixedVisualAirPlayDetector()
    
    if detector.run():
        print("\n🎉 Success! Your AirPlay automation is ready.")
        print("\nThe coordinates have been saved and can be used with:")
        print("• QuickDrop")
        print("• QuickTime Playlist tools")
        print("• Any other AirPlay automation")
    else:
        print("\n😕 Detection failed.")
        print("Check the debug images in 'airplay_debug_fixed' folder")


if __name__ == "__main__":
    main()