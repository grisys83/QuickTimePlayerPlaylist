#!/usr/bin/env python3
"""
QuickTime Playlist - Simple Start
통합 플레이리스트 매니저 (안정화 버전)
"""

import os
# macOS Tkinter 경고 숨기기
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import threading
import time
from pathlib import Path
import random

class QuickTimePlaylistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Playlist Manager")
        self.root.geometry("1000x600")
        
        # UI 반응성 개선
        self.root.update_idletasks()
        
        # 플레이리스트 데이터
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        
        # 설정
        self.airplay_enabled = tk.BooleanVar(value=True)
        self.shuffle_enabled = tk.BooleanVar(value=False)
        self.repeat_mode = tk.StringVar(value="all")  # none, one, all
        
        # UI 설정
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 메뉴바
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="파일 추가", command=self.add_files)
        file_menu.add_command(label="폴더 추가", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="플레이리스트 저장", command=self.save_playlist)
        file_menu.add_command(label="플레이리스트 열기", command=self.load_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 좌측 - 플레이리스트
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(left_frame, text="플레이리스트", font=('Arial', 14, 'bold')).pack()
        
        # 리스트박스와 스크롤바
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                  selectmode=tk.EXTENDED,
                                  exportselection=False,  # 선택 성능 개선
                                  height=20,  # 최소 높이 설정
                                  bg='white',  # 배경색 명시
                                  fg='black')  # 글자색 명시
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # 더블클릭으로 재생
        self.listbox.bind('<Double-Button-1>', lambda e: self.play_selected())
        
        # 리스트 컨트롤
        list_controls = ttk.Frame(left_frame)
        list_controls.pack(fill=tk.X)
        
        ttk.Button(list_controls, text="위로", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_controls, text="아래로", command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_controls, text="삭제", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_controls, text="비우기", command=self.clear_playlist).pack(side=tk.LEFT, padx=2)
        
        # 우측 - 현재 재생 중
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        ttk.Label(right_frame, text="현재 재생 중", font=('Arial', 14, 'bold')).pack()
        
        # 트랙 정보
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=20)
        
        self.now_playing_label = ttk.Label(info_frame, text="재생 중인 트랙 없음", 
                                          font=('Arial', 12), wraplength=280)
        self.now_playing_label.pack()
        
        # 옵션
        options_frame = ttk.LabelFrame(right_frame, text="옵션", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(options_frame, text="Living AirPlay", 
                       variable=self.airplay_enabled).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="셔플", 
                       variable=self.shuffle_enabled).pack(anchor=tk.W)
        
        # 반복 모드 선택
        repeat_frame = ttk.Frame(options_frame)
        repeat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(repeat_frame, text="반복:").pack(side=tk.LEFT)
        ttk.Radiobutton(repeat_frame, text="끔", variable=self.repeat_mode, 
                       value="none").pack(side=tk.LEFT)
        ttk.Radiobutton(repeat_frame, text="1곡", variable=self.repeat_mode, 
                       value="one").pack(side=tk.LEFT)
        ttk.Radiobutton(repeat_frame, text="전체", variable=self.repeat_mode, 
                       value="all").pack(side=tk.LEFT)
        
        # 도구
        tools_frame = ttk.LabelFrame(right_frame, text="도구", padding=10)
        tools_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(tools_frame, text="폴더 추가", 
                  command=self.add_folder).pack(fill=tk.X, pady=2)
        
        # 하단 - 재생 컨트롤
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        self.status_label = ttk.Label(bottom_frame, text="준비")
        self.status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(bottom_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.play_button = ttk.Button(control_frame, text="▶ 전체 재생", 
                                     command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="⏹ 중지", command=self.stop_playback).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏭ 다음", command=self.next_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="▶️ 선택 재생", command=self.play_selected).pack(side=tk.LEFT, padx=5)
        
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[
                ("변환된 비디오", "*_converted.mp4"),
                ("모든 비디오", "*.mp4;*.mov;*.m4v"),
                ("모든 파일", "*.*")
            ]
        )
        
        for file in files:
            # 비디오 파일만 추가 (오디오 파일 제외)
            if Path(file).suffix.lower() not in ['.mp3', '.m4a', '.aac', '.wav', '.flac']:
                self.playlist.append(file)
                self.listbox.insert(tk.END, os.path.basename(file))
            
    def add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
            
        # 변환된 파일 우선, 그 다음 원본 파일
        video_extensions = ['_converted.mp4', '.mp4', '.mov', '.m4v']
        folder_path = Path(folder)
        
        count = 0
        added_files = set()  # 중복 방지
        
        # 변환된 비디오 먼저 추가
        for file in folder_path.glob('*_converted.mp4'):
            self.playlist.append(str(file))
            self.listbox.insert(tk.END, file.name)
            added_files.add(file.stem.replace('_converted', ''))
            count += 1
        
        # 다른 비디오 파일
        for ext in video_extensions[1:]:
            for file in folder_path.glob(f'*{ext}'):
                if file.stem not in added_files:
                    self.playlist.append(str(file))
                    self.listbox.insert(tk.END, file.name)
                    count += 1
        
        # UI 강제 업데이트
        self.listbox.update()
        self.root.update_idletasks()
        
        # 스크롤을 맨 위로
        self.listbox.see(0)
                
        self.status_label.config(text=f"{count}개 파일 추가됨")
        
        
    def move_up(self):
        """선택 항목 위로"""
        selected = self.listbox.curselection()
        if not selected or selected[0] == 0:
            return
            
        index = selected[0]
        # 데이터 교환
        self.playlist[index-1], self.playlist[index] = \
            self.playlist[index], self.playlist[index-1]
        # UI 업데이트
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index-1, item)
        self.listbox.selection_set(index-1)
        
    def move_down(self):
        """선택 항목 아래로"""
        selected = self.listbox.curselection()
        if not selected or selected[0] == len(self.playlist)-1:
            return
            
        index = selected[0]
        # 데이터 교환
        self.playlist[index], self.playlist[index+1] = \
            self.playlist[index+1], self.playlist[index]
        # UI 업데이트
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index+1, item)
        self.listbox.selection_set(index+1)
        
    def remove_selected(self):
        """선택 항목 삭제"""
        selected = list(self.listbox.curselection())
        for index in reversed(selected):
            del self.playlist[index]
            self.listbox.delete(index)
            
    def clear_playlist(self):
        """플레이리스트 비우기"""
        self.playlist.clear()
        self.listbox.delete(0, tk.END)
        self.current_index = 0
        
    def save_playlist(self):
        """플레이리스트 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False, indent=2)
            self.status_label.config(text="플레이리스트 저장됨")
            
    def load_playlist(self):
        """플레이리스트 불러오기"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.playlist = json.load(f)
                
            self.listbox.delete(0, tk.END)
            for filepath in self.playlist:
                self.listbox.insert(tk.END, os.path.basename(filepath))
                
            self.status_label.config(text="플레이리스트 불러옴")
            
    def toggle_playback(self):
        """재생/일시정지"""
        if not self.is_playing:
            if not self.playlist:
                messagebox.showwarning("플레이리스트 비어있음", 
                                     "재생할 파일이 없습니다.")
                return
                
            self.is_playing = True
            self.play_button.config(text="⏸ 일시정지")
            
            # 재생 스레드 시작
            threading.Thread(target=self.playback_thread, daemon=True).start()
        else:
            self.is_playing = False
            self.play_button.config(text="▶ 전체 재생")
            
    def stop_playback(self):
        """재생 중지"""
        self.is_playing = False
        self.current_index = 0
        self.play_button.config(text="▶ 전체 재생")
        
        # QuickTime 종료
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        self.now_playing_label.config(text="재생 중인 트랙 없음")
        self.status_label.config(text="중지됨")
        
    def next_track(self):
        """다음 트랙"""
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            if self.is_playing:
                # 현재 재생 중지
                subprocess.run([
                    'osascript', '-e',
                    'tell application "QuickTime Player" to stop front document'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
    def play_selected(self):
        """선택한 항목만 재생"""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showinfo("선택 없음", "재생할 파일을 선택하세요.")
            return
            
        # 재생 중이면 중지
        if self.is_playing:
            self.stop_playback()
            time.sleep(0.5)
        
        # 선택한 파일만 재생
        selected_index = selected[0]
        video_path = self.playlist[selected_index]
        
        # UI 업데이트
        self.update_now_playing(video_path)
        self.status_label.config(text="선택 재생 중...")
        
        # 별도 스레드에서 재생
        threading.Thread(target=self._play_single_video, args=(video_path,), daemon=True).start()
        
    def _play_single_video(self, video_path):
        """단일 비디오 재생 (스레드용)"""
        self.play_video(video_path)
        self.root.after(0, lambda: self.status_label.config(text="선택 재생 완료"))
                
    def playback_thread(self):
        """재생 스레드"""
        playlist = self.playlist.copy()
        
        if self.shuffle_enabled.get():
            random.shuffle(playlist)
            
        while self.is_playing:
            video_path = playlist[self.current_index]
            
            # UI 업데이트
            self.root.after(0, self.update_now_playing, video_path)
            
            # 비디오 재생
            self.play_video(video_path)
            
            # 반복 모드에 따른 처리
            repeat_mode = self.repeat_mode.get()
            
            if repeat_mode == "one":
                # 1곡 반복 - 인덱스 변경 없음
                continue
            elif repeat_mode == "all":
                # 전체 반복
                self.current_index += 1
                if self.current_index >= len(playlist):
                    self.current_index = 0
                    if self.shuffle_enabled.get():
                        random.shuffle(playlist)
            else:
                # 반복 없음
                self.current_index += 1
                if self.current_index >= len(playlist):
                    break
                    
        self.root.after(0, self.playback_finished)
        
    def play_video(self, video_path):
        """비디오 재생"""
        # 오디오 파일은 재생하지 않음
        if Path(video_path).suffix.lower() in ['.mp3', '.m4a', '.aac', '.wav', '.flac']:
            self.status_label.config(text=f"오디오 파일은 재생할 수 없습니다: {Path(video_path).name}")
            return
                
        # QuickTime에서 재생
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(0.5)
        
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(1.5)
        
        # AirPlay 설정
        if self.airplay_enabled.get():
            self.enable_airplay()
            
        # 재생 시작
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 재생 완료 대기
        time.sleep(4.5)
        while self.is_playing and self.is_video_playing():
            time.sleep(2)
            
    def enable_airplay(self):
        """AirPlay 설정"""
        try:
            subprocess.run(['cliclick', 'm:640,700'])
            time.sleep(0.5)
            subprocess.run(['cliclick', 'c:844,714'])  # AirPlay
            time.sleep(0.5)
            subprocess.run(['cliclick', 'c:970,784'])  # Living
        except:
            pass
            
    def is_video_playing(self):
        """재생 상태 확인"""
        result = subprocess.run([
            'osascript', '-e',
            '''tell application "QuickTime Player"
                if (count documents) > 0 then
                    return playing of front document
                else
                    return false
                end if
            end tell'''
        ], capture_output=True, text=True)
        
        return result.stdout.strip() == "true"
        
    def update_now_playing(self, filepath):
        """현재 재생 중 업데이트"""
        filename = os.path.basename(filepath)
        self.now_playing_label.config(text=filename)
        self.status_label.config(text=f"재생 중: {filename}")
        
        # 리스트박스에서 하이라이트
        for i in range(self.listbox.size()):
            if self.listbox.get(i) == filename:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(i)
                self.listbox.see(i)
                break
                
    def playback_finished(self):
        """재생 완료"""
        self.is_playing = False
        self.current_index = 0
        self.play_button.config(text="▶ 전체 재생")
        self.now_playing_label.config(text="재생 중인 트랙 없음")
        self.status_label.config(text="재생 완료")
        

def main():
    root = tk.Tk()
    app = QuickTimePlaylistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()