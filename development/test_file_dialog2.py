#!/usr/bin/env python3
"""파일 대화상자 테스트 - macOS 호환"""

import tkinter as tk
from tkinter import filedialog
import time

def test_file_dialog():
    root = tk.Tk()
    root.title("QuickTime Playlist Pro - Test")
    root.geometry("300x200")
    
    def select_files():
        # 메인 루프에서 실행되도록 함
        root.update()
        time.sleep(0.1)  # 짧은 지연
        
        files = filedialog.askopenfilenames(
            parent=root,
            title="파일 선택",
            filetypes=[
                ("오디오 파일", "*.mp3;*.m4a;*.aac;*.wav;*.flac"),
                ("모든 파일", "*.*")
            ]
        )
        
        if files:
            print(f"선택된 파일들: {files}")
            for file in files:
                print(f"  - {file}")
        else:
            print("파일이 선택되지 않았습니다.")
    
    btn = tk.Button(root, text="파일 선택", command=select_files)
    btn.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test_file_dialog()