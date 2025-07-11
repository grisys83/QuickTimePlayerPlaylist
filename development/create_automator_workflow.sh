#!/bin/bash
# Automator 워크플로우 생성 스크립트

cat << 'EOF' > QuickTimeHTTPPlaylist.workflow
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>1.1.2</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run AppleScript.action</string>
                <key>ActionName</key>
                <string>Run AppleScript</string>
                <key>ActionParameters</key>
                <dict>
                    <key>source</key>
                    <string>on run {input, parameters}
    
    -- HTTP URL과 로컬 경로 설정
    set httpURL to "http://grisys.synology.me/video.mp4"
    set localPath to "/Volumes/web/video.mp4"
    
    -- 원본 백업
    do shell script "cp '" & localPath & "' '" & localPath & ".backup' 2>/dev/null || true"
    
    -- 입력받은 비디오 파일들 처리
    repeat with videoFile in input
        set videoPath to POSIX path of videoFile
        
        -- 파일 교체
        do shell script "cp '" & videoPath & "' '" & localPath & "'"
        delay 1
        
        -- QuickTime에서 재생
        tell application "QuickTime Player"
            if (count documents) > 0 then
                close every document
            end if
            
            delay 0.5
            open location httpURL
            delay 2
            
            tell document 1
                play
                repeat while (playing is true)
                    delay 1
                end repeat
            end tell
        end tell
    end repeat
    
    -- 원본 복원
    do shell script "mv '" & localPath & ".backup' '" & localPath & "' 2>/dev/null || true"
    
    -- QuickTime 종료
    tell application "QuickTime Player" to quit
    
    return input
end run</string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.Automator.RunScript</string>
                <key>CFBundleVersion</key>
                <string>1.1.2</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunScriptAction</string>
                <key>InputUUID</key>
                <string>E2D6BEB4-2E3A-4FE1-9DCA-3B4D96CED3E3</string>
                <key>Keywords</key>
                <array>
                    <string>Run</string>
                </array>
                <key>OutputUUID</key>
                <string>92D0D73C-E21C-4FD1-91D1-7B4F17448C2D</string>
                <key>UUID</key>
                <string>0A0F3B2C-7B3E-44F7-B7DE-2B9308313E5F</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <string>on run {input, parameters}
    
    (* Your script goes here *)
    
    return input
end run</string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>309.000000:316.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run AppleScript.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.application</string>
    </dict>
</dict>
</plist>
EOF

echo "Automator 워크플로우 생성 완료: QuickTimeHTTPPlaylist.workflow"
echo ""
echo "사용 방법:"
echo "1. Finder에서 QuickTimeHTTPPlaylist.workflow 더블클릭"
echo "2. 비디오 파일들을 드래그 앤 드롭"
echo "3. 또는 Automator에서 열어서 Application으로 저장"