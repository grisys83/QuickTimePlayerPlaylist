#!/usr/bin/env python3
"""
카페 플레이리스트 매니저
하루 종일 안정적으로 재생되는 비디오 플레이리스트 시스템
"""

import os
import sys
import time
import json
import random
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cafe_playlist.log'),
        logging.StreamHandler()
    ]
)

class CafePlaylistManager:
    def __init__(self, config_file='cafe_playlist_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.current_video = None
        self.play_count = 0
        self.errors = []
        self.is_running = False
        self.airplay_enabled = False
        
    def load_config(self):
        """설정 파일 로드 또는 기본값 생성"""
        default_config = {
            "playlist_folder": ".",  # 현재 폴더
            "shuffle": True,
            "repeat": True,
            "volume": 50,
            "airplay_device_index": 1,
            "business_hours": {
                "enabled": True,
                "start": "09:00",
                "end": "22:00"
            },
            "error_retry": 3,
            "pause_between_videos": 2,
            "fullscreen": True,
            "auto_restart_on_error": True,
            "max_errors_before_restart": 5
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        else:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
                
        return default_config
        
    def get_playlist(self):
        """플레이리스트 폴더에서 비디오 파일 목록 가져오기"""
        video_extensions = ['.mp4', '.mov', '.m4v', '.avi']
        playlist_folder = Path(self.config['playlist_folder'])
        
        if not playlist_folder.exists():
            logging.error(f"플레이리스트 폴더가 없습니다: {playlist_folder}")
            return []
            
        videos = []
        for ext in video_extensions:
            videos.extend(playlist_folder.glob(f'*{ext}'))
            
        videos = [str(v.absolute()) for v in videos]
        
        if self.config['shuffle']:
            random.shuffle(videos)
            
        logging.info(f"플레이리스트 로드: {len(videos)}개 비디오")
        return videos
        
    def check_business_hours(self):
        """영업 시간 확인"""
        if not self.config['business_hours']['enabled']:
            return True
            
        current_time = datetime.now().time()
        start_time = datetime.strptime(self.config['business_hours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self.config['business_hours']['end'], '%H:%M').time()
        
        return start_time <= current_time <= end_time
        
    def set_volume(self):
        """볼륨 설정"""
        volume = self.config['volume']
        script = f'''
        tell application "QuickTime Player"
            if (count documents) > 0 then
                set audio volume of document 1 to {volume / 100}
            end if
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        
    def enable_airplay_fullscreen(self):
        """전체화면 모드에서 AirPlay 활성화"""
        if self.airplay_enabled:
            return True
            
        script = f'''
        tell application "System Events"
            tell process "QuickTime Player"
                set frontmost to true
                
                -- 컨트롤 표시
                do shell script "cliclick m:640,719"
                delay 1
                
                -- AirPlay 버튼 클릭 (전체화면 고정 위치)
                do shell script "cliclick c:1180,680"
                delay 1
                
                -- 기기 선택
                repeat {self.config['airplay_device_index']} times
                    key code 125
                    delay 0.2
                end repeat
                key code 36
            end tell
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            self.airplay_enabled = True
            logging.info("AirPlay 활성화 성공")
            return True
        except:
            logging.warning("AirPlay 활성화 실패")
            return False
            
    def play_video(self, video_path):
        """비디오 재생"""
        self.current_video = video_path
        logging.info(f"재생 시작: {os.path.basename(video_path)}")
        
        script = f'''
        tell application "QuickTime Player"
            activate
            
            -- 기존 문서 닫기
            if (count documents) > 0 then
                close every document
            end if
            
            delay 0.5
            
            -- 새 비디오 열기
            open POSIX file "{video_path}"
            delay 2
            
            tell document 1
                play
                
                -- 전체화면 설정
                if {str(self.config['fullscreen']).lower()} then
                    set presentation mode to true
                end if
            end tell
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            time.sleep(2)
            
            # 볼륨 설정
            self.set_volume()
            
            # 첫 비디오에서 AirPlay 설정
            if self.play_count == 0 and self.config['fullscreen']:
                time.sleep(1)
                self.enable_airplay_fullscreen()
                
            self.play_count += 1
            return True
            
        except Exception as e:
            logging.error(f"재생 실패: {e}")
            self.errors.append((datetime.now(), video_path, str(e)))
            return False
            
    def wait_for_video_end(self):
        """비디오 재생 완료 대기"""
        check_script = '''
        tell application "QuickTime Player"
            if (count documents) > 0 then
                if playing of document 1 then
                    return "playing"
                else
                    return "stopped"
                end if
            else
                return "no_document"
            end if
        end tell
        '''
        
        while self.is_running:
            try:
                result = subprocess.run(['osascript', '-e', check_script], 
                                      capture_output=True, text=True)
                status = result.stdout.strip()
                
                if status != "playing":
                    return True
                    
            except:
                return True
                
            time.sleep(2)
            
        return False
        
    def handle_errors(self):
        """에러 처리 및 자동 복구"""
        recent_errors = [e for e in self.errors if e[0] > datetime.now() - timedelta(minutes=10)]
        
        if len(recent_errors) >= self.config['max_errors_before_restart']:
            logging.warning("최대 에러 수 도달. QuickTime 재시작...")
            
            # QuickTime 재시작
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])
            time.sleep(2)
            
            # 에러 기록 초기화
            self.errors = []
            self.airplay_enabled = False
            
            return True
            
        return False
        
    def run_playlist(self):
        """플레이리스트 실행"""
        self.is_running = True
        
        while self.is_running:
            # 영업 시간 확인
            if not self.check_business_hours():
                logging.info("영업 시간이 아닙니다. 대기 중...")
                time.sleep(300)  # 5분 대기
                continue
                
            # 플레이리스트 가져오기
            playlist = self.get_playlist()
            if not playlist:
                logging.error("재생할 비디오가 없습니다.")
                time.sleep(60)
                continue
                
            # 각 비디오 재생
            for video in playlist:
                if not self.is_running:
                    break
                    
                # 비디오 재생
                retry_count = 0
                while retry_count < self.config['error_retry']:
                    if self.play_video(video):
                        break
                    retry_count += 1
                    time.sleep(2)
                    
                if retry_count >= self.config['error_retry']:
                    continue
                    
                # 재생 완료 대기
                self.wait_for_video_end()
                
                # 비디오 간 일시 정지
                time.sleep(self.config['pause_between_videos'])
                
                # 에러 체크 및 복구
                if self.config['auto_restart_on_error']:
                    self.handle_errors()
                    
            # 반복 재생
            if not self.config['repeat']:
                break
                
        logging.info("플레이리스트 종료")
        
    def start(self):
        """플레이리스트 매니저 시작"""
        logging.info("카페 플레이리스트 매니저 시작")
        
        # 플레이리스트 실행 스레드
        playlist_thread = threading.Thread(target=self.run_playlist)
        playlist_thread.start()
        
        # 상태 모니터링
        try:
            while self.is_running:
                # 상태 출력
                if self.current_video:
                    print(f"\r재생 중: {os.path.basename(self.current_video)} | "
                          f"재생 횟수: {self.play_count} | "
                          f"에러: {len(self.errors)}", end='')
                          
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("종료 요청 받음")
            self.stop()
            
    def stop(self):
        """플레이리스트 매니저 중지"""
        self.is_running = False
        
        # QuickTime 종료
        subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])
        
        # 통계 출력
        logging.info(f"\n총 재생 횟수: {self.play_count}")
        logging.info(f"총 에러 횟수: {len(self.errors)}")
        
        # 에러 로그 저장
        if self.errors:
            with open('cafe_playlist_errors.log', 'a') as f:
                for error in self.errors:
                    f.write(f"{error[0]} - {error[1]} - {error[2]}\n")

def create_sample_config():
    """샘플 설정 파일 생성"""
    sample_config = {
        "playlist_folder": ".",  # 현재 폴더
        "shuffle": True,
        "repeat": True,
        "volume": 70,
        "airplay_device_index": 1,
        "business_hours": {
            "enabled": True,
            "start": "09:00",
            "end": "22:00"
        },
        "error_retry": 3,
        "pause_between_videos": 3,
        "fullscreen": True,
        "auto_restart_on_error": True,
        "max_errors_before_restart": 5
    }
    
    with open('cafe_playlist_config.json', 'w') as f:
        json.dump(sample_config, f, indent=4)
        
    print("설정 파일 생성: cafe_playlist_config.json")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-config':
            create_sample_config()
            return
        elif sys.argv[1] == '--help':
            print("카페 플레이리스트 매니저")
            print("사용법:")
            print("  python cafe_playlist_manager.py           # 실행")
            print("  python cafe_playlist_manager.py --create-config  # 설정 파일 생성")
            print("  python cafe_playlist_manager.py --help    # 도움말")
            return
            
    # cliclick 확인
    try:
        subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
    except:
        print("cliclick 설치 필요: brew install cliclick")
        return
        
    # 플레이리스트 매니저 실행
    manager = CafePlaylistManager()
    manager.start()

if __name__ == "__main__":
    main()