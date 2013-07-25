#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
**Air Quality

Module de connexion et de récupération de données sur une base XAIR
"""

import cx_Oracle
import pandas as pd
import pandas.io.sql as psql
import datetime as dt


INVALID_CODES = ['C', 'D', 'I', 'M', 'Z', 'B', 'N', 'X', 'G', 'H']
MISSING_CODE = 'N'


def is_invalid(e):
    """Renvoie Vrai ou Faux suivant que e est dans la liste des codes invalides

    Paramètres:
    e: une lettre en majuscules
    """
    return e in INVALID_CODES


def etats_to_invalid(etats):
    """
    Transforme un dataframe de codes d'état en une grille d'invalidation.

    Paramètres:
    etats: dataframe de codes d'état, tel que retourné par get_mesure avec le
    paramètre brut=True

    Retourne:
    Un dataframe de booléen. Chaque valeur est soit à False, et la mesure
    correspondante (à la même position dans le dataframe de mesure) n'est pas
    invalide, soit à True et la mesure est invalide.
    """
    return etats.applymap(is_invalid)


def to_date(date, dayfirst=False, format=None):
    """
    Transforme un champ date vers un objet python datetime
    Paramètres:
    date:
        - si None, renvoie la date du jour
        - si de type str, renvoie un objet python datetime
        - si de type datetime, le retourne sans modification
    dayfirst: Si True, aide l'analyse du champ date de type str en informant
    le décrypteur que le jour se situe en début de chaîne (ex:11/09/2012
    pourrait être interpreté comme le 09 novembre si dayfirst=False)
    format: chaîne de caractère décrivant précisement le champ date de type
    str. Voir la documentation officielle de python.datetime pour description

    """
    ## TODO: voir si pd.tseries.api ne peut pas remplacer tout ca
    if not date:
        return dt.datetime.fromordinal(dt.date.today().toordinal())  #mieux que dt.datetime.now() car ca met les heures, minutes et secondes à zéro
    elif isinstance(date, dt.datetime):
        return date
    elif isinstance(date, str):
        return pd.to_datetime(date, dayfirst=dayfirst, format=format)
    else:
        raise ValueError, "Les dates doivent être de type None, str ou datetime"


def _format(noms):
    """
    Formate une donnée d'entrée pour être exploitable dans les fonctions liste_*
    et get_*.

    Paramètres:
    noms: chaîne de caractère, liste ou tuples de chaînes de caractères ou
    pandas.Series de chaînes de caractères.

    Retourne:
    Une chaînes de caractères dont chaque élément est séparé du suivant par les
    caractères ',' (simples quotes comprises)

    """
    if isinstance(noms, (list, tuple, pd.Series)):
        noms = ','.join(noms)
    noms = noms.replace(",", "','")
    return noms


def date_range(debut, fin, freq):
    """
    Génère une liste de date en tenant compte des heures de début et fin d'une journée.
    La date de début sera toujours calée à 0h, et celle de fin à 23h

    Paramètres:
    debut: datetime représentant la date de début
    fin: datetime représentant la date de fin
    freq: freq de temps. Valeurs possibles : T (minute), H (heure), D (jour),
    M (mois), Y (année). Peux prendre des cycles, comme 15T pour 15 minutes

    """

    debut_dt = debut.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dt = fin.replace(hour=23, minute=59, second=0, microsecond=0)
    if freq in ('M', 'A'):  #Calle la fréquence sur le début de mois/année
        freq += 'S'
        debut_dt = debut_dt.replace(day=1, minute=0, second=0, microsecond=0)
        fin_dt = fin_dt.replace(day=1, minute=0, second=0, microsecond=0)
    dates_completes = pd.date_range(start=debut_dt, end=fin_dt, freq=freq)
    return dates_completes


class XAIR:
    """Connexion et méthodes de récupération de données depuis une base XAIR.
    Usage :
    import pyair
    xr=pyair.xair.XAIR(user, pwd, adr, port=1521, base='N')
    xr.liste_stations()
    mes=xr.liste_mesures(reseau='OZONE').MESURES
    m=xr.get_mesure(mes=mes, debut="2009-01-01", fin="2009-12-31", freq='H')
    m.describe()
    """


    def __init__(self, user, pwd, adr, port=1521, base='N'):
        self._ORA_FULL = "{0}/{1}@{2}:{3}/{4}".format(user, pwd, adr, port, base)
        self._connect()


    def _connect(self):
        """
        Connexion à la base XAIR
        """

        try:
            #On passe par Oracle Instant Client avec le TNS ORA_FULL
            self.conn = cx_Oracle.connect( self._ORA_FULL )
            self.cursor = self.conn.cursor()
            print('XAIR: Connexion établie')
        except cx_Oracle.Error, e:
            print "Erreur: %s" % (e)
            raise cx_Oracle.Error, 'Echec de connexion'


    def reconnect(self):
        self._connect()


    def disconnect(self):
        """
        Fermeture de la connexion à la base
        """
        self._close()


    def _close( self ):
        self.cursor.close()
        self.conn.close()
        print('XAIR: Connexion fermée')


    def liste_parametres(self, parametre=None):
        """
        Liste des paramètres

        Paramètres:
        parametre: si fourni, retourne l'entrée pour ce parametre uniquement

        """
        condition = ""
        if parametre:
            condition = "WHERE CCHIM='%s'" %parametre
        _sql = """SELECT CCHIM AS PARAMETRE,
        NCON AS LIBELLE,
        NOPOL AS CODE
        FROM NOM_MESURE %s ORDER BY CCHIM""" %condition
        return psql.read_frame(_sql, self.conn)


    def liste_mesures(self, reseau=None, station=None, parametre=None, mesure=None):
        """
        Décrit les mesures:
        - d'un ou des reseaux,
        - d'une ou des stations,
        - d'un ou des parametres
        ou décrit une (des) mesures suivant son (leur) identifiant(s)
        Chaque attribut peut être étendu en rajoutant des noms séparés par des
        virgules ou en les mettant dans une liste/tuple/pandas.Series.
        Ainsi pour avoir la liste des mesures en vitesse et direction de vent:
        parametre="VV,DV" ou = ["VV", "DV"]

        Paramètres:
        reseau : nom du reseau dans lequel lister les mesures
        station: nom de la station où lister les mesures
        parametre: Code chimique du parametre à lister
        mesure: nom de la mesure à décrire

        """

        condition = ""

        if reseau:
            reseau = _format(reseau)
            condition = """INNER JOIN RESEAUMES USING (NOM_COURT_MES)
            WHERE NOM_COURT_RES IN ('%s') """ %reseau

        if parametre:
            parametre = _format(parametre)
            condition = """WHERE CCHIM IN ('%s')"""% parametre

        if station :
            station = _format(station)
            condition = "WHERE NOM_COURT_SIT IN ('%s')" %station

        if mesure:
            mesure = _format(mesure)
            condition = "WHERE IDENTIFIANT IN ('%s')" %mesure

        _sql = """SELECT IDENTIFIANT AS MESURE,
        NOM_MES AS LIBELLE,
        UNITE AS UNITE,
        NOM_COURT_SIT AS STATION,
        CCHIM AS CODE_PARAM,
        NCON AS PARAMETRE
        FROM MESURE INNER JOIN NOM_MESURE USING (NOPOL) %s ORDER BY IDENTIFIANT""" %condition

        return psql.read_frame(_sql, self.conn)


    def detail_df(self, df):
        """
        Renvoie les caractéristiques des mesures d'un dataframe.

        Paramètres:
        df: dataframe à lister, tel que fournie par get_mesure()

        Retourne:
        Les mêmes informations que liste_mesure()
        """
        return self.liste_mesures(mesure=df.columns.tolist())


    def liste_stations(self, station=None, detail=False):
        """
        Liste des stations

        Paramètres:
        station : un nom de station valide (si vide, liste toutes les stations)
        detail : si True, affiche plus de détail sur la (les) station(s).

        """
        condition = ""
        if station:
            station = _format(station)
            condition = "WHERE NOM_COURT_SIT IN ('%s')" %station

        select = ""
        if detail:
            select = """,
            NO_TELEPHONE AS TELEPHONE,
            ADRESSE_IP,
            LONGI AS LONGITUDE,
            LATI AS LATITUDE,
            ALTI AS ALTITUDE,
            AXE AS ADR,
            CODE_POSTAL AS CP,
            FLAG_VALID AS VALID"""

        _sql = """SELECT
        NSIT AS NUMERO,
        NOM_COURT_SIT AS STATION,
        ISIT AS LIBELLE%s
        FROM STATION
        %s
        ORDER BY NSIT"""% (select, condition)
        return psql.read_frame(_sql, self.conn)


    def liste_reseaux(self):
        """Liste des sous-réseaux de mesure"""

        _sql = """SELECT
        NOM_COURT_RES AS RESEAU,
        NOM_RES AS LIBELLE
        FROM RESEAUDEF ORDER BY NOM_COURT_RES"""
        return psql.read_frame(_sql, self.conn)


    def liste_campagnes(self, campagne=None):
        """
        Liste des campagnes de mesure et des stations associées

        Paramètres:
        campagne: Si définie, liste des stations que pour cette campagne

        """
        condition = ""
        if campagne:
            condition = "WHERE NOM_COURT_CM='%s' """ %campagne
        _sql = """SELECT
        NOM_COURT_CM AS CAMPAGNE,
        NOM_COURT_SIT AS STATION,
        LIBELLE AS LIBELLE_CM,
        DATEDEB AS DEBUT,
        DATEFIN AS FIN
        FROM CAMPMES
        INNER JOIN CAMPMES_STATION USING (NOM_COURT_CM)
        %s
        ORDER BY NOM_COURT_CM"""% condition
        return psql.read_frame(_sql, self.conn)


    def liste_reseaux_indices(self):
        """Liste des réseaux d'indices ATMO"""

        _sql = """SELECT NOM_AGGLO AS GROUPE_ATMO, NOM_COURT_GRP FROM GROUPE_ATMO"""
        return psql.read_frame(_sql, self.conn)


    def liste_sites_prelevement(self):
        """Liste les sites de prélèvements manuels"""
        _sql = """SELECT NSIT, LIBELLE FROM SITE_PRELEVEMENT ORDER BY NSIT"""
        return psql.read_frame(_sql, self.conn)


    def get_mesures( self, mes, debut=None, fin=None, freq='H', format=None,
                     dayfirst=False, brut=False):
        """
        Récupération des données de mesure.

        Paramètres:
        mes: Un nom de mesure ou plusieurs séparées par des virgules, une liste
            (list, tuple, pandas.Series) de noms
        debut: Chaine de caractère ou objet datetime décrivant la date de début.
            Défaut=date du jour
        fin: Chaine de caractère ou objet datetime décrivant la date de fin.
            Défaut=date de début
        freq: fréquence de temps. '15T' | 'H' | 'D' | 'M' | 'A' (15T pour quart-horaire)
        format: chaine de caractère décrivant le format des dates (ex:"%Y-%m-%d"
            pour debut/fin="2013-01-28"). Appeler pyair.date.strtime_help() pour
            obtenir la liste des codes possibles.
            Defaut="%Y-%m-%d"
        dayfirst: Si aucun format n'est fourni et que les dates sont des chaines
            de caractères, aide le décrypteur à transformer la date en objet datetime
            en spécifiant que les dates commencent par le jour (ex:11/09/2012
            pourrait être interpreté comme le 09 novembre si dayfirst=False)
        brut: si oui ou non renvoyer le dataframe brut, non invalidé, et les
            codes d'état des mesures
            Defaut=False

        Retourne:
        Un dataframe contenant toutes les mesures demandées.
        Si brut=True, renvoie le  dataframe des mesures brutes non invalidées et
        le dataframe des codes d'états.
        Le dataframe valide (net) peut être alors recalculé en faisant:
        brut, etats = xr.get_mesure(..., brut=True)
        invalides = etats_to_invalid(etats)
        net = brut.mask(invalides)

        """

        def create_index(index, freq):
            """
            Nouvel index [id, date] avec date formaté suivant le pas de temps voulu
            index: index de l'ancien dataframe, tel que [date à minuit, date à ajouter]

            """
            decalage = 1  # sert à compenser l'aberration des temps qui veut qu'on marque sur la fin d'une période (ex: à 24h, la pollution de 23 à minuit)
            if freq == 'T' or freq == '15T':
                f = pd.tseries.offsets.Minute
                decalage = 15
            if freq == 'H':
                f = pd.tseries.offsets.Hour
            if freq == 'D':
                f = pd.tseries.offsets.Day
            if freq == 'M':
                f = pd.tseries.offsets.MonthBegin
            if freq == 'A':
                f = pd.tseries.offsets.YearBegin
            new_index = [date + f(int(delta)-decalage) for date, delta in index]
            #print(index)
            #print(new_index)
            return new_index

        #Reformatage du champ des noms de mesure
        mes = _format(mes)

        #Analyse des champs dates
        debut = to_date(debut, dayfirst, format)
        if not fin:
            fin = debut
        else:
            fin = to_date(fin, dayfirst, format)


        #La freq de temps Q n'existe pas, on passe d'abord par une fréquence 15 minutes
        if freq in ('Q', 'T'):
            freq = '15T'

        # Sélection des champs et de la table en fonctions de la fréquence de temps souhaitée
        if freq == '15T':
            diviseur = 96
            champ_val = ','.join( [ 'Q_M%02i AS "%i"'%(x, x*15) for x in range(1, diviseur+1) ] )
            champ_code = 'Q_ETATV'
            table = 'JOURNALIER'
        elif freq == 'H':
            diviseur = 24
            champ_val =  ','.join( [ 'H_M%02i AS "%i"'%(x, x) for x in range(1, diviseur+1) ] )
            champ_code = 'H_ETAT'
            table = 'JOURNALIER'
        elif freq == 'D':
            diviseur = 1
            champ_val = 'J_M01 AS "1"'
            champ_code = 'J_ETAT'
            table = 'JOURNALIER'
        elif freq == 'M':
            diviseur = 12
            champ_val = ','.join( [ 'M_M%02i AS "%i"'%(x, x) for x in range(1, diviseur+1) ] )
            champ_code = 'M_ETAT'
            table = 'MOIS'
        elif freq == 'A':
            diviseur = 1
            champ_val = 'A_M01 AS "1"'
            champ_code = 'A_ETAT'
            table = 'MOIS'
        else:
            raise ValueError, "freq doit être T, H, D, M ou A"

        if table == 'JOURNALIER':
            champ_date = 'J_DATE'
            debut_db = debut
            fin_db = fin
        else:
            champ_date = 'M_DATE'
            #Pour les freq='M' et 'A', la table contient toutes les valeurs sur une
            #année entière. Pour ne pas perturber la récupération si on passait des
            #dates en milieu d'année, on transforme les dates pour être calées en début
            #et en fin d'année. Le recadrage se fera plus loin dans le code, lors du reindex
            debut_db = debut.replace(month=1, day=1, hour=0, minute=0)
            fin_db = fin.replace(month=12, day=31, hour=23, minute=0)

        debut_db = debut_db.strftime("%Y-%m-%d")
        fin_db = fin_db.strftime("%Y-%m-%d")

        #Récupération des valeurs et codes d'états associés
        _sql = """SELECT
        IDENTIFIANT as "id",
        {champ_date} as "date",
        {champ_code} as "etat",
        {champ_val}
        FROM {table}
        INNER JOIN MESURE USING (NOM_COURT_MES)
        WHERE IDENTIFIANT IN ('{mes}')
        AND {champ_date} BETWEEN TO_DATE('{debut}', 'YYYY-MM-DD') AND TO_DATE('{fin}', 'YYYY-MM-DD')
        ORDER BY IDENTIFIANT, {champ_date} ASC""".format(champ_date=champ_date,
                                                         table=table,
                                                         champ_code=champ_code,
                                                         mes=mes,
                                                         champ_val=champ_val,
                                                         debut=debut_db,
                                                         fin=fin_db)
        ## TODO : A essayer quand la base sera en version 11g
        #_sql = """SELECT *
        #FROM ({selection})
        #UNPIVOT (IDENTIFIANT FOR VAL IN ({champ_as}))""".format(selection=_sql,
                                                                              #champ_date=champ_date,
                                                                              #champ_as=champ_as)

        #On recupere les valeurs depuis la freq dans une dataframe
        rep = psql.read_frame(_sql, self.conn)

        #On créait un multiindex pour manipuler plus facilement le dataframe
        df = rep.set_index(['id', 'date'])

        #Stack le dataframe pour mettre les colonnes en lignes, en supprimant la colonne des états
        #puis on unstack suivant l'id pour avoir les polluants en colonnes
        etats = df['etat']
        df = df.drop('etat', axis=1)
        df_stack = df.stack(dropna=False)
        df = df_stack.unstack('id')

        #Calcul d'un nouvel index avec les bonnes dates. L'index du df est
        #formé du champ date à minuit, et des noms des champs de valeurs
        #qui sont aliassés de 1 à 24 pour les heures, ... voir champ_val.
        #On aggrève alors ces 2 valeurs pour avoir des dates alignées qu'on utilise alors comme index final
        index = create_index(df.index, freq)
        df.reset_index(inplace=True, drop=True)
        df['date'] = index
        df = df.set_index(['date'])
        #Traitement des codes d'état
        #On concatène les codes d'état pour chaque polluant
        #etats = etats.sum(level=0)
        #etats = pd.DataFrame(zip(*etats.apply(list)))
        etats = etats.unstack('id')
        etats.fillna(value=MISSING_CODE*diviseur, inplace=True)
        etats = etats.sum(axis=0)
        etats = pd.DataFrame(zip(*etats.apply(list)))
        etats.index = df.index
        etats.columns = df.columns

        #Remplacement des valeurs aux dates manquantes par des NaN
        dates_completes = date_range(debut, fin, freq)
        df = df.reindex(dates_completes)
        etats = etats.reindex(dates_completes)

        #Invalidation par codes d'état
        #Pour chaque code d'état, regarde si oui ou non il est invalidant en le remplacant par un booléen
        invalid = etats_to_invalid(etats)

        if not brut:
            #dans le dataframe, masque toute valeur invalide par NaN
            dfn = df.mask(invalid)  #DataFrame net
            return dfn
        else:
            return df, etats


    def get_manuelles(self, site, code_parametre, debut, fin, court=False):
        """
        Recupération des mesures manuelles (labo) pour un site

        site: numéro du site (voir fonction liste_sites_prelevement)
        code_parametre: code ISO du paramètre à rechercher (C6H6=V4)
        debut: date de début du premier prélèvement
        fin: date de fin du dernier prélèvement
        court: Renvoie un tableau au format court ou long (colonnes)

        """

        condition = "WHERE MESLA.NOPOL='%s' " %code_parametre
        condition += "AND SITMETH.NSIT=%s " % site
        condition += "AND PRELEV.DATE_DEB>=TO_DATE('%s', 'YYYY-MM-DD') " % debut
        condition += "AND PRELEV.DATE_FIN<=TO_DATE('%s', 'YYYY-MM-DD') " % fin
        if court == False:
            select = """SELECT
                        MESLA.LIBELLE AS MESURE,
                        METH.LIBELLE AS METHODE,
                        ANA.VALEUR AS VALEUR,
                        MESLA.UNITE AS UNITE,
                        ANA.CODE_QUALITE AS CODE_QUALITE,
                        ANA.DATE_ANA AS DATE_ANALYSE,
                        ANA.ID_LABO AS LABO,
                        PRELEV.DATE_DEB AS DEBUT,
                        PRELEV.DATE_FIN AS FIN,
                        ANA.COMMENTAIRE AS COMMENTAIRE,
                        SITE.LIBELLE AS SITE,
                        SITE.AXE AS ADRESSE,
                        COM.NOM_COMMUNE AS COMMUNE"""
        else:
            select = """SELECT
                        MESLA.LIBELLE AS MESURE,
                        ANA.VALEUR AS VALEUR,
                        MESLA.UNITE AS UNITE,
                        ANA.CODE_QUALITE AS CODE_QUALITE,
                        PRELEV.DATE_DEB AS DEBUT,
                        PRELEV.DATE_FIN AS FIN,
                        SITE.AXE AS ADRESSE,
                        COM.NOM_COMMUNE AS COMMUNE"""
        _sql = """%s
        FROM ANALYSE ANA
        INNER JOIN PRELEVEMENT PRELEV ON (ANA.CODE_PRELEV=PRELEV.CODE_PRELEV AND ANA.CODE_SMP=PRELEV.CODE_SMP)
        INNER JOIN MESURE_LABO MESLA ON (ANA.CODE_MES_LABO=MESLA.CODE_MES_LABO AND ANA.CODE_SMP=MESLA.CODE_SMP)
        INNER JOIN SITE_METH_PRELEV SITMETH ON (ANA.CODE_SMP=SITMETH.CODE_SMP)
        INNER JOIN METH_PRELEVEMENT METH ON (SITMETH.CODE_METH_P=METH.CODE_METH_P)
        INNER JOIN SITE_PRELEVEMENT SITE ON (SITE.NSIT=SITMETH.NSIT)
        INNER JOIN COMMUNE COM ON (COM.NINSEE=SITE.NINSEE)
        %s
        ORDER BY MESLA.NOPOL,MESLA.LIBELLE,PRELEV.DATE_DEB"""% (select, condition)
        return psql.read_frame(_sql, self.conn)


    def get_indices(self, res, debut, fin):
        """
        Récupération des indices ATMO pour un réseau donné.

        Paramètres:
        res : Nom du ou des réseaux à chercher (str, list, pandas.Series)
        debut: date de début, format YYYY-MM-JJ (str)
        fin: Date de fin, format YYYY-MM-JJ (str)

        """
        res = _format(res)

        _sql = """SELECT
        J_DATE AS "date",
        NOM_AGGLO AS "reseau",
        C_IND_CALCULE AS "indice"
        FROM RESULTAT_INDICE
        INNER JOIN GROUPE_ATMO USING (NOM_COURT_GRP)
        WHERE NOM_AGGLO IN ('%s')
        AND J_DATE BETWEEN TO_DATE('%s', 'YYYY-MM-DD') AND TO_DATE('%s', 'YYYY-MM-DD') """ %(res, debut, fin)
        rep = psql.read_frame(_sql, self.conn)
        df = rep.set_index(['reseau', 'date'])
        df = df['indice']
        df = df.unstack('reseau')
        dates_completes = date_range(to_date(debut), to_date(fin), freq='D')
        df = df.reindex(dates_completes)
        return df


    #def get_ss_indice():
        #sql = """SELECT
            #GRP.NOM_AGGLO,
            #RES.NOPOL,
            #RES.P_SS_INDICE,
            #RES.P_SS_I_MES
        #FROM RESULTAT_SS_INDICE RES
        #INNER JOIN GROUPE_ATMO GRP USING (NOM_COURT_GRP)
        #WHERE J_DATE=TO_DATE('2011-10-04', 'YYYY-MM-DD');"""

    def get_SQLTXT(self, format_=1):
        """retourne les requêtes actuellement lancées sur le serveur"""

        if format_ == 1:
            _sql = """SELECT u.sid, substr(u.username,1,12) user_name, s.sql_text
            FROM v$sql s,v$session u
            WHERE s.hash_value = u.sql_hash_value
            AND sql_text NOT LIKE '%from v$sql s, v$session u%'
            AND u.username NOT LIKE 'None'
            ORDER BY u.sid"""

        if format_ == 2:
            _sql = """SELECT u.username, s.first_load_time, s.executions, s.sql_text
            FROM dba_users u,v$sqlarea s
            WHERE u.user_id=s.parsing_user_id
            AND u.username LIKE 'LIONEL'
            AND sql_text NOT LIKE '%FROM dba_users u,v$sqlarea s%'
            ORDER BY s.first_load_time"""

        return psql.read_frame(_sql, self.conn)



if __name__ == "__main__":
    xr = XAIR()
    mes = xr.liste_mesures(reseau='OZONE').MESURE
    a = xr.get_mesures(mes, '2012-01-01', fin='2012-12-31', freq='H', brut=False)
