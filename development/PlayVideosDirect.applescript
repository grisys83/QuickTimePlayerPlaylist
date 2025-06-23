-- Direct QuickTime Player Controller
-- Uses presented documents to ensure proper playback

on run
    -- Get files from Finder selection
    tell application "Finder"
        set selectedFiles to selection as alias list
        if selectedFiles is {} then
            display dialog "Please select video files in Finder first" buttons {"OK"} default button 1
            return
        end if
    end tell
    
    -- Play each file
    repeat with videoFile in selectedFiles
        playVideoAndWait(videoFile)
    end repeat
    
    display notification "All videos have been played" with title "QuickTime Playlist"
end run

-- Function to play video and wait for completion
on playVideoAndWait(videoFile)
    tell application "QuickTime Player"
        activate
        
        -- Open the video
        open videoFile
        
        -- Wait for the document to be ready
        delay 1
        
        -- Get the front document (most recently opened)
        if (count of documents) > 0 then
            set currentMovie to front document
            
            -- Present the movie (ensures it's ready to play)
            present currentMovie
            
            -- Play the movie
            play currentMovie
            
            -- Wait for playback to complete
            repeat
                delay 2
                try
                    -- Check if still playing
                    if not (playing of currentMovie) then
                        exit repeat
                    end if
                on error
                    -- Document might be closed
                    exit repeat
                end try
            end repeat
            
            -- Close the document
            try
                close currentMovie saving no
            end try
        end if
    end tell
end playVideoAndWait