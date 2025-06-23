#!/usr/bin/env python3
"""UI 속도 테스트"""

import tkinter as tk
from tkinter import ttk
import time

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UI Speed Test")
        
        # 버튼
        self.button = ttk.Button(root, text="Click Me", command=self.on_click)
        self.button.pack(pady=20)
        
        # 라벨
        self.label = ttk.Label(root, text="Ready")
        self.label.pack()
        
    def on_click(self):
        start = time.time()
        print(f"Button clicked at {start}")
        
        # UI 업데이트
        self.label.config(text="Processing...")
        self.root.update_idletasks()
        
        # 간단한 작업
        result = sum(range(1000))
        
        end = time.time()
        print(f"Completed in {end - start:.3f} seconds")
        self.label.config(text=f"Done! Time: {end - start:.3f}s")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()