# Better Vision Libraries for macOS Automation

## 1. **PyAutoGUI** (가장 쉬움)
```python
import pyautogui

# 스크린샷에서 이미지 찾기
location = pyautogui.locateOnScreen('airplay_icon.png', confidence=0.8)
if location:
    pyautogui.click(location)

# 모든 매치 찾기
all_checkboxes = pyautogui.locateAllOnScreen('checkbox.png', confidence=0.7)
```
- ✅ 매우 쉬운 API
- ✅ 자동 스케일 처리
- ✅ Retina 디스플레이 지원
- ❌ 느릴 수 있음

## 2. **Pillow + PyAutoGUI** (실용적)
```python
from PIL import Image
import pyautogui

# 더 스마트한 이미지 매칭
screenshot = pyautogui.screenshot()
# Pillow로 이미지 처리 후 찾기
```

## 3. **Vision Framework (macOS Native)** - PyObjC
```python
from Quartz import Vision
import Quartz

# macOS의 네이티브 비전 프레임워크 사용
# 텍스트 인식, 객체 감지 등 지원
```

## 4. **EasyOCR** (텍스트 인식)
```python
import easyocr

reader = easyocr.Reader(['en', 'ko'])
result = reader.readtext('screenshot.png')
# "Apple TV", "living" 등 텍스트 직접 찾기
```

## 5. **Playwright/Selenium** 스타일 접근
```python
# 더 고수준 자동화
from playwright.sync_api import sync_playwright

# UI 요소를 더 스마트하게 찾기
```

## 추천: PyAutoGUI로 간단하게 시작하기

```bash
pip install pyautogui pillow
```

```python
import pyautogui
import time

# Retina 디스플레이 자동 처리
pyautogui.PAUSE = 0.5  # 각 동작 사이 대기

# AirPlay 아이콘 찾아 클릭
airplay = pyautogui.locateCenterOnScreen('templates/airplay_icon.png', confidence=0.8)
if airplay:
    pyautogui.click(airplay)
    time.sleep(1)
    
    # Apple TV 체크박스 찾기
    checkbox = pyautogui.locateCenterOnScreen('templates/checkbox.png', confidence=0.7)
    if checkbox:
        pyautogui.click(checkbox)
```

## 가장 스마트한 방법: 텍스트 인식 사용

```python
import easyocr
import pyautogui

# 메뉴에서 "Apple TV" 텍스트 찾기
screenshot = pyautogui.screenshot()
reader = easyocr.Reader(['en'])
results = reader.readtext(screenshot)

for (bbox, text, prob) in results:
    if "Apple TV" in text:
        # 텍스트 위치에서 체크박스 클릭
        x = bbox[0][0] - 60  # 체크박스는 왼쪽에
        y = (bbox[0][1] + bbox[2][1]) // 2
        pyautogui.click(x, y)
```