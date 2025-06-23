#!/usr/bin/env python3
"""
QuickTime Window Controller
정해진 위치와 크기로 QuickTime 창 열기
"""

import subprocess
import time
from pathlib import Path

class QuickTimeWindowController:
    def __init__(self):
        # 기본 창 설정 (논리적 픽셀)
        self.default_settings = {
            'x': 100,        # 왼쪽에서 100픽셀
            'y': 100,        # 위에서 100픽셀
            'width': 800,    # 너비 800픽셀
            'height': 600    # 높이 600픽셀
        }
        
    def set_window(self, x=None, y=None, width=None, height=None):
        """QuickTime 창 위치와 크기 설정"""
        # 기본값 사용
        x = x or self.default_settings['x']
        y = y or self.default_settings['y']
        width = width or self.default_settings['width']
        height = height or self.default_settings['height']
        
        script = f'''
        tell application "QuickTime Player"
            activate
            if (count windows) > 0 then
                tell window 1
                    set bounds to {{{x}, {y}, {x + width}, {y + height}}}
                end tell
            end if
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
        print(f"✅ QuickTime 창 설정: ({x}, {y}) 크기: {width}x{height}")
    
    def open_with_video(self, video_path, x=None, y=None, width=None, height=None):
        """비디오 파일과 함께 열기"""
        # 먼저 비디오 열기
        if video_path and Path(video_path).exists():
            subprocess.run(['open', '-a', 'QuickTime Player', str(video_path)])
            time.sleep(1)  # 파일 로딩 대기
        else:
            # 빈 QuickTime 열기
            subprocess.run(['open', '-a', 'QuickTime Player'])
            time.sleep(0.5)
        
        # 창 위치와 크기 설정
        self.set_window(x, y, width, height)
    
    def center_on_screen(self, width=800, height=600):
        """화면 중앙에 배치"""
        # 화면 크기 가져오기
        script = '''
        tell application "Finder"
            get bounds of window of desktop
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.stdout:
            bounds = result.stdout.strip().split(', ')
            screen_width = int(bounds[2])
            screen_height = int(bounds[3])
            
            # 중앙 계산
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            self.set_window(x, y, width, height)
            print(f"✅ 화면 중앙 배치: ({x}, {y})")
    
    def maximize_window(self):
        """창 최대화"""
        script = '''
        tell application "QuickTime Player"
            activate
            tell application "System Events"
                tell process "QuickTime Player"
                    set value of attribute "AXFullScreen" of window 1 to true
                end tell
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
        print("✅ QuickTime 창 최대화")
    
    def get_current_bounds(self):
        """현재 창 위치와 크기 가져오기"""
        script = '''
        tell application "QuickTime Player"
            if (count windows) > 0 then
                get bounds of window 1
            end if
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.stdout:
            bounds = result.stdout.strip().split(', ')
            return {
                'x': int(bounds[0]),
                'y': int(bounds[1]),
                'width': int(bounds[2]) - int(bounds[0]),
                'height': int(bounds[3]) - int(bounds[1])
            }
        return None

def save_quicktime_preset(name, x, y, width, height):
    """QuickTime 창 프리셋 저장"""
    import json
    from pathlib import Path
    
    presets_file = Path.home() / '.quicktime_presets.json'
    
    # 기존 프리셋 로드
    if presets_file.exists():
        with open(presets_file, 'r') as f:
            presets = json.load(f)
    else:
        presets = {}
    
    # 새 프리셋 추가
    presets[name] = {
        'x': x,
        'y': y,
        'width': width,
        'height': height
    }
    
    # 저장
    with open(presets_file, 'w') as f:
        json.dump(presets, f, indent=2)
    
    print(f"💾 프리셋 '{name}' 저장됨")

def load_quicktime_preset(name):
    """저장된 프리셋 로드"""
    import json
    from pathlib import Path
    
    presets_file = Path.home() / '.quicktime_presets.json'
    
    if presets_file.exists():
        with open(presets_file, 'r') as f:
            presets = json.load(f)
            
        if name in presets:
            return presets[name]
    
    return None

def main():
    print("🎬 QuickTime Window Controller")
    print("=" * 50)
    
    controller = QuickTimeWindowController()
    
    print("\n옵션:")
    print("1. 기본 위치로 열기 (100, 100, 800x600)")
    print("2. 화면 중앙에 열기")
    print("3. 사용자 정의 위치")
    print("4. 현재 위치 저장하기")
    print("5. 저장된 프리셋 사용")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == '1':
        controller.open_with_video(None)
        
    elif choice == '2':
        controller.open_with_video(None)
        controller.center_on_screen()
        
    elif choice == '3':
        x = int(input("X 좌표: "))
        y = int(input("Y 좌표: "))
        width = int(input("너비: "))
        height = int(input("높이: "))
        controller.open_with_video(None, x, y, width, height)
        
    elif choice == '4':
        bounds = controller.get_current_bounds()
        if bounds:
            print(f"\n현재 위치: {bounds}")
            name = input("프리셋 이름: ")
            save_quicktime_preset(name, bounds['x'], bounds['y'], 
                                bounds['width'], bounds['height'])
        else:
            print("❌ QuickTime이 열려있지 않습니다")
            
    elif choice == '5':
        name = input("프리셋 이름: ")
        preset = load_quicktime_preset(name)
        if preset:
            controller.open_with_video(None, **preset)
        else:
            print(f"❌ 프리셋 '{name}'을 찾을 수 없습니다")

if __name__ == "__main__":
    main()