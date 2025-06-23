#!/usr/bin/env python3
"""
QuickTime 플레이리스트 에디터 GUI
- 드래그 앤 드롭으로 파일 추가
- 플레이리스트 편집 (순서 변경, 삭제)
- 오디오 파일 자동 변환
- Living AirPlay 재생
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
import time
import json
from pathlib import Path
import shutil

class PlaylistEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Playlist Editor")
        self.root.geometry("800x600")
        
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.conversion_queue = []
        
        self.setup_ui()
        self.load_playlist()
        
    def setup_ui(self):
        """UI 구성"""
        # 툴바
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="파일 추가", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="폴더 추가", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="삭제", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="위로", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="아래로", command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="저장", command=self.save_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="불러오기", command=self.load_playlist_file).pack(side=tk.LEFT, padx=2)
        
        # 플레이리스트
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                  yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # 드래그 앤 드롭 설정
        self.listbox.bind('<Button-1>', self.on_click)
        self.listbox.bind('<B1-Motion>', self.on_drag)
        self.listbox.bind('<ButtonRelease-1>', self.on_release)
        
        # 상태바
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="준비")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 재생 컨트롤
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_button = ttk.Button(control_frame, text="▶ 재생", 
                                      command=self.play_playlist)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(control_frame, text="⏹ 중지", command=self.stop_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏭ 다음", command=self.next_video).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.airplay_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Living AirPlay", 
                        variable=self.airplay_var).pack(side=tk.LEFT, padx=5)
        
        # 진행 상황
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[
                ("비디오/오디오", "*.mp4;*.mov;*.m4v;*.avi;*.mp3;*.m4a;*.aac;*.wav"),
                ("비디오", "*.mp4;*.mov;*.m4v;*.avi"),
                ("오디오", "*.mp3;*.m4a;*.aac;*.wav"),
                ("모든 파일", "*.*")
            ]
        )
        
        for file in files:
            self.add_to_playlist(file)
            
    def add_folder(self):
        """폴더의 모든 미디어 파일 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
            
        extensions = ['.mp4', '.mov', '.m4v', '.avi', '.mp3', '.m4a', '.aac', '.wav']
        folder_path = Path(folder)
        
        for ext in extensions:
            for file in folder_path.glob(f'*{ext}'):
                self.add_to_playlist(str(file))
                
    def add_to_playlist(self, filepath):
        """플레이리스트에 추가"""
        filepath = Path(filepath)
        
        # 오디오 파일인 경우 변환
        audio_extensions = ['.mp3', '.m4a', '.aac', '.wav']
        if filepath.suffix.lower() in audio_extensions:
            self.convert_audio_to_video(filepath)
        else:
            self.playlist.append(str(filepath))
            self.listbox.insert(tk.END, filepath.name)
            
    def convert_audio_to_video(self, audio_file):
        """오디오를 비디오로 변환 (수정된 ffmpeg 명령)"""
        def convert():
            # ffmpeg 찾기
            ffmpeg = None
            if os.path.exists('/opt/homebrew/bin/ffmpeg'):
                ffmpeg = '/opt/homebrew/bin/ffmpeg'
            elif shutil.which('ffmpeg'):
                ffmpeg = 'ffmpeg'
            else:
                messagebox.showerror("FFmpeg 없음", 
                                   "FFmpeg를 설치하세요: brew install ffmpeg")
                return
                
            output_file = audio_file.parent / f"{audio_file.stem}_video.mp4"
            
            self.status_label.config(text=f"변환 중: {audio_file.name}")
            self.progress.start()
            
            # 먼저 오디오 길이 확인
            duration_cmd = [
                ffmpeg, '-i', str(audio_file),
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(duration_cmd, capture_output=True, 
                                  text=True, stderr=subprocess.STDOUT)
            
            # 길이 파싱
            duration = None
            for line in result.stdout.split('\n'):
                if 'Duration:' in line:
                    parts = line.split('Duration: ')[1].split(',')[0]
                    # HH:MM:SS.ms 형식
                    duration = parts.strip()
                    break
                    
            # 수정된 변환 명령 (정확한 길이 지정)
            cmd = [
                ffmpeg,
                '-i', str(audio_file),
                '-f', 'lavfi', '-i', 'color=black:s=1920x1080:r=1',
                '-map', '1:v', '-map', '0:a',
                '-c:v', 'h264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '256k', '-ac', '2',
                '-movflags', '+faststart'
            ]
            
            # 정확한 길이 지정
            if duration:
                cmd.extend(['-t', duration])
            else:
                cmd.extend(['-shortest'])
                
            cmd.extend([str(output_file), '-y'])
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 성공 시 플레이리스트에 추가
                self.playlist.append(str(output_file))
                self.listbox.insert(tk.END, output_file.name)
                
                self.status_label.config(text=f"변환 완료: {output_file.name}")
                
            except subprocess.CalledProcessError as e:
                messagebox.showerror("변환 실패", 
                                   f"변환 중 오류 발생: {audio_file.name}")
                
            finally:
                self.progress.stop()
                
        # 별도 스레드에서 변환
        thread = threading.Thread(target=convert)
        thread.start()
        
    def remove_selected(self):
        """선택된 항목 삭제"""
        selected = self.listbox.curselection()
        for index in reversed(selected):
            del self.playlist[index]
            self.listbox.delete(index)
            
    def move_up(self):
        """선택 항목 위로 이동"""
        selected = self.listbox.curselection()
        if not selected or selected[0] == 0:
            return
            
        index = selected[0]
        # 데이터 교환
        self.playlist[index-1], self.playlist[index] = \
            self.playlist[index], self.playlist[index-1]
            
        # 리스트박스 업데이트
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index-1, item)
        self.listbox.selection_set(index-1)
        
    def move_down(self):
        """선택 항목 아래로 이동"""
        selected = self.listbox.curselection()
        if not selected or selected[0] == len(self.playlist)-1:
            return
            
        index = selected[0]
        # 데이터 교환
        self.playlist[index], self.playlist[index+1] = \
            self.playlist[index+1], self.playlist[index]
            
        # 리스트박스 업데이트
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index+1, item)
        self.listbox.selection_set(index+1)
        
    def save_playlist(self):
        """플레이리스트 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("저장 완료", "플레이리스트가 저장되었습니다.")
            
    def load_playlist_file(self):
        """플레이리스트 파일 불러오기"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.playlist = json.load(f)
                
            self.update_listbox()
            
    def load_playlist(self):
        """자동 저장된 플레이리스트 불러오기"""
        autosave = Path.home() / '.quicktime_playlist.json'
        if autosave.exists():
            try:
                with open(autosave, 'r', encoding='utf-8') as f:
                    self.playlist = json.load(f)
                self.update_listbox()
            except:
                pass
                
    def update_listbox(self):
        """리스트박스 업데이트"""
        self.listbox.delete(0, tk.END)
        for filepath in self.playlist:
            self.listbox.insert(tk.END, Path(filepath).name)
            
    def play_playlist(self):
        """플레이리스트 재생"""
        if not self.playlist:
            messagebox.showwarning("플레이리스트 비어있음", 
                                 "재생할 파일이 없습니다.")
            return
            
        self.is_playing = True
        self.play_button.config(state=tk.DISABLED)
        self.current_index = 0
        
        # 재생 스레드 시작
        thread = threading.Thread(target=self.play_thread)
        thread.start()
        
    def play_thread(self):
        """재생 스레드"""
        while self.is_playing and self.current_index < len(self.playlist):
            video_path = self.playlist[self.current_index]
            
            # UI 업데이트
            self.root.after(0, self.update_playing, self.current_index)
            
            # 비디오 재생
            self.play_video(video_path)
            
            # 다음으로
            self.current_index += 1
            
        self.root.after(0, self.playback_finished)
        
    def play_video(self, video_path):
        """비디오 재생 (Living AirPlay 포함)"""
        # 기존 문서 닫기
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # 새 비디오 열기
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(2)
        
        # AirPlay 설정
        if self.airplay_var.get():
            self.enable_airplay()
            
        # 재생 시작
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 재생 완료 대기
        time.sleep(5)
        while self.is_playing and self.is_video_playing():
            time.sleep(2)
            
    def enable_airplay(self):
        """Living AirPlay 설정"""
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
        
    def update_playing(self, index):
        """재생 중인 항목 표시"""
        # 모든 항목 배경색 초기화
        for i in range(self.listbox.size()):
            self.listbox.itemconfig(i, background='')
            
        # 현재 재생 중인 항목 강조
        self.listbox.itemconfig(index, background='lightblue')
        self.listbox.see(index)
        
        # 상태 업데이트
        filename = Path(self.playlist[index]).name
        self.status_label.config(text=f"재생 중: {filename}")
        
    def playback_finished(self):
        """재생 완료"""
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.status_label.config(text="재생 완료")
        
        # 모든 항목 배경색 초기화
        for i in range(self.listbox.size()):
            self.listbox.itemconfig(i, background='')
            
    def stop_playlist(self):
        """재생 중지"""
        self.is_playing = False
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to stop front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def next_video(self):
        """다음 비디오"""
        if self.is_playing and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to stop front document'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    def on_click(self, event):
        """드래그 시작"""
        self.drag_start_index = self.listbox.nearest(event.y)
        
    def on_drag(self, event):
        """드래그 중"""
        i = self.listbox.nearest(event.y)
        if i < self.drag_start_index:
            x = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i+1, x)
            self.drag_start_index = i
        elif i > self.drag_start_index:
            x = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i-1, x)
            self.drag_start_index = i
            
    def on_release(self, event):
        """드래그 종료"""
        # 플레이리스트 순서 업데이트
        self.playlist = []
        for i in range(self.listbox.size()):
            item_text = self.listbox.get(i)
            # 원본 경로 찾기
            for path in self.playlist:
                if Path(path).name == item_text:
                    self.playlist.append(path)
                    break
                    
    def __del__(self):
        """자동 저장"""
        autosave = Path.home() / '.quicktime_playlist.json'
        try:
            with open(autosave, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False, indent=2)
        except:
            pass

def main():
    root = tk.Tk()
    app = PlaylistEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()