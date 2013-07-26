# -*- coding: utf-8 -*-
"""
Chaînes de textes utilisés pour les tests unitaires du parser principal et démonstration 
pour son helper.

Les variables qui se terminent en ``*_LABELS`` sont des dictionnaires de 
labels et chaînes d'exemples utilisés par le helper.

Les variables qui se terminent en ``*_TEST_CASE`` sont des chaînes de textes 
utilisés comme sources pour les tests unitaires, ainsi que certaines par le 
helper.

Les variables qui se terminent en ``*_TEST_ATTEMPT*`` sont le résultats 
attendu par les tests unitaires pour les sources qui lui ont été données.
"""

INLINE_SYNTAX_LABELS = {
    'em' : [
        u"Italique",
        u"Je suis %sitalique%s de cette mise en forme.",
    ],
    'strong' : [
        u"Gras",
        u"Je suis un peu %sgras%s avec cette mise en forme.",
    ],
    'q' : [
        u"Citation",
        u"Je %scite%s cette mise en forme.",
    ],
    'code' : [
        u"Code",
        u"Je %scode%s cette mise en forme.",
    ],
    'del' : [
        u"Surligné",
        u"Je suis complètement %sbarré%s de cette mise en forme.",
    ],
    'ins' : [
        u"Souligné",
        u"Je %ssouligne%s cette mise en forme.",
    ],
}
LINKS_SYNTAX_LABELS = {
    'default' : [
        u"Simple",
        u"Je suis un lien %shttp://perdu%s dans cet univers.",
    ],
    'with_title' : [
        u"Avec un titre",
        u"Je suis un lien %sPerdu|http://perdu%s dans cet univers.",
    ],
    #'with_wikiword' : [
        #u"Avec un titre",
        #u"Je suis un lien %sPerdu|Wikipage%s dans cet univers.",
    #],
    'special' : [
        u"Raccourci d'url",
        u"Je suis un raccourci de recherche %sGoogle|google://PyWiki2Xhtml%s.",
    ],
}

#Test simple des mises en formes en ligne
INLINE_TEST_CASE = u"""Je suis un peu __gras__ en ''italique'' mais je tiens à ++souligner++ que je ne suis pas complètement --barré-- ni [Perdu|http://perdu.com] donc ça va."""
INLINE_TEST_ATTEMPT = u"""<p>Je suis un peu <strong>gras</strong> en <em>italique</em> mais je tiens à <ins>souligner</ins> que je ne suis pas complètement <del>barré</del> ni <a href="http://perdu.com">Perdu</a> donc ça va.</p>"""

# Test simple des blocs
SIMPLE_BLOCK_TEST_CASE = u"""Je suis une phrase. 
Je suis une autre phrase, donc pas de retour à la ligne.

Moi je suis un paragraphe séparé.

 Un espace devant une ligne signifie d'afficher le texte tel quel, 
 en conservant la mise en forme originale. Aucun élément de syntaxe n'y sera traité, 
 par exemple ce **gras** ne se fera pas.

!! Un titre pour annoncer une liste

*item1
* item2
*item 3
"""
SIMPLE_BLOCK_TEST_ATTEMPT = u"""<p>Je suis une phrase.
Je suis une autre phrase, donc pas de retour à la ligne.</p>


<p>Moi je suis un paragraphe séparé.</p>


<pre>Un espace devant une ligne signifie d'afficher le texte tel quel, 
en conservant la mise en forme originale. Aucun élément de syntaxe n'y sera traité, 
par exemple ce **gras** ne se fera pas.</pre>


<h4 id="wikititle_1">Un titre pour annoncer une liste</h4>

<ul>
<li>item1</li>
<li>item2</li>
<li>item 3</li>
</ul>"""

# Test simple des blocs
TITLE_TEST_CASE = u"""!!!! Quatres suspensions

!!! Trois suspensions

!!!! Quatres suspensions 2

!!! Deux suspensions

!! Une suspensions

!!! Trois suspensions 2

!! Deux suspensions 2

! Une suspensions 1

"""
TITLE_TEST_ATTEMPT = u"""<h2 id="wikititle_1">Quatres suspensions</h2>


<h3 id="wikititle_2">Trois suspensions</h3>


<h2 id="wikititle_3">Quatres suspensions 2</h2>


<h3 id="wikititle_4">Deux suspensions</h3>


<h4 id="wikititle_5">Une suspensions</h4>


<h3 id="wikititle_6">Trois suspensions 2</h3>


<h4 id="wikititle_7">Deux suspensions 2</h4>


<h5 id="wikititle_8">Une suspensions 1</h5>"""
TITLE_TEST_ATTEMPT2 = u"""<h4 id="wikititle_1">Quatres suspensions</h4>


<h4 id="wikititle_2">Trois suspensions</h4>


<h4 id="wikititle_3">Quatres suspensions 2</h4>


<h4 id="wikititle_4">Deux suspensions</h4>


<h4 id="wikititle_5">Une suspensions</h4>


<h4 id="wikititle_6">Trois suspensions 2</h4>


<h4 id="wikititle_7">Deux suspensions 2</h4>


<h5 id="wikititle_8">Une suspensions 1</h5>"""


# Test des imbrications des listes à puces
BULLETLIST_TEST_CASE = u"""Test simple

*item1
* item2
*item 3

Test à plusieurs niveaux de listes à puces et numérotées

* item 1
* item 2
** item 2.1
*** item 2.1.1
*** item 2.1.2
* item 3
* item 4
*# item 4.1
*# item 4.2
*# item 4.3
* item 5
"""
BULLETLIST_TEST_ATTEMPT = u"""<p>Test simple</p>

<ul>
<li>item1</li>
<li>item2</li>
<li>item 3</li>
</ul>

<p>Test à plusieurs niveaux de listes à puces et numérotées</p>

<ul>
<li>item 1</li>
<li>item 2
<ul>
<li>item 2.1
<ul>
<li>item 2.1.1</li>
<li>item 2.1.2</li>
</ul></li>
</ul></li>
<li>item 3</li>
<li>item 4
<ol>
<li>item 4.1</li>
<li>item 4.2</li>
<li>item 4.3</li>
</ol></li>
<li>item 5</li>
</ul>"""

# Test des wikiwords
WIKIWORDS_TEST_CASE = u"""Dans ce document, le sigle ++$SHOOP++ représente le chemin vers le répertoire où vous avez installé le projet __¶¶¶Shoop¶¶¶__.

* ¶¶¶Python¶¶¶ >= 2.5 

!! Debug

La variable @@DEBUG@@ lorsqu''elle est à ''''True'''' active le mode de ¶¶¶débugguage¶¶¶ ce qui fait que ¶¶¶Django¶¶¶ affichera les pages d''erreur avec la Stacktrace complète de Python. En mode désactivé (à ''''False'''') Django servira la page @@$SHOOP/$TEMPLATES/404.html@@ en cas de page non trouvée et @@$SHOOP/$TEMPLATES/500.html@@ avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.
"""

WIKIWORDS_ENABLED_PAGE = {
    u'Shoop': u'Shoop',
    u'python': u'PythonLoupai',
    u'Django': u'The Django Framework',
}

WIKIWORDS_TEST_ATTEMPT_DISABLED1 = u"""<p>Dans ce document, le sigle <ins>$SHOOP</ins> représente le chemin vers le répertoire où vous avez installé le projet <strong>¶¶¶Shoop¶¶¶</strong>.</p>

<ul>
<li>¶¶¶Python¶¶¶ &#62;= 2.5</li>
</ul>

<h4 id="wikititle_1">Debug</h4>


<p>La variable <code>DEBUG</code> lorsqu<em>elle est à </em><em>True</em><em> active le mode de ¶¶¶débugguage¶¶¶ ce qui fait que ¶¶¶Django¶¶¶ affichera les pages d</em>erreur avec la Stacktrace complète de Python. En mode désactivé (à <em></em>False<em></em>) Django servira la page <code>$SHOOP/$TEMPLATES/404.html</code> en cas de page non trouvée et <code>$SHOOP/$TEMPLATES/500.html</code> avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.</p>"""

WIKIWORDS_TEST_ATTEMPT_DISABLED2 = u"""<p>Dans ce document, le sigle <ins>$SHOOP</ins> représente le chemin vers le répertoire où vous avez installé le projet <strong><span>Shoop</span></strong>.</p>

<ul>
<li><span>Python</span> &#62;= 2.5</li>
</ul>

<h4 id="wikititle_1">Debug</h4>


<p>La variable <code>DEBUG</code> lorsqu<em>elle est à </em><em>True</em><em> active le mode de <span>débugguage</span> ce qui fait que <span>Django</span> affichera les pages d</em>erreur avec la Stacktrace complète de Python. En mode désactivé (à <em></em>False<em></em>) Django servira la page <code>$SHOOP/$TEMPLATES/404.html</code> en cas de page non trouvée et <code>$SHOOP/$TEMPLATES/500.html</code> avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.</p>"""

WIKIWORDS_TEST_ATTEMPT_EMPTYPUBLISHED = u"""<p>Dans ce document, le sigle <ins>$SHOOP</ins> représente le chemin vers le répertoire où vous avez installé le projet <strong><a href="/add/Shoop/">Shoop</a></strong>.</p>

<ul>
<li><a href="/add/Python/">Python</a> &#62;= 2.5</li>
</ul>

<h4 id="wikititle_1">Debug</h4>


<p>La variable <code>DEBUG</code> lorsqu<em>elle est à </em><em>True</em><em> active le mode de <span>débugguage</span> ce qui fait que <a href="/add/Django/">Django</a> affichera les pages d</em>erreur avec la Stacktrace complète de Python. En mode désactivé (à <em></em>False<em></em>) Django servira la page <code>$SHOOP/$TEMPLATES/404.html</code> en cas de page non trouvée et <code>$SHOOP/$TEMPLATES/500.html</code> avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.</p>"""

WIKIWORDS_TEST_ATTEMPT_ENABLED = u"""<p>Dans ce document, le sigle <ins>$SHOOP</ins> représente le chemin vers le répertoire où vous avez installé le projet <strong><a href="/Shoop/">Shoop</a></strong>.</p>

<ul>
<li><a href="/add/Python/">Python</a> &#62;= 2.5</li>
</ul>

<h4 id="wikititle_1">Debug</h4>


<p>La variable <code>DEBUG</code> lorsqu<em>elle est à </em><em>True</em><em> active le mode de <span>débugguage</span> ce qui fait que <a href="/Django/">The Django Framework</a> affichera les pages d</em>erreur avec la Stacktrace complète de Python. En mode désactivé (à <em></em>False<em></em>) Django servira la page <code>$SHOOP/$TEMPLATES/404.html</code> en cas de page non trouvée et <code>$SHOOP/$TEMPLATES/500.html</code> avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.</p>"""

# Test d'un document complet
FULLDOCUMENT_TEST_CASE = u"""!!! Pré-requis

Pour installer le projet, il vous faut :

* Python >= 2.5 
* Sa librairie devel souvent nommée lib-pythonX.X-dev, indispensable si vous avez besoin de compiler vous mêmes certains modules python requis.
* Un compte et une base de donnée sur un serveur de type Mysql, PostgreSQL. Sqlite est supporté par Django mais n''a jamais été testé avec ¶¶¶Shoop¶¶¶.
* Optionnellement pour la mise en production sur __Apache2__, __mod_python__ ou bien __FastCgi__.
* Des modules Python :
** __Django__ 0.96.x $$[Django Installation guide|http://www.djangoproject.com/documentation/0.96/install/]$$ $$[Django Installation FAQ|http://www.djangoproject.com/documentation/0.96/faq/#installation-questions]$$
** __PIL__ $$[Python Image Library|http://www.pythonware.com/products/pil/]$$ pour le traitement des images. (Actuellement pas utilisé)
** __Epydoc__ $$[Automatic API Documentation Generation for Python|http://epydoc.sourceforge.net/]$$ pour la documentation automatique du code intégrée dans l''interface d''administration. (Optionnel)
** __setuptools__ $$[setuptools|http://cheeseshop.python.org/pypi/setuptools]$$ pour aider à l''installation de certains modules python (les pros peuvent faire sans).
** __PyWiki2xhtml__ $$[PyWiki2xhtml|http://svn.logicielslibres.info/bordel/sveetch/PyWiki2xhtml/]$$ un module pour faire de la transformation en xhtml de textes au format wiki de wiki2xhtml.
** __Sveetchies__ $$[Sveetchies|http://svn.logicielslibres.info/bordel/sveetch/Sveetchies/]$$ qui contient des utilitaires nécessaires aux outil de commande en ligne.
** __python-memcached__ $$[Binding python pour memcached|http://www.tummy.com/Community/software/python-memcached/]$$ si vous comptez utiliser le cache avec memcached.
** Pour l''utilisation de PostgreSQL, Django requiert que vous ayez la librairire python ''psycopg'' $$[Module psycopg|http://www.initd.org/projects/psycopg1]$$. Vous pouvez installer Django sans, mais vous n''aurez pas le support PostgreSQL.
** Pour MySQL, il vous faudra python-msqldb $$[MysqlDB pour Python|http://sourceforge.net/projects/mysql-python]$$.

Dans ce document, le sigle ++$SHOOP++ représente le chemin vers le répertoire où vous avez installé le projet __¶¶¶Shoop¶¶¶__.

De même pour ++$DJANGO++ qui représente le répertoire où vous avez installé __Django__.

!!! Configuration et initalisation

Après avoir installé Django, allez dans le répertoire de ¶¶¶Shoop¶¶¶, et ouvrez le fichier @@$SHOOP/settings.py@@ pour éditer la configuration d''installation.

!! Debug

La variable @@DEBUG@@ lorsqu''elle est à ''''True'''' active le mode de débugguage ce qui fait que Django affichera les pages d''erreur avec la Stacktrace complète de Python. En mode désactivé (à ''''False'''') Django servira la page @@$SHOOP/$TEMPLATES/404.html@@ en cas de page non trouvée et @@$SHOOP/$TEMPLATES/500.html@@ avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.

!! Base de données

Tout d''abord, créez une base de donnée avec un accès, puis configurez l''accès à cette BDD en éditant les paramètres suivants :

 DATABASE_ENGINE = ''mysql''
 DATABASE_NAME = ''django''
 DATABASE_USER = ''django''
 DATABASE_PASSWORD = ''django''
 DATABASE_HOST = ''localhost''
 DATABASE_PORT = ''''

!! Envoi de mails

Remplissez correctement __EMAIL_HOST__, __SERVER_EMAIL__, __DEFAULT_FROM_EMAIL__. L''envoi de mails est pour l''instant réservé aux mails d''erreur automatique que Django renvoi aux ++Admins++ en mode @@DEBUG = False@@.

Changez aussi @@ADMINS@@ pour qu''il contiennent une adresse email valide d''un admin prêt à recevoir les mails d''erreurs au cas où.

!! Templates

Dans la ligne suivante modifiez l''emplacement du répertoire de @@$SHOOP/templates/@@ pour qu''il convienne à votre installation :

 TEMPLATE_DIRS = (
     "/chemin/absolu/vers/repertoire/templates/",
 )

L''utilisateur qui lance Django doit avoir les droits de lire dans ce répertoire.

!! Url des médias statiques

Indiquez ensuite l''url pour accéder à ce répertoire. Cela peut être une url relative :

 MEDIA_URL = ''/site_medias/''

Ou bien complète avec son domaine (utile qu''en cas particulier ou en production comme avec Apache) :

 MEDIA_URL = ''http://mondomaine/site_medias/''

Notez bien que Django n''est pas censé servir de fichiers statiques et que si vous en avez besoin vous devez passer par ce répertoire.

En mode ''''DEBUG'''' activé, c''est le serveur de devellopement de Django qui serre les fichiers médias. Cependant en production, Apache devra les servir dans un site virtuel différent (ex: http://medias.monsite.com/) ou un alias vers le répertoire médias, qui devront être dédouané d''un processing par mod_python, pensez à mettre la vraie url complète des médias dans @@MEDIA_URL@@ si c''est le cas.

!! Initialisation des applications et du super utilisateur

Après avoir sauvegardé votre fichier settings une première fois, depuis le répertoire du projet lancez l''outil d''administration en ligne de Django avec la commande de synchronisatio de la BDD :

 python ./manage.py syncdb

Si il retourne une erreur, vous avez surement un problème de connexion au serveur de BDD, vérifier avec votre client BDD préféré que tout les paramètres donnés soient corrects et réessayez.

Si tout se passe bien, le shell vous demandera le nécessaire pour créer le compte super utilisateur. Il est impératif de créer ce compte.

!!! Appliquer les patchs sur Django

Si vous avez déja suivit cette étape au cours d''une précédente installation de ¶¶¶Shoop¶¶¶, il est inutile de poursuivre, passez à l''étape suivante.

Il y a un patch qui modifie très légèrement le noyau de Django de façon transparente.

Ce fichier se trouve à l''emplacement @@$SHOOP/utils/django_oldforms_init.diff@@.

''''Patch'''' s''utilise de la manière @@patch TARGET SOURCEPATCH@@

Par exemple depuis le répertoire de shoop faites :

 patch /usr/lib/python2.5/site-packages/django/oldforms/\\__init\\__.py ./django_oldforms_init.diff

Le chemin @@TARGET@@ diffère surement quelque peu selon votre distribution.

!! Url du site

L''url du site est stocké en BDD pour plusieurs facilités. Accèdez à la BDD par le moyen de votre choix et allez dans la table __sites__ et modifiez l''entrée numéro 1 qui a du être créé pendant le ++syncdb++ pour y mettre votre nom de domaine (ou l''ip avec le :port) ainsi que le titre du site.

!!! Premier démarrage

!! Lancez le serveur de test

Faites la commande :

 python manage.py runserver 0.0.0.0:8000

Cela fait répondre le serveur sur votre ip et le port 8000, vous pouvez changer ces paramètres.

Le site est accessible à l''url :

 http://ip_du_serveur:8000/

!! Administration

Django intègre une interface d''administration. En étant authentifié avec un utilisateur ayant la permission d''y accéder (''''staff_admin'''') ou bien le super utilisateur, vous pouvez y accéder à l''adresse :

 http://ip_du_serveur:8000/admin/

Cette interface est pleinement sécurisé pour peu que vous n''y donniez pas accès à n''importe qui avec des permissions gênantes.

Vous y trouverez les écrans d''administrations de toute les applications.

Vous pouvez créer des __groupes__ de modérations et leur associer des __permissions__, ce qui vous permettra ensuite de gérer efficacement votre équipe de modération.

__Attention__ cet espace est reservé à l''administration. Il est conseillé de ne donner le droit d''accès @@is_staff@@ à cette interface qu''à des personnes ''''averties''''. En effet certains ajouts d''objets ont besoin de relations qui ne sont pas incluses dans les modèles eux mêmes mais dans le manipulateur des formulaires du site qui n''ont aucun rapport avec ceux de l''interface d''administration de Django. Cette dernière est auto-générée et gérée directement par Django gràce aux modèles de données.

!!! Conseils d''utilisations

Pour une mise en production, il est fortement déconseillé d''utiliser directement le serveur embarqué dans Django, mais plutôt Apache2+mod_python.$$[Django+mod_python|http://www.djangoproject.com/documentation/0.96/modpython/]$$ et désactivez le ''''directory listing''''.

Plusieurs méthodes sont possibles, deux ont été testés avec ¶¶¶Shoop¶¶¶. La première solution est à base de Apache+mod_python, la seconde à partir de FastCgi plus un autre serveur web.

!! Apache + mod_python

Un exemple d''installation pour un serveur Apache2.0 avec le module __mod_python__ installé et activé.

! Vhost complet

Vous pouvez simplement tout mettre dans un seul Vhost. La partie ''''dynamique'''' gérée par Django ainsi que les médias gérés directement par Apache comme de simples fichiers ''''statiques''''.

    <VirtualHost X.X.X.X>
            ServerAdmin webmaster@sveetch.net
            ServerName dax.sveetch.net
            SetHandler python-program
            PythonHandler django.core.handlers.modpython
            PythonPath "\\[''/home/shoop/''\\] + sys.path"
            SetEnv DJANGO_SETTINGS_MODULE shoop.settings
            PythonDebug Off
            PythonAutoReload Off
            # Url du fichier robot (optionnel)
            # Alias /robot.txt "/home/shoop/robot.txt"
            # <Location "/robot.txt">
            #     SetHandler None
            # </Location>
            # Médias sur le meme domaine (en mode DEBUG désactivé)
            Alias /site_medias "/home/shoop/site_medias"
            <Location "/site_medias">
                 SetHandler None
            </Location>
            CustomLog /home/shoop/logs/shoop.fr-access_log combined
            ErrorLog /home/shoop/logs/shoop.fr-error_log
    </VirtualHost>

Il est possible que pour une raison vous n''ayez pas installé Django dans le site-package de Python, pour indiquer à Apache ou se trouve votre installation de Django il suffit de modifier la ligne du PythonPath comme ceci :

            PythonPath "\\[''/path/to/Django-0.96'', ''/home/shoop/''\\] + sys.path"

! Vhost Apache pour Django et Lighttpd pour les médias

Il est conseillé d''utiliser cette solution supplémentaire qui permet de séparer la gestion des médias de la partie Django ''''dynamique''''. Notez qu''il est tout aussi possible de faire un vhost supplémentaire dans Apache pour gérer ces médias, cela dit lighttpd est beaucoup mieux dimensionné pour s''en occuper.

Configurez le wwwroot (ou bien un vhost) de lighttpd pour servir le répertoire @@$SHOOP/site_medias/@@, attention lighttpd doit bien sûr tourner sur un autre port que ceux utilisés par Apache.

Ensuite deux options soit vous utilisez directement le domaine globale ou l''ip de votre serveur avec son port et vous n''avez rien à faire, soit vous souhaitez utiliser un nom de domaine sans port dans l''adresse (tel que ''''medias.foo.com'''') et il vous faudra faire une redirection dans un vhost apache vers lighttpd avec un ''''rewriting'''' d''url.

    <VirtualHost *:80>
            ServerAdmin webmaster@mygroovypod.com
            DocumentRoot /home/shoop/site_medias
            SuexecUserGroup shoop users
            ServerName medias.sveetch.net
            CustomLog /home/shoop/logs/medias.shoop.fr-access_log combined
            SetHandler None
            RewriteEngine On
            RewriteRule ^/(.*) http://sveetch.net:81/$1 \\[P\\]
    </VirtualHost>

!! FastCgi

Avec FastCgi, vous n''êtes pas limité au choix de Apache, lighttpd et nginx sont aussi un choix possible. Dans cette situation le serveur web ne fait que transmettre la requête à un démon FastCgi s''occupant de gérer votre application.

Dans tout les cas, vous devrez installer module Python __flup__$$[flup|http://trac.saddi.com/flup]$$ avant tout. 

Je ne traiterais que la méthode que j''ai testé donc avec Apache. Apache requiert que le module __mod_fastcgi__ soit installé et activé. Ensuite il faut lancer le démon FastCgi avec par exemple la commande suivante depuis le répertoire parent de votre installation de ¶¶¶Shoop¶¶¶ :

  django-admin.py runfcgi --settings=shoop.prod_settings host=127.0.0.1 port=3303 pidfile=/home/django/shoop.pid

On y indique le fichier de ''''settings'''' à utiliser, l''adresse hôte et le port pour atteindre le serveur FastCgi par le serveur web (donc une adresse ip interne est parfaite) et le pidfile qui permettra de retrouver le processus à ''''killer'''' pour stopper le serveur.

Ensuite on installe un vhost sur Apache tel que :

    # Spécifie l''adresse interne ou retrouver l''application
    FastCGIExternalServer /home/django/projects/shoop/shoop.fcgi -host 127.0.0.1:3303
    # Le vhost en lui meme
    <VirtualHost *:8000>
            # Nécessaire pour que apache puisse accéder au shoop.fcgi et site_medias
            <directory /home/django/projects/shoop/>
                    Order deny,allow
                    Allow from all
            </directory>
            # Pareil mais pour les medias de l''admin qui sont ailleurs
            <directory /home/django/Django-0.96/django/contrib/admin/media/>
                    Order deny,allow
                    Allow from all
            </directory>
            DocumentRoot /home/django/projects/shoop
            # Logs
            CustomLog /home/django/logs/shoop-access_log combined
            ErrorLog /home/django/logs/shoop-error_log
            # Rewrite pour les parties statiques
            Alias /favicon.ico /home/django/projects/shoop/site_medias/favicon.ico
            Alias /crossdomain.xml /home/django/projects/shoop/crossdomain.xml
            Alias /shoop_medias /home/django/projects/shoop/site_medias
            Alias /admin_medias /home/django/Django-0.96/django/contrib/admin/media
            RewriteEngine On
            RewriteRule ^/(favicon.ico.*)$ /$1 \\[QSA,L,PT\\]
            RewriteRule ^/(crossdomain.xml.*)$ /$1 \\[QSA,L,PT\\]
            RewriteRule ^/(shoop_medias.*)$ /$1 \\[QSA,L,PT\\]
            RewriteRule ^/(admin_medias.*)$ /$1 \\[QSA,L,PT\\]
            RewriteCond %{REQUEST_FILENAME} !-f
            RewriteRule ^/(.*)$ /shoop.fcgi/$1 \\[QSA,L\\]
    </VirtualHost>

Voila, évidemment il est fortement conseillé de lire impérativement le document [How to use Django with FastCGI, SCGI or AJP|http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi/?from=olddocs] pour plus de détails.


Contact : sveetch AT gmail DOT com
"""
FULLDOCUMENT_TEST_ATTEMPT = u"""<h3 id="wikititle_1">Pré-requis</h3>


<p>Pour installer le projet, il vous faut&#160;:</p>

<ul>
<li>Python &#62;= 2.5</li>
<li>Sa librairie devel souvent nommée lib-pythonX.X-dev, indispensable si vous avez besoin de compiler vous mêmes certains modules python requis.</li>
<li>Un compte et une base de donnée sur un serveur de type Mysql, PostgreSQL. Sqlite est supporté par Django mais n''a jamais été testé avec <a href="/Shoop/">Shoop</a>.</li>
<li>Optionnellement pour la mise en production sur <strong>Apache2</strong>, <strong>mod_python</strong> ou bien <strong>FastCgi</strong>.</li>
<li>Des modules Python&#160;:
<ul>
<li><strong>Django</strong> 0.96.x <sup>[<a href="#wiki-footnote-001" id="rev-wiki-footnote-001">1</a>]</sup> <sup>[<a href="#wiki-footnote-002" id="rev-wiki-footnote-002">2</a>]</sup></li>
<li><strong>PIL</strong> <sup>[<a href="#wiki-footnote-003" id="rev-wiki-footnote-003">3</a>]</sup> pour le traitement des images. (Actuellement pas utilisé)</li>
<li><strong>Epydoc</strong> <sup>[<a href="#wiki-footnote-004" id="rev-wiki-footnote-004">4</a>]</sup> pour la documentation automatique du code intégrée dans l<em>interface d</em>administration. (Optionnel)</li>
<li><strong>setuptools</strong> <sup>[<a href="#wiki-footnote-005" id="rev-wiki-footnote-005">5</a>]</sup> pour aider à l''installation de certains modules python (les pros peuvent faire sans).</li>
<li><strong>PyWiki2xhtml</strong> <sup>[<a href="#wiki-footnote-006" id="rev-wiki-footnote-006">6</a>]</sup> un module pour faire de la transformation en xhtml de textes au format wiki de wiki2xhtml.</li>
<li><strong>Sveetchies</strong> <sup>[<a href="#wiki-footnote-007" id="rev-wiki-footnote-007">7</a>]</sup> qui contient des utilitaires nécessaires aux outil de commande en ligne.</li>
<li><strong>python-memcached</strong> <sup>[<a href="#wiki-footnote-008" id="rev-wiki-footnote-008">8</a>]</sup> si vous comptez utiliser le cache avec memcached.</li>
<li>Pour l<em>utilisation de PostgreSQL, Django requiert que vous ayez la librairire python </em>psycopg<em> <sup>[<a href="#wiki-footnote-009" id="rev-wiki-footnote-009">9</a>]</sup>. Vous pouvez installer Django sans, mais vous n</em>aurez pas le support PostgreSQL.</li>
<li>Pour MySQL, il vous faudra python-msqldb <sup>[<a href="#wiki-footnote-010" id="rev-wiki-footnote-010">10</a>]</sup>.</li>
</ul></li>
</ul>

<p>Dans ce document, le sigle <ins>$SHOOP</ins> représente le chemin vers le répertoire où vous avez installé le projet <strong><a href="/Shoop/">Shoop</a></strong>.</p>


<p>De même pour <ins>$DJANGO</ins> qui représente le répertoire où vous avez installé <strong>Django</strong>.</p>


<h3 id="wikititle_2">Configuration et initalisation</h3>


<p>Après avoir installé Django, allez dans le répertoire de <a href="/Shoop/">Shoop</a>, et ouvrez le fichier <code>$SHOOP/settings.py</code> pour éditer la configuration d''installation.</p>


<h4 id="wikititle_3">Debug</h4>


<p>La variable <code>DEBUG</code> lorsqu<em>elle est à </em><em>True</em><em> active le mode de débugguage ce qui fait que Django affichera les pages d</em>erreur avec la Stacktrace complète de Python. En mode désactivé (à <em></em>False<em></em>) Django servira la page <code>$SHOOP/$TEMPLATES/404.html</code> en cas de page non trouvée et <code>$SHOOP/$TEMPLATES/500.html</code> avec un mail (contenant la Stacktrace) aux admins en cas d''erreur serveur.</p>


<h4 id="wikititle_4">Base de données</h4>


<p>Tout d<em>abord, créez une base de donnée avec un accès, puis configurez l</em>accès à cette BDD en éditant les paramètres suivants&#160;:</p>


<pre>DATABASE_ENGINE = <em>mysql</em>
DATABASE_NAME = <em>django</em>
DATABASE_USER = <em>django</em>
DATABASE_PASSWORD = <em>django</em>
DATABASE_HOST = <em>localhost</em>
DATABASE_PORT = <em></em></pre>


<h4 id="wikititle_5">Envoi de mails</h4>


<p>Remplissez correctement <strong>EMAIL_HOST</strong>, <strong>SERVER_EMAIL</strong>, <strong>DEFAULT_FROM_EMAIL</strong>. L<em>envoi de mails est pour l</em>instant réservé aux mails d''erreur automatique que Django renvoi aux <ins>Admins</ins> en mode <code>DEBUG = False</code>.</p>


<p>Changez aussi <code>ADMINS</code> pour qu<em>il contiennent une adresse email valide d</em>un admin prêt à recevoir les mails d''erreurs au cas où.</p>


<h4 id="wikititle_6">Templates</h4>


<p>Dans la ligne suivante modifiez l<em>emplacement du répertoire de <code>$SHOOP/templates/</code> pour qu</em>il convienne à votre installation&#160;:</p>


<pre>TEMPLATE_DIRS = (
    "/chemin/absolu/vers/repertoire/templates/",
)</pre>


<p>L''utilisateur qui lance Django doit avoir les droits de lire dans ce répertoire.</p>


<h4 id="wikititle_7">Url des médias statiques</h4>


<p>Indiquez ensuite l''url pour accéder à ce répertoire. Cela peut être une url relative&#160;:</p>


<pre>MEDIA_URL = <em>/site_medias/</em></pre>


<p>Ou bien complète avec son domaine (utile qu''en cas particulier ou en production comme avec Apache)&#160;:</p>


<pre>MEDIA_URL = <em>http://mondomaine/site_medias/</em></pre>


<p>Notez bien que Django n''est pas censé servir de fichiers statiques et que si vous en avez besoin vous devez passer par ce répertoire.</p>


<p>En mode <em></em>DEBUG<em></em> activé, c<em>est le serveur de devellopement de Django qui serre les fichiers médias. Cependant en production, Apache devra les servir dans un site virtuel différent (ex: http://medias.monsite.com/) ou un alias vers le répertoire médias, qui devront être dédouané d</em>un processing par mod_python, pensez à mettre la vraie url complète des médias dans <code>MEDIA_URL</code> si c''est le cas.</p>


<h4 id="wikititle_8">Initialisation des applications et du super utilisateur</h4>


<p>Après avoir sauvegardé votre fichier settings une première fois, depuis le répertoire du projet lancez l<em>outil d</em>administration en ligne de Django avec la commande de synchronisatio de la BDD&#160;:</p>


<pre>python ./manage.py syncdb</pre>


<p>Si il retourne une erreur, vous avez surement un problème de connexion au serveur de BDD, vérifier avec votre client BDD préféré que tout les paramètres donnés soient corrects et réessayez.</p>


<p>Si tout se passe bien, le shell vous demandera le nécessaire pour créer le compte super utilisateur. Il est impératif de créer ce compte.</p>


<h3 id="wikititle_9">Appliquer les patchs sur Django</h3>


<p>Si vous avez déja suivit cette étape au cours d<em>une précédente installation de <a href="/Shoop/">Shoop</a>, il est inutile de poursuivre, passez à l</em>étape suivante.</p>


<p>Il y a un patch qui modifie très légèrement le noyau de Django de façon transparente.</p>


<p>Ce fichier se trouve à l''emplacement <code>$SHOOP/utils/django_oldforms_init.diff</code>.</p>


<p><em></em>Patch<em></em> s''utilise de la manière <code>patch TARGET SOURCEPATCH</code></p>


<p>Par exemple depuis le répertoire de shoop faites&#160;:</p>


<pre>patch /usr/lib/python2.5/site-packages/django/oldforms/__init__.py ./django_oldforms_init.diff</pre>


<p>Le chemin <code>TARGET</code> diffère surement quelque peu selon votre distribution.</p>


<h4 id="wikititle_10">Url du site</h4>


<p>L<em>url du site est stocké en BDD pour plusieurs facilités. Accèdez à la BDD par le moyen de votre choix et allez dans la table <strong>sites</strong> et modifiez l</em>entrée numéro 1 qui a du être créé pendant le <ins>syncdb</ins> pour y mettre votre nom de domaine (ou l''ip avec le :port) ainsi que le titre du site.</p>


<h3 id="wikititle_11">Premier démarrage</h3>


<h4 id="wikititle_12">Lancez le serveur de test</h4>


<p>Faites la commande&#160;:</p>


<pre>python manage.py runserver 0.0.0.0:8000</pre>


<p>Cela fait répondre le serveur sur votre ip et le port 8000, vous pouvez changer ces paramètres.</p>


<p>Le site est accessible à l''url&#160;:</p>


<pre>http://ip_du_serveur:8000/</pre>


<h4 id="wikititle_13">Administration</h4>


<p>Django intègre une interface d<em>administration. En étant authentifié avec un utilisateur ayant la permission d</em>y accéder (<em></em>staff_admin<em></em>) ou bien le super utilisateur, vous pouvez y accéder à l''adresse&#160;:</p>


<pre>http://ip_du_serveur:8000/admin/</pre>


<p>Cette interface est pleinement sécurisé pour peu que vous n<em>y donniez pas accès à n</em>importe qui avec des permissions gênantes.</p>


<p>Vous y trouverez les écrans d''administrations de toute les applications.</p>


<p>Vous pouvez créer des <strong>groupes</strong> de modérations et leur associer des <strong>permissions</strong>, ce qui vous permettra ensuite de gérer efficacement votre équipe de modération.</p>


<p><strong>Attention</strong> cet espace est reservé à l<em>administration. Il est conseillé de ne donner le droit d</em>accès <code>is_staff</code> à cette interface qu<em>à des personnes </em><em>averties</em><em>. En effet certains ajouts d</em>objets ont besoin de relations qui ne sont pas incluses dans les modèles eux mêmes mais dans le manipulateur des formulaires du site qui n<em>ont aucun rapport avec ceux de l</em>interface d''administration de Django. Cette dernière est auto-générée et gérée directement par Django gràce aux modèles de données.</p>


<h3 id="wikititle_14">Conseils d''utilisations</h3>


<p>Pour une mise en production, il est fortement déconseillé d<em>utiliser directement le serveur embarqué dans Django, mais plutôt Apache2+mod_python.<sup>[<a href="#wiki-footnote-011" id="rev-wiki-footnote-011">11</a>]</sup> et désactivez le </em><em>directory listing</em>''.</p>


<p>Plusieurs méthodes sont possibles, deux ont été testés avec <a href="/Shoop/">Shoop</a>. La première solution est à base de Apache+mod_python, la seconde à partir de FastCgi plus un autre serveur web.</p>


<h4 id="wikititle_15">Apache + mod_python</h4>


<p>Un exemple d''installation pour un serveur Apache2.0 avec le module <strong>mod_python</strong> installé et activé.</p>


<h5 id="wikititle_16">Vhost complet</h5>


<p>Vous pouvez simplement tout mettre dans un seul Vhost. La partie <em></em>dynamique<em></em> gérée par Django ainsi que les médias gérés directement par Apache comme de simples fichiers <em></em>statiques<em></em>.</p>


<pre>   &#60;VirtualHost X.X.X.X&#62;
           ServerAdmin webmaster@sveetch.net
           ServerName dax.sveetch.net
           SetHandler python-program
           PythonHandler django.core.handlers.modpython
           PythonPath "[<em>/home/shoop/</em>] + sys.path"
           SetEnv DJANGO_SETTINGS_MODULE shoop.settings
           PythonDebug Off
           PythonAutoReload Off
           # Url du fichier robot (optionnel)
           # Alias /robot.txt "/home/shoop/robot.txt"
           # &#60;Location "/robot.txt"&#62;
           #     SetHandler None
           # &#60;/Location&#62;
           # Médias sur le meme domaine (en mode DEBUG désactivé)
           Alias /site_medias "/home/shoop/site_medias"
           &#60;Location "/site_medias"&#62;
                SetHandler None
           &#60;/Location&#62;
           CustomLog /home/shoop/logs/shoop.fr-access_log combined
           ErrorLog /home/shoop/logs/shoop.fr-error_log
   &#60;/VirtualHost&#62;</pre>


<p>Il est possible que pour une raison vous n''ayez pas installé Django dans le site-package de Python, pour indiquer à Apache ou se trouve votre installation de Django il suffit de modifier la ligne du PythonPath comme ceci&#160;:</p>


<pre>           PythonPath "[<em>/path/to/Django-0.96</em>, <em>/home/shoop/</em>] + sys.path"</pre>


<h5 id="wikititle_17">Vhost Apache pour Django et Lighttpd pour les médias</h5>


<p>Il est conseillé d<em>utiliser cette solution supplémentaire qui permet de séparer la gestion des médias de la partie Django </em><em>dynamique</em><em>. Notez qu</em>il est tout aussi possible de faire un vhost supplémentaire dans Apache pour gérer ces médias, cela dit lighttpd est beaucoup mieux dimensionné pour s''en occuper.</p>


<p>Configurez le wwwroot (ou bien un vhost) de lighttpd pour servir le répertoire <code>$SHOOP/site_medias/</code>, attention lighttpd doit bien sûr tourner sur un autre port que ceux utilisés par Apache.</p>


<p>Ensuite deux options soit vous utilisez directement le domaine globale ou l<em>ip de votre serveur avec son port et vous n</em>avez rien à faire, soit vous souhaitez utiliser un nom de domaine sans port dans l<em>adresse (tel que </em><em>medias.foo.com</em><em>) et il vous faudra faire une redirection dans un vhost apache vers lighttpd avec un </em><em>rewriting</em><em> d</em>url.</p>


<pre>   &#60;VirtualHost *:80&#62;
           ServerAdmin webmaster@mygroovypod.com
           DocumentRoot /home/shoop/site_medias
           SuexecUserGroup shoop users
           ServerName medias.sveetch.net
           CustomLog /home/shoop/logs/medias.shoop.fr-access_log combined
           SetHandler None
           RewriteEngine On
           RewriteRule ^/(.*) http://sveetch.net:81/$1 [P]
   &#60;/VirtualHost&#62;</pre>


<h4 id="wikititle_18">FastCgi</h4>


<p>Avec FastCgi, vous n<em>êtes pas limité au choix de Apache, lighttpd et nginx sont aussi un choix possible. Dans cette situation le serveur web ne fait que transmettre la requête à un démon FastCgi s</em>occupant de gérer votre application.</p>


<p>Dans tout les cas, vous devrez installer module Python <strong>flup</strong><sup>[<a href="#wiki-footnote-012" id="rev-wiki-footnote-012">12</a>]</sup> avant tout.</p>


<p>Je ne traiterais que la méthode que j''ai testé donc avec Apache. Apache requiert que le module <strong>mod_fastcgi</strong> soit installé et activé. Ensuite il faut lancer le démon FastCgi avec par exemple la commande suivante depuis le répertoire parent de votre installation de <a href="/Shoop/">Shoop</a>&#160;:</p>


<pre> django-admin.py runfcgi --settings=shoop.prod_settings host=127.0.0.1 port=3303 pidfile=/home/django/shoop.pid</pre>


<p>On y indique le fichier de <em></em>settings<em></em> à utiliser, l<em>adresse hôte et le port pour atteindre le serveur FastCgi par le serveur web (donc une adresse ip interne est parfaite) et le pidfile qui permettra de retrouver le processus à </em><em>killer</em>'' pour stopper le serveur.</p>


<p>Ensuite on installe un vhost sur Apache tel que&#160;:</p>


<pre>   # Spécifie l<em>adresse interne ou retrouver l</em>application
   FastCGIExternalServer /home/django/projects/shoop/shoop.fcgi -host 127.0.0.1:3303
   # Le vhost en lui meme
   &#60;VirtualHost *:8000&#62;
           # Nécessaire pour que apache puisse accéder au shoop.fcgi et site_medias
           &#60;directory /home/django/projects/shoop/&#62;
                   Order deny,allow
                   Allow from all
           &#60;/directory&#62;
           # Pareil mais pour les medias de l''admin qui sont ailleurs
           &#60;directory /home/django/Django-0.96/django/contrib/admin/media/&#62;
                   Order deny,allow
                   Allow from all
           &#60;/directory&#62;
           DocumentRoot /home/django/projects/shoop
           # Logs
           CustomLog /home/django/logs/shoop-access_log combined
           ErrorLog /home/django/logs/shoop-error_log
           # Rewrite pour les parties statiques
           Alias /favicon.ico /home/django/projects/shoop/site_medias/favicon.ico
           Alias /crossdomain.xml /home/django/projects/shoop/crossdomain.xml
           Alias /shoop_medias /home/django/projects/shoop/site_medias
           Alias /admin_medias /home/django/Django-0.96/django/contrib/admin/media
           RewriteEngine On
           RewriteRule ^/(favicon.ico.*)$ /$1 [QSA,L,PT]
           RewriteRule ^/(crossdomain.xml.*)$ /$1 [QSA,L,PT]
           RewriteRule ^/(shoop_medias.*)$ /$1 [QSA,L,PT]
           RewriteRule ^/(admin_medias.*)$ /$1 [QSA,L,PT]
           RewriteCond %{REQUEST_FILENAME} !-f
           RewriteRule ^/(.*)$ /shoop.fcgi/$1 [QSA,L]
   &#60;/VirtualHost&#62;</pre>


<p>Voila, évidemment il est fortement conseillé de lire impérativement le document <a href="http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi/?from=olddocs">How to use Django with FastCGI, SCGI or AJP</a> pour plus de détails.</p>



<p>Contact&#160;: sveetch AT gmail DOT com</p>
<div class="footnotes"><h4>Notes</h4>
<p>[<a href="#rev-wiki-footnote-001" id="wiki-footnote-001">1</a>] <a href="http://www.djangoproject.com/documentation/0.96/install/">Django Installation guide</a></p>
<p>[<a href="#rev-wiki-footnote-002" id="wiki-footnote-002">2</a>] <a href="http://www.djangoproject.com/documentation/0.96/faq/#installation-questions">Django Installation FAQ</a></p>
<p>[<a href="#rev-wiki-footnote-003" id="wiki-footnote-003">3</a>] <a href="http://www.pythonware.com/products/pil/">Python Image Library</a></p>
<p>[<a href="#rev-wiki-footnote-004" id="wiki-footnote-004">4</a>] <a href="http://epydoc.sourceforge.net/">Automatic API Documentation Generation for Python</a></p>
<p>[<a href="#rev-wiki-footnote-005" id="wiki-footnote-005">5</a>] <a href="http://cheeseshop.python.org/pypi/setuptools">setuptools</a></p>
<p>[<a href="#rev-wiki-footnote-006" id="wiki-footnote-006">6</a>] <a href="http://svn.logicielslibres.info/bordel/sveetch/PyWiki2xhtml/">PyWiki2xhtml</a></p>
<p>[<a href="#rev-wiki-footnote-007" id="wiki-footnote-007">7</a>] <a href="http://svn.logicielslibres.info/bordel/sveetch/Sveetchies/">Sveetchies</a></p>
<p>[<a href="#rev-wiki-footnote-008" id="wiki-footnote-008">8</a>] <a href="http://www.tummy.com/Community/software/python-memcached/">Binding python pour memcached</a></p>
<p>[<a href="#rev-wiki-footnote-009" id="wiki-footnote-009">9</a>] <a href="http://www.initd.org/projects/psycopg1">Module psycopg</a></p>
<p>[<a href="#rev-wiki-footnote-010" id="wiki-footnote-010">10</a>] <a href="http://sourceforge.net/projects/mysql-python">MysqlDB pour Python</a></p>
<p>[<a href="#rev-wiki-footnote-011" id="wiki-footnote-011">11</a>] <a href="http://www.djangoproject.com/documentation/0.96/modpython/">Django+mod_python</a></p>
<p>[<a href="#rev-wiki-footnote-012" id="wiki-footnote-012">12</a>] <a href="http://trac.saddi.com/flup">flup</a></p></div>
"""