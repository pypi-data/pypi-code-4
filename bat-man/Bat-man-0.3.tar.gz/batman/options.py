import configparser
import os
from batman import definitions
from batman.definitions import get_user_data_folder_with
from batman.codec_interface import base_codec
from batman.codec_interface.base_codec import find_audio_codec_by_technical_name, find_video_codec_by_technical_name
import logging

class Options(object):
    def __init__(self, optionsPath=None):
        self.cfgParser = configparser.ConfigParser()
        self.optionsPath = optionsPath or get_user_data_folder_with("options.cfg")
        try:
            self.cfgParser.read(self.optionsPath)
        except IOError:
            pass
        self.quality = self.cfgParser.getint("Options", "quality", fallback=360)
        # Ranges from 0 to 9 - LAME specific.
        self.VBRquality = self.cfgParser.getint("Options", "VBRquality", fallback=2)
        
        # Audio and video codecs
        self.audioCodecEnabled = self.cfgParser.getboolean("Options", "audioCodecEnabled", fallback=True)
        self.videoCodecEnabled = self.cfgParser.getboolean("Options", "videoCodecEnabled", fallback=False)
        
        audioCodecTechnicalName = self.cfgParser.get("Options", "audioCodecTechnicalName", fallback="libmp3lame")
        videoCodecTechnicalName = self.cfgParser.get("Options", "videoCodecTechnicalName", fallback="")
        
        # See if the codecs exist and if this combination is valid.
        if self.audioCodecEnabled:
            self.audioCodec = find_audio_codec_by_technical_name(audioCodecTechnicalName)
            if self.audioCodec == None:
                raise RuntimeError("Invalid audio codec in options")
        
        if self.videoCodecEnabled:
            self.videoCodec = find_video_codec_by_technical_name(videoCodecTechnicalName)
            if self.videoCodec == None:
                raise RuntimeError("Invalid video codec in options")
        
        if self.audioCodecEnabled and self.videoCodecEnabled:
            # Finding a Interactor is essential now.
            self.interactor = base_codec.find_interactor(self.audioCodec,
                                                         self.videoCodec)
            if self.interactor == None:
                raise RuntimeError("Couldn't find interactor between \"{}\" "\
                                    "audio codec and \"{}\" video codec".format(
                                        audioCodecTechnicalName,
                                        videoCodecTechnicalName
                                    ))
            else:
                logging.info("Interactor found: {}".format(self.interactor.PRETTY_NAME))
        
        # Alright, what happens here: If there is a folder set in the options,
        # check if it exists. If it does, set it as the default folder. If it
        # doesn't, set the user's home as the default folder, but instruct the program
        # to NOT OVERWRITE the original config unless it's changed.
        self._defaultFolderChanged = False
        self._originalDefaultFolder = self.cfgParser.get("Options", "defaultFolder", fallback="")
        if os.path.isdir(self._originalDefaultFolder):
            self._defaultFolder = self._originalDefaultFolder
        else:
            self._defaultFolder = os.path.expanduser("~")
    
    @property
    def defaultFolder(self):
        return self._defaultFolder
    
    @defaultFolder.setter
    def defaultFolder(self, value):
        self._defaultFolder = value
        self._defaultFolderChanged = True
    
    def write(self):
        self.cfgParser["Options"] = {}
        self.cfgParser["Options"]["quality"] = str(self.quality)
        self.cfgParser["Options"]["VBRquality"] = str(self.VBRquality)
        if self._defaultFolderChanged:
            self.cfgParser["Options"]["defaultFolder"] = self._defaultFolder

        self.cfgParser["Options"]["audioCodecEnabled"] = "true" if self.audioCodecEnabled else "false"
        if self.audioCodecEnabled:
            self.cfgParser["Options"]["audioCodecTechnicalName"] = self.audioCodec.TECHNICAL_NAME

        self.cfgParser["Options"]["videoCodecEnabled"] = "true" if self.videoCodecEnabled else "false"
        if self.videoCodecEnabled:
            self.cfgParser["Options"]["videoCodecTechnicalName"] = self.videoCodec.TECHNICAL_NAME

        with open(self.optionsPath, "w") as f:
            self.cfgParser.write(f)

definitions.OPTIONS = Options()

