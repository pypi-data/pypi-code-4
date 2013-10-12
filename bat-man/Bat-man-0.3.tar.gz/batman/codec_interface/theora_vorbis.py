from batman.codec_interface import base_codec, libtheora, libvorbis, ffmpeg_base_codec
import subprocess
from batman import definitions

class TheoraVorbisInteractor(base_codec.Interactor):
    PRETTY_NAME = "OGV(Theora/Vorbis)"

    def __init__(self):
        if definitions.WINDOWS:
            self.ffmpeg_command = definitions.path_with("bin", "ffmpeg.exe")
        else:
            self.ffmpeg_command = "ffmpeg"
    
    @staticmethod
    def can_be_used():
        return libtheora.LibTheora.can_be_used() and \
                libvorbis.LibVorbis.can_be_used()
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-codec:v", "libtheora",
                         "-qscale:v", "7", "-codec:a", "libvorbis", "-qscale:a", "3", out_path])
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".ogv"

base_codec.register_interaction(libtheora.LibTheora, libvorbis.LibVorbis,
                                TheoraVorbisInteractor)

