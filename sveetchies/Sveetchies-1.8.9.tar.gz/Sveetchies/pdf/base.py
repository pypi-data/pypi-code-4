# -*- coding: utf-8 -*-
"""
Prototype de génération d'un document PDF
"""
from reportlab.pdfgen import canvas

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from modelizer import HTMLInterface

class BasePrototypePDF(object):
    """
    Prototype de génération de facture au format PDF
    
    Utilise quasi-exclusivement la surcouche ``Platypus`` pour la création des éléments
    """
    doc_pagesize = letter
    doc_margin = (inch, inch, inch, inch) # Haut, droite, bas, gauche (css like)
    doc_author = "Dummy author"
    doc_title = "Dummy title"
    
    def __init__(self, fonts={}, default_family_font=None, medias_path='', style='Normal'):
        """
        :type fonts: dict
        :param fonts: (optional) Registre de chemins des type de police disponible : 
                      régulier, 'gras', italique et gras+italique; avec respectivement 
                      comme mot clé 'normal', 'bold', 'italic', 'boldItalic'. Seul
                      le type 'normal' est obligatoire, les autres sont optionnels. Les 
                      fichiers de polices doivent êtres au format TTF. Le registre accepte
                      plus polices et est un dictionnaire au format suivant : ::
                      
                        {
                            'NomDeLaPolice': {
                                'NomDuType': 'CheminVersLeTTF',
                            }
                        }
                      
                      Il est déconseillé de ne pas spécifier de police (la police par 
                      défaut embarquée par ReportLab est affreuse et ne supporte pas 
                      certaines méthodes).
        
        :type default_family_font: string
        :param default_family_font: (optional) Nom d'une police à spécifier par défaut 
                                    dans tout les éléments. Vide par défaut, donc aucun 
                                    élément ne spécifie de Police particulière par défaut.
                                    Cette argument est transmis au modelizer.
        
        :type medias_path: string
        :param medias_path: (optional) Chemin des médias utilisés dans le document. Sert 
                            exclusivement pour retrouver les images. Vide par défaut, 
                            donc toute les images doivent être spécifiés avec un chemin 
                            complet valable. Ce chemin est préfixé à TOUT les médias, 
                            donc si vos médias sont dispersés à plusieurs endroits 
                            différents, il est mieux de le laisser vide.
                            Cette argument est transmis au modelizer.
        
        :type style: string
        :param style: (optional) Nom du style à utiliser, doit correspondre à un style 
                      disponible via `reportlab.lib.styles.getSampleStyleSheet`. Le style 
                      par défaut utilisé est 'Normal'.
        """
        self.elements = []
        self.medias_path = medias_path
        self.default_family_font = default_family_font
        
        self.doc_width, self.doc_height = self.doc_pagesize
        
        self.style = self.get_style(style)
        
        self._registred_fonts = []
        self.set_fonts(fonts)
        
        self.modelizer = HTMLInterface(default_family_font=self.default_family_font, medias_path=self.medias_path, style=self.style)
        
    def get_style(self, key):
        """
        Récupère le style par défaut des éléments à utiliser
        
        :type key: string
        :param key: Nom du style à récupérer.
        
        :rtype: dict
        :return: Objet des styles par défaut, l'objet implémente l'interface d'un 
                 dictionnaire.
        """
        return getSampleStyleSheet()[key]
        
    def set_fonts(self, fonts):
        """
        Enregistre les familles de fonts spécifiés pour qu'elles soient prêtes à 
        l'utilisation avec canvas ou Platypus.
        
        Une famille doit avoir au moins le type 'normal' (~=regular) sinon elle sera 
        ignorée, les autres types possibles sont "italic", "bold" et "boldItalic".
        
        Pas de possibilité d'écraser une précédente famille déja enregistrée.
        
        :type fonts: dict
        :param fonts: Registre de chemins des type de police à rendre disponibles.
        """
        # Parcours toute les familles
        for family_key, family_types in fonts.items():
            # Si la famille est déja dans le registre interne, on passe
            if family_key not in self._registred_fonts:
                # Le type normal est le minimum requis
                if 'normal' in family_types:
                    fontkwargs = {}
                    # Parcours et inscris tout les types de la famille
                    for type_key, type_path in family_types.items():
                        type_name = family_key+type_key.title()
                        pdfmetrics.registerFont( TTFont(type_name, type_path) )
                        fontkwargs[type_key] = type_name
                    # Map des types de la famille
                    pdfmetrics.registerFontFamily(family_key, **fontkwargs)
                    # Ajoute le nom de famille au registre interne
                    self._registred_fonts.append(family_key)
        
    def open(self, buffer_response):
        """
        Ouvre le pointeur du document dans le buffer fourni
        
        :type buffer_response: object
        :param buffer_response: Un "File object" ou un objet implémentant la même 
                                interface tel que `cStringIO.StringIO`. Il sera utilisé 
                                comme un pointeur de fichier que ReportLab remplira avec 
                                le document. Attention, le pointeur doit être ouvert et 
                                sa fermeture est la charge de l'utilisateur.
        """
        # Init du template simple de la page
        self.doc = SimpleDocTemplate(
            buffer_response, 
            pagesize=self.doc_pagesize, 
            rightMargin=self.doc_margin[1], 
            leftMargin=self.doc_margin[3], 
            topMargin=self.doc_margin[0],
            bottomMargin=self.doc_margin[2]
        )
        
    def close(self):
        """
        Ferme le pointeur du document
        
        Cela entraîne la génération du document PDF dans le pointeur de fichier qui a été 
        spécifié dans ``BasePrototypePDF.open()``.
        """
        if hasattr(self, 'doc'):
            elements = self.modelizer.elements
            
            self.doc.author = self.doc_author
            self.doc.subject = self.doc.title = self.doc_title
            self.doc.build(elements, onFirstPage=self.onAllPage, onLaterPages=self.onAllPage)
            # TODO: Supprimer "self.doc" pour bien remettre le compteur à zéro (?)
        else:
            # TODO: Faire un raise quelque chose pour bien indiquer que le document n'a 
            # pas encore été ouvert
            pass

    def onAllPage(self, canvas, doc):
        """
        Fonction "callable" utilisé pour injecter l'entête et le pied de page sur toute 
        les pages lors du "build" du document
        
        :type canvas: object `reportlab.pdfgen.canvas`
        :param canvas: Canvas du document à utiliser.
        
        :type doc: object `reportlab.platypus.SimpleDocTemplate`
        :param doc: Objet du document crée lors de l'ouverture du pointeur dans 
                    ``BasePrototypePDF.open()``.
        """
        canvas.saveState()
        self.set_header(canvas, doc)
        self.set_footer(canvas, doc)
        canvas.restoreState()

    def set_header(self, canvas, doc):
        """
        Dessine le paragraphe de l'entête des pages
        
        Méthode à implémenter pour construire l'entête de page.
        
        :type canvas: object `reportlab.pdfgen.canvas`
        :param canvas: Canvas du document à utiliser.
        
        :type doc: object `reportlab.platypus.SimpleDocTemplate`
        :param doc: Objet du document crée lors de l'ouverture du pointeur dans 
                    ``BasePrototypePDF.open()``.
        """
        pass

    def set_footer(self, canvas, doc):
        """
        Dessine le paragraphe du pied de page des pages
        
        Méthode à implémenter pour construire le pied de page.
        
        :type canvas: object `reportlab.pdfgen.canvas`
        :param canvas: Canvas du document à utiliser.
        
        :type doc: object `reportlab.platypus.SimpleDocTemplate`
        :param doc: Objet du document crée lors de l'ouverture du pointeur dans 
                    ``BasePrototypePDF.open()``.
        """
        pass

    def fill(self):
        """
        Procède à l'ajout de tout les éléments de contenu du document (hors entête et 
        pied de page)
        
        Ceci est LA méthode à implémenter dans votre objet d'héritage et qui va lancer 
        la procédure de construction des pages de votre document. N'y incluez pas l'
        entête et le pied de page qui sont gérés dans des méthodes séparés (à moins de 
        savoir ce que vous faites).
        """
        pass
