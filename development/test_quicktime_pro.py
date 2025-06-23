#!/usr/bin/env python3
"""QuickTime Playlist Pro 테스트"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 실행
if __name__ == "__main__":
    print("QuickTime Playlist Pro 테스트 시작...")
    print(f"Python 버전: {sys.version}")
    print(f"현재 디렉토리: {os.getcwd()}")
    
    try:
        from QuickTimePlaylistPro import main
        main()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()