#!/usr/bin/env python3
"""
Check and guide for Accessibility permissions
"""

import subprocess
import sys


def check_accessibility():
    """Check if we have accessibility permissions"""
    print("\n🔍 Checking Accessibility Permissions")
    print("=" * 50)
    
    # Check if accessibility is enabled
    script = '''
    tell application "System Events"
        set isEnabled to UI elements enabled
        return isEnabled
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    if result.stdout.strip() == "true":
        print("✅ Accessibility permissions are ENABLED!")
        print("\nYou can now use the automation scripts.")
    else:
        print("❌ Accessibility permissions are DISABLED!")
        print("\n📋 To enable accessibility permissions:")
        print("\n1. Open System Preferences (시스템 환경설정)")
        print("2. Go to Security & Privacy (보안 및 개인정보 보호)")
        print("3. Click on Privacy tab (개인정보 보호 탭)")
        print("4. Select Accessibility (손쉬운 사용) from the left sidebar")
        print("5. Click the lock 🔒 to make changes")
        print("6. Add Terminal (터미널) or your Python app to the list")
        print("7. Check the checkbox next to Terminal")
        
        print("\n💡 Quick way to open the settings:")
        print("Running command to open System Preferences...")
        
        # Open System Preferences directly to Privacy > Accessibility
        subprocess.run([
            'open', 
            'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
        ])
        
        print("\n⚠️  After granting permission, you may need to:")
        print("- Restart Terminal")
        print("- Re-run your Python script")
        
        return False
    
    return True


def test_simple_automation():
    """Test if we can control QuickTime"""
    print("\n🧪 Testing QuickTime automation...")
    
    script = '''
    tell application "System Events"
        if exists process "QuickTime Player" then
            tell process "QuickTime Player"
                set proc_name to name
                set win_count to count of windows
                return "QuickTime is running with " & (win_count as string) & " windows"
            end tell
        else
            return "QuickTime is not running"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {result.stdout.strip()}")
    else:
        print(f"❌ Error: {result.stderr}")


if __name__ == "__main__":
    print("🔐 macOS Accessibility Permission Checker")
    print("This is required for UI automation\n")
    
    if check_accessibility():
        test_simple_automation()
    else:
        print("\n❗ Please grant accessibility permissions and try again.")
        sys.exit(1)