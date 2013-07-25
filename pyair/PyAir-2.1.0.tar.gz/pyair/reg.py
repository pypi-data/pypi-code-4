#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unicodedata
import scipy.stats as stats
import pandas as pd
import pandas.tseries.offsets as pdoffset
from StringIO import StringIO


class FreqException(Exception):
    def __init__(self, err):
        self.err = "Erreur de fréquence : %s" % err

    def __str__(self):
        return self.err



def moyennes_glissantes(df, sur=8, rep=0.75):
    """
    Calcule de moyennes glissantes

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    sur: (int, par défaut 8) Nombre d'observations sur lequel s'appuiera le
    calcul
    rep: (float, défaut 0.75) Taux de réprésentativité en dessous duquel le
    calcul renverra NaN

    Retourne:
    Un DataFrame des moyennes glissantes calculées
    """
    return pd.rolling_mean(df, window=sur, min_periods=rep*sur)


def consecutive(df, valeur, sur=3):
    """Calcule si une valeur est dépassée durant une période donnée. Détecte
    un dépassement de valeur sur X heures/jours/... consécutifs

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    valeur: (float) valeur à chercher le dépassement (strictement supérieur à)
    sur: (int) Nombre d'observations consécutives où la valeur doit être dépassée

    Retourne:
    Un DataFrame de valeurs, de même taille (shape) que le df d'entrée, dont toutes
    les valeurs sont supprimées, sauf celles supérieures à la valeur de référence
    et positionnées sur les heures de début de dépassements

    """
    #min_ = pd.rolling_min(df, window=sur)
    #dep = min_[min_>valeur]
    dep = pd.rolling_max(df.where(df>valeur), window=sur, min_periods=sur)
    return dep


def depassement(df, valeur):
    """
    Calcule les dépassements d'une valeur.

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    valeur: (float) valeur à chercher le dépassement (strictement supérieur à)

    Retourne:
    Un DataFrame de valeurs, de même taille (shape) que le df d'entrée, dont toutes
    les valeurs sont supprimées, sauf celles supérieures à la valeur de référence
    """

    dep = df.where(df>valeur)
    return dep


def nombre_depassement(df, valeur, freq=None):
    """
    Calcule le nombre de dépassement d'une valeur sur l'intégralité du temps,
    ou suivant un regroupement temporel.

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    valeur: (float) valeur à chercher le dépassement (strictement supérieur à)
    freq: (str ou None): Fréquence de temps sur lequel effectué un regroupement.
    freq peut prendre les valeurs 'H' pour heure, 'D' pour jour, 'W' pour semaine,
    'M' pour mois et 'A' pour année, ou None pour ne pas faire de regroupement.
    Le nombre de dépassement sera alors regroupé suivant cette fréquence de temps.

    Retourne:
    Une Series du nombre de dépassement, total suivant la fréquence intrinsèque
    du DataFrame d'entrée, ou aggloméré suivant la fréquence de temps choisie.
    """

    dep = depassement(df, valeur)
    if freq is not None:
        dep = dep.resample(freq, how='sum')
    return dep.count()


def aot40_vegetation(df, nb_an):
    """
    Calcul de l'AOT40 du 1er mai au 31 juillet

    *AOT40 : AOT 40 ( exprimé en micro g/m³ par heure ) signifie la somme des
    différences entre les concentrations horaires supérieures à 40 parties par
    milliard ( 40 ppb soit 80 micro g/m³ ), durant une période donnée en
    utilisant uniquement les valeurs sur 1 heure mesurées quotidiennement
    entre 8 heures (début de la mesure) et 20 heures (pile, fin de la mesure) CET,
    ce qui correspond à de 8h à 19h TU (donnant bien 12h de mesures, 8h donnant
    la moyenne horaire de 7h01 à 8h00)

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    nb_an: (int) Nombre d'années contenu dans le df, et servant à diviser le
    résultat retourné

    Retourne:
    Un DataFrame de résultat de calcul
    """

    return _aot(df.tshift(1), nb_an=nb_an, limite=80, mois_debut=5, mois_fin=7,
                  heure_debut=8, heure_fin=19)


def aot40_foret(df, nb_an):
    """
    Calcul de l'AOT40 du 1er avril au 30 septembre

    *AOT40 : AOT 40 ( exprimé en micro g/m³ par heure ) signifie la somme des
    différences entre les concentrations horaires supérieures à 40 parties par
    milliard ( 40 ppb soit 80 micro g/m³ ), durant une période donnée en
    utilisant uniquement les valeurs sur 1 heure mesurées quotidiennement
    entre 8 heures et 20 heures (CET) <==> 7h à 19h TU

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    nb_an: (int) Nombre d'années contenu dans le df, et servant à diviser le
    résultat retourné

    Retourne:
    Un DataFrame de résultat de calcul
    """
    return _aot(df.tshift(1), nb_an=nb_an, limite=80, mois_debut=4, mois_fin=9,
                  heure_debut=8, heure_fin=19)


def _aot(df, nb_an=1, limite=80, mois_debut=5, mois_fin=7,
           heure_debut=7, heure_fin=19):
    """
    Calcul de l'AOT de manière paramètrable. Voir AOT40_vegetation ou
    AOT40_foret pour des paramètres préalablement fixés.

    Paramètres:
    df: DataFrame de mesures sur lequel appliqué le calcul
    nb_an: (int) Nombre d'années contenu dans le df, et servant à diviser le
    résultat retourné
    limite: (float) valeur limite au delà de laquelle les différences seront
        additionnées pour calculer l'AOT
    mois_debut: (int) mois de début de calcul
    mois_fin: (int) mois de fin de calcul
    heure_debut: (int) première heure de chaque jour après laquelle les valeurs
        sont retenues
    heure_fin: (int) dernière heure de chaque jour avant laquelle les valeurs
        sont retenues

    Retourne:
    Un DataFrame de résultat de calcul
    """

    res = df[(df.index.month >= mois_debut) & (df.index.month <= mois_fin) &
            (df.index.hour >= heure_debut) & (df.index.hour <= heure_fin)]
    nb_valid = res.count()
    nb_total = res.shape[0]
    pcent = nb_valid.astype(pd.np.float) / nb_total * 100
    brut = (res[res>limite] - limite) / nb_an
    brut = brut.sum()
    net = brut / nb_valid * nb_total
    print("""{total} mesures au totales
    du {m_d} au {m_f}
    entre {h_d} et {h_f}""".format(total=nb_total,
                                   m_d=mois_debut, m_f=mois_fin,
                                   h_d=heure_debut, h_f=heure_fin
                                   )
        )
    aot = pd.DataFrame([brut.round(), nb_valid.round(), pcent.round(), net.round()],
                       index=['brutes', 'mesures valides', '% de rep.', 'nettes'])
    return aot


def compresse(df):
    """
    Compresse un DataFrame en supprimant les lignes dont toutes les Valeurs
    (colonnes) sont vides. Si au moins une valeur est présente sur la ligne, alors
    elle est conservée.

    Paramètres:
    df: DataFrame a présenter

    Retourne:
    Un DataFrame réduit à son strict minimum"""
    return df.dropna(how='all')


def no2(df):
    """
    Calculs réglementaires pour le dioxyde d'azote

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Seuil de RI en moyenne H: 200u
    Seuil d'Alerte sur 3H consécutives: 400u
    Seuil d'Alerte sur 3J consécutifs: 200u
    Valeur limite pour la santé humaine 18H/A: 200u
    Valeur limite pour la santé humaine en moyenne A: 40u
    Objectif de qualité en moyenne A: 40u
    Protection de la végétation en moyenne A: 30u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = "NO2"

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Seuil de RI en moyenne H: 200u": depassement(df, valeur=200),
           u"Seuil d'Alerte sur 3H consécutives: 400u": consecutive(df, valeur=400, sur=3),
           u"Seuil d'Alerte sur 3J consécutifs: 200u": consecutive(df.resample('D', how='max'), valeur=200, sur=3),
           u"Valeur limite pour la santé humaine 18H/A: 200u": depassement(df, valeur=200),
           u"Valeur limite pour la santé humaine en moyenne A: 40u": depassement(df.resample('A', how='mean'), valeur=40),
           u"Objectif de qualité en moyenne A: 40u": depassement(df.resample('A', how='mean'), valeur=40),
           u"Protection de la végétation en moyenne A: 30u": depassement(df.resample('A', how='mean'), valeur=30),
           }

    return polluant, res


def pm10(df):
    """
    Calculs réglementaires pour les particules PM10

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Seuil de RI en moyenne J: 50u
    Seuil d'Alerte en moyenne J: 80u
    Valeur limite pour la santé humaine 35J/A: 50u
    Valeur limite pour la santé humaine en moyenne A: 40u
    Objectif de qualité en moyenne A: 30u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'PM10'
    #Le DataFrame doit être en jour
    if not isinstance(df.index.freq, pdoffset.Day):
        raise FreqException("df doit être en jour.")

    res = {u"Seuil de RI en moyenne J: 50u": depassement(df, valeur=50),
           u"Seuil d'Alerte en moyenne J: 80u": depassement(df, valeur=80),
           u"Valeur limite pour la santé humaine 35J/A: 50u": depassement(df, valeur=50),
           u"Valeur limite pour la santé humaine en moyenne A: 40u": depassement(df.resample('A', how='mean'), valeur=40),
           u"Objectif de qualité en moyenne A: 30u": depassement(df.resample('A', how='mean'), valeur=30),
           }

    return polluant, res


def so2(df):
    """
    Calculs réglementaires pour le dioxyde de soufre

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Seuil de RI en moyenne H: 300u
    Seuil d'Alerte sur 3H consécutives: 500u
    Valeur limite pour la santé humaine 24H/A: 350u
    Valeur limite pour la santé humaine 3J/A: 125u
    Objectif de qualité en moyenne A: 50u
    Protection de la végétation en moyenne A: 20u
    Protection de la végétation du 01/10 au 31/03: 20u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'SO2'

    #Le DataFrame doit être en jour
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Seuil de RI en moyenne H: 300u": depassement(df, valeur=300),
           u"Seuil d'Alerte sur 3H consécutives: 500u": depassement(df, valeur=500),
           u"Valeur limite pour la santé humaine 24H/A: 350u": depassement(df, valeur=350),
           u"Valeur limite pour la santé humaine 3J/A: 125u": depassement(df.resample('D', how='mean'), valeur=125),
           u"Objectif de qualité en moyenne A: 50u": depassement(df.resample('A', how='mean'), valeur=50),
           u"Protection de la végétation en moyenne A: 20u": depassement(df.resample('A', how='mean'), valeur=20),
           u"Protection de la végétation du 01/10 au 31/03: 20u": depassement(df[(df.index.month<=3) | (df.index.month>=10)], valeur=20),
           }

    return polluant, res


def co(df):
    """
    Calculs réglementaires pour le monoxyde de carbone

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Valeur limite pour la santé humaine max J 8H glissantes: 10000u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'CO'

    #Le DataFrame doit être en jour
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Valeur limite pour la santé humaine sur 8H glissantes: 10000u": depassement(moyennes_glissantes(df, sur=8), valeur=10),
           }

    return polluant, res


def o3(df):
    """
    Calculs réglementaires pour l'ozone

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Seuil de RI sur 1H: 180u
    Seuil d'Alerte sur 1H: 240u
    Seuil d'Alerte sur 3H consécutives: 240u
    Seuil d'Alerte sur 3H consécutives: 300u
    Seuil d'Alerte sur 1H: 360u
    Objectif de qualité pour la santé humaine sur 8H glissantes: 120u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'O3'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Seuil de RI sur 1H: 180u": depassement(df, valeur=180),
           u"Seuil d'Alerte sur 1H: 240u": depassement(df, valeur=240),
           u"Seuil d'Alerte sur 1H: 360u": depassement(df, valeur=360),
           u"Seuil d'Alerte sur 3H consécutives: 240u": consecutive(df, valeur=240, sur=3),
           u"Seuil d'Alerte sur 3H consécutives: 300u": consecutive(df, valeur=300, sur=3),
           u"Objectif de qualité pour la santé humaine sur 8H glissantes: 120u": depassement(moyennes_glissantes(df, sur=8), valeur=120),
           }

    return polluant, res



def c6h6(df):
    """
    Calculs réglementaires pour le benzène

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Objectif de qualité en moyenne A: 2u
    Valeur limite pour la santé humaine en moyenne A: 5u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'C6H6'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Objectif de qualité en moyenne A: 2u": depassement(df.resample('A', how='mean'), valeur=2),
           u"Valeur limite pour la santé humaine en moyenne A: 5u": depassement(df.resample('A', how='mean'), valeur=5),
           }

    return polluant, res


def pb(df):
    """
    Calculs réglementaires pour le plomb

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): µg/m3 (microgramme par mètre cube)

    Objectif de qualité en moyenne A: 0.25u
    Valeur limite pour la santé humaine en moyenne A: 0.5u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'Pb'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Objectif de qualité en moyenne A: 0.25u": depassement(df.resample('A', how='mean'), valeur=0.25),
           u"Valeur limite pour la santé humaine en moyenne A: 0.5u": depassement(df.resample('A', how='mean'), valeur=0.5),
           }

    return polluant, res


def arsenic(df):
    """
    Calculs réglementaires pour l'arsenic

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): ng/m3 (nanogramme par mètre cube)

    Valeur cible en moyenne A: 6u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'As'
    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Valeur cible en moyenne A: 6u": depassement(df.resample('A', how='mean'), valeur=6),
           }

    return polluant, res


def cadmium(df):
    """
    Calculs réglementaires pour le cadmium

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): ng/m3 (nanogramme par mètre cube)

    Valeur cible en moyenne A: 5u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'Cd'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Valeur cible en moyenne A: 5u": depassement(df.resample('A', how='mean'), valeur=5),
           }

    return polluant, res


def nickel(df):
    """
    Calculs réglementaires pour le nickel

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): ng/m3 (nanogramme par mètre cube)

    Valeur cible en moyenne A: 20u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'Ni'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Valeur cible en moyenne A: 20u": depassement(df.resample('A', how='mean'), valeur=20),
           }

    return polluant, res


def bap(df):
    """
    Calculs réglementaires pour le benzo(a)pyrène

    Paramètres:
    df: DataFrame contenant les mesures, avec un index temporel
    (voir xair.get_mesure)

    Retourne:
    Une série de résultats dans un DataFrame :
    ******
    unité (u): ng/m3 (nanogramme par mètre cube)

    Valeur cible en moyenne A: 1u

    Les résultats sont donnés en terme d'heure de dépassement

    """

    polluant = 'BaP'

    #Le DataFrame doit être en heure
    if not isinstance(df.index.freq, pdoffset.Hour):
        raise FreqException("df doit être en heure.")

    res = {u"Valeur cible en moyenne A: 1u": depassement(df.resample('A', how='mean'), valeur=1),
           }

    return polluant, res


def print_synthese(fct, df):
    """
    Présente une synthèse des calculs réglementaires en fournissant les valeurs
    calculées suivant les réglementations définies dans chaque fonction de calcul
    et un tableau de nombre de dépassement.

    Paramètres:
    fct: fonction renvoyant les éléments calculées
    df: DataFrame de valeurs d'entrée à fournir à la fonction

    Retourne:
    Imprime sur l'écran les valeurs synthétisées

    """

    res_count = dict()

    polluant, res = fct(df)
    print(u"\nPour le polluant: %s" % polluant)

    print(u"\nValeurs mesurées suivant critères:")
    for k, v in res.iteritems():
        comp = compresse(v)
        if not comp.empty:
            comp.index.name = k
            print(comp.to_string(na_rep='', float_format=lambda x:"%.0f"%x))
        else:
            print(u"\n%s: aucune valeur en dépassement" % k)
        res_count[k] = v.count()

    res_count = pd.DataFrame(res_count).T
    print(u"Nombre de dépassements des critères:\n")
    print(res_count)


def excel_synthese(fct, df, excel_file):
    """
    Enregistre dans un fichier Excel une synthèse des calculs réglementaires en
    fournissant les valeurs calculées suivant les réglementations définies dans
    chaque fonction de calcul et un tableau de nombre de dépassement.
    Les résultats sont enregistrés

    Paramètres:
    fct: fonction renvoyant les éléments calculées
    df: DataFrame de valeurs d'entrée à fournir à la fonction
    excel_file: Chemin du fichier excel où écrire les valeurs

    Retourne:
    Rien

    """

    def sheet_name(name):
        #formatage du nom des feuilles (suppression des guillements, :, ...)
        name = unicodedata.normalize('NFKD', name).encode('ascii','ignore')
        name = k.replace("'", "").replace(":", "").replace(" ", "_")
        name = "%i-%s" % (i, name)
        name = name[:31]
        return name

    res_count = dict()

    polluant, res = fct(df)
    print(u"\nTraitement du polluant: %s" % polluant)

    writer = pd.ExcelWriter(excel_file)

    #Valeurs mesurées suivant critères
    for i, (k, v) in enumerate(res.iteritems()):
        comp = compresse(v)
        comp.index.name = k
        comp = comp.apply(pd.np.round)
        comp.to_excel(writer, sheet_name=sheet_name(k))
        res_count[k] = v.count()

    #Nombre de dépassements des critères
    name = u"Nombre_de_depassements"
    res_count = pd.DataFrame(res_count).T
    res_count.index.name = name
    res_count.to_excel(writer, sheet_name=name)

    writer.save()


def html_synthese(fct, df):
    """
    Retourne au format html une synthèse des calculs réglementaires en
    fournissant les valeurs calculées suivant les réglementations définies dans
    chaque fonction de calcul et un tableau de nombre de dépassement.

    Paramètres:
    fct: fonction renvoyant les éléments calculées
    df: DataFrame de valeurs d'entrée à fournir à la fonction

    Retourne:
    Une chaine de caractère prête à être utilisé dans une page html

    """

    html = str()
    res_count = dict()
    buf = StringIO()
    polluant, res = fct(df)
    html += '<p style="text-align:center"><h2>Pour le polluant: {}</h2></p>'.format(polluant)

    #On enregistre tous les résultats dans le buffer et on calcule la somme de chaque
    for k, v in res.iteritems():
        buf.write("<p>")
        comp = compresse(v)
        if not comp.empty:
            comp.index.name = k
            comp.to_html(buf=buf,
                         float_format=lambda x:"%.1f"%x,
                         sparsify=True,
                         na_rep="")
        else:
            buf.write(u'<table border="1" class="dataframe"><thead><tr style="text-align: right;"><th>{}</th><th>Aucun dépassement</th></tr></table>'.format(k))
        buf.write("</p>")
        res_count[k] = v.count()

    res_count = pd.DataFrame(res_count).T
    res_count.index.name = u"Nombre de dépassements des critères"
    html += "<p>"
    html += res_count.to_html(sparsify=True)
    html += "</p>"

    html += buf.getvalue()

    return html