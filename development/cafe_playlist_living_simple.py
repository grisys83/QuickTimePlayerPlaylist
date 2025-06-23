#!/usr/bin/env python3
"""
카페 Living 플레이리스트 - 심플 버전
한글 macOS 호환성 개선
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

class SimpleLivingPlaylist:
    def __init__(self):
        self.playlist_folder = Path.cwd()
        self.airplay_enabled = False
        self.current_index = 0
        
    def get_playlist(self, shuffle=True):
        """비디오 파일 목록"""
        extensions = ['.mp4', '.mov', '.m4v', '.avi']
        videos = []
        
        for ext in extensions:
            videos.extend(self.playlist_folder.glob(f'*{ext}'))
            
        videos = [str(v.absolute()) for v in videos]
        
        if shuffle:
            random.shuffle(videos)
            
        logging.info(f"비디오 {len(videos)}개 발견")
        return videos
        
    def play_video_simple(self, video_path):
        """심플하게 비디오 재생"""
        logging.info(f"재생: {os.path.basename(video_path)}")
        
        # 방법 1: open 명령만 사용
        subprocess.run(['open', '-a', 'QuickTime Player', video_path])
        time.sleep(3)
        
        # 방법 2: 파일로 AppleScript 실행
        script_content = '''
tell application "QuickTime Player"
    if (count documents) > 0 then
        tell front document
            play
            set presentation mode to true
        end tell
    end if
end tell
'''
        
        # 임시 스크립트 파일 생성
        script_file = Path("/tmp/qt_play.scpt")
        script_file.write_text(script_content)
        
        # 스크립트 실행
        subprocess.run(['osascript', str(script_file)])
        script_file.unlink()  # 삭제
        
        return True
        
    def enable_airplay_living(self):
        """Living AirPlay 설정"""
        if self.airplay_enabled:
            return
            
        time.sleep(2)
        
        # cliclick 명령들을 개별적으로 실행
        subprocess.run(['cliclick', 'm:640,700'])
        time.sleep(1)
        subprocess.run(['cliclick', 'c:970,784'])
        time.sleep(1)
        subprocess.run(['cliclick', 'c:842,710'])
        
        self.airplay_enabled = True
        logging.info("Living AirPlay 설정")
        
    def check_playing(self):
        """재생 상태 확인"""
        script = '''
tell application "QuickTime Player"
    if (count documents) > 0 then
        if playing of front document then
            return "playing"
        else
            return "stopped"
        end if
    else
        return "no_document"
    end if
end tell
'''
        
        # 파일로 실행
        script_file = Path("/tmp/qt_check.scpt")
        script_file.write_text(script)
        
        result = subprocess.run(['osascript', str(script_file)], 
                              capture_output=True, text=True)
        script_file.unlink()
        
        return result.stdout.strip()
        
    def run(self):
        """메인 실행"""
        videos = self.get_playlist()
        if not videos:
            logging.error("비디오 파일이 없습니다")
            return
            
        try:
            while True:
                for i, video in enumerate(videos):
                    # 재생
                    if self.play_video_simple(video):
                        # 첫 비디오에서 AirPlay 설정
                        if i == 0 and self.current_index == 0:
                            self.enable_airplay_living()
                            
                        # 재생 완료 대기
                        while self.check_playing() == "playing":
                            time.sleep(3)
                            
                        time.sleep(2)
                        
                self.current_index += 1
                logging.info(f"플레이리스트 {self.current_index}회 완료")
                
        except KeyboardInterrupt:
            logging.info("종료")
        finally:
            subprocess.run(['osascript', '-e', 'tell application "QuickTime Player" to quit'])

def main():
    # cliclick 확인
    try:
        subprocess.run(['which', 'cliclick'], check=True, capture_output=True)
    except:
        print("cliclick 필요: brew install cliclick")
        return
        
    player = SimpleLivingPlaylist()
    player.run()

if __name__ == "__main__":
    main()