#!/usr/bin/osascript
(*
    Direct AirPlay enabler using AppleScript
    Maintains focus throughout the process
*)

on run
    tell application "QuickTime Player"
        activate
        
        -- Ensure we have a window
        if (count of windows) is 0 then
            display dialog "Please open a video in QuickTime Player first"
            return
        end if
    end tell
    
    -- Use System Events to control QuickTime without losing focus
    tell application "System Events"
        tell process "QuickTime Player"
            set frontmost to true
            
            -- Get window position and size
            set {x, y} to position of window 1
            set {w, h} to size of window 1
            
            -- Show controls by moving mouse to bottom of window
            set controlX to x + (w / 2)
            set controlY to y + h - 100
            
            do shell script "cliclick m:" & controlX & "," & controlY
            delay 0.5
            
            -- Move mouse slightly to keep controls visible
            do shell script "cliclick m:" & (controlX + 5) & "," & controlY
            delay 0.3
            
            -- Click AirPlay icon (adjust these values based on your layout)
            -- AirPlay is typically on the right side of the control bar
            set airplayX to x + w - 150
            set airplayY to y + h - 50
            
            do shell script "cliclick c:" & airplayX & "," & airplayY
            delay 1
            
            -- Click Apple TV checkbox
            -- Based on user observation: checkbox is offset from AirPlay position
            set checkboxX to airplayX - 80
            set checkboxY to airplayY - 160
            
            do shell script "cliclick c:" & checkboxX & "," & checkboxY
            
            display notification "AirPlay enabled" with title "QuickTime"
        end tell
    end tell
end run