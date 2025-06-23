#!/usr/bin/env python3
"""
카페 Living 플레이리스트 - 수정 버전
제대로 닫고, 열고, 재생하는 버전
"""

import os
import sys
import time
import random
import subprocess
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class CafeLivingPlaylistFixed:
    def __init__(self):
        self.playlist_folder = Path.cwd()
        self.airplay_enabled = False
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
        
    def close_all_documents(self):
        """모든 QuickTime 문서 닫기"""
        script = '''
        tell application "QuickTime Player"
            close every document
        end tell
        '''
        subprocess.run(['osascript', '-e', script], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        
    def play_video(self, video_path, first_video=False):
        """비디오 재생"""
        self.current_video = os.path.basename(video_path)
        logging.info(f"재생: {self.current_video}")
        
        # 1. 기존 문서 닫기
        self.close_all_documents()
        
        # 2. 새 비디오 열기
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(3)  # 로딩 대기
        
        # 3. 재생 시작
        play_script = '''
        tell application "QuickTime Player"
            activate
            if (count documents) > 0 then
                tell front document
                    play
                end tell
            end if
        end tell
        '''
        subprocess.run(['osascript', '-e', play_script], 
                      capture_output=True, stderr=subprocess.DEVNULL)
        
        # 4. 전체화면 설정 (별도로)
        time.sleep(1)
        fullscreen_script = '''
        tell application "QuickTime Player"
            if (count documents) > 0 then
                tell front document
                    set presentation mode to true
                end tell
            end if
        end tell
        '''
        subprocess.run(['osascript', '-e', fullscreen_script], 
                      capture_output=True, stderr=subprocess.DEVNULL)
        
        self.play_count += 1
        
        # 첫 비디오에서 AirPlay 설정
        if first_video:
            time.sleep(2)
            self.enable_airplay_living()
            
        return True
        
    def enable_airplay_living(self):
        """Living AirPlay 설정"""
        if self.airplay_enabled:
            return
            
        logging.info("Living AirPlay 설정 중...")
        
        # cliclick 사용
        subprocess.run(['cliclick', 'm:640,700'])
        time.sleep(1)
        subprocess.run(['cliclick', 'c:970,784'])  # AirPlay 버튼
        time.sleep(1)
        subprocess.run(['cliclick', 'c:842,710'])  # Living 선택
        
        self.airplay_enabled = True
        logging.info("AirPlay 설정 완료")
        
    def is_playing(self):
        """재생 중인지 확인"""
        script = '''
        tell application "QuickTime Player"
            if (count documents) > 0 then
                if playing of front document then
                    return "yes"
                else
                    return "no"
                end if
            else
                return "no_document"
            end if
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        return result.stdout.strip() == "yes"
        
    def wait_for_video_end(self):
        """비디오 종료 대기"""
        # 초기 대기 (비디오 시작)
        time.sleep(5)
        
        # 재생 중인 동안 대기
        while self.is_playing():
            time.sleep(3)
            
        logging.info("재생 완료")
        time.sleep(1)
        
    def run(self):
        """메인 실행 루프"""
        videos = self.get_playlist()
        if not videos:
            logging.error("비디오 파일이 없습니다")
            return
            
        logging.info("카페 Living 플레이리스트 시작")
        
        try:
            while True:  # 무한 반복
                for i, video in enumerate(videos):
                    # 비디오 재생
                    if self.play_video(video, first_video=(i == 0 and self.play_count == 0)):
                        # 재생 완료 대기
                        self.wait_for_video_end()
                    else:
                        # 재생 실패 시 5초 대기
                        time.sleep(5)
                        
                logging.info(f"플레이리스트 완료. 총 {self.play_count}개 재생")
                
                # 다시 섞기
                if len(videos) > 1:
                    random.shuffle(videos)
                    
        except KeyboardInterrupt:
            logging.info("종료 요청")
        finally:
            # QuickTime 종료
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])
            logging.info(f"총 재생 횟수: {self.play_count}")

def main():
    # cliclick 확인
    try:
        subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
    except:
        print("cliclick 필요: brew install cliclick")
        return
        
    # 실행
    player = CafeLivingPlaylistFixed()
    player.run()

if __name__ == "__main__":
    main()