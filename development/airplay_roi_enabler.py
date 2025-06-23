#!/usr/bin/env python3
"""
AirPlay ROI-based Enabler
정의된 ROI와 템플릿을 사용하여 AirPlay 활성화
"""

import subprocess
import time
import json
from pathlib import Path
import pyautogui
import cv2
import numpy as np

class ROIBasedAirPlayEnabler:
    def __init__(self):
        self.config_file = Path.home() / '.airplay_roi_config.json'
        self.rois = {}
        self.templates = {}
        self.scale_factor = self.get_scale_factor()
        
        # Load config
        if not self.load_config():
            print("❌ ROI 설정이 없습니다. airplay_roi_tool.py를 먼저 실행하세요.")
            exit(1)
    
    def get_scale_factor(self):
        """Retina 디스플레이 스케일 팩터"""
        logical_width, _ = pyautogui.size()
        screenshot = pyautogui.screenshot()
        return screenshot.width / logical_width
    
    def load_config(self):
        """설정 로드"""
        if not self.config_file.exists():
            return False
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.rois = config.get('rois', {})
            self.templates = config.get('templates', {})
        
        print(f"✅ ROI 설정 로드됨")
        print(f"   ROIs: {list(self.rois.keys())}")
        print(f"   Templates: {list(self.templates.keys())}")
        
        return True
    
    def find_template_in_roi(self, template_name, roi_name):
        """ROI 내에서 템플릿 찾기"""
        if roi_name not in self.rois:
            print(f"❌ ROI '{roi_name}'이 없습니다")
            return None
        
        if template_name not in self.templates:
            print(f"❌ Template '{template_name}'이 없습니다")
            return None
        
        roi = self.rois[roi_name]
        template_info = self.templates[template_name]
        template_path = Path(template_info['path'])
        
        if not template_path.exists():
            print(f"❌ Template 파일이 없습니다: {template_path}")
            return None
        
        print(f"\n🔍 {roi_name} ROI에서 {template_name} 찾는 중...")
        
        # ROI 영역 스크린샷
        roi_screenshot = pyautogui.screenshot(
            region=(roi['x'], roi['y'], roi['width'], roi['height'])
        )
        
        # Template matching with PyAutoGUI
        try:
            # ROI 내에서 템플릿 찾기
            location = pyautogui.locate(str(template_path), roi_screenshot, confidence=0.7)
            
            if location:
                # ROI 내 상대 좌표를 절대 좌표로 변환
                center = pyautogui.center(location)
                absolute_x = roi['x'] + center.x
                absolute_y = roi['y'] + center.y
                
                print(f"   ✅ 발견: ({absolute_x}, {absolute_y})")
                return {'x': absolute_x, 'y': absolute_y}
            else:
                print(f"   ❌ 찾을 수 없음")
                
                # 디버그: ROI 스크린샷 저장
                debug_path = Path.home() / f"debug_{roi_name}.png"
                roi_screenshot.save(debug_path)
                print(f"   💾 디버그 이미지: {debug_path}")
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
        
        return None
    
    def find_with_cv2(self, template_name, roi_name):
        """CV2를 사용한 더 정밀한 템플릿 매칭"""
        if roi_name not in self.rois:
            return None
        
        if template_name not in self.templates:
            return None
        
        roi = self.rois[roi_name]
        template_path = Path(self.templates[template_name]['path'])
        
        if not template_path.exists():
            return None
        
        print(f"\n🔍 CV2로 {roi_name}에서 {template_name} 찾는 중...")
        
        # ROI 스크린샷
        roi_screenshot = pyautogui.screenshot(
            region=(roi['x'], roi['y'], roi['width'], roi['height'])
        )
        
        # CV2로 변환
        roi_cv2 = cv2.cvtColor(np.array(roi_screenshot), cv2.COLOR_RGB2BGR)
        template_cv2 = cv2.imread(str(template_path))
        
        if template_cv2 is None:
            print(f"   ❌ 템플릿 로드 실패")
            return None
        
        # Template matching
        result = cv2.matchTemplate(roi_cv2, template_cv2, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.7:  # 70% 이상 일치
            # 템플릿 중심 좌표 계산
            template_h, template_w = template_cv2.shape[:2]
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            
            # 절대 좌표로 변환
            absolute_x = roi['x'] + center_x
            absolute_y = roi['y'] + center_y
            
            print(f"   ✅ 발견 (신뢰도: {max_val:.2f}): ({absolute_x}, {absolute_y})")
            return {'x': absolute_x, 'y': absolute_y}
        else:
            print(f"   ❌ 찾을 수 없음 (최대 신뢰도: {max_val:.2f})")
            return None
    
    def enable_airplay(self):
        """AirPlay 활성화"""
        print("🚀 ROI-based AirPlay Enabler")
        print("=" * 50)
        
        # QuickTime 활성화
        print("\n📍 QuickTime 활성화...")
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
        time.sleep(1)
        
        # 컨트롤 표시
        if 'control_bar' in self.rois:
            control_roi = self.rois['control_bar']
            control_x = control_roi['x'] + control_roi['width'] // 2
            control_y = control_roi['y'] + control_roi['height'] // 2
            
            print(f"\n📍 컨트롤 표시 (ROI 중앙: {control_x}, {control_y})...")
            pyautogui.moveTo(control_x, control_y, duration=0.5)
            time.sleep(0.8)
        else:
            # Fallback
            width, height = pyautogui.size()
            pyautogui.moveTo(width // 2, height - 100, duration=0.5)
            time.sleep(0.8)
        
        # Step 1: AirPlay 버튼 찾기
        airplay_pos = None
        
        # PyAutoGUI로 시도
        airplay_pos = self.find_template_in_roi('airplay_button', 'airplay_area')
        
        # CV2로 재시도
        if not airplay_pos:
            airplay_pos = self.find_with_cv2('airplay_button', 'airplay_area')
        
        if not airplay_pos:
            print("\n❌ AirPlay 버튼을 찾을 수 없습니다")
            
            # 수동 모드
            print("\n🎯 수동 모드")
            print("   AirPlay 버튼에 마우스를 올려주세요...")
            for i in range(5, 0, -1):
                x, y = pyautogui.position()
                print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
                time.sleep(1)
            airplay_pos = {'x': x, 'y': y}
        
        # AirPlay 클릭
        print(f"\n\n📍 AirPlay 클릭: ({airplay_pos['x']}, {airplay_pos['y']})")
        pyautogui.click(airplay_pos['x'], airplay_pos['y'])
        
        print("⏳ 메뉴 대기...")
        time.sleep(2)
        
        # Step 2: Apple TV 아이콘 찾기
        apple_tv_pos = None
        
        if 'airplay_menu' in self.rois:
            apple_tv_pos = self.find_template_in_roi('apple_tv_icon', 'airplay_menu')
            
            if not apple_tv_pos:
                apple_tv_pos = self.find_with_cv2('apple_tv_icon', 'airplay_menu')
        
        if apple_tv_pos and 'apple_tv_icon' in self.templates:
            template_info = self.templates['apple_tv_icon']
            
            # 체크박스 오프셋 적용
            if 'offsets' in template_info and 'checkbox_offset' in template_info['offsets']:
                offset = template_info['offsets']['checkbox_offset']
                checkbox_x = offset['x']
                checkbox_y = offset['y']
                
                print(f"\n📍 체크박스 클릭 (저장된 위치): ({checkbox_x}, {checkbox_y})")
                pyautogui.click(checkbox_x, checkbox_y)
            else:
                # 기본 오프셋 사용
                checkbox_x = apple_tv_pos['x'] + 246
                checkbox_y = apple_tv_pos['y']
                
                print(f"\n📍 체크박스 클릭 (기본 오프셋): ({checkbox_x}, {checkbox_y})")
                pyautogui.click(checkbox_x, checkbox_y)
        else:
            # 수동 모드
            print("\n🎯 수동 모드 - 체크박스")
            print("   체크박스에 마우스를 올려주세요...")
            for i in range(10, 0, -1):
                x, y = pyautogui.position()
                print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
                time.sleep(1)
            
            print("\n   클릭!")
            pyautogui.click()
        
        print("\n\n✅ AirPlay 활성화 완료!")

def test_roi_config():
    """ROI 설정 테스트"""
    config_file = Path.home() / '.airplay_roi_config.json'
    
    if not config_file.exists():
        print("❌ ROI 설정이 없습니다")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("📊 ROI 설정 확인")
    print("=" * 50)
    
    print("\n🔧 ROIs:")
    for name, roi in config['rois'].items():
        print(f"   {name}: x={roi['x']}, y={roi['y']}, w={roi['width']}, h={roi['height']}")
    
    print("\n🖼️ Templates:")
    for name, template in config['templates'].items():
        print(f"   {name}:")
        print(f"     - ROI: {template['roi']}")
        print(f"     - Path: {template['path']}")
        if 'offsets' in template:
            for offset_name, offset in template['offsets'].items():
                print(f"     - Offset {offset_name}: ({offset['x']}, {offset['y']})")

def main():
    print("🎬 AirPlay ROI-based Enabler")
    
    # 설정 확인
    test_roi_config()
    
    print("\n\n3초 후 시작합니다...")
    time.sleep(3)
    
    enabler = ROIBasedAirPlayEnabler()
    enabler.enable_airplay()

if __name__ == "__main__":
    main()