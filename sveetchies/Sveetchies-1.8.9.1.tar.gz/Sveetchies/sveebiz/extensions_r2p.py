# -*- coding: utf-8 -*-
"""
Extension pour rst2pdf 

À appeler en y ajoutant l'argument ``-e`` tel que par exemple : ::

    rst2pdf -i foo.rst -o foo.pdf -e $SVEETCHIES/sveebiz/extensions_r2p.py

Où ``$SVEETCHIES`` est le chemin d'installation du module *Sveetchies*.
"""
from estimate import EstimateDocument

def install(createpdf, options):
    """
    Méthode d'extension appelée par rst2pdf pour utiliser l'extension des directives de 
    devis
    
    :type createpdf: object
    :param createpdf: Un controleur de création de RST2PDF
    
    :type options: object
    :param options: Objet des options actives de RST2PDF
    
    """
    obj = EstimateDocument(options.infile)
    options.infile = obj.output
