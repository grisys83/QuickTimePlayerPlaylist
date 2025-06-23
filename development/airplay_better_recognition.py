#!/usr/bin/env python3
"""
Better Template Recognition Methods
PyAutoGUI보다 나은 템플릿 인식 방법들
"""

import cv2
import numpy as np
import pyautogui
from pathlib import Path
import time

class BetterTemplateRecognition:
    def __init__(self):
        self.methods = {
            'cv2_basic': self.cv2_template_matching,
            'cv2_multi_scale': self.cv2_multi_scale_matching,
            'cv2_feature': self.cv2_feature_matching,
            'hybrid': self.hybrid_matching
        }
    
    def cv2_template_matching(self, screenshot, template_path, threshold=0.8):
        """OpenCV 기본 템플릿 매칭 - PyAutoGUI보다 정확"""
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        # 스크린샷을 numpy array로 변환
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 여러 매칭 방법 시도
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_match = None
        best_val = 0
        
        for method in methods:
            result = cv2.matchTemplate(screenshot_cv2, template, method)
            
            if method == cv2.TM_SQDIFF_NORMED:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if min_val < (1 - threshold):
                    confidence = 1 - min_val
                    location = min_loc
                else:
                    continue
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val > threshold:
                    confidence = max_val
                    location = max_loc
                else:
                    continue
            
            if confidence > best_val:
                best_val = confidence
                h, w = template.shape[:2]
                best_match = {
                    'x': location[0] + w // 2,
                    'y': location[1] + h // 2,
                    'confidence': confidence,
                    'method': method
                }
        
        return best_match
    
    def cv2_multi_scale_matching(self, screenshot, template_path, scales=[0.8, 0.9, 1.0, 1.1, 1.2]):
        """다양한 스케일로 템플릿 매칭 - 크기 변화에 강함"""
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        best_match = None
        best_val = 0
        
        for scale in scales:
            # 템플릿 리사이즈
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            resized = cv2.resize(template, (width, height))
            
            # 매칭
            result = cv2.matchTemplate(screenshot_cv2, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                h, w = resized.shape[:2]
                best_match = {
                    'x': max_loc[0] + w // 2,
                    'y': max_loc[1] + h // 2,
                    'confidence': max_val,
                    'scale': scale
                }
        
        return best_match if best_val > 0.7 else None
    
    def cv2_feature_matching(self, screenshot, template_path):
        """특징점 매칭 - 회전이나 변형에 강함"""
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # ORB 특징점 검출기
        orb = cv2.ORB_create()
        
        # 특징점 검출
        kp1, des1 = orb.detectAndCompute(template, None)
        kp2, des2 = orb.detectAndCompute(screenshot_cv2, None)
        
        if des1 is None or des2 is None:
            return None
        
        # 매칭
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        if len(matches) < 10:  # 최소 매칭 수
            return None
        
        # 좋은 매칭만 선택
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = matches[:int(len(matches) * 0.3)]
        
        if len(good_matches) < 4:
            return None
        
        # 매칭된 점들의 평균 위치 계산
        pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
        center_x = np.mean(pts[:, 0])
        center_y = np.mean(pts[:, 1])
        
        return {
            'x': int(center_x),
            'y': int(center_y),
            'confidence': len(good_matches) / len(kp1),
            'matches': len(good_matches)
        }
    
    def hybrid_matching(self, screenshot, template_path):
        """여러 방법을 조합한 하이브리드 매칭"""
        results = []
        
        # 1. 기본 CV2 매칭
        result1 = self.cv2_template_matching(screenshot, template_path)
        if result1:
            results.append(result1)
        
        # 2. 멀티스케일 매칭
        result2 = self.cv2_multi_scale_matching(screenshot, template_path)
        if result2:
            results.append(result2)
        
        # 3. PyAutoGUI 시도 (폴백)
        template = str(template_path)
        try:
            location = pyautogui.locate(template, screenshot, confidence=0.6)
            if location:
                center = pyautogui.center(location)
                results.append({
                    'x': center.x,
                    'y': center.y,
                    'confidence': 0.6,
                    'method': 'pyautogui'
                })
        except:
            pass
        
        # 가장 신뢰도 높은 결과 반환
        if results:
            return max(results, key=lambda x: x['confidence'])
        
        return None
    
    def edge_based_matching(self, screenshot, template_path):
        """엣지 기반 매칭 - UI 요소에 효과적"""
        template = cv2.imread(str(template_path))
        if template is None:
            return None
        
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 그레이스케일 변환
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot_cv2, cv2.COLOR_BGR2GRAY)
        
        # 엣지 검출
        template_edges = cv2.Canny(template_gray, 50, 150)
        screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
        
        # 엣지 이미지로 매칭
        result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.6:  # 엣지는 threshold 낮춰도 됨
            h, w = template.shape[:2]
            return {
                'x': max_loc[0] + w // 2,
                'y': max_loc[1] + h // 2,
                'confidence': max_val,
                'method': 'edge'
            }
        
        return None

def test_recognition_methods():
    """인식 방법 비교 테스트"""
    print("🧪 Template Recognition Comparison")
    print("=" * 50)
    
    recognizer = BetterTemplateRecognition()
    
    # 스크린샷
    screenshot = pyautogui.screenshot()
    
    # 템플릿 경로
    template_path = Path(__file__).parent / "templates" / "airplay_icon.png"
    
    if not template_path.exists():
        print("❌ 템플릿 파일이 없습니다")
        return
    
    print(f"\n📄 템플릿: {template_path}")
    
    # 각 방법 테스트
    methods = [
        ('PyAutoGUI', lambda: pyautogui.locate(str(template_path), screenshot, confidence=0.7)),
        ('CV2 Basic', lambda: recognizer.cv2_template_matching(screenshot, template_path)),
        ('CV2 Multi-scale', lambda: recognizer.cv2_multi_scale_matching(screenshot, template_path)),
        ('CV2 Feature', lambda: recognizer.cv2_feature_matching(screenshot, template_path)),
        ('Edge-based', lambda: recognizer.edge_based_matching(screenshot, template_path)),
        ('Hybrid', lambda: recognizer.hybrid_matching(screenshot, template_path))
    ]
    
    results = []
    
    for name, method in methods:
        print(f"\n🔍 {name}:")
        start_time = time.time()
        
        try:
            result = method()
            elapsed = time.time() - start_time
            
            if result:
                if isinstance(result, tuple):  # PyAutoGUI returns Box
                    center = pyautogui.center(result)
                    print(f"   ✅ 발견: ({center.x}, {center.y})")
                    print(f"   ⏱️  시간: {elapsed:.3f}초")
                else:
                    print(f"   ✅ 발견: ({result['x']}, {result['y']})")
                    if 'confidence' in result:
                        print(f"   📊 신뢰도: {result['confidence']:.3f}")
                    print(f"   ⏱️  시간: {elapsed:.3f}초")
                
                results.append((name, True, elapsed))
            else:
                print(f"   ❌ 찾지 못함")
                print(f"   ⏱️  시간: {elapsed:.3f}초")
                results.append((name, False, elapsed))
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            results.append((name, False, 0))
    
    # 결과 요약
    print("\n\n📊 결과 요약:")
    print("-" * 40)
    for name, success, elapsed in results:
        status = "✅" if success else "❌"
        print(f"{status} {name:15} ({elapsed:.3f}초)")

def main():
    print("🎯 Better Template Recognition Demo")
    print("\n이 도구는 PyAutoGUI보다 나은 템플릿 인식 방법들을 보여줍니다:")
    print("1. OpenCV 기본 매칭")
    print("2. 멀티스케일 매칭") 
    print("3. 특징점 매칭")
    print("4. 엣지 기반 매칭")
    print("5. 하이브리드 매칭")
    
    print("\n테스트를 시작합니다...")
    time.sleep(2)
    
    test_recognition_methods()

if __name__ == "__main__":
    main()