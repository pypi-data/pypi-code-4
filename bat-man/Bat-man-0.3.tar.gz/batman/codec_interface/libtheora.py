from batman.codec_interface import base_codec
from batman.codec_interface import ffmpeg_base_codec
import subprocess

class LibTheora(ffmpeg_base_codec.FFMpegBaseVideoCodec):
    PRETTY_NAME = "OGV(Theora)"
    TECHNICAL_NAME = "libtheora"
    SOLO_ENCODING = True
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".ogv"
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-an", "-codec:v", "libtheora",
                         "-qscale:v", "7", out_path])

base_codec.register_video_codec(LibTheora)

