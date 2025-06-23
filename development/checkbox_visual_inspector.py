#!/usr/bin/env python3
"""
Checkbox Visual Inspector
Captures and analyzes the AirPlay menu to understand checkbox positions
"""

import subprocess
import time
import os
from pathlib import Path


def capture_airplay_menu():
    """Capture screenshot of AirPlay menu"""
    
    # Take screenshot
    timestamp = int(time.time())
    screenshot_path = f"/tmp/airplay_menu_{timestamp}.png"
    
    capture_script = f'''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                set menuPos to position of menuWindow
                set menuSize to size of menuWindow
                
                -- Return bounds for screenshot
                return ((item 1 of menuPos) as string) & "," & ((item 2 of menuPos) as string) & "," & ((item 1 of menuSize) as string) & "," & ((item 2 of menuSize) as string)
            else
                return "no menu"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', capture_script], 
                          capture_output=True, text=True)
    
    if result.stdout.strip() != "no menu":
        bounds = result.stdout.strip().split(',')
        x, y, w, h = int(bounds[0]), int(bounds[1]), int(bounds[2]), int(bounds[3])
        
        # Take screenshot of menu area
        subprocess.run(['screencapture', '-R', f'{x},{y},{w},{h}', screenshot_path])
        print(f"📸 Screenshot saved: {screenshot_path}")
        print(f"   Menu bounds: x={x}, y={y}, width={w}, height={h}")
        
        return {'x': x, 'y': y, 'width': w, 'height': h, 'screenshot': screenshot_path}
    
    return None


def analyze_menu_items():
    """Analyze menu items and their checkbox areas"""
    
    analyze_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                set menuPos to position of menuWindow
                set output to "=== Menu Item Analysis ===" & return & return
                
                -- Get all items
                set allElements to every UI element of menuWindow
                set itemCount to count of allElements
                
                repeat with i from 1 to itemCount
                    set elem to item i of allElements
                    set output to output & "Item " & i & ":" & return
                    
                    -- Get properties
                    try
                        set elemPos to position of elem
                        set elemSize to size of elem
                        set elemX to item 1 of elemPos
                        set elemY to item 2 of elemPos
                        set elemW to item 1 of elemSize
                        set elemH to item 2 of elemSize
                        
                        -- Menu-relative coordinates
                        set relX to elemX - (item 1 of menuPos)
                        set relY to elemY - (item 2 of menuPos)
                        
                        set output to output & "  Absolute: (" & elemX & ", " & elemY & ")" & return
                        set output to output & "  Relative: (" & relX & ", " & relY & ")" & return
                        set output to output & "  Size: " & elemW & "x" & elemH & return
                        
                        -- Checkbox area (right side)
                        set checkX to elemX + elemW - 25
                        set checkY to elemY + (elemH / 2)
                        set output to output & "  Checkbox area: (" & (checkX as integer) & ", " & (checkY as integer) & ")" & return
                        
                        -- Name
                        try
                            set elemName to name of elem
                            set output to output & "  Name: " & elemName & return
                        end try
                        
                        -- Enabled state
                        try
                            set isEnabled to enabled of elem
                            set output to output & "  Enabled: " & (isEnabled as string) & return
                        end try
                        
                        -- Selected state
                        try
                            set isSelected to selected of elem
                            set output to output & "  Selected: " & (isSelected as string) & return
                        end try
                        
                    end try
                    
                    set output to output & return
                end repeat
                
                return output
            else
                return "No menu found"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', analyze_script], 
                          capture_output=True, text=True)
    print(result.stdout)


def click_checkbox_visual(item_index=2):
    """Click checkbox using visual analysis"""
    
    # First get menu item info
    get_coords_script = f'''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                set allElements to every UI element of menuWindow
                
                if (count of allElements) >= {item_index} then
                    set targetElem to item {item_index} of allElements
                    set elemPos to position of targetElem
                    set elemSize to size of targetElem
                    
                    -- Calculate checkbox position (right side, centered)
                    set checkX to (item 1 of elemPos) + (item 1 of elemSize) - 25
                    set checkY to (item 2 of elemPos) + ((item 2 of elemSize) / 2)
                    
                    return (checkX as integer as string) & "," & (checkY as integer as string)
                else
                    return "not enough items"
                end if
            else
                return "no menu"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', get_coords_script], 
                          capture_output=True, text=True)
    
    coords = result.stdout.strip()
    if ',' in coords:
        x, y = coords.split(',')
        print(f"🎯 Clicking checkbox at ({x}, {y})")
        
        # Try multiple click methods
        
        # Method 1: Direct cliclick
        subprocess.run(['cliclick', f'c:{x},{y}'])
        time.sleep(0.5)
        
        # Method 2: Double click for stubborn checkboxes
        subprocess.run(['cliclick', f'dc:{x},{y}'])
        
        return True
    
    return False


def interactive_checkbox_finder():
    """Interactive mode to find exact checkbox position"""
    
    print("\n🔍 Interactive Checkbox Finder")
    print("This will help you find the exact checkbox position\n")
    
    # Get current mouse position
    get_mouse = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    print(f"Current mouse position: {get_mouse.stdout.strip()}")
    
    print("\nInstructions:")
    print("1. The AirPlay menu should be open")
    print("2. Move your mouse to the 'living' checkbox")
    print("3. Press Enter when ready")
    
    input("\nPress Enter when mouse is on checkbox...")
    
    # Get new position
    get_mouse = subprocess.run(['cliclick', 'p'], capture_output=True, text=True)
    pos = get_mouse.stdout.strip()
    
    if ':' in pos:
        x, y = pos.split(':')
        print(f"\n✅ Checkbox position: ({x}, {y})")
        
        # Save for future use
        save_script = f'''
        echo "# Living checkbox position" > ~/.living_checkbox_position
        echo "X={x}" >> ~/.living_checkbox_position
        echo "Y={y}" >> ~/.living_checkbox_position
        '''
        
        subprocess.run(['bash', '-c', save_script])
        print("💾 Position saved to ~/.living_checkbox_position")
        
        # Test click
        print("\n🧪 Testing click...")
        subprocess.run(['cliclick', f'c:{x},{y}'])
        
        return {'x': int(x), 'y': int(y)}
    
    return None


def main():
    print("🔍 Checkbox Visual Inspector")
    print("=" * 50)
    
    # Open audio file
    print("\n1️⃣ Opening audio file...")
    music_file = "/Users/parkbyeongsu/Hyang/QuicktimePlaylist/Our Conversation.mp3"
    
    open_script = f'''
    tell application "QuickTime Player"
        activate
        close every window
        delay 0.5
        open POSIX file "{music_file}"
        play document 1
        delay 2
    end tell
    '''
    
    subprocess.run(['osascript', '-e', open_script])
    
    # Click AirPlay
    print("\n2️⃣ Opening AirPlay menu...")
    
    airplay_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set btnList to every button of window 1
            repeat with btn in btnList
                if description of btn contains "외장" then
                    click btn
                    return "opened"
                end if
            end repeat
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', airplay_script])
    time.sleep(1.5)
    
    # Capture and analyze
    print("\n3️⃣ Capturing menu...")
    menu_info = capture_airplay_menu()
    
    print("\n4️⃣ Analyzing menu items...")
    analyze_menu_items()
    
    print("\n5️⃣ Attempting to click living checkbox...")
    if click_checkbox_visual(2):
        print("✅ Clicked!")
    else:
        print("❌ Failed")
    
    # Interactive mode
    print("\n6️⃣ Interactive mode?")
    choice = input("Would you like to manually find the checkbox? (y/n): ")
    
    if choice.lower() == 'y':
        interactive_checkbox_finder()


if __name__ == "__main__":
    main()