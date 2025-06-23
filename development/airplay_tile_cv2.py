#!/usr/bin/env python3
"""
Tile-based AirPlay with CV2
타일 기반 ROI + OpenCV 템플릿 매칭
"""

import subprocess
import time
import json
import cv2
import numpy as np
import pyautogui
from pathlib import Path
from PIL import Image, ImageDraw

class TileCV2AirPlay:
    def __init__(self):
        self.grid_size = 10
        self.window_info = None
        self.config_file = Path.home() / '.airplay_tile_cv2_config.json'
        self.template_dir = Path(__file__).parent / "templates"
        self.scale_factor = self.get_scale_factor()
        
    def get_scale_factor(self):
        """Retina 디스플레이 스케일 팩터"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        return screenshot.width / logical_width
    
    def get_window_info(self):
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
            self.window_info = {
                'x': int(coords[0]),
                'y': int(coords[1]),
                'width': int(coords[2]),
                'height': int(coords[3])
            }
            
            self.tile_width = self.window_info['width'] / self.grid_size
            self.tile_height = self.window_info['height'] / self.grid_size
            
            return True
        return False
    
    def get_tile_roi(self, row_start, col_start, row_end, col_end):
        """타일 범위를 ROI로 변환"""
        x1 = self.window_info['x'] + col_start * self.tile_width
        y1 = self.window_info['y'] + row_start * self.tile_height
        x2 = self.window_info['x'] + (col_end + 1) * self.tile_width
        y2 = self.window_info['y'] + (row_end + 1) * self.tile_height
        
        return {
            'x': int(x1),
            'y': int(y1),
            'width': int(x2 - x1),
            'height': int(y2 - y1)
        }
    
    def cv2_find_in_roi(self, template_path, roi):
        """ROI 내에서 CV2로 템플릿 찾기"""
        if not Path(template_path).exists():
            return None
        
        # ROI 스크린샷 - PyAutoGUI는 물리적 픽셀로 캡처
        screenshot = pyautogui.screenshot(
            region=(roi['x'], roi['y'], roi['width'], roi['height'])
        )
        
        # CV2로 변환
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 템플릿 로드
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        # 멀티스케일 매칭
        best_match = None
        best_val = 0
        
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        
        for scale in scales:
            # 템플릿 리사이즈
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # 매칭
            result = cv2.matchTemplate(screenshot_cv2, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val and max_val > 0.7:
                best_val = max_val
                h, w = resized.shape[:2]
                
                # 물리적 픽셀 좌표 (스크린샷 내)
                phys_x = max_loc[0] + w // 2
                phys_y = max_loc[1] + h // 2
                
                # 논리적 픽셀 좌표로 변환
                logical_x = roi['x'] + phys_x / self.scale_factor
                logical_y = roi['y'] + phys_y / self.scale_factor
                
                best_match = {
                    'x': logical_x,
                    'y': logical_y,
                    'confidence': max_val,
                    'scale': scale
                }
        
        if best_match:
            # 타일 위치 계산
            tile_col = int((best_match['x'] - self.window_info['x']) / self.tile_width)
            tile_row = int((best_match['y'] - self.window_info['y']) / self.tile_height)
            best_match['tile'] = (tile_row, tile_col)
        
        return best_match
    
    def visualize_search(self, roi, found_pos=None):
        """검색 영역 시각화"""
        screenshot = pyautogui.screenshot()
        img = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        draw = ImageDraw.Draw(img)
        
        # ROI 그리기
        draw.rectangle([roi['x'], roi['y'], 
                       roi['x'] + roi['width'], 
                       roi['y'] + roi['height']], 
                       outline='yellow', width=3)
        
        # 찾은 위치 표시
        if found_pos:
            draw.ellipse([found_pos['x'] - 10, found_pos['y'] - 10,
                         found_pos['x'] + 10, found_pos['y'] + 10],
                         outline='green', width=3)
        
        # 저장
        viz_path = Path.home() / f"airplay_search_{time.time():.0f}.png"
        img.save(viz_path)
        print(f"   💾 시각화: {viz_path}")
    
    def enable_airplay(self):
        """타일 + CV2 기반 AirPlay 활성화"""
        print("🚀 Tile-based AirPlay with CV2")
        print("=" * 50)
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 창 정보
        if not self.get_window_info():
            print("❌ QuickTime 창을 찾을 수 없습니다")
            return
        
        print(f"📐 창 크기: {self.window_info['width']}x{self.window_info['height']}")
        print(f"📐 타일 크기: {self.tile_width:.1f}x{self.tile_height:.1f}")
        
        # 컨트롤 표시 - 타일 (8,5)
        control_roi = self.get_tile_roi(8, 5, 8, 5)
        control_x = control_roi['x'] + control_roi['width'] // 2
        control_y = control_roi['y'] + control_roi['height'] // 2
        
        print(f"\n📍 컨트롤 표시: 타일 (8,5) = ({control_x}, {control_y})")
        pyautogui.moveTo(control_x, control_y, duration=0.5)
        time.sleep(0.8)
        
        # AirPlay 검색 영역 - 하단 2행, 우측 4열
        print("\n🔍 AirPlay 버튼 검색...")
        airplay_roi = self.get_tile_roi(8, 6, 9, 9)
        print(f"   검색 영역: 타일 (8-9, 6-9)")
        print(f"   ROI: {airplay_roi}")
        
        # AirPlay 템플릿 찾기
        airplay_template = self.template_dir / "airplay_icon.png"
        airplay_pos = None
        
        if airplay_template.exists():
            airplay_pos = self.cv2_find_in_roi(airplay_template, airplay_roi)
            
            if airplay_pos:
                print(f"   ✅ 발견: 타일 {airplay_pos['tile']}")
                print(f"   좌표: ({airplay_pos['x']}, {airplay_pos['y']})")
                print(f"   신뢰도: {airplay_pos['confidence']:.3f}")
        
        if not airplay_pos:
            # 폴백: 타일 (9, 8) 사용
            fallback_roi = self.get_tile_roi(9, 8, 9, 8)
            airplay_pos = {
                'x': fallback_roi['x'] + fallback_roi['width'] // 2,
                'y': fallback_roi['y'] + fallback_roi['height'] // 2,
                'tile': (9, 8)
            }
            print(f"   ⚠️ 폴백: 타일 {airplay_pos['tile']} 사용")
        
        # 시각화
        self.visualize_search(airplay_roi, airplay_pos)
        
        # AirPlay 클릭
        print(f"\n📍 AirPlay 클릭...")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        
        print("⏳ 메뉴 대기...")
        time.sleep(2)
        
        # 체크박스 검색 영역 - 중앙 6x6 타일
        print("\n🔍 체크박스 검색...")
        menu_roi = self.get_tile_roi(2, 2, 7, 7)
        print(f"   검색 영역: 타일 (2-7, 2-7)")
        
        # Apple TV 아이콘 찾기
        appletv_template = self.template_dir / "apple_tv_icon.png"
        appletv_pos = None
        
        if appletv_template.exists():
            appletv_pos = self.cv2_find_in_roi(appletv_template, menu_roi)
            
            if appletv_pos:
                print(f"   ✅ Apple TV 발견: 타일 {appletv_pos['tile']}")
                
                # 체크박스는 오른쪽에
                checkbox_x = appletv_pos['x'] + 246
                checkbox_y = appletv_pos['y']
                
                print(f"\n📍 체크박스 클릭: ({checkbox_x}, {checkbox_y})")
                pyautogui.click(checkbox_x, checkbox_y)
                
                print("\n✅ 완료!")
                return
        
        # 수동 모드
        print("\n🎯 수동 모드")
        print("   체크박스에 마우스를 올려주세요...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            tile_col = int((x - self.window_info['x']) / self.tile_width)
            tile_row = int((y - self.window_info['y']) / self.tile_height)
            print(f"\r   {i}초... 타일 ({tile_row},{tile_col})  ", end='', flush=True)
            time.sleep(1)
        
        print("\n   클릭!")
        pyautogui.click()
        
        print("\n✅ 완료!")

def main():
    print("🎯 Tile-based AirPlay with OpenCV")
    print("\n특징:")
    print("- 10x10 타일 그리드로 상대적 위치 계산")
    print("- OpenCV 멀티스케일 템플릿 매칭")
    print("- 시각화된 검색 영역")
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    enabler = TileCV2AirPlay()
    enabler.enable_airplay()

if __name__ == "__main__":
    main()