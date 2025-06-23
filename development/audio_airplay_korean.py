#!/usr/bin/env python3
"""
Audio AirPlay Controller for Korean macOS
Uses accessibility API to find AirPlay controls
"""

import subprocess
import time
import json
from pathlib import Path


class KoreanAudioAirPlayController:
    def __init__(self):
        # Korean UI text mappings
        self.korean_mappings = {
            'airplay_button': '외장 재생 메뉴 보기',  # External Playback Menu
            'rewind': '되감기',
            'fast_forward': '앞으로 빨리감기',
            'mute': '소리 끔',
            'close': '닫기 버튼',
            'zoom': '확대/축소 버튼',
            'minimize': '최소화 버튼'
        }
        
    def find_and_activate_airplay(self):
        """Find and activate AirPlay for audio"""
        print("\n🎵 Korean Audio AirPlay Controller")
        print("=" * 50)
        
        # Check permissions
        if not self._check_accessibility_permission():
            print("❌ 접근성 권한이 필요합니다!")
            print("시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > 접근성")
            return False
        
        # Find AirPlay button
        print("\n🔍 AirPlay 버튼 찾는 중...")
        airplay_button = self._find_airplay_button()
        
        if not airplay_button:
            print("❌ AirPlay 버튼을 찾을 수 없습니다")
            return False
        
        print(f"✅ AirPlay 버튼 발견: {airplay_button['position']}")
        
        # Click AirPlay button
        print("\n🖱️ AirPlay 메뉴 열기...")
        self._click_at_position(airplay_button['position'])
        time.sleep(2)
        
        # Find and click Apple TV
        print("\n📺 Apple TV 옵션 찾는 중...")
        apple_tv = self._find_apple_tv_option()
        
        if apple_tv:
            print(f"✅ Apple TV 발견: {apple_tv['title']}")
            self._click_at_position(apple_tv['position'])
            print("\n✅ AirPlay 활성화 완료!")
            return True
        else:
            print("❌ Apple TV를 찾을 수 없습니다")
            # Close menu
            subprocess.run(['osascript', '-e', 
                          'tell application "System Events" to key code 53'])
            return False
    
    def _check_accessibility_permission(self):
        """Check accessibility permissions"""
        script = '''
        tell application "System Events"
            set isEnabled to UI elements enabled
            return isEnabled
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        return result.stdout.strip() == "true"
    
    def _find_airplay_button(self):
        """Find AirPlay button using Korean description"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                delay 0.5
                
                if exists window 1 then
                    tell window 1
                        set allButtons to every button
                        repeat with btn in allButtons
                            try
                                set btnDesc to description of btn
                                set btnPos to position of btn
                                set btnSize to size of btn
                                
                                if btnDesc contains "외장 재생" then
                                    return (item 1 of btnPos as string) & "," & (item 2 of btnPos as string) & "|" & (item 1 of btnSize as string) & "," & (item 2 of btnSize as string)
                                end if
                            end try
                        end repeat
                    end tell
                end if
                
                return ""
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            parts = result.stdout.strip().split('|')
            pos = parts[0].split(',')
            size = parts[1].split(',')
            
            return {
                'position': (int(pos[0]), int(pos[1])),
                'size': (int(size[0]), int(size[1])),
                'center': (int(pos[0]) + int(size[0])//2, int(pos[1]) + int(size[1])//2)
            }
        
        return None
    
    def _click_at_position(self, position):
        """Click at specific position using accessibility API"""
        x, y = position
        script = f'''
        tell application "System Events"
            click at {{{x}, {y}}}
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
    
    def _find_apple_tv_option(self):
        """Find Apple TV in the AirPlay menu"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                delay 0.5
                
                -- Look for menu items
                set menuItems to {}
                
                -- Check all windows for menu-like structures
                repeat with win in windows
                    try
                        -- Check for standard menu items
                        if exists menu item 1 of menu 1 of win then
                            set menuItemList to every menu item of menu 1 of win
                            repeat with mi in menuItemList
                                try
                                    set miTitle to title of mi
                                    set miPos to position of mi
                                    set end of menuItems to miTitle & "|" & (item 1 of miPos as string) & "," & (item 2 of miPos as string)
                                end try
                            end repeat
                        end if
                        
                        -- Check for checkboxes (common in AirPlay menus)
                        if exists checkbox 1 of win then
                            set checkboxList to every checkbox of win
                            repeat with cb in checkboxList
                                try
                                    set cbTitle to title of cb
                                    set cbPos to position of cb
                                    set end of menuItems to "CB:" & cbTitle & "|" & (item 1 of cbPos as string) & "," & (item 2 of cbPos as string)
                                end try
                            end repeat
                        end if
                        
                        -- Check for static text items
                        if exists static text 1 of win then
                            set textList to every static text of win
                            repeat with txt in textList
                                try
                                    set txtValue to value of txt
                                    set txtPos to position of txt
                                    
                                    -- Look for Apple TV related text
                                    if txtValue contains "Apple TV" or txtValue contains "TV" then
                                        set end of menuItems to "TXT:" & txtValue & "|" & (item 1 of txtPos as string) & "," & (item 2 of txtPos as string)
                                    end if
                                end try
                            end repeat
                        end if
                    end try
                end repeat
                
                return menuItems
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            items = []
            lines = result.stdout.strip().split(', ')
            
            for line in lines:
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    title = parts[0].replace('CB:', '').replace('TXT:', '')
                    pos_parts = parts[1].split(',')
                    
                    items.append({
                        'title': title,
                        'position': (int(pos_parts[0]), int(pos_parts[1]))
                    })
            
            # Look for Apple TV
            for item in items:
                if 'tv' in item['title'].lower() or 'apple' in item['title'].lower():
                    return item
            
            # If not found, return the second item (first is usually "이 컴퓨터")
            if len(items) > 1:
                return items[1]
        
        return None
    
    def save_coordinates(self):
        """Save detected coordinates for future use"""
        print("\n💾 좌표 감지 및 저장...")
        
        # Find AirPlay button
        airplay_button = self._find_airplay_button()
        if not airplay_button:
            print("❌ AirPlay 버튼을 찾을 수 없습니다")
            return False
        
        # Click and find Apple TV
        self._click_at_position(airplay_button['center'])
        time.sleep(2)
        
        apple_tv = self._find_apple_tv_option()
        
        # Close menu
        subprocess.run(['osascript', '-e', 
                      'tell application "System Events" to key code 53'])
        
        if not apple_tv:
            # Use estimated position
            apple_tv = {
                'title': 'Apple TV (추정)',
                'position': (airplay_button['center'][0] + 50, airplay_button['center'][1] + 70)
            }
        
        # Save results
        results = {
            'airplay_button': {
                'position': airplay_button['position'],
                'center': airplay_button['center'],
                'size': airplay_button['size']
            },
            'apple_tv': {
                'position': apple_tv['position'],
                'title': apple_tv['title']
            },
            'detection_method': 'korean_accessibility_api',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        settings_file = Path.home() / '.korean_audio_airplay_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 설정 저장 완료: {settings_file}")
        print(f"\n📍 감지된 좌표:")
        print(f"   AirPlay 버튼: {airplay_button['center']}")
        print(f"   Apple TV: {apple_tv['position']}")
        
        return True


def main():
    controller = KoreanAudioAirPlayController()
    
    print("🎵 한국어 macOS Audio AirPlay Controller")
    print("\n옵션:")
    print("1. AirPlay 자동 활성화")
    print("2. 좌표 감지 및 저장")
    print("3. 저장된 좌표로 AirPlay 활성화")
    
    # For testing, we'll use option 1
    print("\n선택: 1 (자동 활성화)")
    
    # Make sure QuickTime is playing
    print("\n▶️ QuickTime에서 재생 확인...")
    play_script = '''
    tell application "QuickTime Player"
        if exists document 1 then
            if playing of document 1 is false then
                play document 1
            end if
            return "playing"
        else
            return "no document"
        end if
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', play_script], 
                          capture_output=True, text=True)
    
    if "no document" in result.stdout:
        print("❌ QuickTime에 열린 파일이 없습니다")
        print("오디오 파일을 먼저 열어주세요")
        return
    
    # Activate AirPlay
    success = controller.find_and_activate_airplay()
    
    if success:
        print("\n🎉 성공!")
    else:
        print("\n💡 좌표 저장 옵션을 시도해보세요")
        controller.save_coordinates()


if __name__ == "__main__":
    main()