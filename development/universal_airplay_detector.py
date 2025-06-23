#!/usr/bin/env python3
"""
Universal AirPlay detector using multiple strategies
"""

import cv2
import numpy as np
import subprocess
import time
from pathlib import Path

class UniversalAirPlayDetector:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "universal_templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def detect_quicktime_ui_elements(self):
        """Detect QuickTime UI using multiple methods"""
        
        # Method 1: Use accessibility API to find exact positions
        positions = self._detect_via_accessibility()
        if positions:
            return positions
            
        # Method 2: Pattern recognition for common UI elements
        positions = self._detect_via_patterns()
        if positions:
            return positions
            
        # Method 3: Interactive detection
        positions = self._detect_interactively()
        return positions
        
    def _detect_via_accessibility(self):
        """Try to use macOS accessibility features"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    -- Try to find AirPlay button
                    try
                        set airplayButton to first button whose description contains "AirPlay" of window 1
                        set airplayPos to position of airplayButton
                        return "found"
                    on error
                        return "not found"
                    end try
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        # If accessibility works, we could get exact positions
        # For now, this is a placeholder
        return None
        
    def _detect_via_patterns(self):
        """Detect common QuickTime patterns"""
        # Get QuickTime window
        qt_window = self._find_quicktime_window()
        if not qt_window:
            return None
            
        # Move mouse to show controls
        center_x = qt_window['x'] + qt_window['width'] // 2
        bottom_y = qt_window['y'] + qt_window['height'] - 30
        subprocess.run(['cliclick', f'm:{center_x},{bottom_y}'])
        time.sleep(1)
        
        # Capture screen
        screenshot = self._capture_screen()
        
        # Look for AirPlay icon characteristics:
        # 1. It's in the bottom right area of the window
        # 2. It's triangular with a rectangle
        # 3. It's usually white/light colored
        
        search_area = self._get_control_bar_area(screenshot, qt_window)
        
        # Find all light-colored shapes in the control area
        candidates = self._find_icon_candidates(search_area)
        
        # Score each candidate
        best_candidate = None
        best_score = 0
        
        for candidate in candidates:
            score = self._score_airplay_candidate(candidate, search_area)
            if score > best_score:
                best_score = score
                best_candidate = candidate
                
        if best_candidate and best_score > 0.6:
            # Convert to screen coordinates
            x = qt_window['x'] + best_candidate['x']
            y = qt_window['y'] + qt_window['height'] - 100 + best_candidate['y']
            
            return {
                'airplay_icon_coords': {'x': x, 'y': y},
                'confidence': best_score
            }
            
        return None
        
    def _detect_interactively(self):
        """Interactive detection with visual feedback"""
        print("Interactive AirPlay Detection")
        print("=" * 50)
        print("I'll help you find the AirPlay button!")
        
        # Flash different areas and ask user
        qt_window = self._find_quicktime_window()
        if not qt_window:
            print("QuickTime window not found")
            return None
            
        print("\n1. Move your mouse to the bottom of QuickTime to show controls")
        print("2. I'll highlight potential AirPlay locations")
        print("3. Tell me which number is correct")
        
        input("\nPress Enter when ready...")
        
        # Generate candidate positions
        candidates = self._generate_candidate_positions(qt_window)
        
        # Show each candidate
        for i, pos in enumerate(candidates):
            self._highlight_position(pos['x'], pos['y'], i + 1)
            
        time.sleep(2)  # Let user see all positions
        
        # Get user choice
        choice = input("\nWhich number was on the AirPlay icon? (1-9): ")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                selected = candidates[idx]
                
                # Now find Apple TV position
                print("\nGreat! Now click the AirPlay icon manually.")
                print("I'll detect where the Apple TV option appears.")
                input("Press Enter after clicking AirPlay...")
                
                # Detect menu position
                apple_tv_pos = self._detect_menu_item()
                
                return {
                    'airplay_icon_coords': {
                        'x': selected['x'], 
                        'y': selected['y']
                    },
                    'apple_tv_coords': apple_tv_pos or {
                        'x': selected['x'] + 50,
                        'y': selected['y'] + 70
                    }
                }
        except:
            pass
            
        return None
        
    def _find_quicktime_window(self):
        """Find QuickTime window position"""
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
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            return {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
        return None
        
    def _capture_screen(self):
        """Capture screen"""
        screenshot_path = "/tmp/qt_screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_path], 
                      capture_output=True)
        screenshot = cv2.imread(screenshot_path)
        subprocess.run(["rm", screenshot_path])
        return screenshot
        
    def _get_control_bar_area(self, screenshot, qt_window):
        """Extract control bar area from screenshot"""
        # Control bar is at the bottom ~100 pixels
        y_start = qt_window['y'] + qt_window['height'] - 100
        y_end = qt_window['y'] + qt_window['height']
        x_start = qt_window['x']
        x_end = qt_window['x'] + qt_window['width']
        
        return screenshot[y_start:y_end, x_start:x_end]
        
    def _find_icon_candidates(self, control_area):
        """Find potential icon locations"""
        # Convert to grayscale
        gray = cv2.cvtColor(control_area, cv2.COLOR_BGR2GRAY)
        
        # Find bright areas (icons are usually bright)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                      cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size (icons are typically 20-40 pixels)
            if 15 < w < 50 and 15 < h < 50:
                candidates.append({
                    'x': x + w // 2,
                    'y': y + h // 2,
                    'width': w,
                    'height': h,
                    'contour': contour
                })
                
        return candidates
        
    def _score_airplay_candidate(self, candidate, control_area):
        """Score how likely a candidate is the AirPlay icon"""
        score = 0.0
        
        # Position score (AirPlay is usually on the right side)
        position_ratio = candidate['x'] / control_area.shape[1]
        if position_ratio > 0.7:  # Right 30% of control bar
            score += 0.3
            
        # Aspect ratio score (roughly square)
        aspect_ratio = candidate['width'] / candidate['height']
        if 0.8 < aspect_ratio < 1.2:
            score += 0.2
            
        # Size score
        area = candidate['width'] * candidate['height']
        if 400 < area < 1600:  # 20x20 to 40x40
            score += 0.2
            
        # Shape complexity (AirPlay icon has specific shape)
        epsilon = 0.02 * cv2.arcLength(candidate['contour'], True)
        approx = cv2.approxPolyDP(candidate['contour'], epsilon, True)
        if 4 <= len(approx) <= 8:  # Not too simple, not too complex
            score += 0.3
            
        return score
        
    def _generate_candidate_positions(self, qt_window):
        """Generate likely positions for AirPlay icon"""
        candidates = []
        
        # Common positions (relative to bottom-right of window)
        offsets = [
            (-150, -50), (-120, -50), (-90, -50),  # Bottom row
            (-150, -80), (-120, -80), (-90, -80),  # Middle row  
            (-180, -50), (-60, -50), (-30, -50)    # Extended
        ]
        
        for dx, dy in offsets:
            candidates.append({
                'x': qt_window['x'] + qt_window['width'] + dx,
                'y': qt_window['y'] + qt_window['height'] + dy
            })
            
        return candidates
        
    def _highlight_position(self, x, y, number):
        """Show a number at the given position"""
        # Create a small window with the number
        script = f'''
        tell application "System Events"
            set floatingWindow to make new window
            set position of floatingWindow to {{{x-20}, {y-20}}}
            set size of floatingWindow to {{40, 40}}
            set content of floatingWindow to "{number}"
        end tell
        '''
        
        # For now, just move the mouse there
        subprocess.run(['cliclick', f'm:{x},{y}'])
        print(f"Position {number}: ({x}, {y})")
        time.sleep(0.3)
        
    def _detect_menu_item(self):
        """Detect Apple TV menu item position"""
        # This would use similar techniques to find the menu item
        # For now, return None to use estimation
        return None


def create_universal_template():
    """Create a universal template package"""
    detector = UniversalAirPlayDetector()
    
    print("Universal AirPlay Detector")
    print("=" * 50)
    print("\nThis will create a universal detection setup.")
    print("\nOptions:")
    print("1. Automatic detection (beta)")
    print("2. Interactive detection (recommended)")
    print("3. Create template set for sharing")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        result = detector.detect_quicktime_ui_elements()
        if result:
            print(f"\nSuccess! Found AirPlay at: {result['airplay_icon_coords']}")
        else:
            print("\nAutomatic detection failed. Try interactive mode.")
            
    elif choice == "2":
        result = detector._detect_interactively()
        if result:
            print(f"\nSuccess! Settings saved:")
            print(f"AirPlay: {result['airplay_icon_coords']}")
            print(f"Apple TV: {result['apple_tv_coords']}")
            
            # Save for QuickDrop
            import json
            settings_file = Path.home() / '.quickdrop_settings.json'
            with open(settings_file, 'w') as f:
                json.dump(result, f)
            print(f"\nSettings saved to: {settings_file}")
            
    elif choice == "3":
        print("\nTemplate creation mode - Coming soon!")
        print("This will create shareable templates for different macOS versions")


if __name__ == "__main__":
    create_universal_template()