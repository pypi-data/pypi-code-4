from batman.codec_interface import base_codec, libx264, aac, ffmpeg_base_codec
import subprocess
from batman import definitions

class LibX264_AACInteractor(base_codec.Interactor):
    PRETTY_NAME = "MP4(libx264/AAC)"

    def __init__(self):
        if definitions.WINDOWS:
            self.ffmpeg_command = definitions.path_with("bin", "ffmpeg.exe")
        else:
            self.ffmpeg_command = "ffmpeg"
    
    @staticmethod
    def can_be_used():
        return libx264.LibX264.can_be_used() and \
                aac.AAC.can_be_used()
    
    def encode(self, out_path, avi_file):
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-codec:v", "libx264",
                         "-codec:a", "aac", out_path])
    
    def make_valid_file_name_from_caption(self, caption):
        return ffmpeg_base_codec.prepare_caption(caption) + ".mp4"

base_codec.register_interaction(libx264.LibX264, aac.AAC,
                                LibX264_AACInteractor)

