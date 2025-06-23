#!/usr/bin/env python3
"""
Tile-based AirPlay Enabler
QuickTime 창을 10x10 타일로 나누어 상대적 위치로 UI 요소 찾기
"""

import subprocess
import time
import json
from pathlib import Path
import pyautogui
from PIL import Image, ImageDraw

class TileBasedAirPlayEnabler:
    def __init__(self):
        self.grid_size = 10  # 10x10 grid
        self.window_info = None
        self.tiles = {}
        self.config_file = Path.home() / '.airplay_tile_config.json'
        self.debug_mode = True
        
    def get_window_info(self):
        """QuickTime 창 정보 가져오기"""
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
            
            # 타일 크기 계산
            self.tile_width = self.window_info['width'] / self.grid_size
            self.tile_height = self.window_info['height'] / self.grid_size
            
            print(f"📐 창 정보: {self.window_info}")
            print(f"📐 타일 크기: {self.tile_width:.1f} x {self.tile_height:.1f}")
            
            return True
        return False
    
    def get_tile_coords(self, row, col):
        """타일 좌표 계산 (0-indexed)"""
        if not self.window_info:
            return None
        
        x = self.window_info['x'] + (col * self.tile_width)
        y = self.window_info['y'] + (row * self.tile_height)
        
        return {
            'x': int(x),
            'y': int(y),
            'width': int(self.tile_width),
            'height': int(self.tile_height),
            'center_x': int(x + self.tile_width / 2),
            'center_y': int(y + self.tile_height / 2)
        }
    
    def get_roi_from_tiles(self, start_row, start_col, end_row, end_col):
        """여러 타일을 합쳐서 ROI 생성"""
        if not self.window_info:
            return None
        
        start_tile = self.get_tile_coords(start_row, start_col)
        end_tile = self.get_tile_coords(end_row, end_col)
        
        return {
            'x': start_tile['x'],
            'y': start_tile['y'],
            'width': end_tile['x'] + end_tile['width'] - start_tile['x'],
            'height': end_tile['y'] + end_tile['height'] - start_tile['y']
        }
    
    def define_rois(self):
        """타일 기반 ROI 정의"""
        rois = {}
        
        # 1. Control Bar ROI - 하단 2개 행 (8-9), 전체 열 (0-9)
        rois['control_bar'] = self.get_roi_from_tiles(8, 0, 9, 9)
        
        # 2. AirPlay Area ROI - 하단 2개 행 (8-9), 우측 4개 열 (6-9)
        rois['airplay_area'] = self.get_roi_from_tiles(8, 6, 9, 9)
        
        # 3. Menu ROI - 중앙 6개 행 (2-7), 중앙 6개 열 (2-7)
        rois['menu_area'] = self.get_roi_from_tiles(2, 2, 7, 7)
        
        # 4. Full Control Area - 하단 5개 행 (5-9), 중앙 6개 열 (2-7)
        rois['control_area'] = self.get_roi_from_tiles(5, 2, 9, 7)
        
        return rois
    
    def visualize_grid(self, highlight_rois=None):
        """그리드와 ROI 시각화"""
        if not self.window_info:
            return
        
        print("\n📸 그리드 시각화...")
        
        # 전체 스크린샷
        screenshot = pyautogui.screenshot()
        img = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        draw = ImageDraw.Draw(img)
        
        # 그리드 그리기
        for row in range(self.grid_size + 1):
            y = self.window_info['y'] + row * self.tile_height
            draw.line([(self.window_info['x'], y), 
                      (self.window_info['x'] + self.window_info['width'], y)], 
                      fill='gray', width=1)
        
        for col in range(self.grid_size + 1):
            x = self.window_info['x'] + col * self.tile_width
            draw.line([(x, self.window_info['y']), 
                      (x, self.window_info['y'] + self.window_info['height'])], 
                      fill='gray', width=1)
        
        # ROI 하이라이트
        if highlight_rois:
            colors = {'control_bar': 'red', 'airplay_area': 'green', 
                     'menu_area': 'blue', 'control_area': 'yellow'}
            
            for name, roi in highlight_rois.items():
                if name in colors:
                    draw.rectangle([roi['x'], roi['y'], 
                                  roi['x'] + roi['width'], 
                                  roi['y'] + roi['height']], 
                                  outline=colors[name], width=3)
                    draw.text((roi['x'] + 5, roi['y'] + 5), name, fill=colors[name])
        
        # 저장
        grid_path = Path.home() / "quicktime_tile_grid.png"
        img.save(grid_path)
        print(f"   💾 저장: {grid_path}")
    
    def find_in_tiles(self, template_path, start_row, start_col, end_row, end_col):
        """특정 타일 범위에서 템플릿 찾기"""
        roi = self.get_roi_from_tiles(start_row, start_col, end_row, end_col)
        
        if not roi or not Path(template_path).exists():
            return None
        
        # ROI 스크린샷
        try:
            roi_screenshot = pyautogui.screenshot(
                region=(roi['x'], roi['y'], roi['width'], roi['height'])
            )
            
            # 템플릿 찾기
            location = pyautogui.locate(str(template_path), roi_screenshot, confidence=0.7)
            
            if location:
                center = pyautogui.center(location)
                absolute_x = roi['x'] + center.x
                absolute_y = roi['y'] + center.y
                
                # 어느 타일에 있는지 계산
                tile_col = int((absolute_x - self.window_info['x']) / self.tile_width)
                tile_row = int((absolute_y - self.window_info['y']) / self.tile_height)
                
                print(f"   ✅ 발견: 타일 ({tile_row}, {tile_col}), 좌표 ({absolute_x}, {absolute_y})")
                
                return {
                    'x': absolute_x,
                    'y': absolute_y,
                    'tile_row': tile_row,
                    'tile_col': tile_col
                }
        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
        
        return None
    
    def enable_airplay(self):
        """타일 기반 AirPlay 활성화"""
        print("🚀 Tile-based AirPlay Enabler")
        print("=" * 50)
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 창 정보 가져오기
        if not self.get_window_info():
            print("❌ QuickTime 창을 찾을 수 없습니다")
            return
        
        # ROI 정의
        rois = self.define_rois()
        
        # 디버그: 그리드 시각화
        if self.debug_mode:
            self.visualize_grid(rois)
        
        # 컨트롤 표시 - 타일 (8,5) 근처로 마우스 이동
        control_tile = self.get_tile_coords(8, 5)
        print(f"\n📍 컨트롤 표시 (타일 8,5): ({control_tile['center_x']}, {control_tile['center_y']})")
        pyautogui.moveTo(control_tile['center_x'], control_tile['center_y'], duration=0.5)
        time.sleep(0.8)
        
        # AirPlay 버튼 찾기 - 우측 하단 영역 (행 8-9, 열 6-9)
        print("\n🔍 AirPlay 버튼 검색 (우측 하단 타일)...")
        
        template_path = Path(__file__).parent / "templates" / "airplay_icon.png"
        
        airplay_pos = None
        if template_path.exists():
            airplay_pos = self.find_in_tiles(str(template_path), 8, 6, 9, 9)
        
        if not airplay_pos:
            # 수동 폴백 - 타일 (9,8) 위치 사용
            fallback_tile = self.get_tile_coords(9, 8)
            print(f"\n📍 폴백: 타일 (9,8) 사용")
            airplay_pos = {
                'x': fallback_tile['center_x'],
                'y': fallback_tile['center_y']
            }
        
        # AirPlay 클릭
        print(f"\n📍 AirPlay 클릭: ({airplay_pos['x']}, {airplay_pos['y']})")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        
        print("⏳ 메뉴 대기...")
        time.sleep(2)
        
        # 메뉴에서 체크박스 찾기 - 중앙 영역 (행 2-7, 열 2-7)
        print("\n🔍 메뉴에서 Apple TV 찾기...")
        
        # 체크박스 위치 추정 - 메뉴 중앙 타일 근처
        menu_tile = self.get_tile_coords(5, 5)
        
        print(f"\n📍 체크박스 추정 위치 (타일 5,5): ({menu_tile['center_x']}, {menu_tile['center_y']})")
        
        # 수동 조정
        print("\n🎯 체크박스 위치 조정")
        print("   마우스를 체크박스로 이동하세요...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            tile_col = int((x - self.window_info['x']) / self.tile_width)
            tile_row = int((y - self.window_info['y']) / self.tile_height)
            print(f"\r   {i}초... 타일 ({tile_row},{tile_col}) 좌표 ({x},{y})  ", end='', flush=True)
            time.sleep(1)
        
        print("\n   클릭!")
        pyautogui.click()
        
        print("\n✅ AirPlay 활성화 완료!")

def main():
    print("🎯 Tile-based AirPlay Enabler")
    print("\n이 도구는 QuickTime 창을 10x10 타일로 나누어")
    print("상대적 위치로 UI 요소를 찾습니다.")
    
    print("\n주요 영역:")
    print("- 컨트롤바: 하단 2개 행 (타일 80-99)")
    print("- AirPlay: 우측 하단 (타일 86-99)")
    print("- 메뉴: 중앙 영역 (타일 22-77)")
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    enabler = TileBasedAirPlayEnabler()
    enabler.enable_airplay()

if __name__ == "__main__":
    main()