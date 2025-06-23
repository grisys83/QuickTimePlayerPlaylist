#!/usr/bin/env python3
"""
Audio AirPlay Timer Detector - Camera-style countdown detection
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import time
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import threading


class CountdownWindow:
    """Visual countdown window"""
    def __init__(self, seconds=10):
        self.root = tk.Tk()
        self.root.title("📸 Screenshot Countdown")
        self.root.geometry("400x200")
        self.root.configure(bg='black')
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 100
        self.root.geometry(f"+{x}+{y}")
        
        # Countdown label
        self.label = tk.Label(
            self.root,
            text=str(seconds),
            font=('Arial', 80, 'bold'),
            fg='white',
            bg='black'
        )
        self.label.pack(expand=True)
        
        # Action label
        self.action_label = tk.Label(
            self.root,
            text="Get ready...",
            font=('Arial', 20),
            fg='gray',
            bg='black'
        )
        self.action_label.pack(pady=(0, 20))
        
        self.seconds = seconds
        self.running = True
        
    def start(self):
        """Start countdown"""
        def countdown():
            for i in range(self.seconds, 0, -1):
                if not self.running:
                    break
                    
                # Update color based on time
                if i <= 3:
                    color = '#ff4444'  # Red
                    self.root.configure(bg='#330000')
                    self.label.configure(bg='#330000')
                    self.action_label.configure(bg='#330000')
                elif i <= 5:
                    color = '#ffaa00'  # Orange
                    self.root.configure(bg='#332200')
                    self.label.configure(bg='#332200')
                    self.action_label.configure(bg='#332200')
                else:
                    color = '#44ff44'  # Green
                    self.root.configure(bg='#003300')
                    self.label.configure(bg='#003300')
                    self.action_label.configure(bg='#003300')
                
                self.label.configure(text=str(i), fg=color)
                
                if i == 1:
                    self.action_label.configure(text="📸 CAPTURE!", fg='white')
                    
                time.sleep(1)
            
            # Flash and close
            self.root.configure(bg='white')
            self.label.configure(text="📸", fg='black', bg='white')
            self.action_label.configure(text="Captured!", fg='black', bg='white')
            time.sleep(0.2)
            self.root.destroy()
        
        # Run countdown in thread
        thread = threading.Thread(target=countdown)
        thread.start()
        
        # Run tkinter mainloop
        self.root.mainloop()
    
    def stop(self):
        """Stop countdown"""
        self.running = False
        if self.root:
            self.root.destroy()


class AudioAirPlayTimerDetector:
    def __init__(self):
        self.scale_factor = self._get_scale_factor()
        self.debug_dir = Path("audio_airplay_timer_debug")
        self.debug_dir.mkdir(exist_ok=True)
        
    def _get_scale_factor(self):
        """Get display scale factor"""
        try:
            logical_width, _ = pyautogui.size()
            screenshot = pyautogui.screenshot()
            physical_width = screenshot.width
            return physical_width / logical_width
        except:
            return 2.0
    
    def _countdown_capture(self, seconds, message):
        """Show visual countdown and capture"""
        print(f"\n📸 {message}")
        print(f"   Countdown will start in a new window")
        print(f"   Position your screen as needed during countdown")
        
        # Create and show countdown window
        countdown = CountdownWindow(seconds)
        countdown.start()
        
        # Take screenshot after countdown
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        print("✅ Screenshot captured!")
        return screenshot_cv2
    
    def detect_audio_airplay(self):
        """Detect AirPlay button and Apple TV checkbox with timer"""
        print("\n🎵 Audio AirPlay Timer Detection")
        print("=" * 50)
        print("\nThis tool uses camera-style countdown timers")
        print("You'll have time to position everything correctly")
        
        print("\n📋 We'll capture:")
        print("1. QuickTime window with AirPlay button")
        print("2. AirPlay popup menu after clicking")
        
        input("\nPress Enter to start...")
        
        # Step 1: Capture QuickTime window
        print("\n📍 Step 1: Capture QuickTime Window")
        print("Make sure QuickTime is visible with an audio file")
        input("Press Enter to start 10-second countdown...")
        
        screenshot1 = self._countdown_capture(10, "Capturing QuickTime window")
        cv2.imwrite(str(self.debug_dir / "01_quicktime_window.png"), screenshot1)
        
        # Find QuickTime window
        qt_window = self._find_quicktime_window()
        if not qt_window:
            print("❌ Could not find QuickTime window")
            return None
            
        print(f"✅ Found QuickTime window: {qt_window['width']}x{qt_window['height']}")
        
        # Detect AirPlay button
        airplay_coords = self._detect_airplay_button(qt_window, screenshot1)
        if not airplay_coords:
            print("❌ Could not detect AirPlay button")
            return None
            
        print(f"✅ Found AirPlay button at: ({airplay_coords['x']}, {airplay_coords['y']})")
        
        # Step 2: Click AirPlay and capture popup
        print("\n📍 Step 2: Capture AirPlay Popup")
        print("I will click the AirPlay button and capture the popup")
        print("\n⚠️  IMPORTANT: After I click, DO NOT move the mouse!")
        input("Press Enter when ready...")
        
        # Click AirPlay
        print("🖱️ Clicking AirPlay button...")
        pyautogui.click(airplay_coords['x'], airplay_coords['y'])
        
        # Give popup time to appear
        print("⏳ Waiting for popup (2 seconds)...")
        time.sleep(2)
        
        # Countdown for popup capture
        print("\n📸 Capturing popup menu...")
        input("Press Enter to start 5-second countdown...")
        
        screenshot2 = self._countdown_capture(5, "Capturing AirPlay popup")
        cv2.imwrite(str(self.debug_dir / "02_airplay_popup.png"), screenshot2)
        
        # Detect Apple TV checkbox
        apple_tv_coords = self._detect_apple_tv_checkbox(airplay_coords, screenshot2)
        if not apple_tv_coords:
            print("❌ Could not detect Apple TV checkbox")
            # Close popup
            pyautogui.click(100, 100)
            return None
            
        print(f"✅ Found Apple TV checkbox at: ({apple_tv_coords['x']}, {apple_tv_coords['y']})")
        
        # Close popup
        pyautogui.click(100, 100)
        
        # Save results
        results = {
            'airplay_icon_coords': airplay_coords,
            'apple_tv_coords': apple_tv_coords,
            'window_type': 'audio',
            'detection_method': 'timer_based'
        }
        
        self._save_results(results)
        return results
    
    def _find_quicktime_window(self):
        """Find QuickTime window bounds"""
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
        return None
    
    def _detect_airplay_button(self, qt_window, screenshot):
        """Detect AirPlay button in screenshot"""
        # AirPlay button is typically at bottom right
        airplay_x = qt_window['x'] + qt_window['width'] - 45
        airplay_y = qt_window['y'] + qt_window['height'] - 35
        
        # Highlight detected position
        annotated = screenshot.copy()
        phys_x = int(airplay_x * self.scale_factor)
        phys_y = int(airplay_y * self.scale_factor)
        
        cv2.circle(annotated, (phys_x, phys_y), 30, (0, 255, 0), 3)
        cv2.putText(annotated, "AirPlay?", (phys_x - 40, phys_y - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imwrite(str(self.debug_dir / "03_airplay_detected.png"), annotated)
        
        # Ask user to confirm
        response = input("\n✅ Is the green circle on the AirPlay button? (y/n): ")
        if response.lower() == 'y':
            return {'x': airplay_x, 'y': airplay_y}
        
        # Manual selection
        print("\n👆 Manual selection needed")
        print("Please open the debug image and note the AirPlay button coordinates")
        print(f"Debug image: {self.debug_dir / '01_quicktime_window.png'}")
        
        x = int(input("Enter X coordinate: "))
        y = int(input("Enter Y coordinate: "))
        
        return {'x': x, 'y': y}
    
    def _detect_apple_tv_checkbox(self, airplay_coords, screenshot):
        """Detect Apple TV checkbox in popup screenshot"""
        # Define ROI around AirPlay button
        roi_size = 600
        roi_x = max(0, airplay_coords['x'] - roi_size // 2)
        roi_y = max(0, airplay_coords['y'] - roi_size // 2)
        
        # Annotate screenshot
        annotated = screenshot.copy()
        phys_roi_x = int(roi_x * self.scale_factor)
        phys_roi_y = int(roi_y * self.scale_factor)
        phys_roi_size = int(roi_size * self.scale_factor)
        
        cv2.rectangle(annotated, 
                     (phys_roi_x, phys_roi_y),
                     (phys_roi_x + phys_roi_size, phys_roi_y + phys_roi_size),
                     (255, 255, 0), 3)
        
        # Estimated checkbox position
        checkbox_x = airplay_coords['x'] + 50
        checkbox_y = airplay_coords['y'] + 70
        
        phys_cb_x = int(checkbox_x * self.scale_factor)
        phys_cb_y = int(checkbox_y * self.scale_factor)
        
        cv2.circle(annotated, (phys_cb_x, phys_cb_y), 20, (0, 0, 255), 3)
        cv2.putText(annotated, "Apple TV?", (phys_cb_x - 40, phys_cb_y - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imwrite(str(self.debug_dir / "04_popup_annotated.png"), annotated)
        
        # Ask user to confirm
        response = input("\n✅ Is the red circle on the Apple TV checkbox? (y/n): ")
        if response.lower() == 'y':
            return {'x': checkbox_x, 'y': checkbox_y}
        
        # Manual selection
        print("\n👆 Manual selection needed")
        print("Please open the debug image and note the Apple TV checkbox coordinates")
        print(f"Debug image: {self.debug_dir / '02_airplay_popup.png'}")
        
        x = int(input("Enter X coordinate: "))
        y = int(input("Enter Y coordinate: "))
        
        return {'x': x, 'y': y}
    
    def _save_results(self, results):
        """Save detection results"""
        # Save to audio-specific settings
        audio_settings = Path.home() / '.audio_airplay_settings.json'
        with open(audio_settings, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Settings saved to: {audio_settings}")
        
        # Update templates
        templates_file = Path.home() / '.airplay_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        templates['audio_airplay_timer'] = results
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)


def main():
    print("📸 Audio AirPlay Timer Detector")
    print("Camera-style countdown for perfect timing")
    
    detector = AudioAirPlayTimerDetector()
    result = detector.detect_audio_airplay()
    
    if result:
        print("\n✅ Detection complete!")
        print(f"\n📍 Coordinates saved:")
        print(f"   AirPlay: ({result['airplay_icon_coords']['x']}, {result['airplay_icon_coords']['y']})")
        print(f"   Apple TV: ({result['apple_tv_coords']['x']}, {result['apple_tv_coords']['y']})")
        print(f"\n📁 Debug images: {detector.debug_dir}")
        
        # Test option
        test = input("\n🧪 Test these coordinates? (y/n): ")
        if test.lower() == 'y':
            print("\n🎯 Testing in 3...")
            time.sleep(1)
            print("   2...")
            time.sleep(1)
            print("   1...")
            time.sleep(1)
            
            # Click AirPlay
            pyautogui.click(result['airplay_icon_coords']['x'], 
                          result['airplay_icon_coords']['y'])
            time.sleep(1.5)
            
            # Click Apple TV
            pyautogui.click(result['apple_tv_coords']['x'], 
                          result['apple_tv_coords']['y'])
            
            print("\n✅ Test complete!")
    else:
        print("\n❌ Detection failed")


if __name__ == "__main__":
    main()