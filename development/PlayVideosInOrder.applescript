-- QuickTime Sequential Video Player
-- Select multiple MP4 files in Finder and play them in order

on run
    -- Get selected files from Finder
    tell application "Finder"
        set selectedFiles to selection as alias list
        if selectedFiles is {} then
            display dialog "Please select video files in Finder first" buttons {"OK"} default button 1
            return
        end if
    end tell
    
    -- Play each file sequentially
    repeat with videoFile in selectedFiles
        playVideo(videoFile)
    end repeat
    
    display notification "All videos have been played" with title "QuickTime Playlist"
end run

-- Function to play a single video file
on playVideo(videoFile)
    tell application "QuickTime Player"
        activate
        
        -- Open the video file
        set currentDoc to open videoFile
        
        -- Start playing
        play currentDoc
        
        -- Wait for video to finish
        repeat while (playing of currentDoc)
            delay 0.5
        end repeat
        
        -- Close the document
        close currentDoc saving no
    end tell
end playVideo

-- Handler for drag and drop
on open droppedItems
    repeat with videoFile in droppedItems
        playVideo(videoFile)
    end repeat
    
    display notification "All videos have been played" with title "QuickTime Playlist"
end open