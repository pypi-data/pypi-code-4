from batman.codec_interface import base_codec
from batman.codec_interface import ffmpeg_base_codec
import subprocess

class LibVorbis(ffmpeg_base_codec.FFMpegBaseAudioCodec):
    PRETTY_NAME = "OGG(Vorbis)"
    TECHNICAL_NAME = "libvorbis"
    SOLO_ENCODING = True
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".ogg"
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-vn", "-codec:a", "libvorbis",
                         "-qscale:a", "3", out_path])

base_codec.register_audio_codec(LibVorbis)

