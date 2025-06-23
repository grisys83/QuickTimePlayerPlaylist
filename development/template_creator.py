#!/usr/bin/env python3
"""
Template Creator Tool
템플릿과 오프셋을 쉽게 정의하는 도구
"""

import subprocess
import time
import json
from pathlib import Path
import pyautogui
from PIL import Image, ImageDraw

class TemplateCreator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self.config_file = Path.home() / '.airplay_templates.json'
        self.templates = {}
        
    def capture_template(self, name, size=60):
        """마우스 위치 중심으로 템플릿 캡처"""
        print(f"\n🎯 '{name}' 템플릿 캡처")
        print(f"   템플릿 크기: {size}x{size}")
        print("   마우스를 대상 위에 놓으세요...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   {i}초... 위치: ({x}, {y})  ", end='', flush=True)
            time.sleep(1)
        
        # 마우스 위치
        center_x, center_y = pyautogui.position()
        print(f"\n   ✅ 중심: ({center_x}, {center_y})")
        
        # 템플릿 영역
        x = center_x - size // 2
        y = center_y - size // 2
        
        # 캡처
        screenshot = pyautogui.screenshot(region=(x, y, size, size))
        
        # 저장
        template_path = self.template_dir / f"{name}.png"
        screenshot.save(template_path)
        
        # 정보 저장
        self.templates[name] = {
            'path': str(template_path),
            'size': size,
            'captured_at': {'x': center_x, 'y': center_y},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"   💾 저장: {template_path}")
        
        # 미리보기
        self.preview_template(screenshot, name)
        
        return template_path
    
    def define_offset(self, from_template, to_name):
        """템플릿에서 특정 위치까지 오프셋 정의"""
        if from_template not in self.templates:
            print(f"❌ '{from_template}' 템플릿이 없습니다")
            return
        
        print(f"\n🎯 오프셋 정의: {from_template} → {to_name}")
        
        from_pos = self.templates[from_template]['captured_at']
        print(f"   기준점: ({from_pos['x']}, {from_pos['y']})")
        
        print(f"\n   마우스를 {to_name} 위치에 놓으세요...")
        
        for i in range(5, 0, -1):
            x, y = pyautogui.position()
            offset_x = x - from_pos['x']
            offset_y = y - from_pos['y']
            print(f"\r   {i}초... 오프셋: ({offset_x:+d}, {offset_y:+d})  ", end='', flush=True)
            time.sleep(1)
        
        # 최종 위치
        to_x, to_y = pyautogui.position()
        offset_x = to_x - from_pos['x']
        offset_y = to_y - from_pos['y']
        
        print(f"\n   ✅ 오프셋: ({offset_x:+d}, {offset_y:+d})")
        
        # 저장
        if 'offsets' not in self.templates[from_template]:
            self.templates[from_template]['offsets'] = {}
        
        self.templates[from_template]['offsets'][to_name] = {
            'x': offset_x,
            'y': offset_y,
            'absolute': {'x': to_x, 'y': to_y}
        }
        
        return (offset_x, offset_y)
    
    def preview_template(self, image, name):
        """템플릿 미리보기"""
        preview_path = self.template_dir / f"{name}_preview.png"
        
        # 크게 확대
        width, height = image.size
        preview = image.resize((width * 3, height * 3), Image.NEAREST)
        
        # 중앙 표시
        draw = ImageDraw.Draw(preview)
        center_x = preview.width // 2
        center_y = preview.height // 2
        
        # 십자선
        draw.line([(center_x - 20, center_y), (center_x + 20, center_y)], fill='red', width=2)
        draw.line([(center_x, center_y - 20), (center_x, center_y + 20)], fill='red', width=2)
        
        preview.save(preview_path)
        print(f"   👁️  미리보기: {preview_path}")
    
    def save_config(self):
        """설정 저장"""
        with open(self.config_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
        print(f"\n💾 설정 저장: {self.config_file}")
    
    def load_config(self):
        """설정 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.templates = json.load(f)
            print(f"✅ 기존 템플릿 로드: {len(self.templates)}개")
            
            for name, info in self.templates.items():
                print(f"   - {name}")
                if 'offsets' in info:
                    for offset_name in info['offsets']:
                        print(f"     → {offset_name}")

def quick_setup():
    """빠른 설정"""
    print("🚀 Quick Template Setup")
    print("=" * 50)
    
    creator = TemplateCreator()
    creator.load_config()
    
    # QuickTime 활성화
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    time.sleep(1)
    
    # 컨트롤 표시
    width, height = pyautogui.size()
    print("📍 컨트롤 표시...")
    pyautogui.moveTo(width // 2, height - 100, duration=0.5)
    time.sleep(1)
    
    # 1. AirPlay 버튼 템플릿
    print("\n1️⃣ AirPlay 버튼 템플릿")
    creator.capture_template('airplay_button', size=50)
    
    # 2. AirPlay 클릭
    print("\n📍 AirPlay 버튼을 클릭하세요...")
    print("   5초 드립니다...")
    time.sleep(5)
    
    # 3. Apple TV 아이콘 템플릿
    print("\n2️⃣ Apple TV 아이콘 템플릿")
    creator.capture_template('apple_tv_icon', size=60)
    
    # 4. 체크박스 오프셋
    print("\n3️⃣ 체크박스 오프셋")
    creator.define_offset('apple_tv_icon', 'checkbox')
    
    # 저장
    creator.save_config()
    
    print("\n✅ 설정 완료!")
    print("\n📊 템플릿 요약:")
    for name, info in creator.templates.items():
        print(f"\n{name}:")
        print(f"  - 위치: ({info['captured_at']['x']}, {info['captured_at']['y']})")
        if 'offsets' in info:
            for offset_name, offset in info['offsets'].items():
                print(f"  - {offset_name} 오프셋: ({offset['x']:+d}, {offset['y']:+d})")

def main():
    print("🎯 Template Creator Tool")
    print("\n옵션:")
    print("1. 빠른 설정 (추천)")
    print("2. 수동 설정")
    
    # 자동으로 빠른 설정 실행
    print("\n빠른 설정을 시작합니다...")
    time.sleep(2)
    
    quick_setup()

if __name__ == "__main__":
    main()