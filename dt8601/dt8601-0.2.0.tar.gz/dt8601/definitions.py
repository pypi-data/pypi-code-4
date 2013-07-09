# -*- coding: utf-8 -*-
__author__ = 'armin'

DAYS_IN_MONTH = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MIN_YEAR = 1900
MAX_YEAR = 2222
VALID_TIMEZONES = ['−12:00', '−11:00', '−10:00', '−09:30', '−09:00', '−08:00', '−07:00',
                   '−06:00', '−05:00', '−04:30', '−04:00', '−03:30', '−03:00', '−02:00',
                   '−01:00', '±00:00', '+01:00', '+02:00', '+03:00', '+03:30', '+04:00',
                   '+04:30', '+05:00', '+05:30', '+05:45', '+06:00', '+06:30', '+07:00',
                   '+08:00', '+08:45', '+09:00', '+09:30', '+10:00', '+10:30', '+11:00',
                   '+11:30', '+12:00', '+12:45', '+13:00', '+14:00']

'''

== States for Germany ==

BW -> Baden-Württemberg
BY -> Bayern
BE -> Berlin
BB -> Brandenburg
HB -> Bremen
HH -> Hamburg
HE -> Hessen
MV -> Mecklenburg-Vorpommern
NI -> Niedersachsen
NW -> Nordrhein-Westfalen
RP -> Rheinland-Pfalz
SL -> Saarland
SN -> Sachsen
ST -> Sachsen-Anhalt
SH -> Schleswig-Holstein
TH -> Thüringen


== States for Austria ==

BL -> Burgenland
K  -> Kärnten
NÖ -> Niederösterreich
OÖ -> Oberösterreich
S  -> Salzburg
ST -> Steiermark
T  -> Tirol
V  -> Vorarlberg
W  -> Wien


== States for Italy ==

AB -> Abruzzo
VA -> Valle d’Aosta/Val d’Aoste
PU -> Puglia
BA -> Basilicata
ER -> Emilia-Romagn
FV -> Friuli-Venezia Giulia
CL -> Calabria
CA -> Campania
LZ -> Lazio
LI -> Liguria
LO -> Lombardia
MA -> Marche
MO -> Molise
PI -> Piemonte
SA -> Sardegna
SI -> Sicilia
TO -> Toscana
TA -> Trentino-Alto Adige
UM -> Umbria
VE -> Veneto


== States for U.S.A. ==

AL -> Alabama
AK -> Alaska
AZ -> Arizona
AR -> Arkansas
CA -> Kalifornien
CO -> Colorado
CT -> Connecticut
DE -> Delaware
DC -> District of Columbia
FL -> Florida
GA -> Georgia
HI -> Hawaii
ID -> Idaho
IL -> Illinois
IN -> Indiana
IA -> Iowa
KS -> Kansas
KY -> Kentucky
LA -> Louisiana
ME -> Maine
MD -> Maryland
MA -> Massachusetts
MI -> Michigan
MN -> Minnesota
MS -> Mississippi
MO -> Missouri
MT -> Montana
NE -> Nebraska
NV -> Nevada
NH -> New Hampshire
NJ -> New Jersey
NM -> New Mexico
NY -> New York
NC -> North Carolina
ND -> North Dakota
OH -> Ohio
OK -> Oklahoma
OR -> Oregon
PA -> Pennsylvania
RI -> Rhode Island
SC -> South Carolina
SD -> South Dakota
TN -> Tennessee
TX -> Texas
UT -> Utah
VT -> Vermont
VA -> Virginia
WA -> Washington
WV -> West Virginia
WI -> Wisconsin
WY -> Wyoming


'''

COUNTRYDATA = {
    'DE': {
        'weekend': ['SA', 'SU'],
        'start_of_week': 'MO',
        'first_week': 'ISO',
        'long_day_names': {'MO':'Montag', 'TU':'Dienstag', 'WE':'Mittwoch', 'TH':'Donnerstag',
                           'FR':'Freitag', 'SA':'Samstag', 'SU':'Sonntag'},
        'short_day_names': {'MO':'MO', 'TU':'DI', 'WE':'MI', 'TH':'DO', 'FR':'FR', 'SA':'SA', 'SU':'SO'},
        'long_month_names': ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                             'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
        'short_month_names': ['', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'holidays': [ {'name': 'Neujahrstag', 'date': 'F:01-01::'},
                    {'name': 'H. drei Könige', 'date': 'F:01-06::', 'states': ['BW', 'BY', 'ST']},
                    {'name': 'Karfreitag', 'date': 'V:easter:-2::'},
                    {'name': 'Ostersonntag', 'date': 'V:easter:::'},
                    {'name': 'Ostermontag', 'date': 'V:easter:+1::'},
                    {'name': 'Tag der Arbeit', 'date': 'F:05-01::'},
                    {'name': 'Christi Himmelfahrt', 'date': 'V:easter:+39::'},
                    {'name': 'Pfingstsonntag', 'date': 'V:easter:+49::'},
                    {'name': 'Pfingstmontag', 'date': 'V:easter:+50::'},
                    {'name': 'Fronleichnam', 'date': 'V:easter:+60::', 'states': ['BW', 'BY', 'HE', 'NW', 'RP', 'SL']},
                    {'name': 'Maria Himmelfahrt', 'states': ['BY'], 'date': 'F:08-15::'},
                    {'name': 'Tag der deutschen Einheit', 'date': 'F:10-03::'},
                    {'name': 'Reformationstag', 'states': ['BB', 'SN', 'MV', 'ST', 'TH'], 'date': 'F:10-31::'},
                    {'name': 'Allerheiligen', 'date': 'F:11-01::', 'states': ['BW', 'BY', 'NW', 'RP', 'SL']},
                    {'name': 'Buß- und Bettag', 'date': 'V:advent:-WE::1995-', 'states': ['SN']},
                    {'name': 'Buß- und Bettag', 'date': 'V:advent:-WE::-1994'},
                    {'name': '1. Weihnachtstag', 'date': 'F:12-25::'},
                    {'name': '2. Weihnachtstag', 'date': 'F:12-26::'},
                    ],
    },
    'IT': {
        'weekend': ['SA', 'SU'],
        'start_of_week': 'MO',
        'first_week': 'ISO',
        'long_day_names': {'MO':'Lunedi', 'TU':'Martedi', 'WE':'Mercoledi', 'TH':'Giovedi',
                           'FR':'Vrenerdi', 'SA':'Sabado', 'SU':'Domenica'},
        'short_day_names': {'MO':'LU', 'TU':'MA', 'WE':'ME', 'TH':'GI', 'FR':'VR', 'SA':'SA', 'SU':'DO'},
        'long_month_names': ['', 'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                             'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
        'short_month_names': ['', 'Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
        'holidays': [ {'name': 'Capodanno', 'date': 'F:01-01::'},
                    {'name': 'Epifania', 'date': 'F:01-06::'},
                    {'name': 'Pasqua', 'date': 'V:easter:::'},
                    {'name': 'Pasquetta', 'date': 'V:easter:+1::'},
                    {'name': 'Anniversario della Liberazione', 'date': 'F:04-25::'},
                    {'name': 'Festa del Lavoro', 'date': 'F:05-01::'},
                    {'name': 'Lunedi di Pentecoste', 'date': 'V:easter:E+50::', 'states': ['TA']},
                    {'name': 'Festa della Repubblica', 'date': 'F:06-02::'},
                    {'name': 'Ferragosto', 'date': 'F:08-15::'},
                    {'name': 'Tutti i Santi', 'date': 'F:11-01::'},
                    {'name': 'Immacolata Concezione', 'date': 'F:12-08::'},
                    {'name': 'Natale', 'date': 'F:12-25::'},
                    {'name': 'Santo Stefano', 'date': 'F:12-26::'},
                    ]
    },
    'AT': {
        'weekend': ['SA', 'SU'],
        'start_of_week': 'MO',
        'first_week': 'ISO',
        'long_day_names': {'MO':'Montag', 'TU':'Dienstag', 'WE':'Mittwoch', 'TH':'Donnerstag',
                           'FR':'Freitag', 'SA':'Samstag', 'SU':'Sonntag'},
        'short_day_names': {'MO':'MO', 'TU':'DI', 'WE':'MI', 'TH':'DO', 'FR':'FR', 'SA':'SA', 'SU':'SO'},
        'long_month_names': ['', 'Jänner', 'Februar', 'März', 'April', 'Mai', 'Juni',
                             'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
        'short_month_names': ['', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'holidays': [
                    {'name': 'Neujahrstag', 'date': 'F:01-01::'},
                    {'name': 'H. drei Könige', 'date': 'F:01-06::'},
                    {'name': 'Josef', 'date': 'F:03-19::', 'states': ['K', 'ST', 'T', 'V']},
                    {'name': 'Karfreitag', 'date': 'V:easter:-2::'},
                    {'name': 'Ostersonntag', 'date': 'V:easter:::'},
                    {'name': 'Ostermontag', 'date': 'V:easter:+1::'},
                    {'name': 'Staatsfeiertag', 'date': 'F:05-01::'},
                    {'name': 'Christi Himmelfahrt', 'date': 'V:easter:+39::'},
                    {'name': 'Pfingstmontag', 'date': 'V:easter:+50::'},
                    {'name': 'Fronleichnam', 'date': 'V:easter:+60::'},
                    {'name': 'Maria Himmelfahrt', 'date': 'F:08-15::'},
                    {'name': 'Nationalfeiertag', 'date': 'F:10-26::'},
                    {'name': 'Allerheiligen', 'date': 'F:11-01::'},
                    {'name': 'Maria Empfängnis', 'date': 'F:12-08::'},
                    {'name': 'Christtag', 'date': 'F:12-25::'},
                    {'name': 'Stefanitag', 'date': 'F:12-26::'},
                    ]
    },
    # TODO: have a look at http://www.timeanddate.com/holidays/us/
    'US': {
        'weekend': ['SA', 'SU'],
        'start_of_week': 'SU',
        'first_week': 'JAN1',
        'long_day_names': {'MO':'Monday', 'TU':'Tuesday', 'WE':'Wednesday', 'TH':'Thursday',
                           'FR':'Friday', 'SA':'Saturday', 'SU':'Sunday'},
        'short_day_names': {'MO':'MO', 'TU':'TU', 'WE':'WE', 'TH':'TH', 'FR':'FR', 'SA':'SA', 'SU':'SU'},
        'long_month_names': ['', 'January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December'],
        'short_month_names': ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'holidays': [
                    {'name': "New Year's Day", 'date': 'F:01-01:SA-FR,SU+MO:'},
                    {'name': 'Martin Luther King Day', 'date': 'V:jan:+MO+MO+MO::'},
                    {'name': "Washington's Birthday", 'date': 'V:feb:+MO+MO+MO::'},
                    {'name': 'Memorial Day', 'date': 'V:jun:-1-MO::'},
                    {'name': 'Independence Day', 'date': 'F:07-04:SA-FR,SU+MO:'},
                    {'name': 'Labor Day', 'date': 'V:sep:+MO::'},
                    {'name': 'Columbus Day', 'date': 'V:oct:+MO+MO::'},
                    {'name': "Veterans Day", 'date': 'F:11-11:SA-FR,SU+MO:'},
                    {'name': 'Thanksgiving', 'date': 'V:nov:+TH+TH+TH+TH:SA-FR,SU+MO:'},
                    {'name': 'Christmas Day', 'date': 'F:12-25:SA-FR,SU+MO:'},
                    {'name': 'Lee Jackson Day', 'date': 'V:jan:+MO+MO+FR::', 'states': ['VA']},
                    {'name': "Robert E. Lee's Birthday", 'date': 'V:jan:+MO+MO+MO::', 'states': ['AL', 'AR', 'GA', 'MS']},
                    {'name': "Robert E. Lee's Birthday", 'date': 'V:jan:+MO+MO+SA::', 'states': ['FL']},
                    ]
    }
}

