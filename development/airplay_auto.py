#!/usr/bin/env python3
"""
AirPlay Auto Enabler
템플릿과 타일 기반으로 자동 실행
"""

import subprocess
import time
import json
import cv2
import numpy as np
import pyautogui
from pathlib import Path

class AirPlayAuto:
    def __init__(self):
        self.template_config = Path.home() / '.airplay_templates.json'
        self.templates = {}
        self.scale_factor = self.get_scale_factor()
        self.load_templates()
        
    def get_scale_factor(self):
        """Get Retina display scale factor"""
        try:
            logical_width, _ = pyautogui.size()
            screenshot = pyautogui.screenshot()
            physical_width = screenshot.width
            return physical_width / logical_width
        except:
            return 2.0  # Default for Retina
        
    def load_templates(self):
        """저장된 템플릿 로드"""
        if self.template_config.exists():
            with open(self.template_config, 'r') as f:
                self.templates = json.load(f)
                print(f"✅ 템플릿 로드 완료: {len(self.templates)}개")
        else:
            print("❌ 템플릿 설정이 없습니다")
            print("   template_creator_slow.py를 먼저 실행하세요")
            exit(1)
    
    def get_quicktime_window(self):
        """QuickTime 창 정보"""
        script = '''
        tell application "System Events"
            tell process "QuickTime Player"
                if exists window 1 then
                    set windowPos to position of window 1
                    set windowSize to size of window 1
                    return (item 1 of windowPos as string) & "," & ¬
                           (item 2 of windowPos as string) & "," & ¬
                           (item 1 of windowSize as string) & "," & ¬
                           (item 2 of windowSize as string)
                end if
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.stdout.strip():
            coords = result.stdout.strip().split(',')
            return {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
        return None
    
    def cv2_find_template(self, template_path, roi=None):
        """CV2로 템플릿 찾기"""
        if not Path(template_path).exists():
            return None
        
        # 스크린샷
        if roi:
            screenshot = pyautogui.screenshot(
                region=(roi['x'], roi['y'], roi['width'], roi['height'])
            )
        else:
            screenshot = pyautogui.screenshot()
        
        # CV2 변환
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 템플릿 로드
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        # 멀티스케일 매칭
        best_match = None
        best_val = 0
        
        for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
            # 리사이즈
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # 매칭
            result = cv2.matchTemplate(screenshot_cv2, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val and max_val > 0.7:
                best_val = max_val
                h, w = resized.shape[:2]
                
                # 물리적 픽셀 좌표 (템플릿 매칭 결과)
                phys_x = max_loc[0] + w // 2
                phys_y = max_loc[1] + h // 2
                
                # 논리적 픽셀 좌표로 변환
                logical_x = phys_x / self.scale_factor
                logical_y = phys_y / self.scale_factor
                
                if roi:
                    logical_x += roi['x']
                    logical_y += roi['y']
                
                best_match = {
                    'x': logical_x,
                    'y': logical_y,
                    'confidence': max_val
                }
        
        return best_match
    
    def enable_airplay(self):
        """AirPlay 자동 활성화"""
        print("🚀 AirPlay Auto Enabler")
        print("=" * 50)
        
        # QuickTime 확인
        window = self.get_quicktime_window()
        if not window:
            print("❌ QuickTime이 실행되지 않았습니다")
            return False
        
        print(f"✅ QuickTime 창: {window['width']}x{window['height']}")
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 컨트롤 표시
        print("📍 컨트롤 표시...")
        control_x = window['x'] + window['width'] // 2
        control_y = window['y'] + window['height'] - 100
        pyautogui.moveTo(control_x, control_y, duration=0.5)
        time.sleep(1)
        
        # 1. AirPlay 버튼 찾기
        print("\n🔍 AirPlay 버튼 검색...")
        
        if 'airplay_button' in self.templates:
            template_path = self.templates['airplay_button']['path']
            
            # 하단 영역에서 검색
            roi = {
                'x': window['x'],
                'y': window['y'] + window['height'] - 200,
                'width': window['width'],
                'height': 200
            }
            
            airplay_pos = self.cv2_find_template(template_path, roi)
            
            if airplay_pos:
                print(f"   ✅ 발견: ({airplay_pos['x']}, {airplay_pos['y']})")
                print(f"   신뢰도: {airplay_pos['confidence']:.3f}")
            else:
                # 저장된 위치 사용
                saved_pos = self.templates['airplay_button']['captured_at']
                airplay_pos = {'x': saved_pos['x'], 'y': saved_pos['y']}
                print(f"   ⚠️ 저장된 위치 사용: ({airplay_pos['x']}, {airplay_pos['y']})")
        else:
            print("   ❌ AirPlay 템플릿 없음")
            return False
        
        # AirPlay 클릭
        print(f"\n📍 AirPlay 클릭...")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        
        print("⏳ 메뉴 대기...")
        time.sleep(2)
        
        # 2. 체크박스 클릭
        print("\n🔍 체크박스 위치 계산...")
        
        if 'apple_tv_icon' in self.templates:
            template_info = self.templates['apple_tv_icon']
            
            # Apple TV 아이콘 찾기 (옵션)
            template_path = template_info['path']
            appletv_pos = self.cv2_find_template(template_path)
            
            if appletv_pos:
                print(f"   ✅ Apple TV 발견: ({appletv_pos['x']}, {appletv_pos['y']})")
                
                # 오프셋 적용
                if 'offsets' in template_info and 'checkbox' in template_info['offsets']:
                    offset = template_info['offsets']['checkbox']
                    checkbox_x = appletv_pos['x'] + offset['x']
                    checkbox_y = appletv_pos['y'] + offset['y']
                else:
                    # 기본 오프셋
                    checkbox_x = appletv_pos['x'] + 246
                    checkbox_y = appletv_pos['y']
            else:
                # 저장된 절대 위치 사용
                if 'offsets' in template_info and 'checkbox' in template_info['offsets']:
                    checkbox_pos = template_info['offsets']['checkbox']['absolute']
                    checkbox_x = checkbox_pos['x']
                    checkbox_y = checkbox_pos['y']
                    print(f"   ⚠️ 저장된 체크박스 위치 사용")
                else:
                    print("   ❌ 체크박스 위치 정보 없음")
                    return False
        else:
            print("   ❌ Apple TV 템플릿 없음")
            return False
        
        print(f"\n📍 체크박스 클릭: ({checkbox_x}, {checkbox_y})")
        pyautogui.click(checkbox_x, checkbox_y)
        
        print("\n✅ AirPlay 활성화 완료!")
        return True
    
    def quick_enable(self):
        """빠른 활성화 (저장된 위치만 사용)"""
        print("⚡ Quick AirPlay Enable")
        print("=" * 50)
        
        # QuickTime 활성화
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(0.5)
        
        # 컨트롤 표시
        window = self.get_quicktime_window()
        if window:
            pyautogui.moveTo(
                window['x'] + window['width'] // 2,
                window['y'] + window['height'] - 100,
                duration=0.3
            )
            time.sleep(0.5)
        
        # AirPlay 클릭
        if 'airplay_button' in self.templates:
            pos = self.templates['airplay_button']['captured_at']
            print(f"📍 AirPlay: ({pos['x']}, {pos['y']})")
            pyautogui.click(pos['x'], pos['y'])
            time.sleep(1.5)
        
        # 체크박스 클릭
        if 'apple_tv_icon' in self.templates:
            if 'offsets' in self.templates['apple_tv_icon']:
                if 'checkbox' in self.templates['apple_tv_icon']['offsets']:
                    pos = self.templates['apple_tv_icon']['offsets']['checkbox']['absolute']
                    print(f"📍 Checkbox: ({pos['x']}, {pos['y']})")
                    pyautogui.click(pos['x'], pos['y'])
        
        print("✅ 완료!")

def main():
    print("🎬 QuickTime AirPlay Auto")
    
    enabler = AirPlayAuto()
    
    # 템플릿 정보 표시
    print("\n📊 로드된 템플릿:")
    for name in enabler.templates:
        print(f"   - {name}")
    
    print("\n옵션:")
    print("1. 자동 활성화 (템플릿 매칭)")
    print("2. 빠른 활성화 (저장된 위치)")
    
    # 자동으로 1번 실행
    print("\n3초 후 자동 활성화 시작...")
    time.sleep(3)
    
    enabler.enable_airplay()

if __name__ == "__main__":
    main()