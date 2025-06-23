#!/usr/bin/env python3
"""오디오 변환 테스트"""

import sys
from pathlib import Path
from audio_to_video_enhanced import AudioToVideoConverter

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 test_convert.py <audio_file>")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    if not Path(audio_file).exists():
        print(f"파일을 찾을 수 없습니다: {audio_file}")
        sys.exit(1)
        
    print(f"변환 시작: {audio_file}")
    
    converter = AudioToVideoConverter()
    output = converter.convert_to_video(audio_file)
    
    if output:
        print(f"변환 성공: {output}")
    else:
        print("변환 실패")