-- Fixed QuickTime Video Player for Automator
-- Properly waits for videos to load and play

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
                
                -- Open the video
                set currentMovie to open videoFile
                
                -- Wait for the movie to load
                delay 2
                
                -- Play the movie
                play currentMovie
                
                -- Get the duration and wait
                set movieDuration to duration of currentMovie
                set currentTime to current time of currentMovie
                
                -- Wait until the movie finishes
                repeat while currentTime < movieDuration
                    delay 1
                    try
                        set currentTime to current time of currentMovie
                    on error
                        -- Movie might have been closed
                        exit repeat
                    end try
                end repeat
                
                -- Close the movie
                try
                    close currentMovie saving no
                end try
            end tell
            
        on error errMsg
            display dialog "Error playing file: " & errMsg buttons {"OK"} default button 1
        end try
    end repeat
    
    return input
end run