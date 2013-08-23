from distutils.core import setup

setup(
    name            ='sportdaten',
    version         ='1.0.0',
    py_modules      =['sportdaten'],
    author          ='pashaf',
    author_email    ='pascalhaefliger@gmx.ch',
    url             ='None',
    description     ='Das ist das Modul sportdaten.py. Es beinhaltet die Funktionen säubern, spdaten_listen und die Klasse SportlerList. Es können Daten aus Textdateien mit dem Format: Name,Geb,[Zeiten] eingelesen und verarbeitet werden. WICHTIG: Pfad zu den Dateien mus mit os.chdir(...) angebegen werden.',
    )
