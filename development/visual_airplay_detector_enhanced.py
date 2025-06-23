#!/usr/bin/env python3
"""
Enhanced Visual AirPlay Detector - Interactive detection with extensive visual feedback
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
import threading

class EnhancedVisualAirPlayDetector:
    def __init__(self):
        self.debug_dir = Path("airplay_debug_enhanced")
        self.debug_dir.mkdir(exist_ok=True)
        self.scale_factor = self._get_scale_factor()
        self.templates_dir = Path("templates")
        self.results = {}
        self.debug_images = []  # Store debug images for review
        self.confirmation_window = None
        
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
        
        # Add timestamp and description to image
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
                              cv2.FONT_HERSHEY_SIMPLEX, ann['fontScale'], 
                              ann['color'], ann['thickness'])
                elif ann['type'] == 'circle':
                    cv2.circle(debug_img, ann['center'], ann['radius'], 
                             ann['color'], ann['thickness'])
                elif ann['type'] == 'arrow':
                    cv2.arrowedLine(debug_img, ann['pt1'], ann['pt2'], 
                                  ann['color'], ann['thickness'])
                elif ann['type'] == 'crosshair':
                    cv2.drawMarker(debug_img, ann['center'], ann['color'], 
                                 cv2.MARKER_CROSS, ann['size'], ann['thickness'])
        
        timestamp_full = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = self.debug_dir / f"{name}_{timestamp_full}.png"
        cv2.imwrite(str(filename), debug_img)
        
        # Store for later review
        self.debug_images.append({
            'filename': filename,
            'name': name,
            'description': description,
            'image': debug_img,
            'timestamp': timestamp
        })
        
        print(f"📸 Saved debug image: {filename.name}")
        return filename
    
    def capture_screen_region(self, x, y, width, height):
        """Capture specific region of screen"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot_np = np.array(screenshot)
        return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    def highlight_region_on_screen(self, x, y, width, height, duration=1):
        """Visually highlight a region on screen (shows in debug image)"""
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Convert logical to physical coordinates for annotation
        phys_x = int(x * self.scale_factor)
        phys_y = int(y * self.scale_factor)
        phys_width = int(width * self.scale_factor)
        phys_height = int(height * self.scale_factor)
        
        annotations = [
            {'type': 'rectangle', 
             'pt1': (phys_x, phys_y), 
             'pt2': (phys_x + phys_width, phys_y + phys_height),
             'color': (0, 255, 255), 'thickness': 4},
            {'type': 'text', 
             'text': f'Search Area ({x}, {y}) {width}x{height}',
             'org': (phys_x, phys_y - 10),
             'fontScale': 1, 'color': (0, 255, 255), 'thickness': 2}
        ]
        
        self.save_debug_image(screenshot_cv2, "highlighted_region", annotations,
                            f"Searching in this region")
        
    def detect_airplay_button(self):
        """Detect AirPlay button with visual feedback"""
        print("\n🔍 Detecting AirPlay button...")
        print("Please make sure QuickTime Player is open with a video loaded")
        
        # User confirmation
        if not self.confirm_ready("Is QuickTime Player open with a video?"):
            return None
            
        time.sleep(1)
        
        # Take initial screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Save original screenshot
        self.save_debug_image(screenshot_cv2, "01_original_screenshot", 
                            description="Full desktop screenshot")
        
        # Try to find QuickTime window
        qt_window = self._find_quicktime_window()
        if qt_window:
            # Highlight QuickTime window
            annotations = [
                {'type': 'rectangle',
                 'pt1': (qt_window['x'], qt_window['y']),
                 'pt2': (qt_window['x'] + qt_window['width'], 
                        qt_window['y'] + qt_window['height']),
                 'color': (0, 255, 0), 'thickness': 3},
                {'type': 'text',
                 'text': 'QuickTime Window',
                 'org': (qt_window['x'], qt_window['y'] - 10),
                 'fontScale': 1, 'color': (0, 255, 0), 'thickness': 2}
            ]
            self.save_debug_image(screenshot_cv2, "02_quicktime_window", annotations,
                                "QuickTime window detected")
        
        # Move mouse to show controls
        if qt_window:
            center_x = qt_window['x'] + qt_window['width'] // 2
            bottom_y = qt_window['y'] + qt_window['height'] - 50
            
            print("\n📍 Moving mouse to show controls...")
            pyautogui.moveTo(center_x, bottom_y, duration=0.5)
            time.sleep(1)
            
            # Take screenshot with controls visible
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            self.save_debug_image(screenshot_cv2, "03_controls_visible",
                                description="Controls should be visible now")
        
        # Try multiple detection methods
        methods = [
            ("Template Matching", self._detect_by_template),
            ("Color Detection", self._detect_by_color),
            ("Shape Detection", self._detect_by_shape)
        ]
        
        for method_name, method in methods:
            print(f"\n🔄 Trying {method_name}...")
            result = method(screenshot_cv2)
            if result:
                # Show detection result for confirmation
                if self.confirm_detection(screenshot_cv2, result, f"AirPlay button detected by {method_name}"):
                    return result
                else:
                    print(f"   User rejected {method_name} result, trying next method...")
        
        print("❌ Could not detect AirPlay button automatically")
        return self._manual_selection(screenshot_cv2)
    
    def _find_quicktime_window(self):
        """Find QuickTime window bounds"""
        try:
            # Use AppleScript to get window bounds
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
            if result.stdout.strip():
                coords = result.stdout.strip().split(',')
                return {
                    'x': int(coords[0]),
                    'y': int(coords[1]),
                    'width': int(coords[2]),
                    'height': int(coords[3])
                }
        except:
            pass
        return None
    
    def _detect_by_template(self, screenshot):
        """Detect using template matching"""
        print("  📋 Trying template matching...")
        
        # Look for existing templates
        template_files = list(self.templates_dir.glob("airplay*.png"))
        
        if not template_files:
            print("  ❌ No template files found")
            return None
        
        best_match = None
        best_confidence = 0
        all_matches = []
        
        for template_file in template_files:
            template = cv2.imread(str(template_file))
            if template is None:
                continue
            
            print(f"    Testing template: {template_file.name}")
            
            # Try multiple scales
            scales = [0.8, 0.9, 1.0, 1.1, 1.2]
            
            for scale in scales:
                scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
                result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > 0.5:  # Lower threshold for more matches
                    h, w = scaled_template.shape[:2]
                    match_info = {
                        'location': max_loc,
                        'size': (w, h),
                        'confidence': max_val,
                        'template': template_file.name,
                        'scale': scale
                    }
                    all_matches.append(match_info)
                    
                    if max_val > best_confidence:
                        best_confidence = max_val
                        best_match = match_info
        
        # Save debug image with all matches
        if all_matches:
            annotated = screenshot.copy()
            for i, match in enumerate(all_matches):
                loc = match['location']
                w, h = match['size']
                color = (0, 255, 0) if match == best_match else (0, 255, 255)
                
                cv2.rectangle(annotated, loc, (loc[0] + w, loc[1] + h), color, 2)
                cv2.putText(annotated, f"{match['confidence']:.2f}", 
                           (loc[0], loc[1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            self.save_debug_image(annotated, "04_template_matches",
                                description=f"Found {len(all_matches)} potential matches")
        
        if best_match and best_confidence > 0.6:
            loc = best_match['location']
            w, h = best_match['size']
            
            # Physical coordinates
            phys_x = loc[0] + w // 2
            phys_y = loc[1] + h // 2
            
            # Convert to logical
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            # Save best match detail
            detail_img = screenshot.copy()
            annotations = [
                {'type': 'rectangle', 'pt1': loc, 
                 'pt2': (loc[0] + w, loc[1] + h),
                 'color': (0, 255, 0), 'thickness': 3},
                {'type': 'crosshair', 'center': (phys_x, phys_y),
                 'color': (255, 0, 0), 'size': 30, 'thickness': 2},
                {'type': 'text', 'text': f'Best Match: {best_confidence:.2%}',
                 'org': (loc[0], loc[1] - 10),
                 'fontScale': 0.8, 'color': (0, 255, 0), 'thickness': 2}
            ]
            self.save_debug_image(detail_img, "05_best_template_match", annotations,
                                f"Template: {best_match['template']}, Scale: {best_match['scale']}")
            
            print(f"  ✅ Found AirPlay button at ({logical_x}, {logical_y}) with confidence {best_confidence:.2f}")
            return {'x': logical_x, 'y': logical_y, 'confidence': best_confidence}
        
        print(f"  ❌ No good template match (best: {best_confidence:.2f})")
        return None
    
    def _detect_by_color(self, screenshot):
        """Detect by looking for blue AirPlay icon color"""
        print("  🎨 Trying color detection...")
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Multiple blue color ranges to try
        color_ranges = [
            {"name": "Standard_Blue", "lower": [100, 50, 50], "upper": [130, 255, 255]},
            {"name": "Light_Blue", "lower": [90, 30, 100], "upper": [120, 255, 255]},
            {"name": "Dark_Blue", "lower": [105, 100, 20], "upper": [125, 255, 200]},
            {"name": "Cyan_Blue", "lower": [85, 50, 50], "upper": [95, 255, 255]}
        ]
        
        best_candidate = None
        all_candidates = []
        
        for idx, color_range in enumerate(color_ranges):
            lower = np.array(color_range["lower"])
            upper = np.array(color_range["upper"])
            
            # Create mask
            mask = cv2.inRange(hsv, lower, upper)
            
            # Apply morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Save mask for debugging
            self.save_debug_image(mask, f"06_color_mask_{idx}_{color_range['name']}",
                                description=f"Color mask for {color_range['name']}")
            
            # Look for button-like contours
            annotated = screenshot.copy()
            range_candidates = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 5000:  # Reasonable size for button
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # AirPlay button characteristics
                    if 0.5 < aspect_ratio < 3.0:
                        # Calculate circularity
                        perimeter = cv2.arcLength(contour, True)
                        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                        
                        candidate = {
                            'x': x + w//2,
                            'y': y + h//2,
                            'area': area,
                            'rect': (x, y, w, h),
                            'aspect': aspect_ratio,
                            'circularity': circularity,
                            'color_range': color_range['name']
                        }
                        range_candidates.append(candidate)
                        all_candidates.append(candidate)
                        
                        # Draw candidate on annotated image
                        cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(annotated, f"A:{area:.0f}", (x, y-5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            if range_candidates:
                # Save candidates image
                self.save_debug_image(annotated, f"07_color_candidates_{idx}_{color_range['name']}",
                                    description=f"Found {len(range_candidates)} candidates")
                
                # Sort by score (combination of area and shape)
                for c in range_candidates:
                    c['score'] = c['area'] * (1 - abs(c['aspect'] - 1.5) * 0.3) * c['circularity']
                
                range_candidates.sort(key=lambda x: x['score'], reverse=True)
                
                if not best_candidate or range_candidates[0]['score'] > best_candidate['score']:
                    best_candidate = range_candidates[0]
        
        # Show all candidates
        if all_candidates:
            all_annotated = screenshot.copy()
            for i, cand in enumerate(sorted(all_candidates, key=lambda x: x.get('score', 0), reverse=True)[:10]):
                x, y, w, h = cand['rect']
                color = (0, 255, 0) if cand == best_candidate else (0, 200, 200)
                cv2.rectangle(all_annotated, (x, y), (x+w, y+h), color, 2)
                cv2.putText(all_annotated, f"{i+1}", (x+w//2-10, y+h//2),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            self.save_debug_image(all_annotated, "08_all_color_candidates",
                                description=f"Top {min(10, len(all_candidates))} candidates by score")
        
        if best_candidate:
            phys_x = best_candidate['x']
            phys_y = best_candidate['y']
            
            # Convert to logical
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            # Final annotated image
            final_annotated = screenshot.copy()
            x, y, w, h = best_candidate['rect']
            cv2.rectangle(final_annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.circle(final_annotated, (phys_x, phys_y), 25, (0, 255, 0), 3)
            cv2.putText(final_annotated, "AirPlay?", (phys_x - 30, phys_y - 30),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            info_text = f"Area: {best_candidate['area']:.0f}, Aspect: {best_candidate['aspect']:.2f}"
            cv2.putText(final_annotated, info_text, (x, y + h + 20),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            self.save_debug_image(final_annotated, "09_color_detection_result",
                                description=f"Best candidate from {best_candidate['color_range']}")
            
            print(f"  ✅ Found potential AirPlay button at ({logical_x}, {logical_y})")
            return {'x': logical_x, 'y': logical_y, 'confidence': 0.6}
        
        print("  ❌ No suitable color candidates found")
        return None
    
    def _detect_by_shape(self, screenshot):
        """Detect by looking for specific shapes"""
        print("  🔷 Trying shape detection...")
        
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        self.save_debug_image(edges, "10_edge_detection", description="Canny edge detection")
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        annotated = screenshot.copy()
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:
                # Approximate polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Look for triangular or rectangular shapes
                if 3 <= len(approx) <= 8 and 0.5 < aspect_ratio < 3.0:
                    candidates.append({
                        'x': x + w//2,
                        'y': y + h//2,
                        'area': area,
                        'vertices': len(approx),
                        'rect': (x, y, w, h)
                    })
                    
                    # Draw on annotated image
                    cv2.drawContours(annotated, [approx], -1, (0, 255, 0), 2)
                    cv2.putText(annotated, f"V:{len(approx)}", (x, y-5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        if candidates:
            self.save_debug_image(annotated, "11_shape_candidates",
                                description=f"Found {len(candidates)} shape candidates")
            
            # Sort by area
            candidates.sort(key=lambda x: x['area'], reverse=True)
            best = candidates[0]
            
            phys_x = best['x']
            phys_y = best['y']
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            print(f"  ✅ Found potential AirPlay button at ({logical_x}, {logical_y})")
            return {'x': logical_x, 'y': logical_y, 'confidence': 0.5}
        
        print("  ❌ No suitable shape candidates found")
        return None
    
    def _manual_selection(self, screenshot):
        """Allow manual selection of AirPlay button"""
        print("\n👆 Manual selection mode")
        print("Click on the AirPlay button in the window that will open...")
        
        # Scale down screenshot for display if needed
        height, width = screenshot.shape[:2]
        max_display_width = 1400
        max_display_height = 900
        
        scale = min(max_display_width / width, max_display_height / height, 1.0)
        if scale < 1.0:
            display_img = cv2.resize(screenshot, None, fx=scale, fy=scale)
        else:
            display_img = screenshot.copy()
            scale = 1.0
        
        # Create window for selection
        cv2.namedWindow('Select AirPlay Button', cv2.WINDOW_NORMAL)
        
        clicked_pos = None
        hover_pos = None
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal clicked_pos, hover_pos
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convert display coordinates back to original
                clicked_pos = (int(x / scale), int(y / scale))
                cv2.destroyAllWindows()
            elif event == cv2.EVENT_MOUSEMOVE:
                hover_pos = (x, y)
        
        cv2.setMouseCallback('Select AirPlay Button', mouse_callback)
        
        # Add instructions on image
        instructions = display_img.copy()
        cv2.putText(instructions, "Click on the AirPlay button", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(instructions, "Press ESC to cancel", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Add visual hints
        cv2.putText(instructions, "AirPlay icon looks like: [>]", (50, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(instructions, "Usually on the right side of controls", (50, 180),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        print("Waiting for click...")
        while clicked_pos is None:
            # Show image with crosshair at mouse position
            display_with_cursor = instructions.copy()
            if hover_pos:
                cv2.drawMarker(display_with_cursor, hover_pos, (255, 0, 0), 
                             cv2.MARKER_CROSS, 30, 2)
                # Show coordinates
                cv2.putText(display_with_cursor, f"({int(hover_pos[0]/scale)}, {int(hover_pos[1]/scale)})", 
                           (hover_pos[0] + 10, hover_pos[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            cv2.imshow('Select AirPlay Button', display_with_cursor)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to cancel
                cv2.destroyAllWindows()
                print("❌ Selection cancelled")
                return None
        
        if clicked_pos:
            phys_x, phys_y = clicked_pos
            logical_x = int(phys_x / self.scale_factor)
            logical_y = int(phys_y / self.scale_factor)
            
            # Save annotated image
            annotations = [
                {'type': 'circle', 'center': clicked_pos, 'radius': 30,
                 'color': (0, 255, 0), 'thickness': 3},
                {'type': 'crosshair', 'center': clicked_pos,
                 'color': (255, 0, 0), 'size': 50, 'thickness': 2},
                {'type': 'text', 'text': 'User Selected AirPlay',
                 'org': (clicked_pos[0] - 80, clicked_pos[1] - 40),
                 'fontScale': 1, 'color': (0, 255, 0), 'thickness': 2},
                {'type': 'arrow', 'pt1': (clicked_pos[0] - 100, clicked_pos[1] - 100),
                 'pt2': clicked_pos, 'color': (0, 255, 0), 'thickness': 3}
            ]
            self.save_debug_image(screenshot, "12_manual_selection", annotations,
                                description="User manually selected AirPlay button location")
            
            print(f"✅ Manual selection at ({logical_x}, {logical_y})")
            return {'x': logical_x, 'y': logical_y, 'confidence': 1.0}
        
        return None
    
    def detect_apple_tv_checkbox(self, airplay_coords):
        """Detect Apple TV checkbox after clicking AirPlay"""
        print("\n🔍 Detecting Apple TV checkbox...")
        
        # Confirm before clicking
        if not self.confirm_ready("Ready to click AirPlay button?"):
            return None
        
        # Click AirPlay button
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # Show controls by moving mouse
        print("  Moving mouse to show controls...")
        pyautogui.moveTo(airplay_coords['x'], airplay_coords['y'] - 50, duration=0.5)
        time.sleep(0.5)
        
        # Take screenshot before clicking
        before_click = pyautogui.screenshot()
        before_click_np = np.array(before_click)
        before_click_cv2 = cv2.cvtColor(before_click_np, cv2.COLOR_RGB2BGR)
        
        # Mark where we'll click
        phys_x = int(airplay_coords['x'] * self.scale_factor)
        phys_y = int(airplay_coords['y'] * self.scale_factor)
        
        annotations = [
            {'type': 'circle', 'center': (phys_x, phys_y), 'radius': 20,
             'color': (0, 0, 255), 'thickness': 3},
            {'type': 'text', 'text': 'Clicking here',
             'org': (phys_x - 50, phys_y - 30),
             'fontScale': 0.8, 'color': (0, 0, 255), 'thickness': 2}
        ]
        self.save_debug_image(before_click_cv2, "13_before_airplay_click", annotations,
                            description="About to click AirPlay button")
        
        # Click AirPlay
        print(f"  Clicking AirPlay at ({airplay_coords['x']}, {airplay_coords['y']})...")
        pyautogui.click(airplay_coords['x'], airplay_coords['y'])
        time.sleep(1.5)
        
        # Take screenshot of popup
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        self.save_debug_image(screenshot_cv2, "14_airplay_popup",
                            description="AirPlay menu should be visible")
        
        # Try to detect the popup area
        popup_region = self._detect_popup_region(before_click_cv2, screenshot_cv2)
        if popup_region:
            annotations = [
                {'type': 'rectangle',
                 'pt1': (popup_region['x'], popup_region['y']),
                 'pt2': (popup_region['x'] + popup_region['width'],
                        popup_region['y'] + popup_region['height']),
                 'color': (255, 0, 0), 'thickness': 3},
                {'type': 'text', 'text': 'Detected Popup',
                 'org': (popup_region['x'], popup_region['y'] - 10),
                 'fontScale': 1, 'color': (255, 0, 0), 'thickness': 2}
            ]
            self.save_debug_image(screenshot_cv2, "15_popup_detected", annotations,
                                description="Popup region detected")
        
        # Look for checkbox/Apple TV option
        apple_tv_result = self._find_apple_tv_option(screenshot_cv2, airplay_coords)
        
        if apple_tv_result:
            # Show for confirmation
            if self.confirm_detection(screenshot_cv2, apple_tv_result, "Apple TV checkbox detected"):
                return apple_tv_result
        
        print("❌ Could not detect Apple TV checkbox automatically")
        
        # Manual selection
        print("\n👆 Please click on the Apple TV checkbox...")
        result = self._manual_selection(screenshot_cv2)
        
        # Close popup by clicking elsewhere
        pyautogui.click(100, 100)
        
        return result
    
    def _detect_popup_region(self, before, after):
        """Detect the popup region by comparing before/after"""
        # Calculate difference
        diff = cv2.absdiff(before, after)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Threshold
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            
            # Save diff image
            self.save_debug_image(thresh, "16_popup_diff",
                                description="Difference between before/after click")
            
            return {'x': x, 'y': y, 'width': w, 'height': h}
        
        return None
    
    def _find_apple_tv_option(self, screenshot, airplay_coords):
        """Find Apple TV option in the popup"""
        # Common offsets from AirPlay button to Apple TV checkbox
        phys_airplay_x = int(airplay_coords['x'] * self.scale_factor)
        phys_airplay_y = int(airplay_coords['y'] * self.scale_factor)
        
        # Search in a region below AirPlay button
        search_region = {
            'x': max(0, phys_airplay_x - 200),
            'y': phys_airplay_y + 20,
            'width': 400,
            'height': 300
        }
        
        # Crop region
        x, y, w, h = search_region['x'], search_region['y'], search_region['width'], search_region['height']
        region = screenshot[y:y+h, x:x+w]
        
        # Save search region
        annotations = [
            {'type': 'rectangle',
             'pt1': (0, 0),
             'pt2': (w, h),
             'color': (255, 255, 0), 'thickness': 2},
            {'type': 'text', 'text': 'Search Region',
             'org': (10, 30),
             'fontScale': 1, 'color': (255, 255, 0), 'thickness': 2}
        ]
        self.save_debug_image(region, "17_checkbox_search_region", annotations,
                            description="Looking for checkbox in this area")
        
        # Look for checkbox patterns
        candidates = self._find_checkbox_candidates(region)
        
        if candidates:
            # Convert back to full image coordinates
            for cand in candidates:
                cand['x'] += x
                cand['y'] += y
            
            # Sort by distance from expected position
            expected_x = phys_airplay_x + 50
            expected_y = phys_airplay_y + 70
            
            candidates.sort(key=lambda c: 
                          ((c['x'] - expected_x)**2 + (c['y'] - expected_y)**2)**0.5)
            
            best = candidates[0]
            
            # Convert to logical coordinates
            logical_x = int(best['x'] / self.scale_factor)
            logical_y = int(best['y'] / self.scale_factor)
            
            return {'x': logical_x, 'y': logical_y, 'confidence': 0.7}
        
        # Try default offset
        default_x = airplay_coords['x'] + 50
        default_y = airplay_coords['y'] + 70
        
        return {'x': default_x, 'y': default_y, 'confidence': 0.3}
    
    def _find_checkbox_candidates(self, region):
        """Find checkbox-like patterns in region"""
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Look for square shapes
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        annotated = region.copy()
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 1000:  # Checkbox size
                x, y, w, h = cv2.boundingRect(contour)
                aspect = w / h if h > 0 else 0
                
                # Square-ish shape
                if 0.7 < aspect < 1.3:
                    candidates.append({
                        'x': x + w//2,
                        'y': y + h//2,
                        'area': area,
                        'rect': (x, y, w, h)
                    })
                    
                    cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if candidates:
            self.save_debug_image(annotated, "18_checkbox_candidates",
                                description=f"Found {len(candidates)} checkbox candidates")
        
        return candidates
    
    def confirm_ready(self, message):
        """Show confirmation dialog"""
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno("Confirmation", message)
        root.destroy()
        return result
    
    def confirm_detection(self, screenshot, coords, title):
        """Show detection result for confirmation"""
        # Create confirmation window
        root = tk.Tk()
        root.title(title)
        
        # Convert coordinates
        phys_x = int(coords['x'] * self.scale_factor)
        phys_y = int(coords['y'] * self.scale_factor)
        
        # Create annotated image
        annotated = screenshot.copy()
        cv2.circle(annotated, (phys_x, phys_y), 30, (0, 255, 0), 3)
        cv2.drawMarker(annotated, (phys_x, phys_y), (255, 0, 0), cv2.MARKER_CROSS, 50, 2)
        
        # Crop region around detection
        crop_size = 200
        x1 = max(0, phys_x - crop_size)
        y1 = max(0, phys_y - crop_size)
        x2 = min(screenshot.shape[1], phys_x + crop_size)
        y2 = min(screenshot.shape[0], phys_y + crop_size)
        
        cropped = annotated[y1:y2, x1:x2]
        
        # Convert to PIL image
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cropped_rgb)
        
        # Resize if too large
        max_size = 400
        if pil_image.width > max_size or pil_image.height > max_size:
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(pil_image)
        
        # Create GUI
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()
        
        label = tk.Label(frame, text=f"Is this the correct location?\nCoordinates: ({coords['x']}, {coords['y']})")
        label.pack(pady=(0, 10))
        
        image_label = tk.Label(frame, image=photo)
        image_label.pack(pady=(0, 10))
        
        if 'confidence' in coords:
            conf_label = tk.Label(frame, text=f"Confidence: {coords['confidence']:.1%}")
            conf_label.pack()
        
        result = [False]
        
        def on_yes():
            result[0] = True
            root.destroy()
        
        def on_no():
            result[0] = False
            root.destroy()
        
        button_frame = tk.Frame(frame)
        button_frame.pack()
        
        yes_button = tk.Button(button_frame, text="Yes, correct", command=on_yes, 
                              bg="green", fg="white", padx=20, pady=10)
        yes_button.pack(side=tk.LEFT, padx=5)
        
        no_button = tk.Button(button_frame, text="No, try again", command=on_no,
                             bg="red", fg="white", padx=20, pady=10)
        no_button.pack(side=tk.LEFT, padx=5)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop()
        
        return result[0]
    
    def show_debug_images(self, title):
        """Show summary of all debug images"""
        if not self.debug_images:
            return
        
        print(f"\n📸 Debug Images Summary ({title}):")
        print("=" * 60)
        for i, img_info in enumerate(self.debug_images):
            print(f"{i+1:2d}. {img_info['name']:<30} {img_info['timestamp']}")
            print(f"    {img_info['description']}")
            print(f"    {img_info['filename'].name}")
        print("=" * 60)
        
        # Create HTML summary
        html_path = self.debug_dir / "summary.html"
        with open(html_path, 'w') as f:
            f.write(f"<html><head><title>{title}</title></head><body>\n")
            f.write(f"<h1>{title}</h1>\n")
            f.write("<style>img { max-width: 800px; border: 1px solid #ccc; }</style>\n")
            
            for img_info in self.debug_images:
                f.write(f"<h2>{img_info['name']} - {img_info['timestamp']}</h2>\n")
                f.write(f"<p>{img_info['description']}</p>\n")
                f.write(f"<img src='{img_info['filename'].name}'><br><br>\n")
            
            f.write("</body></html>")
        
        print(f"\n🌐 HTML summary saved to: {html_path}")
    
    def save_results(self):
        """Save detection results"""
        results_file = Path("airplay_detection_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
        # Also update template files
        templates_file = Path.home() / '.airplay_templates.json'
        templates = {
            'airplay_button': {
                'captured_at': self.results['airplay_button']
            },
            'apple_tv_icon': {
                'offsets': {
                    'checkbox': {
                        'absolute': self.results['apple_tv_checkbox']
                    }
                }
            }
        }
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        print(f"💾 Templates saved to: {templates_file}")
    
    def run_full_detection(self):
        """Run the complete detection process"""
        print("🎯 Enhanced Visual AirPlay Detection")
        print("=" * 60)
        print("This tool will help you detect AirPlay controls with:")
        print("• Multiple detection methods")
        print("• Visual confirmation for each step")
        print("• Detailed debug images")
        print("• Manual fallback options")
        print("=" * 60)
        
        # Step 1: Detect AirPlay button
        airplay_result = self.detect_airplay_button()
        if not airplay_result:
            print("\n❌ Failed to detect AirPlay button")
            self.show_debug_images("Failed to detect AirPlay button")
            return False
        
        self.results['airplay_button'] = airplay_result
        
        # Step 2: Detect Apple TV checkbox
        apple_tv_result = self.detect_apple_tv_checkbox(airplay_result)
        if not apple_tv_result:
            print("\n❌ Failed to detect Apple TV checkbox")
            self.show_debug_images("Failed to detect Apple TV checkbox")
            return False
        
        self.results['apple_tv_checkbox'] = apple_tv_result
        
        # Save results
        self.save_results()
        
        # Show summary of debug images
        self.show_debug_images("Detection Complete!")
        
        print("\n✅ Detection complete!")
        print(f"📁 Debug images saved in: {self.debug_dir}")
        print(f"🌐 Open {self.debug_dir}/summary.html to review all images")
        
        return True


def main():
    detector = EnhancedVisualAirPlayDetector()
    
    print("\n🚀 Enhanced Visual AirPlay Detector")
    print("This tool provides extensive visual feedback and debug information")
    
    if detector.run_full_detection():
        print("\n🎉 Success! You can now use these coordinates in your automation scripts.")
        print("\nNext steps:")
        print("1. The coordinates have been saved to airplay_detection_results.json")
        print("2. Templates have been saved to ~/.airplay_templates.json")
        print("3. Review debug images in the 'airplay_debug_enhanced' folder")
        print("4. Open summary.html to see all detection steps")
        
        # Offer to test
        test = input("\n🧪 Would you like to test the detected coordinates? (y/n): ")
        if test.lower() == 'y':
            print("\nTesting AirPlay activation...")
            coords = detector.results
            
            # Activate QuickTime
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
            time.sleep(1)
            
            # Show controls
            pyautogui.moveTo(coords['airplay_button']['x'], coords['airplay_button']['y'] - 50, duration=0.5)
            time.sleep(1)
            
            # Click AirPlay
            pyautogui.click(coords['airplay_button']['x'], coords['airplay_button']['y'])
            time.sleep(1.5)
            
            # Click checkbox
            pyautogui.click(coords['apple_tv_checkbox']['x'], coords['apple_tv_checkbox']['y'])
            
            print("✅ Test complete! AirPlay should now be active.")
    else:
        print("\n😕 Detection failed. Please check the debug images for more information.")
        print("\nTroubleshooting tips:")
        print("1. Make sure QuickTime Player is open with a video")
        print("2. Ensure the video is playing or paused (not stopped)")
        print("3. Try manual selection if automatic detection fails")
        print("4. Check the debug images to see what went wrong")
        print("5. Review summary.html for a complete overview")


if __name__ == "__main__":
    main()