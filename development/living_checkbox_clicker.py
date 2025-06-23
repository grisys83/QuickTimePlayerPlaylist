#!/usr/bin/env python3
"""
Living Checkbox Clicker - Focused solution for clicking the living checkbox
Uses multiple methods to ensure success
"""

import subprocess
import time
import os


def debug_airplay_menu():
    """Debug what's in the AirPlay menu to understand structure"""
    
    debug_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                set output to "=== AirPlay Menu Debug ===" & return
                
                -- Get all UI elements
                set allElements to every UI element of menuWindow
                set output to output & "Total UI elements: " & (count of allElements) & return & return
                
                -- Detail each element
                repeat with i from 1 to count of allElements
                    set elem to item i of allElements
                    set output to output & "Element " & i & ":" & return
                    
                    -- Get class
                    try
                        set elemClass to class of elem as string
                        set output to output & "  Class: " & elemClass & return
                    end try
                    
                    -- Get name
                    try
                        set elemName to name of elem
                        set output to output & "  Name: " & elemName & return
                    end try
                    
                    -- Get description
                    try
                        set elemDesc to description of elem
                        set output to output & "  Description: " & elemDesc & return
                    end try
                    
                    -- Get position
                    try
                        set elemPos to position of elem
                        set output to output & "  Position: (" & (item 1 of elemPos as string) & ", " & (item 2 of elemPos as string) & ")" & return
                    end try
                    
                    -- Get size
                    try
                        set elemSize to size of elem
                        set output to output & "  Size: " & (item 1 of elemSize as string) & "x" & (item 2 of elemSize as string) & return
                    end try
                    
                    set output to output & return
                end repeat
                
                return output
            else
                return "No AirPlay menu found"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', debug_script], 
                          capture_output=True, text=True)
    print(result.stdout)


def click_living_checkbox_method1():
    """Method 1: Click the checkbox area to the right of 'living' text"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                
                -- Find the living element
                set allElements to every UI element of menuWindow
                repeat with i from 1 to count of allElements
                    set elem to item i of allElements
                    
                    try
                        -- Check if this is the living item
                        set elemName to name of elem
                        if elemName contains "living" then
                            -- Get position and size
                            set elemPos to position of elem
                            set elemSize to size of elem
                            set elemX to item 1 of elemPos
                            set elemY to item 2 of elemPos
                            set elemWidth to item 1 of elemSize
                            set elemHeight to item 2 of elemSize
                            
                            -- Click on the right side (checkbox area)
                            set checkboxX to elemX + elemWidth - 20
                            set checkboxY to elemY + (elemHeight / 2)
                            
                            -- Use cliclick to click exact position
                            do shell script "cliclick c:" & (checkboxX as integer) & "," & (checkboxY as integer)
                            
                            return "Clicked checkbox at (" & checkboxX & ", " & checkboxY & ")"
                        end if
                    end try
                end repeat
                
                return "living not found"
            else
                return "No menu window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()


def click_living_checkbox_method2():
    """Method 2: Click by index position (living is usually 2nd)"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                
                -- Get the 2nd UI element (living)
                set allElements to every UI element of menuWindow
                if (count of allElements) >= 2 then
                    set livingElem to item 2 of allElements
                    
                    -- Get its bounds
                    set elemPos to position of livingElem
                    set elemSize to size of livingElem
                    set rightEdge to (item 1 of elemPos) + (item 1 of elemSize) - 20
                    set centerY to (item 2 of elemPos) + ((item 2 of elemSize) / 2)
                    
                    -- Click the checkbox area
                    do shell script "cliclick c:" & (rightEdge as integer) & "," & (centerY as integer)
                    
                    return "Clicked position 2 checkbox"
                else
                    return "Not enough elements"
                end if
            else
                return "No menu window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()


def click_living_checkbox_method3():
    """Method 3: Find checkbox by role and click it"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                
                -- Look for checkbox elements
                try
                    set checkboxes to every checkbox of menuWindow
                    if (count of checkboxes) >= 2 then
                        -- Click the 2nd checkbox (living)
                        click checkbox 2 of menuWindow
                        return "Clicked checkbox 2"
                    else
                        return "Not enough checkboxes"
                    end if
                on error
                    -- Try radio buttons
                    try
                        set radioButtons to every radio button of menuWindow
                        if (count of radioButtons) >= 2 then
                            click radio button 2 of menuWindow
                            return "Clicked radio button 2"
                        end if
                    end try
                end try
                
                return "No checkboxes found"
            else
                return "No menu window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()


def click_living_checkbox_method4():
    """Method 4: Use perform action to click"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                
                -- Try different click methods on 2nd element
                set allElements to every UI element of menuWindow
                if (count of allElements) >= 2 then
                    set targetElem to item 2 of allElements
                    
                    -- Try perform action
                    try
                        perform action "AXPress" of targetElem
                        return "Performed AXPress on element 2"
                    on error
                        -- Try click
                        try
                            click targetElem
                            return "Clicked element 2"
                        on error
                            -- Get position for manual click
                            set elemPos to position of targetElem
                            set elemSize to size of targetElem
                            return "Element at (" & (item 1 of elemPos) & ", " & (item 2 of elemPos) & ") size " & (item 1 of elemSize) & "x" & (item 2 of elemSize)
                        end try
                    end try
                end if
                
                return "Could not click"
            else
                return "No menu window"
            end if
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()


def main():
    print("🎯 Living Checkbox Clicker")
    print("=" * 50)
    
    # First open an audio file
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
    
    # Click AirPlay button
    print("\n2️⃣ Clicking AirPlay button...")
    
    airplay_script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- Find and click AirPlay
            set btnList to every button of window 1
            repeat with btn in btnList
                try
                    if description of btn contains "외장" then
                        click btn
                        return "Clicked AirPlay"
                    end if
                end try
            end repeat
            
            return "AirPlay not found"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', airplay_script], 
                          capture_output=True, text=True)
    print(f"   {result.stdout.strip()}")
    
    time.sleep(1.5)
    
    # Debug menu contents
    print("\n3️⃣ Debugging menu contents...")
    debug_airplay_menu()
    
    # Try all methods
    print("\n4️⃣ Trying to click living checkbox...")
    
    methods = [
        ("Method 1 (right side click)", click_living_checkbox_method1),
        ("Method 2 (index position)", click_living_checkbox_method2),
        ("Method 3 (checkbox role)", click_living_checkbox_method3),
        ("Method 4 (perform action)", click_living_checkbox_method4),
    ]
    
    for name, method in methods:
        print(f"\n   {name}:")
        result = method()
        print(f"   Result: {result}")
        
        if "Clicked" in result or "Success" in result:
            print("\n✅ Success!")
            break
        
        time.sleep(0.5)
    
    print("\n💡 If none of the methods worked:")
    print("   1. Check the debug output above")
    print("   2. Look for the position of element 2")
    print("   3. Use cliclick to manually click the checkbox area")


if __name__ == "__main__":
    main()