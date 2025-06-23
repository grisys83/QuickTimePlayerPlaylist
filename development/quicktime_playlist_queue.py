#!/usr/bin/env python3
"""
QuickTime 플레이리스트 큐 시스템
- 재생 중에도 큐에 추가 가능
- 재생 상태 실시간 추적
- Roon 스타일의 큐 관리
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
from datetime import datetime
import queue

class PlaylistQueue:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Playlist Queue")
        self.root.geometry("900x700")
        
        # 큐 시스템
        self.play_queue = []  # 재생 대기 큐
        self.play_history = []  # 재생 기록
        self.current_track = None
        self.is_playing = False
        self.player_thread = None
        
        # 재생 상태 파일
        self.state_file = Path.home() / '.quicktime_queue_state.json'
        self.queue_file = Path.home() / '.quicktime_queue.json'
        
        # 스레드 간 통신
        self.command_queue = queue.Queue()
        
        self.setup_ui()
        self.load_state()
        self.start_player_thread()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임을 3개 섹션으로 분할
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 1. 현재 재생 중 (상단)
        self.setup_now_playing(main_frame)
        
        # 2. 재생 큐 (중간)
        self.setup_play_queue(main_frame)
        
        # 3. 라이브러리/파일 브라우저 (하단)
        self.setup_library(main_frame)
        
        # 상태바
        self.setup_status_bar()
        
    def setup_now_playing(self, parent):
        """현재 재생 중 섹션"""
        frame = ttk.LabelFrame(parent, text="현재 재생 중", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        # 트랙 정보
        self.now_playing_label = ttk.Label(frame, text="재생 중인 트랙 없음", 
                                          font=('Arial', 14, 'bold'))
        self.now_playing_label.pack(anchor=tk.W)
        
        # 진행 상황
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.time_label = ttk.Label(progress_frame, text="0:00")
        self.time_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.duration_label = ttk.Label(progress_frame, text="0:00")
        self.duration_label.pack(side=tk.LEFT)
        
        # 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=(10, 0))
        
        ttk.Button(control_frame, text="⏮", width=3, 
                  command=self.previous_track).pack(side=tk.LEFT, padx=2)
        
        self.play_pause_button = ttk.Button(control_frame, text="▶", width=3,
                                           command=self.toggle_play_pause)
        self.play_pause_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(control_frame, text="⏹", width=3,
                  command=self.stop_playback).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(control_frame, text="⏭", width=3,
                  command=self.next_track).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, 
                                                              fill=tk.Y, padx=10)
        
        self.airplay_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Living AirPlay", 
                       variable=self.airplay_var).pack(side=tk.LEFT)
        
    def setup_play_queue(self, parent):
        """재생 큐 섹션"""
        frame = ttk.LabelFrame(parent, text="재생 큐", padding=5)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 큐 툴바
        queue_toolbar = ttk.Frame(frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(queue_toolbar, text="큐 비우기", 
                  command=self.clear_queue).pack(side=tk.LEFT, padx=2)
        ttk.Button(queue_toolbar, text="선택 제거", 
                  command=self.remove_from_queue).pack(side=tk.LEFT, padx=2)
        ttk.Button(queue_toolbar, text="위로", 
                  command=self.move_queue_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(queue_toolbar, text="아래로", 
                  command=self.move_queue_down).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(queue_toolbar, text="").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="0개 대기 중")
        self.queue_count_label.pack(side=tk.RIGHT, padx=5)
        
        # 큐 리스트
        queue_frame = ttk.Frame(frame)
        queue_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(queue_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.queue_listbox = tk.Listbox(queue_frame, selectmode=tk.EXTENDED,
                                       yscrollcommand=scrollbar.set)
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.queue_listbox.yview)
        
        # 드래그 앤 드롭
        self.queue_listbox.bind('<Double-Button-1>', self.play_from_queue)
        
    def setup_library(self, parent):
        """라이브러리/파일 브라우저 섹션"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 파일 브라우저 탭
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="파일 추가")
        
        # 파일 추가 버튼들
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="파일 추가", 
                  command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="폴더 추가", 
                  command=self.add_folder).pack(side=tk.LEFT, padx=2)
        
        # 최근 추가된 파일 목록
        self.recent_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.recent_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 더블클릭으로 큐에 추가
        self.recent_listbox.bind('<Double-Button-1>', self.add_to_queue_from_recent)
        
        # 재생 기록 탭
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="재생 기록")
        
        self.history_listbox = tk.Listbox(history_frame)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_status_bar(self):
        """상태바"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="준비", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.connection_label = ttk.Label(status_frame, text="● QuickTime 연결", 
                                         foreground="green")
        self.connection_label.pack(side=tk.RIGHT, padx=5)
        
    def start_player_thread(self):
        """재생 스레드 시작"""
        self.player_thread = threading.Thread(target=self.player_loop, daemon=True)
        self.player_thread.start()
        
    def player_loop(self):
        """재생 루프 (별도 스레드)"""
        while True:
            try:
                # 명령 처리
                try:
                    command = self.command_queue.get_nowait()
                    if command == 'play':
                        self.is_playing = True
                    elif command == 'pause':
                        self.is_playing = False
                    elif command == 'stop':
                        self.is_playing = False
                        self.current_track = None
                    elif command == 'next':
                        self.play_next_in_queue()
                except queue.Empty:
                    pass
                
                # 재생 처리
                if self.is_playing:
                    if self.current_track is None and self.play_queue:
                        self.play_next_in_queue()
                    elif self.current_track and not self.is_video_playing():
                        # 현재 트랙 종료, 다음 트랙 재생
                        self.track_finished()
                        
                time.sleep(1)
                
            except Exception as e:
                print(f"Player thread error: {e}")
                
    def play_next_in_queue(self):
        """큐에서 다음 트랙 재생"""
        if not self.play_queue:
            self.is_playing = False
            self.current_track = None
            self.root.after(0, self.update_now_playing, None)
            return
            
        # 큐에서 트랙 가져오기
        track = self.play_queue.pop(0)
        self.current_track = track
        
        # 재생 기록에 추가
        self.play_history.append({
            'file': track,
            'played_at': datetime.now().isoformat()
        })
        
        # UI 업데이트
        self.root.after(0, self.update_now_playing, track)
        self.root.after(0, self.update_queue_display)
        self.root.after(0, self.update_history_display)
        
        # QuickTime에서 재생
        self.play_in_quicktime(track)
        
    def play_in_quicktime(self, filepath):
        """QuickTime에서 파일 재생"""
        # 기존 문서 닫기
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # 오디오 파일 체크 및 변환
        if Path(filepath).suffix.lower() in ['.mp3', '.m4a', '.aac', '.wav']:
            filepath = self.convert_audio_file(filepath)
            
        # 새 파일 열기
        subprocess.run(['open', '-a', 'QuickTime Player', filepath])
        time.sleep(2)
        
        # AirPlay 설정
        if self.airplay_var.get():
            self.enable_airplay()
            
        # 재생 시작
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def convert_audio_file(self, audio_file):
        """오디오 파일을 비디오로 변환"""
        video_file = Path(audio_file).parent / f"{Path(audio_file).stem}_video.mp4"
        
        if video_file.exists():
            return str(video_file)
            
        # ffmpeg 찾기
        ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        if not os.path.exists(ffmpeg) and not shutil.which('ffmpeg'):
            return audio_file
            
        # 오디오 길이 확인
        duration_cmd = [ffmpeg, '-i', audio_file, '-f', 'null', '-']
        result = subprocess.run(duration_cmd, capture_output=True, 
                              text=True, stderr=subprocess.STDOUT)
        
        duration = None
        for line in result.stdout.split('\n'):
            if 'Duration:' in line:
                duration = line.split('Duration: ')[1].split(',')[0].strip()
                break
                
        # 변환
        cmd = [
            ffmpeg, '-i', audio_file,
            '-f', 'lavfi', '-i', 'color=black:s=1920x1080:r=1',
            '-map', '1:v', '-map', '0:a',
            '-c:v', 'h264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
            '-c:a', 'copy'  # 오디오는 재인코딩하지 않음
        ]
        
        if duration:
            cmd.extend(['-t', duration])
        else:
            cmd.extend(['-shortest'])
            
        cmd.extend([str(video_file), '-y'])
        
        subprocess.run(cmd, capture_output=True)
        
        return str(video_file)
        
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
        
    def track_finished(self):
        """트랙 재생 완료"""
        self.save_state()
        
        if self.play_queue:
            self.play_next_in_queue()
        else:
            self.is_playing = False
            self.current_track = None
            self.root.after(0, self.update_now_playing, None)
            
    def add_files(self):
        """파일 선택 대화상자"""
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[
                ("미디어 파일", "*.mp4;*.mov;*.m4v;*.avi;*.mp3;*.m4a;*.aac;*.wav"),
                ("비디오", "*.mp4;*.mov;*.m4v;*.avi"),
                ("오디오", "*.mp3;*.m4a;*.aac;*.wav"),
                ("모든 파일", "*.*")
            ]
        )
        
        for file in files:
            self.add_to_queue(file)
            self.recent_listbox.insert(tk.END, Path(file).name)
            
    def add_folder(self):
        """폴더의 모든 미디어 파일 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
            
        extensions = ['.mp4', '.mov', '.m4v', '.avi', '.mp3', '.m4a', '.aac', '.wav']
        folder_path = Path(folder)
        
        count = 0
        for ext in extensions:
            for file in folder_path.glob(f'*{ext}'):
                self.add_to_queue(str(file))
                self.recent_listbox.insert(tk.END, file.name)
                count += 1
                
        self.status_label.config(text=f"{count}개 파일이 큐에 추가됨")
        
    def add_to_queue(self, filepath):
        """큐에 추가"""
        self.play_queue.append(filepath)
        self.update_queue_display()
        self.save_state()
        
        # 재생 중이 아니면 자동 시작
        if not self.is_playing and len(self.play_queue) == 1:
            self.command_queue.put('play')
            
    def add_to_queue_from_recent(self, event):
        """최근 목록에서 더블클릭으로 큐에 추가"""
        selection = self.recent_listbox.curselection()
        if selection:
            filename = self.recent_listbox.get(selection[0])
            # 실제 경로 찾기 (간단히 구현)
            for i in range(self.recent_listbox.size()):
                if self.recent_listbox.get(i) == filename:
                    # 실제로는 파일 경로 매핑이 필요
                    self.add_to_queue(filename)
                    break
                    
    def play_from_queue(self, event):
        """큐에서 더블클릭으로 즉시 재생"""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            # 해당 인덱스까지의 트랙을 건너뛰기
            self.play_queue = self.play_queue[index:]
            self.command_queue.put('next')
            
    def update_now_playing(self, track):
        """현재 재생 중 UI 업데이트"""
        if track:
            self.now_playing_label.config(text=Path(track).name)
            self.play_pause_button.config(text="⏸")
        else:
            self.now_playing_label.config(text="재생 중인 트랙 없음")
            self.play_pause_button.config(text="▶")
            self.progress_bar['value'] = 0
            
    def update_queue_display(self):
        """큐 표시 업데이트"""
        self.queue_listbox.delete(0, tk.END)
        for i, track in enumerate(self.play_queue):
            self.queue_listbox.insert(tk.END, f"{i+1}. {Path(track).name}")
            
        count = len(self.play_queue)
        self.queue_count_label.config(text=f"{count}개 대기 중")
        
    def update_history_display(self):
        """재생 기록 업데이트"""
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.play_history[-50:]):  # 최근 50개만
            time_str = datetime.fromisoformat(item['played_at']).strftime('%H:%M')
            self.history_listbox.insert(tk.END, 
                                       f"{time_str} - {Path(item['file']).name}")
                                       
    def toggle_play_pause(self):
        """재생/일시정지 토글"""
        if self.is_playing:
            self.command_queue.put('pause')
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to pause front document'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.play_pause_button.config(text="▶")
        else:
            self.command_queue.put('play')
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to play front document'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.play_pause_button.config(text="⏸")
            
    def stop_playback(self):
        """재생 중지"""
        self.command_queue.put('stop')
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def next_track(self):
        """다음 트랙"""
        self.command_queue.put('next')
        
    def previous_track(self):
        """이전 트랙 (재생 기록에서)"""
        if len(self.play_history) > 1:
            # 마지막 트랙을 큐 맨 앞에 추가
            last_track = self.play_history[-2]['file']  # -1은 현재 트랙
            self.play_queue.insert(0, last_track)
            self.update_queue_display()
            self.command_queue.put('next')
            
    def clear_queue(self):
        """큐 비우기"""
        self.play_queue.clear()
        self.update_queue_display()
        self.save_state()
        
    def remove_from_queue(self):
        """선택된 항목 큐에서 제거"""
        selected = list(self.queue_listbox.curselection())
        for index in reversed(selected):
            del self.play_queue[index]
        self.update_queue_display()
        self.save_state()
        
    def move_queue_up(self):
        """큐에서 위로 이동"""
        selected = self.queue_listbox.curselection()
        if selected and selected[0] > 0:
            index = selected[0]
            self.play_queue[index-1], self.play_queue[index] = \
                self.play_queue[index], self.play_queue[index-1]
            self.update_queue_display()
            self.queue_listbox.selection_set(index-1)
            
    def move_queue_down(self):
        """큐에서 아래로 이동"""
        selected = self.queue_listbox.curselection()
        if selected and selected[0] < len(self.play_queue)-1:
            index = selected[0]
            self.play_queue[index], self.play_queue[index+1] = \
                self.play_queue[index+1], self.play_queue[index]
            self.update_queue_display()
            self.queue_listbox.selection_set(index+1)
            
    def save_state(self):
        """상태 저장"""
        state = {
            'current_track': self.current_track,
            'is_playing': self.is_playing,
            'play_queue': self.play_queue,
            'play_history': self.play_history[-100:],  # 최근 100개만
            'airplay_enabled': self.airplay_var.get()
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
    def load_state(self):
        """상태 불러오기"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    
                self.play_queue = state.get('play_queue', [])
                self.play_history = state.get('play_history', [])
                self.airplay_var.set(state.get('airplay_enabled', True))
                
                self.update_queue_display()
                self.update_history_display()
            except:
                pass
                
    def on_closing(self):
        """종료 시"""
        self.save_state()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PlaylistQueue(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()