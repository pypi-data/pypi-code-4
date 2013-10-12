from batman.codec_interface import base_codec
from batman.codec_interface import ffmpeg_base_codec
import subprocess

class LibX264(ffmpeg_base_codec.FFMpegBaseVideoCodec):
    PRETTY_NAME = "MP4(libx264)"
    TECHNICAL_NAME = "libx264"
    SOLO_ENCODING = True
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".mp4"
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-an",
                         "-codec:v", "libx264", out_path])

base_codec.register_video_codec(LibX264)

