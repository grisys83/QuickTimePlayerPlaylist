#!/usr/bin/env python3
"""
카페 Living 플레이리스트 - 최종 버전
"""

import os
import sys
import time
import random
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class CafeLivingPlaylist:
    def __init__(self):
        self.playlist_folder = Path.cwd()
        self.play_count = 0
        
    def get_playlist(self, shuffle=True):
        """비디오 파일 목록"""
        extensions = ['.mp4', '.mov', '.m4v', '.avi']
        videos = []
        
        for ext in extensions:
            videos.extend(self.playlist_folder.glob(f'*{ext}'))
            
        videos = [str(v.absolute()) for v in videos]
        
        if shuffle:
            random.shuffle(videos)
            
        logging.info(f"플레이리스트: {len(videos)}개 비디오")
        return videos
        
    def play_video(self, video_path, first_video=False):
        """비디오 재생"""
        filename = os.path.basename(video_path)
        logging.info(f"재생: {filename}")
        
        # 1. 기존 문서 닫기
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to close every document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # 2. 새 비디오 열기
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(2)  # 빠르게 진행
        
        # 3. 즉시 AirPlay 설정 (속도 우선)
        self.enable_airplay()
        
        # 4. AppleScript로 재생 시작
        time.sleep(1)
        subprocess.run([
            'osascript', '-e',
            'tell application "QuickTime Player" to play front document'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 5. 전체화면 (선택사항)
        # time.sleep(1)
        # subprocess.run([
        #     'osascript', '-e',
        #     'tell application "QuickTime Player" to set presentation mode of front document to true'
        # ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Play 버튼 좌표 저장 (나중에 필요할 경우를 위해)
        # play_button = (712, 712)
        
        self.play_count += 1
            
        return True
        
    def enable_airplay(self):
        """Living AirPlay 설정 - 매번 실행"""
        try:
            logging.info("Living AirPlay 설정 중...")
            # 컨트롤 표시
            subprocess.run(['cliclick', 'm:640,700'])
            time.sleep(0.5)
            
            # AirPlay 버튼 클릭 (새 좌표)
            subprocess.run(['cliclick', 'c:844,714'])
            time.sleep(0.5)
            
            # Living 선택 (새 좌표)
            subprocess.run(['cliclick', 'c:970,784'])
            logging.info("AirPlay 설정 완료")
        except:
            logging.warning("AirPlay 설정 실패")
            
    def is_playing(self):
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
        
    def run(self):
        """메인 실행"""
        videos = self.get_playlist()
        if not videos:
            logging.error("비디오 파일이 없습니다")
            return
            
        logging.info("시작")
        
        try:
            while True:
                for i, video in enumerate(videos):
                    # 재생
                    self.play_video(video, first_video=(i == 0))
                    
                    # 재생 시작 대기
                    time.sleep(5)
                    
                    # 재생 완료 대기
                    while self.is_playing():
                        time.sleep(3)
                        
                    time.sleep(2)
                    
                logging.info(f"플레이리스트 1회 완료 ({self.play_count}개)")
                random.shuffle(videos)
                
        except KeyboardInterrupt:
            logging.info("종료")
        finally:
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])

def main():
    if not subprocess.run(['which', 'cliclick'], capture_output=True).returncode == 0:
        print("cliclick 필요: brew install cliclick")
        return
        
    CafeLivingPlaylist().run()

if __name__ == "__main__":
    main()