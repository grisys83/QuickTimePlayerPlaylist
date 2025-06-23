-- Test various QuickTime Player commands and properties

tell application "QuickTime Player"
    -- Get application properties
    log "=== Application Properties ==="
    log "Version: " & (version as string)
    log "Name: " & (name as string)
    
    -- Test if we have any documents open
    if (count of documents) > 0 then
        set doc to document 1
        
        log "=== Document Properties ==="
        log "Name: " & (name of doc)
        log "Path: " & (path of doc)
        
        -- Get all properties of the document
        try
            properties of doc
        on error errMsg
            log "Error getting document properties: " & errMsg
        end try
        
        -- Check for audio/video output options
        try
            log "=== Testing Output Commands ==="
            -- These might not work but let's try
            get audio output of doc
        on error errMsg
            log "No 'audio output' property: " & errMsg
        end try
        
        try
            get video output of doc
        on error errMsg
            log "No 'video output' property: " & errMsg
        end try
        
        try
            get output device of doc
        on error errMsg
            log "No 'output device' property: " & errMsg
        end try
        
        try
            get airplay device of doc
        on error errMsg
            log "No 'airplay device' property: " & errMsg
        end try
    else
        log "No documents open"
    end if
    
    -- Check for device-related elements
    log "=== Available Devices ==="
    try
        log "Video recording devices: " & (count of video recording devices)
        repeat with vdev in video recording devices
            log "  - " & (name of vdev) & " (ID: " & (id of vdev) & ")"
        end repeat
    on error errMsg
        log "Error listing video devices: " & errMsg
    end try
    
    try
        log "Audio recording devices: " & (count of audio recording devices)
        repeat with adev in audio recording devices
            log "  - " & (name of adev) & " (ID: " & (id of adev) & ")"
        end repeat
    on error errMsg
        log "Error listing audio devices: " & errMsg
    end try
end tell