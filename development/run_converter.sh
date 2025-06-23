#!/bin/bash
# QuickTime Converter 최적화 실행

# Python 최적화 모드로 실행
python3 -O QuickTimeConverter.py

# 또는 높은 우선순위로 실행 (관리자 권한 필요)
# sudo nice -n -10 python3 QuickTimeConverter.py