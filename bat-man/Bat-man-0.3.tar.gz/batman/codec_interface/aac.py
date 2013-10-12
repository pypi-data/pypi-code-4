from batman.codec_interface import base_codec
from batman.codec_interface import ffmpeg_base_codec
import subprocess

class AAC(ffmpeg_base_codec.FFMpegBaseAudioCodec):
    PRETTY_NAME = "AAC"
    TECHNICAL_NAME = "aac"
    SOLO_ENCODING = True
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".aac"
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-vn",
                         "-codec:a", "aac", out_path])

base_codec.register_audio_codec(AAC)
