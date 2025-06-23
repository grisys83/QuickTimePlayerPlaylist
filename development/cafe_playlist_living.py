#!/usr/bin/env python3
"""
카페 플레이리스트 - Living AirPlay 전용 버전
하루 종일 안정적으로 Living으로 재생
"""

import os
import sys
import time
import json
import random
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('cafe_living_playlist.log'),
        logging.StreamHandler()
    ]
)

class CafeLivingPlaylist:
    def __init__(self, playlist_folder=None):
        # 기본값: 스크립트와 같은 폴더
        if playlist_folder is None:
            self.playlist_folder = Path(__file__).parent
        else:
            self.playlist_folder = Path(playlist_folder)
        self.airplay_enabled = False
        self.current_video = None
        self.play_count = 0
        
    def get_playlist(self, shuffle=True):
        """비디오 파일 목록 가져오기"""
        video_extensions = ['.mp4', '.mov', '.m4v', '.avi']
        videos = []
        
        for ext in video_extensions:
            videos.extend(self.playlist_folder.glob(f'*{ext}'))
            
        videos = [str(v.absolute()) for v in videos]
        
        if shuffle:
            random.shuffle(videos)
            
        logging.info(f"플레이리스트: {len(videos)}개 비디오")
        return videos
        
    def enable_airplay_living(self):
        """Living으로 AirPlay 설정"""
        if self.airplay_enabled:
            return True
            
        script = '''
        -- 컨트롤바 표시
        do shell script "cliclick m:640,700"
        delay 1
        
        -- AirPlay 버튼 클릭
        do shell script "cliclick c:970,784"
        delay 1
        
        -- Living 선택
        do shell script "cliclick c:842,710"
        delay 0.5
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            self.airplay_enabled = True
            logging.info("Living AirPlay 활성화 완료")
            return True
        except Exception as e:
            logging.error(f"AirPlay 활성화 실패: {e}")
            return False
            
    def play_video(self, video_path, first_video=False):
        """비디오 재생"""
        self.current_video = os.path.basename(video_path)
        logging.info(f"재생: {self.current_video}")
        
        # 방법 1: open 명령 사용
        try:
            # QuickTime Player로 직접 열기
            subprocess.run(['open', '-a', 'QuickTime Player', video_path], check=True)
            time.sleep(2)
            
            # 재생 및 설정 (에러 무시)
            script = '''
            tell application "QuickTime Player"
                if (count documents) > 0 then
                    tell document 1
                        play
                        set presentation mode to true
                        set audio volume to 0.7
                    end tell
                end if
            end tell
            '''
            
            # check=False로 에러 무시
            subprocess.run(['osascript', '-e', script], check=False)
            self.play_count += 1
            
            # 첫 번째 비디오에서만 AirPlay 설정
            if first_video:
                time.sleep(2)
                self.enable_airplay_living()
                
            return True
            
        except Exception as e:
            logging.warning(f"AppleScript 경고 (무시 가능): {e}")
            return True  # 실제로는 재생되고 있으므로 True 반환
            
    def wait_for_video_end(self):
        """비디오 종료 대기"""
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
        
        while True:
            try:
                result = subprocess.run(['osascript', '-e', check_script], 
                                      capture_output=True, text=True)
                if result.stdout.strip() != "playing":
                    return True
            except:
                return True
                
            time.sleep(2)
            
    def run(self):
        """메인 실행 루프"""
        logging.info("카페 Living 플레이리스트 시작")
        
        # 비디오 파일 확인
        test_playlist = self.get_playlist(shuffle=False)
        if not test_playlist:
            logging.error(f"{self.playlist_folder} 폴더에 비디오 파일이 없습니다")
            logging.error("지원 형식: .mp4, .mov, .m4v, .avi")
            return
            
        try:
            while True:
                playlist = self.get_playlist()
                if not playlist:
                    logging.error("재생할 비디오가 없습니다")
                    time.sleep(60)
                    continue
                    
                # 플레이리스트 재생
                for i, video in enumerate(playlist):
                    success = self.play_video(video, first_video=(i == 0))
                    
                    if success:
                        self.wait_for_video_end()
                        time.sleep(2)  # 비디오 간 짧은 대기
                    else:
                        time.sleep(5)  # 에러 시 대기
                        
                logging.info(f"플레이리스트 완료. 총 {self.play_count}개 재생")
                
        except KeyboardInterrupt:
            logging.info("종료 요청")
        finally:
            # QuickTime 종료
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])
            logging.info(f"총 재생 횟수: {self.play_count}")

def main():
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("카페 Living 플레이리스트")
            print("사용법:")
            print("  python3 cafe_playlist_living.py          # 현재 폴더의 비디오 재생")
            print("  python3 cafe_playlist_living.py [폴더]   # 특정 폴더의 비디오 재생")
            return
        playlist_folder = sys.argv[1]
    else:
        playlist_folder = None  # 기본값: 스크립트와 같은 폴더
        
    # cliclick 확인
    try:
        subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
    except:
        print("cliclick 필요: brew install cliclick")
        return
        
    # 실행
    player = CafeLivingPlaylist(playlist_folder)
    player.run()

if __name__ == "__main__":
    main()