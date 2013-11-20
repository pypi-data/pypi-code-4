# -*- coding: utf-8 -*-
# Author:  Karel Antonio Verdecia Ortiz <kverdecia@uci.cu, kverdecia@uci.cu>
"""
This file is part of the languagedet Python package.
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
import abc


class DetectionError(Exception):
    pass


class Detector(object):
    """Clase base para la detección automática de idioma.
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def available(self):
        """Devuelve un conjunto con los códigos ISO-639 de los idiomas
        que pueden ser detectados por la clase.
        """
    
    @abc.abstractmethod
    def __call__(self, text, tokenizer=None):
        """Detecta el idioma del texto que se pasa por parámetro.
        
        Parameters
        ----------
        text: string o iter<string>
            Texto que será analizado. Puede ser una cadena o un objeto 
            iterable con las palábras del texto que se va a analizar. La
            codificación de caracteres del texto o de las palabras debe 
            ser `utf-8`.
        tokenizer: función
            Si el valor que se pasa en el parámetro `text` es una cadena y
            el algoritmo de detección de idioma implementado por la clase
            necesita una lista de palabras entonces se utilizará una 
            función que recibirá el texto por parámetro y devolverá una 
            lista con las palabras del texto. Dicha función debe ser pasada
            en este parámetro. Si no se especifica ninguna función en este
            parámetro se separarán las palabras por los espacios en blanco.
            
        Returns: string
            Devuelve el codigo ISO-639 del idioma detectado.
            
        Raises
        ------
        DetectionError
            Si no se pudo detectar el idioma.
        """
    