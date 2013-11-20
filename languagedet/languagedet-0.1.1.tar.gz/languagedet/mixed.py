# -*- coding: utf-8 -*-
# Author:  Karel Antonio Verdecia Ortiz <kverdecia@uci.cu, kverdecia@uci.cu>
"""
This file is part of the languagedet Python package.
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
import os
import re
import cPickle
import pkg_resources
from languagedet.detector import DetectionError, Detector
from languagedet.stopwords import StopWordsDetector
from languagedet.textcat import TextCatDetector


class MixedDetector(Detector):
    """Clase para detectar idioma utilizando stopwords.
    """
    def __init__(self, stopwords=None, threshold=3, textcat_config=None):
        """
        Parameters
        ----------
        config_path: string
            Camino del fichero de configuración que se utilizará para
            inicializar el handler de textcat.
        """
        self._stop = StopWordsDetector(stopwords, threshold)
        self._textcat = TextCatDetector(textcat_config)
    
    @property
    def available(self):
        languages = set(self._textcat.available)
        languages.update(set(self._stop.available))
        return list(languages)
    
    def __call__(self, text, tokenizer=None):
        try:
            return self._stop(text)
        except DetectionError, e:
            return self._textcat(text)
        
