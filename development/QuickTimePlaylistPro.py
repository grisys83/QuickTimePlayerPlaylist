#!/usr/bin/env python3
"""
QuickTime Playlist Pro
The Ultimate AirPlay Music & Video Experience for HomePod Users

통합 기능:
- 스마트 플레이리스트 관리
- 오디오를 아름다운 비디오로 자동 변환
- HomePod/Apple TV AirPlay 자동 연결
- Roon 스타일 큐 시스템
- 카페/매장 모드
- 클라우드 동기화 준비
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import threading
import time
import json
import queue
import shutil
import random
from pathlib import Path
from datetime import datetime
import webbrowser

# 필요한 모듈 import 시도
try:
    from audio_to_video_enhanced import AudioToVideoConverter
except ImportError:
    AudioToVideoConverter = None

class QuickTimePlaylistPro:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTime Playlist Pro - HomePod Edition")
        self.root.geometry("1200x800")
        
        # 앱 상태
        self.version = "1.0.0"
        self.is_pro_mode = True
        self.current_mode = "normal"  # normal, cafe, party
        
        # 플레이리스트 데이터
        self.playlist = []
        self.play_queue = []
        self.play_history = []
        self.current_index = 0
        self.is_playing = False
        self.current_track = None
        
        # 재생 옵션
        self.shuffle_enabled = tk.BooleanVar(value=False)
        self.repeat_enabled = tk.BooleanVar(value=True)
        self.airplay_enabled = tk.BooleanVar(value=True)
        
        # 스레드 관련
        self.player_thread = None
        self.command_queue = queue.Queue()
        
        # 모드 변수
        self.mode_var = tk.StringVar(value="normal")
        
        # 변환할 파일들
        self.files_to_convert = []
        
        # 설정
        self.settings = self.load_settings()
        
        # 테마 설정
        self.setup_theme()
        
        # UI 구성
        self.setup_menu()
        self.setup_ui()
        
        # 플레이어 스레드 시작
        self.start_player_thread()
        
        # 초기화 메시지
        self.show_welcome()
        
        # 종료 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_theme(self):
        """모던 테마 설정"""
        style = ttk.Style()
        
        # 다크 모드 스타일
        style.theme_use('default')
        
        # 색상 정의
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007AFF',  # Apple Blue
            'success': '#34C759',
            'warning': '#FF9500',
            'danger': '#FF3B30',
            'sidebar': '#2d2d2d',
            'hover': '#3d3d3d'
        }
        
        # 커스텀 스타일
        style.configure('Title.TLabel', font=('SF Pro Display', 24, 'bold'))
        style.configure('Heading.TLabel', font=('SF Pro Display', 16, 'bold'))
        style.configure('Accent.TButton', foreground=self.colors['accent'])
        
    def setup_menu(self):
        """메뉴바 설정"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새 플레이리스트", command=self.new_playlist)
        file_menu.add_command(label="플레이리스트 열기", command=self.open_playlist)
        file_menu.add_command(label="플레이리스트 저장", command=self.save_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="설정", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit_app)
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="편집", menu=edit_menu)
        edit_menu.add_command(label="모두 선택", command=self.select_all)
        edit_menu.add_command(label="선택 제거", command=self.remove_selected)
        
        # 재생 메뉴
        play_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="재생", menu=play_menu)
        play_menu.add_command(label="재생/일시정지", command=self.toggle_playback)
        play_menu.add_command(label="다음 트랙", command=self.next_track)
        play_menu.add_command(label="이전 트랙", command=self.previous_track)
        play_menu.add_separator()
        play_menu.add_checkbutton(label="셔플", variable=self.shuffle_enabled, command=self.toggle_shuffle)
        play_menu.add_checkbutton(label="반복", variable=self.repeat_enabled, command=self.toggle_repeat)
        
        # 모드 메뉴
        mode_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="모드", menu=mode_menu)
        mode_menu.add_radiobutton(label="일반 모드", variable=self.mode_var, value="normal", command=self.change_mode)
        mode_menu.add_radiobutton(label="카페 모드", variable=self.mode_var, value="cafe", command=self.change_mode)
        mode_menu.add_radiobutton(label="파티 모드", variable=self.mode_var, value="party", command=self.change_mode)
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="오디오 일괄 변환", command=self.batch_convert)
        tools_menu.add_command(label="AirPlay 기기 검색", command=self.scan_airplay)
        tools_menu.add_command(label="메타데이터 편집기", command=self.edit_metadata)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용 가이드", command=self.show_guide)
        help_menu.add_command(label="HomePod 커뮤니티", command=self.open_community)
        help_menu.add_separator()
        help_menu.add_command(label="정보", command=self.show_about)
        
    def setup_ui(self):
        """메인 UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 좌측 사이드바
        self.setup_sidebar(main_container)
        
        # 중앙 콘텐츠 영역
        self.setup_content_area(main_container)
        
        # 하단 플레이어
        self.setup_player_controls()
        
    def setup_sidebar(self, parent):
        """사이드바 설정"""
        sidebar = ttk.Frame(parent, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        sidebar.pack_propagate(False)
        
        # 로고/타이틀
        title_frame = ttk.Frame(sidebar)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(title_frame, text="♫", font=('Arial', 36)).pack()
        ttk.Label(title_frame, text="QuickTime Playlist Pro", 
                 style='Heading.TLabel').pack()
        ttk.Label(title_frame, text="HomePod Edition", 
                 font=('SF Pro', 10)).pack()
        
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 라이브러리
        ttk.Label(sidebar, text="라이브러리", 
                 font=('SF Pro', 12, 'bold')).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        library_frame = ttk.Frame(sidebar)
        library_frame.pack(fill=tk.X, padx=20)
        
        self.create_sidebar_button(library_frame, "🎵 모든 음악", self.show_all_music)
        self.create_sidebar_button(library_frame, "🎬 비디오", self.show_videos)
        self.create_sidebar_button(library_frame, "📱 AirPlay 큐", self.show_queue)
        self.create_sidebar_button(library_frame, "⭐ 즐겨찾기", self.show_favorites)
        
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 플레이리스트
        ttk.Label(sidebar, text="플레이리스트", 
                 font=('SF Pro', 12, 'bold')).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        playlist_frame = ttk.Frame(sidebar)
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 플레이리스트 목록
        self.playlist_listbox = tk.Listbox(playlist_frame, 
                                          selectmode=tk.SINGLE,
                                          bg=self.colors['sidebar'],
                                          fg=self.colors['fg'],
                                          selectbackground=self.colors['accent'],
                                          borderwidth=0,
                                          highlightthickness=0)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 플레이리스트 추가 버튼
        add_playlist_btn = ttk.Button(sidebar, text="+ 새 플레이리스트",
                                     command=self.create_playlist)
        add_playlist_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # AirPlay 상태
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        airplay_frame = ttk.Frame(sidebar)
        airplay_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.airplay_status = ttk.Label(airplay_frame, 
                                       text="● AirPlay: Living",
                                       foreground=self.colors['success'])
        self.airplay_status.pack(side=tk.LEFT)
        
        ttk.Button(airplay_frame, text="변경", width=6,
                  command=self.change_airplay).pack(side=tk.RIGHT)
        
    def setup_content_area(self, parent):
        """중앙 콘텐츠 영역"""
        content = ttk.Frame(parent)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 탭 뷰
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 현재 재생 중 탭
        self.now_playing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.now_playing_tab, text="현재 재생 중")
        self.setup_now_playing_tab()
        
        # 큐 탭
        self.queue_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.queue_tab, text="재생 큐")
        self.setup_queue_tab()
        
        # 라이브러리 탭
        self.library_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.library_tab, text="라이브러리")
        self.setup_library_tab()
        
        # 변환 도구 탭
        self.converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_tab, text="비디오 변환")
        self.setup_converter_tab()
        
    def setup_now_playing_tab(self):
        """현재 재생 중 탭"""
        # 앨범 아트
        art_frame = ttk.Frame(self.now_playing_tab)
        art_frame.pack(pady=20)
        
        self.album_art_label = ttk.Label(art_frame, text="🎵",
                                        font=('Arial', 120))
        self.album_art_label.pack()
        
        # 트랙 정보
        info_frame = ttk.Frame(self.now_playing_tab)
        info_frame.pack(pady=20)
        
        self.track_title = ttk.Label(info_frame, text="재생 중인 트랙 없음",
                                    font=('SF Pro Display', 24, 'bold'))
        self.track_title.pack()
        
        self.track_artist = ttk.Label(info_frame, text="",
                                     font=('SF Pro', 16))
        self.track_artist.pack(pady=5)
        
        self.track_album = ttk.Label(info_frame, text="",
                                    font=('SF Pro', 14),
                                    foreground='gray')
        self.track_album.pack()
        
        # 진행 바
        progress_frame = ttk.Frame(self.now_playing_tab)
        progress_frame.pack(fill=tk.X, padx=50, pady=20)
        
        self.time_current = ttk.Label(progress_frame, text="0:00")
        self.time_current.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='determinate',
                                           length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.time_total = ttk.Label(progress_frame, text="0:00")
        self.time_total.pack(side=tk.LEFT)
        
        # 가사/비주얼라이저 (향후 기능)
        visual_frame = ttk.LabelFrame(self.now_playing_tab, 
                                     text="비주얼라이저", 
                                     padding=20)
        visual_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(visual_frame, text="♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫",
                 font=('Arial', 20)).pack(expand=True)
        
    def setup_queue_tab(self):
        """재생 큐 탭"""
        # 큐 컨트롤
        queue_controls = ttk.Frame(self.queue_tab)
        queue_controls.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(queue_controls, text="큐 비우기",
                  command=self.clear_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="큐 저장",
                  command=self.save_queue).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(queue_controls, text="").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.queue_info = ttk.Label(queue_controls, text="0개 대기 중")
        self.queue_info.pack(side=tk.RIGHT, padx=5)
        
        # 큐 리스트
        queue_frame = ttk.Frame(self.queue_tab)
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(queue_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스로 큐 표시
        self.queue_listbox = tk.Listbox(queue_frame, 
                                       selectmode=tk.EXTENDED,
                                       yscrollcommand=scrollbar.set)
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.queue_listbox.yview)
        
        # 더블클릭으로 즉시 재생
        self.queue_listbox.bind('<Double-Button-1>', self.play_from_queue)
        
    def setup_library_tab(self):
        """라이브러리 탭"""
        # 버튼 프레임
        button_frame = ttk.Frame(self.library_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="파일 추가",
                  command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="폴더 추가",
                  command=self.add_folder).pack(side=tk.LEFT, padx=5)
        
        # 라이브러리 리스트
        library_frame = ttk.Frame(self.library_tab)
        library_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(library_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스
        self.library_listbox = tk.Listbox(library_frame,
                                         selectmode=tk.EXTENDED,
                                         yscrollcommand=scrollbar.set)
        self.library_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.library_listbox.yview)
        
        # 더블클릭으로 큐에 추가
        self.library_listbox.bind('<Double-Button-1>', self.add_to_queue_from_library)
        
    def setup_converter_tab(self):
        """비디오 변환 탭"""
        # 설명
        info_frame = ttk.Frame(self.converter_tab)
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(info_frame, text="오디오를 아름다운 비디오로 변환",
                 style='Heading.TLabel').pack()
        ttk.Label(info_frame, 
                 text="앨범 커버, 제목, 아티스트 정보가 포함된 비디오를 생성합니다.",
                 foreground='gray').pack(pady=5)
        
        # 파일 선택
        file_frame = ttk.LabelFrame(self.converter_tab, text="파일 선택", padding=20)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 버튼
        ttk.Button(file_frame, text="오디오 파일 선택",
                  command=self.select_audio_files).pack(pady=10)
        
        # 선택된 파일 리스트
        self.convert_listbox = tk.Listbox(file_frame, height=10)
        self.convert_listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 변환 옵션
        options_frame = ttk.LabelFrame(self.converter_tab, text="변환 옵션", padding=10)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.hd_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="HD 품질 (1920x1080)",
                       variable=self.hd_var).pack(anchor=tk.W)
        
        self.artwork_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="앨범 아트 포함",
                       variable=self.artwork_var).pack(anchor=tk.W)
        
        # 변환 버튼
        convert_btn = ttk.Button(self.converter_tab, 
                                text="변환 시작",
                                command=self.start_conversion,
                                style='Accent.TButton')
        convert_btn.pack(pady=20)
        
        # 진행 상황
        self.conversion_progress = ttk.Progressbar(self.converter_tab,
                                                  mode='indeterminate')
        self.conversion_progress.pack(fill=tk.X, padx=20, pady=10)
        
    def setup_player_controls(self):
        """하단 플레이어 컨트롤"""
        player_frame = ttk.Frame(self.root)
        player_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(player_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        controls = ttk.Frame(player_frame)
        controls.pack(fill=tk.X, padx=20, pady=10)
        
        # 좌측: 트랙 정보
        track_info = ttk.Frame(controls)
        track_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.mini_track_title = ttk.Label(track_info, text="재생 중인 트랙 없음",
                                         font=('SF Pro', 12, 'bold'))
        self.mini_track_title.pack(anchor=tk.W)
        
        self.mini_track_artist = ttk.Label(track_info, text="",
                                          font=('SF Pro', 10),
                                          foreground='gray')
        self.mini_track_artist.pack(anchor=tk.W)
        
        # 중앙: 재생 컨트롤
        play_controls = ttk.Frame(controls)
        play_controls.pack(side=tk.LEFT, padx=50)
        
        ttk.Button(play_controls, text="⏮", width=3,
                  command=self.previous_track).pack(side=tk.LEFT, padx=2)
        
        self.play_btn = ttk.Button(play_controls, text="▶", width=3,
                                  command=self.toggle_playback)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(play_controls, text="⏭", width=3,
                  command=self.next_track).pack(side=tk.LEFT, padx=2)
        
        # 우측: 볼륨 및 옵션
        options_frame = ttk.Frame(controls)
        options_frame.pack(side=tk.RIGHT)
        
        # AirPlay
        ttk.Checkbutton(options_frame, text="AirPlay",
                       variable=self.airplay_enabled).pack(side=tk.LEFT, padx=5)
        
        # 셔플
        self.shuffle_btn = ttk.Button(options_frame, text="🔀", width=3,
                                     command=self.toggle_shuffle)
        self.shuffle_btn.pack(side=tk.LEFT, padx=2)
        
        # 반복
        self.repeat_btn = ttk.Button(options_frame, text="🔁", width=3,
                                    command=self.toggle_repeat)
        self.repeat_btn.pack(side=tk.LEFT, padx=2)
        
        # 볼륨
        ttk.Label(options_frame, text="🔊").pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(options_frame, from_=0, to=100,
                                     orient=tk.HORIZONTAL, length=100,
                                     command=self.change_volume)
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT)
        
    def create_sidebar_button(self, parent, text, command):
        """사이드바 버튼 생성"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.colors['sidebar'],
                       fg=self.colors['fg'],
                       bd=0,
                       padx=10,
                       pady=5,
                       anchor=tk.W,
                       font=('SF Pro', 11))
        btn.pack(fill=tk.X, pady=2)
        
        # 호버 효과
        btn.bind('<Enter>', lambda e: btn.config(bg=self.colors['hover']))
        btn.bind('<Leave>', lambda e: btn.config(bg=self.colors['sidebar']))
        
        return btn
        
    def show_welcome(self):
        """환영 메시지"""
        welcome = tk.Toplevel(self.root)
        welcome.title("환영합니다!")
        welcome.geometry("500x350")
        
        ttk.Label(welcome, text="QuickTime Playlist Pro",
                 font=('SF Pro Display', 24, 'bold')).pack(pady=20)
        
        ttk.Label(welcome, text="HomePod을 위한 완벽한 플레이리스트 솔루션",
                 font=('SF Pro', 14)).pack()
        
        features = ttk.Frame(welcome)
        features.pack(pady=20)
        
        feature_list = [
            "✓ 오디오를 아름다운 비디오로 자동 변환",
            "✓ HomePod/Apple TV AirPlay 자동 연결",
            "✓ 스마트 큐 시스템",
            "✓ 카페/매장 모드 지원",
            "✓ 메타데이터 기반 시각화"
        ]
        
        for feature in feature_list:
            ttk.Label(features, text=feature,
                     font=('SF Pro', 11)).pack(anchor=tk.W, pady=2)
        
        # 모토
        ttk.Label(welcome, text='"우린 전설이 될 거에요"',
                 font=('SF Pro', 12, 'italic'),
                 foreground='gray').pack(pady=10)
        
        ttk.Button(welcome, text="시작하기",
                  command=welcome.destroy).pack(pady=20)
        
        # 5초 후 자동 닫기
        welcome.after(5000, welcome.destroy)
        
    def load_settings(self):
        """설정 불러오기"""
        settings_file = Path.home() / '.quicktime_playlist_pro.json'
        
        default_settings = {
            'airplay_device': 'Living',
            'auto_convert': True,
            'hd_quality': True,
            'cafe_mode_hours': {'start': '09:00', 'end': '22:00'},
            'theme': 'dark',
            'last_playlist': None,
            'airplay_coordinates': {
                'control': [640, 700],
                'button': [844, 714],
                'device': [970, 784]
            }
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    default_settings.update(settings)
            except:
                pass
                
        return default_settings
        
    def save_settings(self):
        """설정 저장"""
        settings_file = Path.home() / '.quicktime_playlist_pro.json'
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
            
    # 플레이어 관련 메서드
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
                        self.play_next()
                    elif command == 'previous':
                        self.play_previous()
                except queue.Empty:
                    pass
                
                # 재생 처리
                if self.is_playing:
                    if self.current_track is None and self.play_queue:
                        self.play_next()
                    elif self.current_track and not self.is_video_playing():
                        # 현재 트랙 종료, 다음 트랙 재생
                        self.track_finished()
                        
                time.sleep(1)
                
            except Exception as e:
                print(f"Player thread error: {e}")
                
    def toggle_playback(self):
        """재생/일시정지"""
        if not self.is_playing:
            if not self.play_queue and not self.playlist:
                messagebox.showwarning("플레이리스트 비어있음", 
                                     "재생할 파일이 없습니다.")
                return
                
            # 큐가 비어있으면 플레이리스트에서 큐로 복사
            if not self.play_queue and self.playlist:
                self.play_queue = self.playlist.copy()
                if self.shuffle_enabled.get():
                    random.shuffle(self.play_queue)
                self.update_queue_display()
                
            self.command_queue.put('play')
            self.play_btn.config(text="⏸")
        else:
            self.command_queue.put('pause')
            self.play_btn.config(text="▶")
            # QuickTime 일시정지
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to pause front document'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    def next_track(self):
        """다음 트랙"""
        self.command_queue.put('next')
        
    def previous_track(self):
        """이전 트랙"""
        self.command_queue.put('previous')
        
    def play_next(self):
        """다음 트랙 재생"""
        if not self.play_queue:
            if self.repeat_enabled.get() and self.playlist:
                # 반복 모드일 때 다시 시작
                self.play_queue = self.playlist.copy()
                if self.shuffle_enabled.get():
                    random.shuffle(self.play_queue)
            else:
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
        
        # QuickTime에서 재생
        self.play_in_quicktime(track)
        
    def play_previous(self):
        """이전 트랙 재생"""
        if len(self.play_history) > 1:
            # 현재 트랙을 큐 맨 앞에 추가
            if self.current_track:
                self.play_queue.insert(0, self.current_track)
                
            # 이전 트랙 가져오기
            previous = self.play_history[-2]
            self.play_queue.insert(0, previous['file'])
            
            # 다음 트랙 재생
            self.play_next()
            
    def play_in_quicktime(self, filepath):
        """QuickTime에서 파일 재생"""
        # 기존 문서 닫기
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # 오디오 파일 체크 및 변환
        if Path(filepath).suffix.lower() in ['.mp3', '.m4a', '.aac', '.wav', '.flac']:
            filepath = self.convert_audio_file(filepath)
            if not filepath:
                return
                
        # 새 파일 열기
        subprocess.run(['open', '-a', 'QuickTime Player', filepath])
        time.sleep(2)
        
        # AirPlay 설정
        if self.airplay_enabled.get():
            self.enable_airplay()
            
        # 재생 시작
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def convert_audio_file(self, audio_file):
        """오디오 파일을 비디오로 변환"""
        if AudioToVideoConverter:
            converter = AudioToVideoConverter()
            output = converter.convert_to_video(audio_file)
            return output
        else:
            # 간단한 변환 - 이전 쉘 스크립트와 동일한 방식
            video_file = Path(audio_file).with_suffix('_airplay.mp4')
            if video_file.exists():
                return str(video_file)
                
            ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
            if not os.path.exists(ffmpeg) and not shutil.which('ffmpeg'):
                return audio_file
                
            cmd = [
                ffmpeg,
                '-f', 'lavfi', '-i', 'color=black:s=1920x1080:r=1',
                '-i', audio_file,
                '-map', '0:v', '-map', '1:a:0',  # 명시적 맵핑
                '-c:v', 'h264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '256k', '-ac', '2',  # 스테레오 강제
                '-shortest', '-movflags', '+faststart',
                str(video_file), '-y', '-loglevel', 'error'
            ]
            
            subprocess.run(cmd, capture_output=True)
            return str(video_file) if video_file.exists() else audio_file
            
    def enable_airplay(self):
        """AirPlay 설정"""
        try:
            coords = self.settings['airplay_coordinates']
            subprocess.run(['cliclick', f"m:{coords['control'][0]},{coords['control'][1]}"])
            time.sleep(0.5)
            subprocess.run(['cliclick', f"c:{coords['button'][0]},{coords['button'][1]}"])
            time.sleep(0.5)
            subprocess.run(['cliclick', f"c:{coords['device'][0]},{coords['device'][1]}"])
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
        if self.play_queue or (self.repeat_enabled.get() and self.playlist):
            self.play_next()
        else:
            self.is_playing = False
            self.current_track = None
            self.root.after(0, self.update_now_playing, None)
            self.play_btn.config(text="▶")
            
    def update_now_playing(self, track):
        """현재 재생 중 UI 업데이트"""
        if track:
            filename = Path(track).name
            self.track_title.config(text=filename)
            self.mini_track_title.config(text=filename)
            
            # 메타데이터 추출 시도 (간단히)
            self.track_artist.config(text="")
            self.track_album.config(text="")
            self.mini_track_artist.config(text="")
        else:
            self.track_title.config(text="재생 중인 트랙 없음")
            self.track_artist.config(text="")
            self.track_album.config(text="")
            self.mini_track_title.config(text="재생 중인 트랙 없음")
            self.mini_track_artist.config(text="")
            
    def update_queue_display(self):
        """큐 표시 업데이트"""
        self.queue_listbox.delete(0, tk.END)
        for i, track in enumerate(self.play_queue):
            self.queue_listbox.insert(tk.END, f"{i+1}. {Path(track).name}")
            
        count = len(self.play_queue)
        self.queue_info.config(text=f"{count}개 대기 중")
        
    # 파일 관리 메서드
    def add_files(self):
        """파일 추가"""
        try:
            files = filedialog.askopenfilenames(
                title="파일 선택",
                filetypes=[
                    ("미디어 파일", "*.mp4;*.mov;*.m4v;*.avi;*.mp3;*.m4a;*.aac;*.wav;*.flac"),
                    ("비디오", "*.mp4;*.mov;*.m4v;*.avi"),
                    ("오디오", "*.mp3;*.m4a;*.aac;*.wav;*.flac"),
                    ("모든 파일", "*.*")
                ]
            )
            
            if files:
                for file in files:
                    self.playlist.append(file)
                    self.library_listbox.insert(tk.END, Path(file).name)
                    print(f"파일 추가됨: {file}")
                
                print(f"총 추가된 파일 개수: {len(files)}")
                print(f"현재 플레이리스트 크기: {len(self.playlist)}")
                messagebox.showinfo("파일 추가", f"{len(files)}개 파일이 추가되었습니다.")
            else:
                print("파일이 선택되지 않았습니다.")
                
        except Exception as e:
            print(f"파일 추가 오류: {e}")
            messagebox.showerror("오류", f"파일 추가 중 오류 발생: {e}")
            
    def add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
            
        extensions = ['.mp4', '.mov', '.m4v', '.avi', '.mp3', '.m4a', '.aac', '.wav', '.flac']
        folder_path = Path(folder)
        
        count = 0
        for ext in extensions:
            for file in folder_path.glob(f'*{ext}'):
                self.playlist.append(str(file))
                self.library_listbox.insert(tk.END, file.name)
                count += 1
                
        messagebox.showinfo("폴더 추가", f"{count}개 파일이 추가되었습니다.")
        
    def add_to_queue_from_library(self, event):
        """라이브러리에서 큐에 추가"""
        selection = self.library_listbox.curselection()
        if not selection:
            # 클릭한 위치의 아이템 선택
            index = self.library_listbox.nearest(event.y)
            self.library_listbox.selection_set(index)
            selection = (index,)
            
        for index in selection:
            if index < len(self.playlist):
                self.play_queue.append(self.playlist[index])
                print(f"큐에 추가됨: {self.playlist[index]}")
        
        self.update_queue_display()
        
        # 재생 중이 아니면 자동 시작
        if not self.is_playing and self.play_queue:
            self.toggle_playback()
            
    def play_from_queue(self, event):
        """큐에서 즉시 재생"""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            # 해당 인덱스까지의 트랙을 건너뛰기
            self.play_queue = self.play_queue[index:]
            self.command_queue.put('next')
            
    # 플레이리스트 관리
    def new_playlist(self):
        """새 플레이리스트"""
        self.playlist.clear()
        self.play_queue.clear()
        self.library_listbox.delete(0, tk.END)
        self.queue_listbox.delete(0, tk.END)
        self.current_index = 0
        messagebox.showinfo("새 플레이리스트", "새 플레이리스트가 생성되었습니다.")
        
    def open_playlist(self):
        """플레이리스트 열기"""
        filename = filedialog.askopenfilename(
            title="플레이리스트 열기",
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.playlist = data.get('playlist', [])
                self.library_listbox.delete(0, tk.END)
                
                for filepath in self.playlist:
                    self.library_listbox.insert(tk.END, Path(filepath).name)
                    
                messagebox.showinfo("열기 완료", "플레이리스트를 불러왔습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"플레이리스트 열기 실패: {e}")
                
    def save_playlist(self):
        """플레이리스트 저장"""
        filename = filedialog.asksaveasfilename(
            title="플레이리스트 저장",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'playlist': self.playlist,
                    'created_at': datetime.now().isoformat(),
                    'version': self.version
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                messagebox.showinfo("저장 완료", "플레이리스트가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"플레이리스트 저장 실패: {e}")
                
    # 설정 및 기타 기능
    def toggle_shuffle(self):
        """셔플 토글"""
        if self.shuffle_enabled.get():
            self.shuffle_btn.config(relief=tk.SUNKEN)
        else:
            self.shuffle_btn.config(relief=tk.RAISED)
            
    def toggle_repeat(self):
        """반복 토글"""
        if self.repeat_enabled.get():
            self.repeat_btn.config(relief=tk.SUNKEN)
        else:
            self.repeat_btn.config(relief=tk.RAISED)
            
    def change_volume(self, value):
        """볼륨 변경"""
        volume = int(float(value))
        # macOS 시스템 볼륨 조절 (AppleScript)
        subprocess.run([
            'osascript', '-e',
            f'set volume output volume {volume}'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def change_mode(self):
        """모드 변경"""
        mode = self.mode_var.get()
        self.current_mode = mode
        
        if mode == "cafe":
            messagebox.showinfo("카페 모드", 
                              "카페 모드가 활성화되었습니다.\n"
                              "24시간 연속 재생이 가능합니다.")
        elif mode == "party":
            messagebox.showinfo("파티 모드", 
                              "파티 모드가 활성화되었습니다.\n"
                              "자동 셔플과 비주얼 효과가 강화됩니다.")
            self.shuffle_enabled.set(True)
            self.toggle_shuffle()
            
    def clear_queue(self):
        """큐 비우기"""
        self.play_queue.clear()
        self.update_queue_display()
        
    def save_queue(self):
        """큐 저장"""
        filename = filedialog.asksaveasfilename(
            title="큐 저장",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.play_queue, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("저장 완료", "큐가 저장되었습니다.")
            
    def select_all(self):
        """모두 선택"""
        self.library_listbox.select_set(0, tk.END)
        
    def remove_selected(self):
        """선택 제거"""
        selected = list(self.library_listbox.curselection())
        for index in reversed(selected):
            if index < len(self.playlist):
                del self.playlist[index]
                self.library_listbox.delete(index)
                
    # 오디오 변환 기능
    def select_audio_files(self):
        """변환할 오디오 파일 선택"""
        files = filedialog.askopenfilenames(
            title="오디오 파일 선택",
            filetypes=[
                ("오디오", "*.mp3;*.m4a;*.aac;*.wav;*.flac"),
                ("모든 파일", "*.*")
            ]
        )
        
        self.files_to_convert = list(files)
        self.convert_listbox.delete(0, tk.END)
        for file in files:
            self.convert_listbox.insert(tk.END, Path(file).name)
            
    def start_conversion(self):
        """변환 시작"""
        if not self.files_to_convert:
            messagebox.showwarning("파일 없음", "변환할 파일을 선택하세요.")
            return
            
        # 변환 스레드 시작
        threading.Thread(target=self.convert_files, daemon=True).start()
        
    def convert_files(self):
        """파일 변환 (스레드)"""
        self.conversion_progress.start()
        
        converted = 0
        failed = 0
        
        # 상태 레이블 추가
        self.root.after(0, self.convert_listbox.delete, 0, tk.END)
        
        for i, audio_file in enumerate(self.files_to_convert):
            try:
                # 진행 상태 업데이트
                self.root.after(0, self.convert_listbox.insert, tk.END, 
                              f"변환 중... ({i+1}/{len(self.files_to_convert)}) {Path(audio_file).name}")
                
                if AudioToVideoConverter:
                    converter = AudioToVideoConverter()
                    output = converter.convert_to_video(audio_file)
                    if output:
                        converted += 1
                        self.root.after(0, self.convert_listbox.delete, tk.END)
                        self.root.after(0, self.convert_listbox.insert, tk.END, 
                                      f"✓ 완료: {Path(audio_file).name}")
                    else:
                        failed += 1
                        self.root.after(0, self.convert_listbox.insert, tk.END, 
                                      f"✗ 실패: {Path(audio_file).name}")
                else:
                    # 간단한 변환
                    output = self.convert_audio_file(audio_file)
                    if output:
                        converted += 1
                        self.root.after(0, self.convert_listbox.delete, tk.END)
                        self.root.after(0, self.convert_listbox.insert, tk.END, 
                                      f"✓ 완료: {Path(audio_file).name}")
                    else:
                        failed += 1
                        self.root.after(0, self.convert_listbox.insert, tk.END, 
                                      f"✗ 실패: {Path(audio_file).name}")
            except Exception as e:
                print(f"변환 오류: {e}")
                failed += 1
                self.root.after(0, self.convert_listbox.insert, tk.END, 
                              f"✗ 오류: {Path(audio_file).name} - {str(e)}")
                
        self.conversion_progress.stop()
        
        # 결과 표시
        self.root.after(0, messagebox.showinfo, "변환 완료", 
                       f"변환 완료: {converted}개 성공, {failed}개 실패")
        
    # 기타 UI 메서드
    def show_settings(self):
        """설정 창"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("500x400")
        
        ttk.Label(settings_window, text="설정", 
                 style='Title.TLabel').pack(pady=20)
        
        # AirPlay 설정
        airplay_frame = ttk.LabelFrame(settings_window, text="AirPlay 설정", padding=20)
        airplay_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(airplay_frame, text="기기 이름:").pack(anchor=tk.W)
        device_entry = ttk.Entry(airplay_frame)
        device_entry.insert(0, self.settings.get('airplay_device', 'Living'))
        device_entry.pack(fill=tk.X, pady=5)
        
        # 저장 버튼
        def save_settings():
            self.settings['airplay_device'] = device_entry.get()
            self.save_settings()
            messagebox.showinfo("저장 완료", "설정이 저장되었습니다.")
            settings_window.destroy()
            
        ttk.Button(settings_window, text="저장", 
                  command=save_settings).pack(pady=20)
        
    def show_about(self):
        """정보 창"""
        about_window = tk.Toplevel(self.root)
        about_window.title("QuickTime Playlist Pro 정보")
        about_window.geometry("400x300")
        
        ttk.Label(about_window, text="♫", font=('Arial', 48)).pack(pady=20)
        ttk.Label(about_window, text="QuickTime Playlist Pro",
                 style='Title.TLabel').pack()
        ttk.Label(about_window, text=f"버전 {self.version}",
                 font=('SF Pro', 12)).pack(pady=5)
        
        ttk.Label(about_window, text="HomePod 사용자를 위한 혁명적인 플레이리스트 솔루션",
                 font=('SF Pro', 11), wraplength=350).pack(pady=10)
        
        ttk.Label(about_window, text='"애플의 썩어빠진 CoreAudio 비공개를 고발하는 앱"',
                 font=('SF Pro', 10, 'italic'),
                 foreground='gray').pack(pady=10)
        
        ttk.Button(about_window, text="확인",
                  command=about_window.destroy).pack(pady=20)
        
    def show_guide(self):
        """사용 가이드"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("사용 가이드")
        guide_window.geometry("600x400")
        
        # 스크롤 가능한 텍스트
        text_frame = ttk.Frame(guide_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        guide_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=guide_text.yview)
        
        guide_content = """QuickTime Playlist Pro 사용 가이드

1. 시작하기
   - 파일 추가: 라이브러리 탭에서 '파일 추가' 또는 '폴더 추가' 클릭
   - 재생: 파일을 더블클릭하여 큐에 추가 후 재생 버튼 클릭

2. AirPlay 설정
   - 자동으로 'Living' 기기에 연결됩니다
   - 다른 기기로 변경하려면 사이드바의 '변경' 버튼 클릭

3. 오디오 변환
   - '비디오 변환' 탭에서 오디오 파일 선택
   - 앨범 아트와 메타데이터가 포함된 비디오로 변환

4. 모드
   - 일반 모드: 기본 재생 모드
   - 카페 모드: 24시간 연속 재생
   - 파티 모드: 자동 셔플과 향상된 비주얼

5. 단축키
   - Space: 재생/일시정지
   - →: 다음 트랙
   - ←: 이전 트랙

문제가 있으신가요?
HomePod 커뮤니티를 방문해보세요!
"""
        
        guide_text.insert('1.0', guide_content)
        guide_text.config(state='disabled')
        
    def open_community(self):
        """커뮤니티 열기"""
        webbrowser.open("https://reddit.com/r/HomePod")
        
    def batch_convert(self):
        """일괄 변환"""
        self.notebook.select(self.converter_tab)
        messagebox.showinfo("일괄 변환", 
                          "비디오 변환 탭에서 여러 파일을 선택하여 일괄 변환할 수 있습니다.")
        
    def scan_airplay(self):
        """AirPlay 기기 검색"""
        messagebox.showinfo("AirPlay 검색", 
                          "시스템 환경설정 > 디스플레이에서 AirPlay 기기를 확인하세요.\n"
                          "QuickTime은 프로그래밍 방식의 기기 검색을 지원하지 않습니다.")
        
    def edit_metadata(self):
        """메타데이터 편집기"""
        messagebox.showinfo("메타데이터 편집", 
                          "향후 업데이트에서 지원될 예정입니다.\n"
                          "현재는 자동으로 메타데이터를 추출합니다.")
        
    def show_all_music(self):
        """모든 음악 표시"""
        self.notebook.select(self.library_tab)
        
    def show_videos(self):
        """비디오만 표시"""
        self.notebook.select(self.library_tab)
        # 필터링 기능은 향후 구현
        
    def show_queue(self):
        """큐 표시"""
        self.notebook.select(self.queue_tab)
        
    def show_favorites(self):
        """즐겨찾기 표시"""
        messagebox.showinfo("즐겨찾기", "향후 업데이트에서 지원될 예정입니다.")
        
    def create_playlist(self):
        """새 플레이리스트 생성"""
        # 간단한 입력 대화상자 구현
        dialog = tk.Toplevel(self.root)
        dialog.title("새 플레이리스트")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="플레이리스트 이름:").pack(pady=10)
        
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def create():
            name = name_entry.get()
            if name:
                self.playlist_listbox.insert(tk.END, name)
                messagebox.showinfo("생성 완료", f"'{name}' 플레이리스트가 생성되었습니다.")
            dialog.destroy()
            
        def on_enter(event):
            create()
            
        name_entry.bind('<Return>', on_enter)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="생성", command=create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
    def change_airplay(self):
        """AirPlay 기기 변경"""
        messagebox.showinfo("AirPlay 변경", 
                          "설정에서 기기 이름을 변경하거나\n"
                          "수동으로 QuickTime에서 AirPlay 기기를 선택하세요.")
        
    def on_closing(self):
        """종료 시"""
        self.save_settings()
        
        # 재생 중지
        if self.is_playing:
            subprocess.run([
                'osascript', '-e',
                'tell application "QuickTime Player" to close every document'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        self.root.destroy()
        
    def quit_app(self):
        """앱 종료"""
        self.on_closing()

def main():
    # 스플래시 스크린
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("400x200+500+300")
    splash.configure(bg='#1e1e1e')
    
    tk.Label(splash, text="♫", font=('Arial', 60), 
            bg='#1e1e1e', fg='white').pack(pady=20)
    tk.Label(splash, text="QuickTime Playlist Pro", 
            font=('SF Pro Display', 20, 'bold'),
            bg='#1e1e1e', fg='white').pack()
    tk.Label(splash, text="Loading...", font=('SF Pro', 12),
            bg='#1e1e1e', fg='gray').pack(pady=10)
    
    splash.update()
    
    # 메인 앱 준비
    root = tk.Tk()
    root.withdraw()  # 숨기기
    
    # 함수로 처리
    def show_main():
        splash.destroy()
        root.deiconify()
    
    # 2초 후 메인 앱 표시
    splash.after(2000, show_main)
    
    app = QuickTimePlaylistPro(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()