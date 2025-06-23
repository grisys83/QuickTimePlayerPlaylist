-- Test UI automation for AirPlay control
tell application "System Events"
    tell process "QuickTime Player"
        set frontmost to true
        delay 1
        
        -- Try to access menu bar
        try
            click menu bar item "View" of menu bar 1
            delay 0.5
            
            -- Look for AirPlay-related menu items
            set menuItems to name of every menu item of menu "View" of menu bar item "View" of menu bar 1
            repeat with itemName in menuItems
                if itemName contains "AirPlay" or itemName contains "Output" then
                    log "Found: " & itemName
                end if
            end repeat
        on error errMsg
            log "Error accessing View menu: " & errMsg
        end try
        
        -- Try keyboard shortcut for View menu
        try
            keystroke "v" using command down
            delay 0.5
        on error
            log "Could not use keyboard shortcut"
        end try
    end tell
end tell