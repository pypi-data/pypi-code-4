# -*- coding: utf-8 -*-
# Author:  Karel Antonio Verdecia Ortiz <kverdecia@uci.cu, kverdecia@uci.cu>
"""
This file is part of the languagedet Python package.
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
import cPickle
import pkg_resources
from languagedet.detector import DetectionError, Detector


class StopWordsDetector(Detector):
    """Clase para detectar idioma utilizando stopwords.
    """
    def __init__(self, stopwords=None, threshold=3):
        """
        Parameters
        ----------
        stopwords: dict<string, iterable<string>>
            Diccionario con los `stopwords` de los idiomas que se van a 
            detectar. Las llaves de este diccionario contienden los 
            códigos ISO-639 de los idiomas que serán detectados por la
            clase y sus valores son objetos iterables con los `stopwords`
            de cada idioma. Los `stopwords` deben ser cadenas en 
            codificación `utf-8`.
        threshold: int
            Diferencia mínima que debe existir entre la cantidad de 
            stopwords del idioma con más stopwords y el segundo idioma con
            más stopwords.
        """
        if stopwords is None:
            path = 'data/stopwords.pickle'
            stream = pkg_resources.resource_stream(__name__, path)
            stopwords = cPickle.load(stream)
        self._stopwords = stopwords
        self._threshold = threshold
    
    @property
    def available(self):
        return self._stopwords.keys()
    
    def __call__(self, text, tokenizer=None):
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        if tokenizer is None:
            tokenizer = lambda x: x.split()
        if not callable(tokenizer):
            raise TypeError("The parameter tokenizer must be None or a function.")
        if isinstance(text, basestring):
            text = [token.strip() for token in tokenizer(text)]
        language_stops = dict()
        for language, stopwords in self._stopwords.items():
            tokens = set([token for token in text if token in stopwords])
            language_stops[language] = len(tokens)
        data = [(freq, lang) for lang, freq in language_stops.items()]
        data = sorted(data, reverse=True)
        if data[0][0] - data[1][0] < self._threshold:
            languages = [lang for freq, lang in data if freq==data[0][0]]
            raise DetectionError("Language not detected: threshold not reached.",
                set(languages))
        return data[0][1]
        
        