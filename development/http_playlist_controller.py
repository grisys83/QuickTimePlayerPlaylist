#!/usr/bin/env python3
"""
HTTP URL 기반 QuickTime 플레이리스트 컨트롤러
웹 서버의 고정 URL을 통해 동적으로 비디오를 교체하여 플레이리스트 구현
"""

import os
import sys
import time
import shutil
import subprocess
import threading
from pathlib import Path

class HTTPPlaylistController:
    def __init__(self, http_url, local_path, playlist):
        """
        Args:
            http_url: QuickTime에서 열 HTTP URL (예: http://grisys.synology.me/video.mp4)
            local_path: 실제 파일 경로 (예: /Volumes/web/video.mp4)
            playlist: 재생할 비디오 파일 목록
        """
        self.http_url = http_url
        self.local_path = Path(local_path)
        self.playlist = [Path(p) for p in playlist]
        self.current_index = 0
        self.is_playing = False
        
    def backup_original(self):
        """원본 파일 백업"""
        if self.local_path.exists():
            backup_path = self.local_path.with_suffix('.backup' + self.local_path.suffix)
            shutil.copy2(self.local_path, backup_path)
            print(f"원본 파일 백업: {backup_path}")
            
    def restore_original(self):
        """원본 파일 복원"""
        backup_path = self.local_path.with_suffix('.backup' + self.local_path.suffix)
        if backup_path.exists():
            shutil.copy2(backup_path, self.local_path)
            os.remove(backup_path)
            print("원본 파일 복원 완료")
            
    def replace_video(self, video_path):
        """웹 서버의 비디오 파일 교체"""
        try:
            # 기존 파일 삭제
            if self.local_path.exists():
                os.remove(self.local_path)
                
            # 새 파일 복사
            shutil.copy2(video_path, self.local_path)
            print(f"비디오 교체: {video_path.name} -> {self.local_path}")
            
            # 파일 시스템 동기화
            os.sync()
            time.sleep(0.5)  # 웹 서버가 파일 변경을 인식할 시간
            
        except Exception as e:
            print(f"파일 교체 실패: {e}")
            return False
        return True
        
    def open_quicktime_with_url(self):
        """QuickTime Player로 HTTP URL 열기"""
        script = f'''
        tell application "QuickTime Player"
            activate
            open location "{self.http_url}"
            
            -- 전체화면 설정 (선택사항)
            delay 2
            set presentation mode of document 1 to true
            
            play document 1
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script])
        
    def monitor_playback(self):
        """재생 상태 모니터링 및 다음 비디오로 전환"""
        while self.is_playing and self.current_index < len(self.playlist):
            # QuickTime 재생 상태 확인
            check_script = '''
            tell application "QuickTime Player"
                if (count documents) > 0 then
                    if playing of document 1 is false then
                        return "stopped"
                    else
                        return "playing"
                    end if
                else
                    return "no_document"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', check_script], 
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            
            if status == "stopped" or status == "no_document":
                # 다음 비디오로 전환
                self.current_index += 1
                if self.current_index < len(self.playlist):
                    print(f"\n다음 비디오 재생: {self.playlist[self.current_index].name}")
                    
                    # 파일 교체
                    if self.replace_video(self.playlist[self.current_index]):
                        # QuickTime 새로고침
                        refresh_script = '''
                        tell application "QuickTime Player"
                            if (count documents) > 0 then
                                close document 1
                            end if
                            delay 0.5
                            open location "''' + self.http_url + '''"
                            delay 1
                            play document 1
                        end tell
                        '''
                        subprocess.run(['osascript', '-e', refresh_script])
                    
            time.sleep(2)  # 2초마다 상태 확인
            
    def start_playlist(self):
        """플레이리스트 재생 시작"""
        if not self.playlist:
            print("재생할 비디오가 없습니다.")
            return
            
        # 원본 백업
        self.backup_original()
        
        try:
            # 첫 번째 비디오로 시작
            print(f"첫 번째 비디오 재생: {self.playlist[0].name}")
            if not self.replace_video(self.playlist[0]):
                return
                
            # QuickTime 열기
            self.open_quicktime_with_url()
            
            # 재생 모니터링 시작
            self.is_playing = True
            monitor_thread = threading.Thread(target=self.monitor_playback)
            monitor_thread.start()
            
            # 사용자 입력 대기
            print("\n플레이리스트 재생 중...")
            print("종료하려면 Enter를 누르세요.")
            input()
            
            # 재생 중지
            self.is_playing = False
            monitor_thread.join()
            
            # QuickTime 종료
            subprocess.run(['osascript', '-e', 
                          'tell application "QuickTime Player" to quit'])
            
        finally:
            # 원본 복원
            self.restore_original()
            
def main():
    if len(sys.argv) < 4:
        print("사용법: python http_playlist_controller.py <HTTP_URL> <LOCAL_PATH> <VIDEO1> [VIDEO2] ...")
        print("예시: python http_playlist_controller.py http://grisys.synology.me/video.mp4 /Volumes/web/video.mp4 video1.mp4 video2.mp4")
        sys.exit(1)
        
    http_url = sys.argv[1]
    local_path = sys.argv[2]
    playlist = sys.argv[3:]
    
    controller = HTTPPlaylistController(http_url, local_path, playlist)
    controller.start_playlist()

if __name__ == "__main__":
    main()