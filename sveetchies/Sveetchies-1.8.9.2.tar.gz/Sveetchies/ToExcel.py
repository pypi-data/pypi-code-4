# -*- coding: utf-8 -*-
"""
Exportation de données vers un nouveau fichier Excel

Ceci est plus un exemple d'utilisation concret et fonctionnel de ``xlwt`` qu'une 
interface du type "couteau suisse".

Créé un nouveau fichier Excel rempli par une liste de tuple de données, optionnellement 
avec une ligne d'entête (pour les titres de colonnes).

L'exportation ne peut se faire que dans un nouveau fichier et pas en éditant un fichier 
déja existant, si le nom de fichier ciblé existe déja il sera complètement écrasé.

Le système de styles est assez simple, un style pour la ligne d'entête et un style pour 
toute les données, les cellules de dates (reconnus dans le tuple de données si c'est une 
instance de datetime) sont forcés au format de date spécifié dans les paramètres par 
défaut.

Requiert :

    * xlwt (testé uniquement avec la version 0.7.2) : http://www.python-excel.org/
"""
__title__ = "Python datas to Excel file"
__version__ = "0.0.3"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2010-2011 sveetch.biz"
__license__ = "GPL"

from datetime import datetime
from decimal import Decimal

import xlwt

# Paramètres par défaut
DEFAULT_BOOL_LABELS = {
    'yes': 'Oui',
    'no': 'Non',
}
DEFAULT_STYLES = {
    'header':{
        'font': {
            'bold': True,
            'color': 'white',
        },
        'align': {
            'wrap': True,
            'vert': 'center',
            'horiz': 'center',
        },
        'pattern': {
            'pattern': 'solid_pattern',
            'fore_color': 'gray50',
        },
    },
    'data_common':{
        'align': {
            'wrap': True,
            'vert': 'center',
            'horiz': 'center',
        },
    }
}
DEFAULT_DATE_FORMAT = 'DD-MM-YYYY'

class ExcelExporter(object):
    """
    Interface d'exportation de données vers un nouveau fichier Excel
    """
    def __init__(self, target, default_bool_labels=DEFAULT_BOOL_LABELS, default_styles=DEFAULT_STYLES, default_date_format=DEFAULT_DATE_FORMAT):
        """
        :type target: string or file or StringIO
        :param target: Cible du contenu du document, un string pour indiquer un chemin 
                       de fichier à créer, ou un file object ou un StringIO à remplir 
                       sans créer directement de fichier. Si None, le document est crée 
                       en mémoire mais aucun fichier n'est créé.
        """
        self.target = target
        self.default_bool_labels = default_bool_labels
        self.default_styles = default_styles
        self.default_date_format = default_date_format
        
        self.order = []
        self.sheets = {}
        self.headers = {}
        self.datas = {}
        
        self.get_styles()
    
    def get_styles(self):
        """
        Init des styles appliquables
        """
        self.style_header = self.get_easyxf(self.default_styles['header'])
        
        self.style_data_common = self.get_easyxf(self.default_styles['data_common'])

        self.style_data_date = self.get_easyxf(self.default_styles['data_common'])
        self.style_data_date.num_format_str = self.default_date_format
    
    def get_easyxf(self, style_dict):
        """
        Compile un dictionnaire de styles de cellules dans un easyxf
        
        Une ligne de styles est rendu sous la forme :
        
            <element>:(<attribute> <value>,)+;)+
        """
        elements = []
        
        for element_title, element_attrs in style_dict.items():
            attrs = []
            for k,v in element_attrs.items():
                attrs.append("%s %s" % (k, str(v).lower()))
            attrs = ','.join(attrs)
            elements.append("%s:%s" % (element_title, attrs))
        
        output = ';'.join(elements)
        if not output.endswith(';'):
            output += ';'
        return xlwt.easyxf(output)
    
    def new(self):
        """
        Ouvre un nouveau workbook
        """
        self.workbook = xlwt.Workbook()
    
    def close(self):
        """
        Ferme le workbook et crée son fichier
        """
        if len(self.sheets)>0:
            for item in self.order:
                self.process_sheet(item)
                
            if self.target:
                self.workbook.save(self.target)
    
    def set_sheet(self, name, datas, header=None):
        """
        Enregistre une nouvelle feuille de données dans le registre interne
        """
        self.order.append(name)
        self.headers[name] = header
        self.datas[name] = datas
        self.sheets[name] = None
    
    def process_sheet(self, sheetname):
        """
        Construction des cellules d'une feuille
        """
        row = 0 # compteur de l'indice de ligne
        
        worksheet = self.workbook.add_sheet(sheetname)
        
        # Ajoute une ligne d'entête des colonnes si il y'en a un de fourni
        if sheetname in self.headers and self.headers[sheetname]:
            self.write_row_cells(worksheet, row, self.headers[sheetname], style=self.style_header)
            row += 1
        # S'occupe des lignes de données
        for item_row in self.datas[sheetname]:
            self.write_row_cells(worksheet, row, item_row)
            row += 1
    
    def write_row_cells(self, worksheet, row_id, cells, style=None):
        """
        Construction des cellules d'une feuille
        """
        if not style:
            style = self.style_data_common
        
        row = worksheet.row(row_id)
        
        col = 0
        for content in cells:
            self.set_cell(worksheet, row, col, content, style)
            col += 1
        row.set_style(style)
    
    def set_cell(self, worksheet, row, col, content, style):
        """
        Format le contenu et son style selon le type du contenu
        """
        if isinstance(content, Decimal):
            style.num_format_str = "General"
            row.set_cell_number(col, content, style)
        elif isinstance(content, datetime):
            style.num_format_str='YYYY-MM-DD'
            row.set_cell_date(col, content, style)
        elif isinstance(content, bool):
            style.num_format_str = "General"
            if content:
                content = self.default_bool_labels['yes']
            else:
                content = self.default_bool_labels['no']
            row.write(col, content, style)
        elif content == None:
            style.num_format_str = "General"
            row.write(col, '', style)
        else:
            style.num_format_str = "General"
            row.write(col, content, style)

# Simple démonstration
if __name__ == "__main__":
    import StringIO
    
    filename = 'toast.xls'
    #filename = None
    
    #output_object = StringIO.StringIO()
    output_object = open(filename, 'wb')

    starttime = datetime.now()
    
    
    # Ouverture du workbook
    e = ExcelExporter(target=output_object)
    e.new()
    
    # Créé une nouvelle feuille
    e.set_sheet(
        "cocolapin", # Nom de la feuille
        # Données
        (
            ('1', u'Yop', 1, datetime.now()),
            ('2', True, 42, datetime.now()),
            ('3', u'Téléphone en €ros', 10000, datetime.now()),
            ('4', u'Hello World!', 3.1456, datetime.now()),
        ),
        # Entête optionnelle
        header=('ID', 'TITRE', 'NOMBRE', 'DATE')
    )
    
    # Fermeture du workbook
    print e.close()
    
    #output_object.seek(0)
    #pdf = output_object.getvalue()
    output_object.close()

    endtime = datetime.now()
    print "~~~ Durée : %s" % str(endtime-starttime)
