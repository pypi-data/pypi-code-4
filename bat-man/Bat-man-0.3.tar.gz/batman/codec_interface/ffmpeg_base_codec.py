from batman.codec_interface import base_codec
from batman import definitions
import re
import os

def prepare_caption(caption):
    caption = re.sub("\/", "-", caption)
    caption = re.sub("\"", "", caption)
    caption = re.sub("'", "", caption) # Double and single quotes
    # Ignore last dot, just in case
    caption = re.sub("[.]$", "", caption)
    # Any other dots...
    caption = re.sub("[.]", "_", caption)
    
    return caption

class FFMpegBaseAudioCodec(base_codec.BaseAudioCodec):
    def __init__(self):
        if definitions.WINDOWS:
            self.ffmpeg_command = definitions.path_with("bin", "ffmpeg.exe")
        else:
            self.ffmpeg_command = "ffmpeg"
    
    @staticmethod
    def can_be_used():
        if not definitions.WINDOWS:
            return True # Same situation as LAME
        else:
            ffmpeg_cmd = definitions.path_with("bin", "ffmpeg.exe")
            if os.path.exists(ffmpeg_cmd):
                return True
            else:
                return False

class FFMpegBaseVideoCodec(base_codec.BaseVideoCodec):
    def __init__(self):
        if definitions.WINDOWS:
            self.ffmpeg_command = definitions.path_with("bin", "ffmpeg.exe")
        else:
            self.ffmpeg_command = "ffmpeg"

    @staticmethod
    def can_be_used():
        if not definitions.WINDOWS:
            return True # Same situation as LAME
        else:
            ffmpeg_cmd = definitions.path_with("bin", "ffmpeg.exe")
            if os.path.exists(ffmpeg_cmd):
                return True
            else:
                return False

