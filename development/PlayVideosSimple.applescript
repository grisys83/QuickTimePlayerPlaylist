-- Simple QuickTime Video Player for Automator
-- Handles file paths more reliably

on run {input, parameters}
    -- Check if input is provided
    if input is {} or input is missing value then
        display dialog "No files selected. Please select video files first." buttons {"OK"} default button 1
        return
    end if
    
    -- Process each file
    repeat with fileItem in input
        try
            -- Convert to proper file reference
            set videoFile to fileItem as alias
            
            tell application "QuickTime Player"
                activate
                
                -- Open and play the video
                set currentMovie to open videoFile
                play currentMovie
                
                -- Wait until the video finishes
                repeat while (playing of currentMovie is true)
                    delay 1
                end repeat
                
                -- Close the movie
                close currentMovie saving no
            end tell
            
        on error errMsg
            display dialog "Error playing file: " & errMsg buttons {"OK"} default button 1
        end try
    end repeat
    
    return input
end run