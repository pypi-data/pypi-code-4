# -*- coding: utf-8 -*-
"""
Démonstration
"""
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.units import inch

from Sveetchies.pdf.base import BasePrototypePDF

LIPSUM_1 = """Nunc pulvinar, lorem eget bibendum adipiscing, mi metus porttitor neque, non mattis velit metus vitae lorem. Praesent gravida mollis leo sed congue. Duis egestas, ipsum a fringilla varius, dolor lacus feugiat tortor, rutrum tincidunt arcu nisl at justo. Proin vel diam ut ipsum rutrum pulvinar eget id ligula."""
LIPSUM_2 = """Nulla fringilla, eros a mollis hendrerit, ante felis ultrices leo, sed luctus sapien felis vel sapien. Nulla lectus leo, aliquet nec mollis vitae, pellentesque nec ante. Sed consectetur bibendum rhoncus. Nullam ultricies turpis non mi tempor ullamcorper. Donec ligula lectus, dictum ut sed."""
LIPSUM_3 = """Phasellus malesuada dictum purus, vel vehicula nunc aliquet eget. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Curabitur scelerisque felis ac massa ultricies ac fermentum lorem luctus. Donec nec eros a nibh venenatis bibendum eget in nisi."""
LIPSUM_4 = """Ut malesuada, erat eu elementum vestibulum, arcu mi hendrerit magna, a feugiat mauris velit vel nisi. Etiam ligula quam, posuere ut rhoncus vel, venenatis eget purus! Vivamus adipiscing tristique ligula; eu pulvinar nisi fringilla a. Cras erat dui, consequat eget pulvinar sit amet, commodo quis urna. Sed amet."""

class SamplePDF(BasePrototypePDF):
    """
    Démonstration d'héritage de `Sveetchies.pdf.base.BasePrototypePDF`
    """
    doc_author = "David Thenon <sveetch@gmail.com>"
    doc_title = "Sample"

    def fill(self):
        """
        Procède à l'ajout de tout les éléments de contenu du document (hors entête et 
        pied de page)
        """
        self.page_1()
        self.page_2()
        self.page_3()
        self.page_4()

    def page_1(self):
        """
        Page de test 1, les titres et paragraphes
        """
        self.modelizer.H1(self.doc_title)
        
        self.modelizer.H2("Titres et paragraphes")
        
        self.modelizer.H3("Section 1")
        
        self.modelizer.H4("Section 1.1")
        
        self.modelizer.P(LIPSUM_1)
        
        self.modelizer.H4("Section 1.2")
        
        self.modelizer.P(LIPSUM_2, border_size=1, border_color=colors.red, background=colors.yellow, padding=(0.05*inch, 0.05*inch, 0.05*inch, 0.05*inch))
        
        self.modelizer.H3("Section 2")
        
        self.modelizer.H4("Section 2.1")
        
        self.modelizer.P(LIPSUM_3)
        
        self.modelizer.H4("Section 2.2")
        
        self.modelizer.P(LIPSUM_4)
        
        self.modelizer.BREAK()

    def page_2(self):
        """
        Page de test 2, les images
        """
        self.modelizer.H2("Images")
        
        self.modelizer.P(LIPSUM_2)
        
        self.modelizer.H3(u"Centré")
        
        self.modelizer.IMG("sveetchbiz.png", margin=(0.2*inch, 0, 0.2*inch, 0))
        
        self.modelizer.H3(u"Gauche")
        
        self.modelizer.IMG("sveetchbiz.png", margin=(0.2*inch, 0, 0.2*inch, 0), align="left")
        
        self.modelizer.H3(u"Droite")
        
        self.modelizer.IMG("sveetchbiz.png", margin=(0.2*inch, 0, 0.2*inch, 0), align="right")
        
        self.modelizer.BREAK()

    def page_3(self):
        """
        Page de test 3, les listes à puces
        """
        self.modelizer.H2(u"Liste à puces")
        
        items = [i.strip()+";" for i in LIPSUM_1.split('.') if len(i.strip())>0]
        self.modelizer.UL(items)
        
        self.modelizer.BREAK()

    def page_4(self):
        """
        Page de test 4, les tableaux
        """
        self.modelizer.H2(u"Tableaux")
        
        header_rows = ['id', 'title', 'category', 'options']
        body_row = [
            [
                'id',
                'title',
                'category',
                'options',
            ],
        ]
        
        self.modelizer.TABLE(header_rows=header_rows, body_row=body_row, col_sizing='proportional')
        
        self.modelizer.BREAK()
    
    def set_footer(self, canvas, doc):
        """
        Dessine le paragraphe du pied de page des pages
        """
        txt = u"<strong><u>Ceci est un pied de page</u></strong>"
        p = self.modelizer.P(txt, align="center", passive=True)
        p.wrap(self.doc_width, 0.40 * inch) 
        p.drawOn(canvas, 0, 0.40 * inch) 

#
if __name__ == "__main__":
    # Utilise la police freetype intégré dans la démo de `Sveetchies.gantt`
    font_basepath = '../gantt/demos/fonts/'
    fonts_registry = {
        'LiberationSansSerif': {
            'normal': font_basepath+'liberation_sans/LiberationSans-Regular.ttf',
            'bold': font_basepath+'liberation_sans/LiberationSans-Bold.ttf',
            'italic': font_basepath+'liberation_sans/LiberationSans-Italic.ttf',
            'boldItalic': font_basepath+'liberation_sans/LiberationSans-BoldItalic.ttf',
        }
    }
    
    # Instance du prototype
    proto = SamplePDF(fonts=fonts_registry, default_family_font='LiberationSansSerif')
    # Pointeur de fichier à utilisé comme buffer ouvert par le prototype
    f = open('sample.pdf', 'wb')
    # Ouverture du document, remplissage et fermeture
    proto.open(f)
    proto.fill()
    proto.close()
    # Fermeture du pointeur de fichier et sauvegarde du document
    f.close()
