"""Das ist das Modul sportdaten.py. Es beinhaltet die Funktionen säubern, spdaten_listen
und die Klasse SportlerList. Es können Daten aus Textdateien mit dem Format: Name,Geb,[Zeiten]
eingelesen und verarbeitet werden.
WICHTIG: Pfad zu den Dateien mus mit os.chdir(...) angebegen werden."""

def säubern(zeit_string):
    """säubert die Zeitangaben und erstell ein einheitliches Format"""
    if '-' in zeit_string:
        trenner = '-'
    elif ':' in zeit_string:
        trenner=':'
    else:
        return(zeit_string)
    (mins,seks)=zeit_string.split(trenner)
    return(mins + '.' + seks)

def spdaten_listen(dateiname):
    """Liest Daten aus einer Textdatei und gibt einen SporlterList-Objekt zurück"""
    try:
        with open(dateiname) as d:
            daten =d.readline()
            first =daten.strip().split(',')
            Person=SportlerList(first.pop(0),first.pop(0),first)
            return(Person)
    except FileNotFoundError as ioerr:
        print('Dateifehler: ', ioerr)
        print('Überprüfen sie den Pfad oder Dateinamen')
        return (None)

class SportlerList(list):
    """Ein Objekt, das einen Namen, ein Geb.Datum und eine Liste von Zeiten speichert.
    hat die Funktionen von list in sich."""
    def __init__(self,ein_name,ein_geb=None,ein_zeiten=[]):
        list.__init__([])
        self.name=ein_name
        self.geb=ein_geb
        self.extend(ein_zeiten)

    def top3(self):
        return(sorted(set([säubern(t) for t in self]))[0:3])

