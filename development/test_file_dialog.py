#!/usr/bin/env python3
"""파일 대화상자 테스트"""

import tkinter as tk
from tkinter import filedialog

def test_file_dialog():
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    
    print("파일 대화상자 열기...")
    
    # 간단한 파일 선택
    files = filedialog.askopenfilenames(
        title="테스트 파일 선택",
        filetypes=[("모든 파일", "*.*")]
    )
    
    if files:
        print(f"선택된 파일들: {files}")
    else:
        print("파일이 선택되지 않았습니다.")
        
    root.destroy()

if __name__ == "__main__":
    test_file_dialog()