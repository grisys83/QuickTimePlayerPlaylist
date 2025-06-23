#!/usr/bin/env python3
"""
Template Creator Tool - Slower Version
충분한 시간을 주는 템플릿 생성 도구
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
        
    def capture_template(self, name, size=60, wait_time=10):
        """마우스 위치 중심으로 템플릿 캡처"""
        print(f"\n🎯 '{name}' 템플릿 캡처")
        print(f"   템플릿 크기: {size}x{size}")
        print(f"   마우스를 대상 위에 놓으세요...")
        print(f"   {wait_time}초 드립니다...\n")
        
        for i in range(wait_time, 0, -1):
            x, y = pyautogui.position()
            print(f"\r   ⏰ {i:2d}초... 마우스 위치: ({x:4d}, {y:4d})  ", end='', flush=True)
            time.sleep(1)
        
        # 마우스 위치
        center_x, center_y = pyautogui.position()
        print(f"\n\n   ✅ 캡처 위치: ({center_x}, {center_y})")
        
        # 카운트다운
        print("\n   📸 캡처 카운트다운...")
        for i in range(3, 0, -1):
            print(f"\r   {i}... ", end='', flush=True)
            time.sleep(1)
        print("\r   📸 찰칵!")
        
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
        
        print(f"\n   💾 저장: {template_path}")
        
        # 미리보기
        self.preview_template(screenshot, name)
        
        return template_path
    
    def define_offset(self, from_template, to_name, wait_time=10):
        """템플릿에서 특정 위치까지 오프셋 정의"""
        if from_template not in self.templates:
            print(f"❌ '{from_template}' 템플릿이 없습니다")
            return
        
        print(f"\n🎯 오프셋 정의: {from_template} → {to_name}")
        
        from_pos = self.templates[from_template]['captured_at']
        print(f"   기준점: ({from_pos['x']}, {from_pos['y']})")
        
        print(f"\n   마우스를 {to_name} 위치에 놓으세요...")
        print(f"   {wait_time}초 드립니다...\n")
        
        for i in range(wait_time, 0, -1):
            x, y = pyautogui.position()
            offset_x = x - from_pos['x']
            offset_y = y - from_pos['y']
            print(f"\r   ⏰ {i:2d}초... 현재 오프셋: ({offset_x:+4d}, {offset_y:+4d})  ", end='', flush=True)
            time.sleep(1)
        
        # 최종 위치
        to_x, to_y = pyautogui.position()
        offset_x = to_x - from_pos['x']
        offset_y = to_y - from_pos['y']
        
        print(f"\n\n   ✅ 최종 오프셋: ({offset_x:+d}, {offset_y:+d})")
        print(f"   절대 위치: ({to_x}, {to_y})")
        
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
    
    def wait_with_countdown(self, message, seconds):
        """카운트다운과 함께 대기"""
        print(f"\n⏳ {message}")
        print(f"   {seconds}초 대기...\n")
        
        for i in range(seconds, 0, -1):
            print(f"\r   {i:2d}초 남음... ", end='', flush=True)
            time.sleep(1)
        print("\r   ✅ 계속합니다!    ")
    
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

def slow_setup():
    """느린 설정 (충분한 시간 제공)"""
    print("🚀 Template Setup - Slow Version")
    print("=" * 50)
    print("\n⚠️ 각 단계마다 10초씩 드립니다!")
    
    creator = TemplateCreator()
    creator.load_config()
    
    # QuickTime 활성화
    print("\n📍 QuickTime 활성화...")
    subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to activate'])
    creator.wait_with_countdown("QuickTime이 활성화되기를 기다립니다", 3)
    
    # 컨트롤 표시
    width, height = pyautogui.size()
    print("\n📍 컨트롤 표시...")
    print("   마우스를 화면 하단으로 이동합니다...")
    pyautogui.moveTo(width // 2, height - 100, duration=1.0)
    creator.wait_with_countdown("컨트롤이 표시되기를 기다립니다", 3)
    
    # 1. AirPlay 버튼 템플릿
    print("\n" + "="*50)
    print("1️⃣ AirPlay 버튼 템플릿 캡처")
    print("="*50)
    print("\n준비사항:")
    print("- QuickTime 컨트롤이 보이는지 확인")
    print("- AirPlay 버튼 위치 확인 (우측 하단)")
    creator.wait_with_countdown("준비 시간", 5)
    
    creator.capture_template('airplay_button', size=50, wait_time=10)
    
    # 2. AirPlay 클릭
    print("\n" + "="*50)
    print("📍 AirPlay 버튼 클릭")
    print("="*50)
    print("\n다음 작업:")
    print("- 방금 캡처한 AirPlay 버튼을 클릭하세요")
    print("- 메뉴가 열릴 때까지 기다리세요")
    creator.wait_with_countdown("AirPlay 버튼을 클릭할 시간", 10)
    
    # 3. Apple TV 아이콘 템플릿
    print("\n" + "="*50)
    print("2️⃣ Apple TV 아이콘 템플릿 캡처")
    print("="*50)
    print("\n준비사항:")
    print("- AirPlay 메뉴가 열려있는지 확인")
    print("- Apple TV 디바이스 아이콘이 보이는지 확인")
    creator.wait_with_countdown("준비 시간", 5)
    
    creator.capture_template('apple_tv_icon', size=60, wait_time=10)
    
    # 4. 체크박스 오프셋
    print("\n" + "="*50)
    print("3️⃣ 체크박스 오프셋 정의")
    print("="*50)
    print("\n준비사항:")
    print("- 체크박스 위치 확인")
    print("- 보통 Apple TV 아이콘 오른쪽에 있습니다")
    creator.wait_with_countdown("준비 시간", 5)
    
    creator.define_offset('apple_tv_icon', 'checkbox', wait_time=10)
    
    # 저장
    creator.save_config()
    
    print("\n" + "="*50)
    print("✅ 설정 완료!")
    print("="*50)
    
    print("\n📊 템플릿 요약:")
    for name, info in creator.templates.items():
        print(f"\n{name}:")
        print(f"  - 캡처 위치: ({info['captured_at']['x']}, {info['captured_at']['y']})")
        print(f"  - 캡처 시간: {info['timestamp']}")
        if 'offsets' in info:
            for offset_name, offset in info['offsets'].items():
                print(f"  - {offset_name} 오프셋: ({offset['x']:+d}, {offset['y']:+d})")
                print(f"    절대 위치: ({offset['absolute']['x']}, {offset['absolute']['y']})")
    
    print("\n💡 다음 단계:")
    print("1. templates 폴더에서 캡처된 이미지 확인")
    print("2. airplay_tile_cv2.py 실행하여 테스트")

def main():
    print("🎯 Template Creator - Slow Version")
    print("\n충분한 시간을 제공하는 템플릿 생성 도구입니다.")
    print("각 단계마다 10초씩 드립니다.")
    
    print("\n3초 후 시작합니다...")
    time.sleep(3)
    
    slow_setup()

if __name__ == "__main__":
    main()