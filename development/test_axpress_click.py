#!/usr/bin/env python3
"""
Test AXPress action for clicking checkboxes
Uses accessibility actions instead of click
"""

import subprocess
import time


def test_ax_actions():
    """Test different AX actions on menu items"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                set output to "=== Testing AX Actions ===" & return & return
                
                -- Get the 2nd UI element (living)
                set allElements to every UI element of menuWindow
                if (count of allElements) >= 2 then
                    set livingElem to item 2 of allElements
                    
                    -- Get available actions
                    set output to output & "Available actions:" & return
                    try
                        set actionList to actions of livingElem
                        repeat with anAction in actionList
                            set actionName to name of anAction
                            set actionDesc to description of anAction
                            set output to output & "  - " & actionName & ": " & actionDesc & return
                        end repeat
                    on error
                        set output to output & "  (Could not get actions)" & return
                    end try
                    
                    set output to output & return & "Trying actions:" & return
                    
                    -- Try AXPress
                    try
                        perform action "AXPress" of livingElem
                        set output to output & "  ✅ AXPress succeeded" & return
                    on error errMsg
                        set output to output & "  ❌ AXPress failed: " & errMsg & return
                    end try
                    
                    delay 0.5
                    
                    -- Try AXShowMenu
                    try
                        perform action "AXShowMenu" of livingElem
                        set output to output & "  ✅ AXShowMenu succeeded" & return
                    on error errMsg
                        set output to output & "  ❌ AXShowMenu failed: " & errMsg & return
                    end try
                    
                    delay 0.5
                    
                    -- Try direct value setting
                    try
                        set value of livingElem to 1
                        set output to output & "  ✅ Set value succeeded" & return
                    on error errMsg
                        set output to output & "  ❌ Set value failed: " & errMsg & return
                    end try
                    
                    -- Get element properties
                    set output to output & return & "Element properties:" & return
                    try
                        set elemRole to role of livingElem
                        set output to output & "  Role: " & elemRole & return
                    end try
                    
                    try
                        set elemSubrole to subrole of livingElem
                        set output to output & "  Subrole: " & elemSubrole & return
                    end try
                    
                    try
                        set elemValue to value of livingElem
                        set output to output & "  Value: " & (elemValue as string) & return
                    end try
                    
                    return output
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
    print(result.stdout)


def test_checkbox_selection():
    """Test selecting checkbox by setting its value"""
    
    script = '''
    tell application "System Events"
        tell process "QuickTime Player"
            if (count of windows) > 1 then
                set menuWindow to window 2
                
                -- Try to find checkboxes or radio buttons
                try
                    -- Method 1: Look for checkboxes
                    set checkboxList to every checkbox of menuWindow
                    if (count of checkboxList) > 0 then
                        repeat with i from 1 to count of checkboxList
                            set cb to item i of checkboxList
                            if i = 2 then
                                -- Select the 2nd checkbox (living)
                                set value of cb to 1
                                return "Set checkbox " & i & " to selected"
                            end if
                        end repeat
                    end if
                on error
                    -- Method 2: Look for radio buttons
                    try
                        set radioList to every radio button of menuWindow
                        if (count of radioList) > 0 then
                            repeat with i from 1 to count of radioList
                                set rb to item i of radioList
                                if i = 2 then
                                    set value of rb to 1
                                    return "Set radio button " & i & " to selected"
                                end if
                            end repeat
                        end if
                    end try
                end try
                
                -- Method 3: Try UI elements with checkbox-like properties
                set allElements to every UI element of menuWindow
                repeat with i from 1 to count of allElements
                    set elem to item i of allElements
                    if i = 2 then
                        try
                            -- Check if it has a value property
                            set currentValue to value of elem
                            if currentValue is 0 then
                                set value of elem to 1
                                return "Set element " & i & " value to 1"
                            else
                                set value of elem to 0
                                delay 0.1
                                set value of elem to 1
                                return "Toggled element " & i & " value"
                            end if
                        on error
                            -- No value property
                        end try
                    end if
                end repeat
                
                return "Could not find selectable elements"
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
    print("🧪 Testing AXPress and Checkbox Selection")
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
    
    # Test AX actions
    print("\n3️⃣ Testing AX actions...")
    test_ax_actions()
    
    # Test checkbox selection
    print("\n4️⃣ Testing checkbox selection...")
    result = test_checkbox_selection()
    print(f"Result: {result}")


if __name__ == "__main__":
    main()