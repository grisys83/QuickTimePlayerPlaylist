#!/usr/bin/env python3
"""
AirPlay ROI Definition Tool
ROI를 직접 정의하고 템플릿을 저장하는 도구
"""

import subprocess
import time
import json
from pathlib import Path
import pyautogui
from PIL import Image, ImageDraw

class ROIDefinitionTool:
    def __init__(self):
        self.rois = {}
        self.templates = {}
        self.config_file = Path.home() / '.airplay_roi_config.json'
        self.template_dir = Path(__file__).parent / "roi_templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def capture_roi(self, name, description):
        """ROI 영역을 캡처"""
        print(f"\n🎯 {name} ROI 정의")
        print(f"   {description}")
        
        print("\n   1. 마우스를 ROI 좌상단에 위치시키세요")
        print("   5초 후 위치를 기록합니다...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        x1, y1 = pyautogui.position()
        print(f"\n   ✅ 좌상단: ({x1}, {y1})")
        
        print("\n   2. 마우스를 ROI 우하단에 위치시키세요")
        print("   5초 후 위치를 기록합니다...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        x2, y2 = pyautogui.position()
        print(f"\n   ✅ 우하단: ({x2}, {y2})")
        
        # ROI 저장
        roi = {
            'x': min(x1, x2),
            'y': min(y1, y2),
            'width': abs(x2 - x1),
            'height': abs(y2 - y1)
        }
        
        self.rois[name] = roi
        print(f"\n   📐 ROI: {roi}")
        
        # ROI 스크린샷 저장
        screenshot = pyautogui.screenshot(region=(roi['x'], roi['y'], roi['width'], roi['height']))
        roi_path = self.template_dir / f"{name}_roi.png"
        screenshot.save(roi_path)
        print(f"   💾 ROI 저장: {roi_path}")
        
        return roi
    
    def capture_template(self, name, roi_name, description):
        """ROI 내에서 템플릿 캡처"""
        if roi_name not in self.rois:
            print(f"❌ ROI '{roi_name}'이 정의되지 않았습니다")
            return None
        
        roi = self.rois[roi_name]
        
        print(f"\n🎯 {name} 템플릿 캡처")
        print(f"   {description}")
        print(f"   ROI 영역: {roi}")
        
        # ROI 영역 하이라이트 (시각적 피드백)
        print("\n   ROI 영역을 확인하세요...")
        
        # 템플릿 영역 정의
        print("\n   템플릿 영역을 정의하세요")
        print("   1. 마우스를 템플릿 중앙에 위치시키세요")
        print("   5초 후 위치를 기록합니다...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        center_x, center_y = pyautogui.position()
        
        # 템플릿 크기 입력
        print(f"\n   ✅ 중앙: ({center_x}, {center_y})")
        
        # 기본 템플릿 크기
        template_width = 60
        template_height = 60
        
        # 템플릿 영역 계산
        template_x = center_x - template_width // 2
        template_y = center_y - template_height // 2
        
        # 템플릿 캡처
        template_screenshot = pyautogui.screenshot(
            region=(template_x, template_y, template_width, template_height)
        )
        
        template_path = self.template_dir / f"{name}.png"
        template_screenshot.save(template_path)
        
        self.templates[name] = {
            'path': str(template_path),
            'roi': roi_name,
            'offset_from_center': {
                'x': center_x - (roi['x'] + roi['width'] // 2),
                'y': center_y - (roi['y'] + roi['height'] // 2)
            }
        }
        
        print(f"\n   💾 템플릿 저장: {template_path}")
        
        return self.templates[name]
    
    def define_offset(self, from_template, to_position, name):
        """템플릿에서 특정 위치까지의 오프셋 정의"""
        print(f"\n🎯 오프셋 정의: {from_template} → {name}")
        
        if from_template not in self.templates:
            print(f"❌ 템플릿 '{from_template}'이 없습니다")
            return None
        
        print(f"\n   마우스를 {name} 위치에 놓으세요")
        print("   5초 후 위치를 기록합니다...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        target_x, target_y = pyautogui.position()
        
        # 현재 템플릿 위치 찾기 (시뮬레이션)
        print(f"\n   타겟 위치: ({target_x}, {target_y})")
        
        # 오프셋 저장
        if 'offsets' not in self.templates[from_template]:
            self.templates[from_template]['offsets'] = {}
        
        self.templates[from_template]['offsets'][name] = {
            'x': target_x,
            'y': target_y,
            'description': f"Offset from {from_template} to {name}"
        }
        
        print(f"   ✅ 오프셋 저장됨")
        
        return self.templates[from_template]['offsets'][name]
    
    def save_config(self):
        """설정 저장"""
        config = {
            'rois': self.rois,
            'templates': self.templates,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 설정 저장: {self.config_file}")
    
    def load_config(self):
        """설정 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.rois = config.get('rois', {})
                self.templates = config.get('templates', {})
                print(f"✅ 설정 로드됨: {self.config_file}")
                return True
        return False
    
    def visualize_rois(self):
        """ROI 시각화"""
        print("\n📸 ROI 시각화...")
        
        # 전체 스크린샷
        screenshot = pyautogui.screenshot()
        
        # PIL Image로 변환
        img = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        draw = ImageDraw.Draw(img)
        
        # 각 ROI 그리기
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
        
        for i, (name, roi) in enumerate(self.rois.items()):
            color = colors[i % len(colors)]
            x, y, w, h = roi['x'], roi['y'], roi['width'], roi['height']
            
            # 사각형 그리기
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            
            # 라벨 추가
            draw.text((x + 5, y + 5), name, fill=color)
        
        # 저장
        viz_path = Path.home() / "airplay_roi_visualization.png"
        img.save(viz_path)
        print(f"   💾 저장: {viz_path}")

def main():
    print("🎯 AirPlay ROI Definition Tool")
    print("=" * 50)
    
    tool = ROIDefinitionTool()
    
    # 기존 설정 로드
    if tool.load_config():
        print("\n기존 설정을 로드했습니다.")
        print(f"ROIs: {list(tool.rois.keys())}")
        print(f"Templates: {list(tool.templates.keys())}")
    
    # QuickTime 활성화
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # 컨트롤 표시
    width, height = pyautogui.size()
    print("📍 컨트롤 표시...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(1)
    
    print("\n🔧 ROI 정의 시작")
    print("=" * 50)
    
    # 1. Control Bar ROI
    print("\n1️⃣ Control Bar ROI 정의")
    tool.capture_roi('control_bar', 'QuickTime 하단 컨트롤바 전체 영역')
    
    # 2. AirPlay Button ROI
    print("\n2️⃣ AirPlay Button ROI 정의")
    tool.capture_roi('airplay_area', '컨트롤바 우측의 AirPlay 버튼 주변 영역')
    
    # 3. AirPlay 버튼 템플릿
    print("\n3️⃣ AirPlay 버튼 템플릿 캡처")
    time.sleep(2)  # 컨트롤 다시 표시
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(1)
    tool.capture_template('airplay_button', 'airplay_area', 'AirPlay 버튼 아이콘')
    
    # 4. AirPlay 클릭
    print("\n📍 AirPlay 버튼을 수동으로 클릭하세요...")
    print("   5초 드립니다...")
    time.sleep(5)
    
    # 5. Menu ROI
    print("\n4️⃣ AirPlay Menu ROI 정의")
    tool.capture_roi('airplay_menu', 'AirPlay 메뉴 전체 영역')
    
    # 6. Apple TV 아이콘 템플릿
    print("\n5️⃣ Apple TV 아이콘 템플릿 캡처")
    tool.capture_template('apple_tv_icon', 'airplay_menu', 'Apple TV 디바이스 아이콘')
    
    # 7. 체크박스 오프셋
    print("\n6️⃣ 체크박스 오프셋 정의")
    tool.define_offset('apple_tv_icon', 'checkbox', 'checkbox_offset')
    
    # 저장
    tool.save_config()
    
    # 시각화
    tool.visualize_rois()
    
    print("\n✅ ROI 정의 완료!")
    print("\n📊 정의된 ROIs:")
    for name, roi in tool.rois.items():
        print(f"   - {name}: {roi}")
    
    print("\n📊 정의된 Templates:")
    for name, template in tool.templates.items():
        print(f"   - {name}: ROI={template['roi']}")
        if 'offsets' in template:
            for offset_name, offset in template['offsets'].items():
                print(f"     → {offset_name}: ({offset['x']}, {offset['y']})")

if __name__ == "__main__":
    main()