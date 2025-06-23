-- Test script to check QuickTime Player behavior
-- Run this to diagnose the issue

on run
    -- Test with a simple dialog first
    display dialog "Starting QuickTime test..." buttons {"OK"} default button 1
    
    tell application "QuickTime Player"
        activate
        
        -- Create a test to see QuickTime's behavior
        display dialog "QuickTime Player activated. Number of open documents: " & (count of documents) buttons {"OK"} default button 1
    end tell
    
    -- Ask user to select a single file for testing
    set testFile to choose file with prompt "Select ONE video file to test:" of type {"public.movie"}
    
    tell application "QuickTime Player"
        activate
        
        -- Open the file
        set testMovie to open testFile
        display dialog "Movie opened. Starting playback..." buttons {"OK"} default button 1
        
        -- Play the movie
        play testMovie
        
        -- Wait a moment
        delay 3
        
        -- Check playing status
        set isPlaying to playing of testMovie
        display dialog "Is playing: " & isPlaying buttons {"OK"} default button 1
        
        -- Get duration
        set movieDuration to duration of testMovie
        display dialog "Movie duration: " & movieDuration & " seconds" buttons {"OK"} default button 1
        
        -- Ask if user wants to close
        display dialog "Test complete. Close the movie?" buttons {"Yes", "No"} default button 1
        if button returned of result is "Yes" then
            close testMovie saving no
        end if
    end tell
end run