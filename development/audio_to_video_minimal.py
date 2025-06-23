#!/usr/bin/env python3
"""
미니멀 오디오→비디오 변환기
- Apple Music 스타일 블러 배경
- Noto Sans CJK 폰트
- 빠른 변환 속도
"""

import subprocess
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.id3 import ID3, APIC
import io
import shutil

class MinimalAudioToVideoConverter:
    def __init__(self):
        self.output_width = 1920
        self.output_height = 1080
        
        # Noto Sans CJK 폰트 경로들
        self.font_paths = [
            "/System/Library/Fonts/Supplemental/NotoSansCJKkr-Regular.otf",
            "/System/Library/Fonts/Supplemental/NotoSansCJKkr-Bold.otf",
            "/Library/Fonts/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc",  # 대체 폰트
            "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # 한글 대체
        ]
        
    def get_font(self, size, bold=False):
        """폰트 로드"""
        font_index = 1 if bold else 0
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        return ImageFont.load_default()
        
    def extract_metadata(self, audio_file):
        """메타데이터 추출 (간소화)"""
        metadata = {
            'title': Path(audio_file).stem,
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
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
            background = metadata['cover'].resize((self.output_width, self.output_height), 
                                                Image.Resampling.LANCZOS)
            # 강한 블러 효과
            background = background.filter(ImageFilter.GaussianBlur(radius=50))
            
            # 어둡게 만들기
            enhancer = Image.new('RGB', background.size, (0, 0, 0))
            background = Image.blend(background, enhancer, 0.5)
            
            img.paste(background, (0, 0))
            
            # 중앙 앨범 커버
            cover_size = 500
            cover = metadata['cover'].resize((cover_size, cover_size), 
                                           Image.Resampling.LANCZOS)
            
            # 앨범 커버에 약간의 그림자
            shadow_img = Image.new('RGBA', (self.output_width, self.output_height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            shadow_x = (self.output_width - cover_size) // 2
            shadow_y = 200
            shadow_draw.rectangle([shadow_x - 10, shadow_y - 10, 
                                 shadow_x + cover_size + 10, shadow_y + cover_size + 10], 
                                fill=(0, 0, 0, 128))
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=20))
            
            img = Image.alpha_composite(img.convert('RGBA'), shadow_img).convert('RGB')
            img.paste(cover, (shadow_x, shadow_y))
        else:
            # 기본 검은 배경
            draw = ImageDraw.Draw(img)
            # 중앙에 음표 아이콘
            note_font = self.get_font(180)
            draw.text((self.output_width // 2, 400), "♫", 
                     font=note_font, anchor="mm", fill=(100, 100, 100))
        
        # 텍스트 추가
        draw = ImageDraw.Draw(img)
        text_y = 750
        
        # 제목
        title_font = self.get_font(56, bold=True)
        draw.text((self.output_width // 2, text_y), metadata['title'], 
                 font=title_font, anchor="mt", fill=(255, 255, 255))
        
        # 아티스트
        artist_font = self.get_font(40)
        draw.text((self.output_width // 2, text_y + 80), metadata['artist'], 
                 font=artist_font, anchor="mt", fill=(200, 200, 200))
        
        # 앨범
        album_font = self.get_font(32)
        draw.text((self.output_width // 2, text_y + 140), metadata['album'], 
                 font=album_font, anchor="mt", fill=(150, 150, 150))
        
        return img
        
    def should_skip_conversion(self, audio_file, output_file):
        """변환을 건너뛸지 결정"""
        if not output_file.exists():
            return False
            
        # 파일 크기 비교 (비디오가 오디오의 50% 이상이면 정상)
        audio_size = Path(audio_file).stat().st_size
        video_size = output_file.stat().st_size
        
        if video_size > audio_size * 0.5:
            # 추가로 비디오 파일이 정상인지 확인
            try:
                ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
                result = subprocess.run(
                    [ffmpeg, '-i', str(output_file), '-f', 'null', '-'],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except:
                return False
        return False
    
    def convert_to_video(self, audio_file, output_file=None):
        """빠른 비디오 변환"""
        if output_file is None:
            output_file = Path(audio_file).with_suffix('.mp4').parent / f"{Path(audio_file).stem}_converted.mp4"
            
        # 이미 변환된 파일 확인
        if self.should_skip_conversion(audio_file, output_file):
            print(f"⏭️  건너뜀: {Path(audio_file).name} (이미 변환됨)")
            return str(output_file)
            
        # 메타데이터 추출
        print(f"처리 중: {Path(audio_file).name}")
        metadata = self.extract_metadata(audio_file)
        
        # 비주얼 생성
        visual_frame = self.create_visual_frame(metadata)
        
        # 임시 이미지 저장
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            visual_frame.save(tmp.name, 'JPEG', quality=85)  # JPEG로 저장 (더 빠름)
            temp_image = tmp.name
            
        # ffmpeg 명령 (최적화)
        ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        if not os.path.exists(ffmpeg):
            print("\n❌ FFmpeg not found!")
            print("Please install FFmpeg:")
            print("  brew install ffmpeg")
            print("Or download from: https://ffmpeg.org/download.html")
            return None
        
        cmd = [
            ffmpeg,
            '-loop', '1',
            '-framerate', '1',  # 1fps
            '-i', temp_image,
            '-i', audio_file,
            '-map', '0:v',
            '-map', '1:a:0',
            '-c:v', 'h264',
            '-preset', 'ultrafast',  # 가장 빠른 인코딩
            '-tune', 'stillimage',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '256k',
            '-ac', '2',
            '-shortest',
            '-movflags', '+faststart',
            str(output_file),
            '-y',
            '-loglevel', 'error'
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ 완료: {output_file}")
            os.unlink(temp_image)
            return str(output_file)
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 실패: {e}")
            if os.path.exists(temp_image):
                os.unlink(temp_image)
            return None

def batch_convert(audio_files):
    """일괄 변환"""
    converter = MinimalAudioToVideoConverter()
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] ", end='')
        output = converter.convert_to_video(audio_file)
        if output:
            results.append(output)
            
    return results

def main():
    if len(sys.argv) < 2:
        print("사용법: python audio_to_video_minimal.py <audio_file> [audio_file2] ...")
        sys.exit(1)
        
    try:
        import mutagen
        from PIL import Image
    except ImportError:
        print("필요한 패키지를 설치하세요:")
        print("pip3 install mutagen pillow")
        sys.exit(1)
        
    audio_files = sys.argv[1:]
    
    print(f"미니멀 비디오 변환 시작 ({len(audio_files)}개 파일)")
    print("=" * 50)
    
    results = batch_convert(audio_files)
    
    print("\n" + "=" * 50)
    print(f"변환 완료: {len(results)}/{len(audio_files)}개 성공")

if __name__ == "__main__":
    main()