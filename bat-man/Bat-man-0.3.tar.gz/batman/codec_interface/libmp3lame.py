from batman.codec_interface import base_codec
from batman import definitions

import os
import re
import subprocess
import tempfile

class LibMP3Lame(base_codec.BaseAudioCodec):
    PRETTY_NAME = "MP3(Lame)"
    TECHNICAL_NAME = "libmp3lame"
    SOLO_ENCODING = True
    
    def __init__(self):
        if definitions.WINDOWS:
            self.lame_command = definitions.path_with("bin", "lame.exe")
            self.ffmpeg_command = definitions.path_with("bin", "ffmpeg.exe")
        else:
            self.lame_command = "lame"
            self.ffmpeg_command = "ffmpeg"
    
    @staticmethod
    def can_be_used():
        if not definitions.WINDOWS:
            # I don't know how to check it, then, let's assume everything is OK.
            return True
        else:
            lame_cmd = definitions.path_with("bin", "lame.exe")
            ffmpeg_cmd = definitions.path_with("bin", "ffmpeg.exe")
            if os.path.exists(lame_cmd) and os.path.exists(ffmpeg_cmd):
                return True
            else:
                return False
    
    def make_valid_file_name_from_caption(self, caption):
        caption = re.sub("\/", "-", caption)
        caption = re.sub("\"", "", caption)
        caption = re.sub("'", "", caption) # Double and single quotes
        # Ignore last dot, just in case
        caption = re.sub("[.]$", "", caption)
        # Any other dots...
        caption = re.sub("[.]", "_", caption)
        
        treated_result = caption + ".mp3"
        return treated_result
    
    def encode(self, out_path, avi_file):
        if definitions.WINDOWS:
            wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav_file.close()
        else:
            wav_file = tempfile.NamedTemporaryFile(suffix=".wav")
        subprocess.call([self.ffmpeg_command, "-y", "-i", avi_file, "-vn",
                         wav_file.name],
                         stdout=subprocess.DEVNULL)
        subprocess.call([self.lame_command, "-V2", wav_file.name, out_path],
                        stdout=subprocess.DEVNULL)
        if definitions.WINDOWS:
            os.unlink(wav_file.name)

base_codec.register_audio_codec(LibMP3Lame)

