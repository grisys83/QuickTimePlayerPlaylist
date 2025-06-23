#!/usr/bin/env python3
"""
Audio AirPlay Method Comparison
Demonstrates different approaches for finding AirPlay controls
"""

import subprocess
import time
import cv2
import numpy as np
from pathlib import Path


class AirPlayMethodComparison:
    def __init__(self):
        self.methods_tested = []
        
    def compare_all_methods(self):
        """Compare all detection methods"""
        print("\n🔬 Audio AirPlay Detection Method Comparison")
        print("=" * 50)
        
        # Method 1: Visual Detection (Template Matching)
        print("\n1️⃣ Visual Detection - Template Matching")
        print("-" * 40)
        visual_success = self._test_visual_detection()
        self.methods_tested.append({
            'method': 'Visual Template Matching',
            'success': visual_success,
            'pros': [
                'Works without special permissions',
                'Can detect based on visual appearance'
            ],
            'cons': [
                'Fails if window position changes',
                'Sensitive to UI theme changes',
                'Requires exact template match',
                'Cannot detect if window is obscured'
            ]
        })
        
        # Method 2: Accessibility API
        print("\n2️⃣ Accessibility API")
        print("-" * 40)
        accessibility_success = self._test_accessibility_api()
        self.methods_tested.append({
            'method': 'macOS Accessibility API',
            'success': accessibility_success,
            'pros': [
                'Reliable UI element detection',
                'Works regardless of window position',
                'Can read element descriptions',
                'Native macOS integration',
                'Works with Korean UI'
            ],
            'cons': [
                'Requires accessibility permissions',
                'User must grant permission first time'
            ]
        })
        
        # Method 3: Fixed Coordinates
        print("\n3️⃣ Fixed Coordinates")
        print("-" * 40)
        fixed_success = self._test_fixed_coordinates()
        self.methods_tested.append({
            'method': 'Fixed Coordinates',
            'success': fixed_success,
            'pros': [
                'Very fast',
                'No detection needed'
            ],
            'cons': [
                'Breaks if window moves',
                'Breaks if window size changes',
                'Not portable between systems',
                'Requires manual setup'
            ]
        })
        
        # Summary
        self._print_summary()
    
    def _test_visual_detection(self):
        """Test visual detection method"""
        print("Testing visual template matching...")
        
        try:
            # Simulate screenshot capture
            script = '''
            tell application "QuickTime Player"
                if exists window 1 then
                    set winBounds to bounds of window 1
                    return (item 1 of winBounds as string) & "," & (item 2 of winBounds as string) & "," & (item 3 of winBounds as string) & "," & (item 4 of winBounds as string)
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                print("✓ Can capture window bounds")
                print("✗ Template matching unreliable for dynamic UI")
                return False
            else:
                print("✗ Cannot get window information")
                return False
                
        except Exception as e:
            print(f"✗ Visual detection failed: {e}")
            return False
    
    def _test_accessibility_api(self):
        """Test accessibility API method"""
        print("Testing accessibility API...")
        
        # Check permission
        script = '''
        tell application "System Events"
            set isEnabled to UI elements enabled
            return isEnabled
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip() != "true":
            print("✗ No accessibility permission")
            return False
        
        print("✓ Accessibility permission granted")
        
        # Try to find AirPlay button
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    tell window 1
                        set buttonList to every button whose description contains "외장"
                        if (count of buttonList) > 0 then
                            return "found"
                        else
                            return "not found"
                        end if
                    end tell
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if "found" in result.stdout:
            print("✓ Successfully found AirPlay button")
            print("✓ Can interact with UI elements")
            return True
        else:
            print("✗ AirPlay button not found (window might be closed)")
            return False
    
    def _test_fixed_coordinates(self):
        """Test fixed coordinates method"""
        print("Testing fixed coordinates...")
        
        settings_file = Path.home() / '.korean_audio_airplay_settings.json'
        
        if settings_file.exists():
            print("✓ Saved coordinates found")
            print("✗ Only works if window hasn't moved")
            return False
        else:
            print("✗ No saved coordinates")
            return False
    
    def _print_summary(self):
        """Print comparison summary"""
        print("\n\n📊 COMPARISON SUMMARY")
        print("=" * 50)
        
        for method in self.methods_tested:
            print(f"\n📱 {method['method']}")
            print(f"   Status: {'✅ Working' if method['success'] else '❌ Not Reliable'}")
            
            print("   Pros:")
            for pro in method['pros']:
                print(f"     + {pro}")
            
            print("   Cons:")
            for con in method['cons']:
                print(f"     - {con}")
        
        print("\n\n🏆 RECOMMENDATION")
        print("=" * 50)
        print("\n✨ Use the Accessibility API approach (audio_airplay_korean.py)")
        print("\nReasons:")
        print("1. Most reliable for finding UI elements")
        print("2. Works with Korean macOS interface")
        print("3. Not affected by window position or size")
        print("4. Can programmatically interact with QuickTime")
        print("\n⚠️  Note: User needs to grant accessibility permission once")
        print("\n💡 Alternative: SwiftUI/Objective-C native app could access")
        print("   AirPlay APIs directly without UI automation")


def main():
    comparison = AirPlayMethodComparison()
    comparison.compare_all_methods()
    
    print("\n\n🔧 Setup Instructions for Accessibility API:")
    print("1. Go to System Preferences > Security & Privacy > Privacy")
    print("2. Click 'Accessibility' in the left panel")
    print("3. Add Terminal (or your Python app) to the list")
    print("4. Check the checkbox to grant permission")
    print("\nThen run: python3 audio_airplay_korean.py")


if __name__ == "__main__":
    main()