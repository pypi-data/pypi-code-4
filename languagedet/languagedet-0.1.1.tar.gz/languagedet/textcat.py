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
from languagedet._textcat import _TextCat


class TextCatDetector(Detector):
    """Clase para detectar idioma utilizando stopwords.
    """
    re_cat = re.compile(r'\[((..)--utf8)\]')
    
    def __init__(self, config_path=None):
        """
        Parameters
        ----------
        config_path: string
            Camino del fichero de configuración que se utilizará para
            inicializar el handler de textcat.
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'data', 
                'textcat.conf')
        if isinstance(config_path, unicode):
            config_path = config_path.encode('utf-8')
        self._textcat = _TextCat(config_path)
    
    @property
    def available(self):
        return ['da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pt',
            'ru', 'sv', 'tr']
    
    def __call__(self, text, tokenizer=None):
        if not isinstance(text, basestring):
            text = " ".join(text)
        text = text.lower()
        result = self._textcat.classify(text)
        if result == "UNKNOWN":
            raise DetectionError("Language not detected: unknown language.")
        if result == "SHORT":
            raise DetectionError("Language not detected: text too short.")
        items = self.re_cat.findall(result)
        if len(items) == 0 or len(items) > 1:
            languages = [lang[0] for lang in items]
            raise DetectionError("Language not detected: More than one language selected.",
                languages)
        return items[0][1]
        
        