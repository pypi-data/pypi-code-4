#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
**Timeprocessing

Profils temporels (journalier, hebdomadaire, annuel)

Exemple d'utilisation
profil_hebdo(df, func='mean')
profil_journalier(df, func='max')
profil_annuel(df, func=numpy.std)

"""

import numpy as np
import calendar as cal
import pandas as pd


def _get_funky(func):
    """Renvoie une fonction numpy correspondant au nom passé en paramètre,
    sinon renvoie la fonction elle-même"""

    if isinstance(func, str):
        try:
            func = getattr(np, func)
        except:
            raise NameError, u"Nom de fonction non comprise"
    return func


def profil_journalier(df, func='mean'):
    """
    Calcul du profil journalier

    Paramètres:
    df: DataFrame de données dont l'index est une série temporelle
        (cf module xair par exemple)
    func: function permettant le calcul. Soit un nom de fonction numpy ('mean', 'max', ...)
        soit la fonction elle-même (np.mean, np.max, ...)
    Retourne:
    Un DataFrame de moyennes par heure sur une journée
    """

    func = _get_funky(func)
    res = df.groupby(lambda x: x.hour).aggregate(func)
    return res


def profil_hebdo(df, func='mean'):
    """
    Calcul du profil journalier

    Paramètres:
    df: DataFrame de données dont l'index est une série temporelle
        (cf module xair par exemple)
    func: function permettant le calcul. Soit un nom de fonction numpy ('mean', 'max', ...)
        soit la fonction elle-même (np.mean, np.max, ...)
    Retourne:
    Un DataFrame de moyennes par journée sur la semaine
    """

    func = _get_funky(func)
    res = df.groupby(lambda x: x.weekday).aggregate(func)
    #On met des noms de jour à la place des numéros dans l'index
    res.index = [cal.day_name[i] for i in range(0,7)]
    return res


def profil_annuel(df, func='mean'):
    """
    Calcul du profil annuel

    Paramètres:
    df: DataFrame de données dont l'index est une série temporelle
        (cf module xair par exemple)
    func: function permettant le calcul. Soit un nom de fonction numpy ('mean', 'max', ...)
        soit la fonction elle-même (np.mean, np.max, ...)
    Retourne:
    Un DataFrame de moyennes par mois
    """

    func = _get_funky(func)
    res = df.groupby(lambda x: x.month).aggregate(func)
    #On met des noms de mois à la place des numéros dans l'index
    res.index = [cal.month_name[i] for i in range(1,13)]
    return res


def strtime_help():
    """
    Print a help message on the time strptime format
    """

    print """
%a  Locale's abbreviated weekday name.
%A  Locale's full weekday name.
%b  Locale's abbreviated month name.
%B  Locale's full month name.
%c  Locale's appropriate date and time representativity.
%d  Day of the month as a decimal number [01,31].
%H  Hour (24-hour clock) as a decimal number [00,23].
%I  Hour (12-hour clock) as a decimal number [01,12].
%j  Day of the year as a decimal number [001,366].
%m  Month as a decimal number [01,12].
%M  Minute as a decimal number [00,59].
%p  Locale's equivalent of either AM or PM.  (1)
%S  Second as a decimal number [00,61].  (2)
%U  Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0.
%w  Weekday as a decimal number [0(Sunday),6].
%W  Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0.
%x  Locale's appropriate date representativity.
%X  Locale's appropriate time representativity.
%y  Year without century as a decimal number [00,99].
%Y  Year with century as a decimal number.
%Z  Time zone name (no characters if no time zone exists).
%%  A literal "%" character.
"""



