#!/usr/bin/env python3
"""
미니멀 오디오→비디오 변환기 (Apple Music 스타일)
- 앨범 커버 블러 배경
- Noto Sans CJK 폰트
- 빠른 변환 속도
"""

import subprocess
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.id3 import ID3, APIC
import io
import shutil

class AudioToVideoConverter:
    def __init__(self):
        self.output_width = 1920
        self.output_height = 1080
        
        # Noto Sans CJK 폰트 경로들
        self.font_paths = [
            "/System/Library/Fonts/Supplemental/NotoSansCJKkr-Regular.otf",
            "/System/Library/Fonts/Supplemental/NotoSansCJKkr-Bold.otf",
            "/Library/Fonts/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc",  # 대체 폰트
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # 한글 대체
            "/System/Library/Fonts/Helvetica.ttc"  # 최후의 대체
        ]
        
    def get_font(self, size, bold=False):
        """폰트 로드"""
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        return ImageFont.load_default()
        
    def extract_metadata(self, audio_file):
        """메타데이터 추출"""
        metadata = {
            'title': Path(audio_file).stem,
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'duration': None,
            'cover': None
        }
        
        try:
            audio = mutagen.File(audio_file)
            if audio is None:
                return metadata
                
            # 제목
            if 'TIT2' in audio:
                metadata['title'] = str(audio['TIT2'])
            elif 'title' in audio:
                metadata['title'] = str(audio['title'][0])
            elif '\xa9nam' in audio:
                metadata['title'] = str(audio['\xa9nam'][0])
                
            # 아티스트
            if 'TPE1' in audio:
                metadata['artist'] = str(audio['TPE1'])
            elif 'artist' in audio:
                metadata['artist'] = str(audio['artist'][0])
            elif '\xa9ART' in audio:
                metadata['artist'] = str(audio['\xa9ART'][0])
                
            # 앨범
            if 'TALB' in audio:
                metadata['album'] = str(audio['TALB'])
            elif 'album' in audio:
                metadata['album'] = str(audio['album'][0])
            elif '\xa9alb' in audio:
                metadata['album'] = str(audio['\xa9alb'][0])
                
            # 길이
            if hasattr(audio.info, 'length'):
                metadata['duration'] = audio.info.length
                
            # 앨범 커버
            metadata['cover'] = self.extract_cover_art(audio)
            
        except Exception as e:
            print(f"메타데이터 추출 오류: {e}")
            
        return metadata
        
    def extract_cover_art(self, audio):
        """앨범 커버 추출"""
        try:
            if isinstance(audio, MP3):
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        return Image.open(io.BytesIO(tag.data))
                        
            elif isinstance(audio, MP4):
                if 'covr' in audio:
                    covers = audio['covr']
                    if covers:
                        return Image.open(io.BytesIO(covers[0]))
                        
            elif isinstance(audio, FLAC):
                if audio.pictures:
                    return Image.open(io.BytesIO(audio.pictures[0].data))
                    
        except:
            pass
            
        return None
        
    def create_visual_frame(self, metadata):
        """Apple Music 스타일 미니멀 프레임"""
        # 베이스 이미지 (검은색)
        img = Image.new('RGB', (self.output_width, self.output_height), (0, 0, 0))
        
        if metadata['cover']:
            # 블러 배경 생성
            background = metadata['cover'].resize((self.output_width + 200, self.output_height + 200), 
                                                Image.Resampling.LANCZOS)
            # 크롭 (중앙 부분만)
            left = 100
            top = 100
            background = background.crop((left, top, left + self.output_width, top + self.output_height))
            
            # 강한 블러 효과
            background = background.filter(ImageFilter.GaussianBlur(radius=60))
            
            # 어둡게 만들기
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(0.3)  # 30% 밝기
            
            img.paste(background, (0, 0))
            
            # 중앙 앨범 커버
            cover_size = 500
            cover = metadata['cover'].resize((cover_size, cover_size), 
                                           Image.Resampling.LANCZOS)
            
            # 앨범 커버 위치
            cover_x = (self.output_width - cover_size) // 2
            cover_y = 200
            
            # 그림자 효과 (단순화)
            shadow = Image.new('RGBA', (self.output_width, self.output_height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            for i in range(20, 0, -2):
                alpha = int(80 * (1 - i/20))
                shadow_draw.rectangle([cover_x - i, cover_y - i, 
                                     cover_x + cover_size + i, cover_y + cover_size + i], 
                                    fill=(0, 0, 0, alpha))
            
            img = Image.alpha_composite(img.convert('RGBA'), shadow).convert('RGB')
            img.paste(cover, (cover_x, cover_y))
        else:
            # 기본 그라데이션 배경
            draw = ImageDraw.Draw(img)
            for y in range(self.output_height):
                gray = int(20 * (1 - y / self.output_height))
                draw.line([(0, y), (self.output_width, y)], fill=(gray, gray, gray))
            
            # 중앙에 음표 아이콘
            note_font = self.get_font(200)
            draw.text((self.output_width // 2, 400), "♫", 
                     font=note_font, anchor="mm", fill=(80, 80, 80))
        
        # 텍스트 추가
        draw = ImageDraw.Draw(img)
        text_y = 750
        
        # 제목 (텍스트 길이 제한)
        title_font = self.get_font(56, bold=True)
        title = self.truncate_text(metadata['title'], title_font, self.output_width - 200)
        draw.text((self.output_width // 2, text_y), title, 
                 font=title_font, anchor="mt", fill=(255, 255, 255))
        
        # 아티스트
        artist_font = self.get_font(40)
        artist = self.truncate_text(metadata['artist'], artist_font, self.output_width - 200)
        draw.text((self.output_width // 2, text_y + 80), artist, 
                 font=artist_font, anchor="mt", fill=(200, 200, 200))
        
        # 앨범
        album_font = self.get_font(32)
        album = self.truncate_text(metadata['album'], album_font, self.output_width - 200)
        draw.text((self.output_width // 2, text_y + 140), album, 
                 font=album_font, anchor="mt", fill=(150, 150, 150))
        
        return img
        
    def truncate_text(self, text, font, max_width):
        """텍스트가 너무 길면 자르기"""
        try:
            if font.getlength(text) <= max_width:
                return text
        except:
            # 폴백: 문자 수로 추정
            if len(text) * 30 <= max_width:
                return text
            
        while len(text) > 0:
            try:
                if font.getlength(text + "...") <= max_width:
                    break
            except:
                if len(text + "...") * 30 <= max_width:
                    break
            text = text[:-1]
            
        return text + "..."
        
    def convert_to_video(self, audio_file, output_file=None):
        """빠른 비디오 변환"""
        if output_file is None:
            output_file = Path(audio_file).with_suffix('.mp4')
            
        # 메타데이터 추출
        print(f"처리 중: {Path(audio_file).name}")
        metadata = self.extract_metadata(audio_file)
        
        # 비주얼 생성
        visual_frame = self.create_visual_frame(metadata)
        
        # 임시 이미지 저장 (JPEG로 저장하여 속도 향상)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            visual_frame.save(tmp.name, 'JPEG', quality=90, optimize=True)
            temp_image = tmp.name
            
        # ffmpeg 명령 (최적화)
        ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        
        cmd = [
            ffmpeg,
            '-loop', '1',
            '-framerate', '1',  # 1fps로 설정
            '-i', temp_image,
            '-i', audio_file,
            '-map', '0:v',
            '-map', '1:a:0',  # 첫 번째 오디오 스트림만
            '-c:v', 'h264',
            '-preset', 'veryfast',  # 빠른 인코딩 (ultrafast보다 품질 좋음)
            '-tune', 'stillimage',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '256k',
            '-ac', '2',  # 스테레오
            '-shortest',
            '-movflags', '+faststart',
            str(output_file),
            '-y',
            '-loglevel', 'error'
        ]
        
        print("변환 중...")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ 완료: {output_file}")
            
            # 임시 파일 삭제
            os.unlink(temp_image)
            
            return str(output_file)
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 변환 실패: {e}")
            if os.path.exists(temp_image):
                os.unlink(temp_image)
            return None

def batch_convert(audio_files):
    """일괄 변환"""
    converter = AudioToVideoConverter()
    results = []
    
    total = len(audio_files)
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{total}] ", end='')
        output = converter.convert_to_video(audio_file)
        if output:
            results.append(output)
            
    return results

def main():
    if len(sys.argv) < 2:
        print("사용법: python audio_to_video_enhanced.py <audio_file> [audio_file2] ...")
        sys.exit(1)
        
    # 필요한 패키지 확인
    try:
        import mutagen
        from PIL import Image
    except ImportError:
        print("필요한 패키지를 설치하세요:")
        print("pip3 install mutagen pillow")
        sys.exit(1)
        
    audio_files = sys.argv[1:]
    
    print(f"Apple Music 스타일 비디오 변환")
    print(f"파일 개수: {len(audio_files)}")
    print("=" * 50)
    
    results = batch_convert(audio_files)
    
    print("\n" + "=" * 50)
    print(f"변환 완료: {len(results)}/{len(audio_files)}개 성공")
    
    if results:
        print("\n변환된 파일:")
        for result in results:
            print(f"  - {result}")

if __name__ == "__main__":
    main()