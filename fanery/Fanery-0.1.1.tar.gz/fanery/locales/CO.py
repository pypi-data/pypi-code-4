# -*- coding: utf-8 -*-

from dateutil import tz
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU

ISO2 = 'CO'
TZ = tz.gettz('America/Bogota')
WORKDAY = (MO, TU, WE, TH, FR)
WEEKEND = (SA, SU)

def holidays(year = None):
    # from https://es.wikipedia.org/wiki/Anexo:Días_feriados_en_Colombia
    from fanery.locales import easter, relativedelta as rd
    from dateutil.rrule import rrule, WEEKLY, MO
    from datetime import datetime as dt
    year = year or dt.today().year
    easter = easter(year)
    # first monday
    fm = rd(weekday = MO(+1))
    return (
            dt(year, 1, 1),         # Año Nuevo
            dt(year, 1, 6) + fm,    # Epifanía (Reyes Magos)
            dt(year, 3, 19) + fm,   # San José
            easter + rd(days = -7), # Domingo de Ramos
            easter + rd(days = -3), # Jueves Santo
            easter + rd(days = -2), # Viernes Santo
            easter,                 # Domingo de Pascua
            dt(year, 5, 1),         # Día del Trabajo
            easter + rd(days = 43), # Ascensión de Jesús
            easter + rd(days = 64), # Corpus Christi
            easter + rd(days = 71), # Sagrado Corazón de Jesús
            dt(year, 6, 29) + fm,   # san Pedro y san Pablo
            dt(year, 7, 20),        # Grito de Independencia
            dt(year, 8, 7),         # Batalla de Boyacá
            dt(year, 8, 15) + fm,   # Asunción de la Virgen
            dt(year, 10, 12) + fm,  # Día de la Raza
            dt(year, 11, 1) + fm,   # Todos los Santos
            dt(year, 11, 11) + fm,  # Independencia de Cartagena[
            dt(year, 12, 8),        # Inmaculada Concepción
            dt(year, 12, 25))       # Navidad
