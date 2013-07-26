# -*- coding: utf-8 -*-
"""
Chaînes de textes utilisés pour les tests unitaires du parser avec macros et 
démonstration pour son helper.

Les variables qui se terminent en ``*_TEST_CASE`` sont des chaînes de textes 
utilisés comme sources pour les tests unitaires, ainsi que certaines par le 
helper.

Les variables qui se terminent en ``*_TEST_ATTEMPT*`` sont le résultats 
attendu par les tests unitaires pour les sources qui lui ont été données.
"""

# Macro 'htmlpass'
HTMLPASS_TEST_CASE = u"""{% htmlpass %}<div class="prout">
    <p><strong>Hello</strong> World !</p>
</div>{% endhtmlpass %}
"""

HTMLPASS_TEST_ATTEMPT = u"""<div class="macro_htmlpass"><div class="prout">
    <p><strong>Hello</strong> World !</p>
</div></div>"""

# Macro 'attach'
ATTACH_TEST_CASE = u"""Foo lorem ipsum salace nec vergiture.

* Moopa
** {% attach 1 %}{% endattach %}
* Moope
* [Moopi|http://sveetch.net/download.py?file=cocolapin.xls&validate=true]
** Moopo
** Moopu

Ceci est un {% attach 42 %}Plop de texte{% endattach %} mégamagique.

Mais ça c'est totalement {% attach 33 %}pas correct{% endattach %} alors que ceci le devrait : {% attach 11 %}{% endattach %}.
"""

ATTACH_TEST_ATTEMPT = u"""<p>Foo lorem ipsum salace nec vergiture.</p>

<ul>
<li>Moopa
<ul>
<li><a href="http://perdu.com/prout.pdf">Prout !</a></li>
</ul></li>
<li>Moope</li>
<li><a href="http://sveetch.net/download.py?file=cocolapin.xls&#38;validate=true">Moopi</a>
<ul>
<li>Moopo</li>
<li>Moopu</li>
</ul></li>
</ul>

<p>Ceci est un <a href="http://sveetch.net/download.py?coco%7Cfile=cocolapin.xls&#38;validate=true">Plop de texte</a> mégamagique.</p>


<p>Mais ça c'est totalement pas correct alors que ceci le devrait&#160;: <a href="http://perdu.com/plouf.pdf">http://perdu.com/plouf.pdf</a>.</p>"""

# Macro 'mediaplayer'
MEDIAPLAYER_TEST_CASE = u"""{% mediaplayer %}
file: /medias/flash/mediaplayer/video.flv
src: /medias/flash/mediaplayer/player.swf
{% endmediaplayer %}
"""

MEDIAPLAYER_TEST_ATTEMPT = u"""<div class="macro_mediaplayer">
<div id="mediaplayer_0" class="player_container"></div>
<script type="text/javascript">
//<![CDATA[
$('#mediaplayer_0').flash({
        'width': '320', 'allowfullscreen': 'true', 'src': '/medias/flash/mediaplayer/player.swf', 'allowscriptaccess': 'always', 'height': '240',
        'flashvars': { 'file': '/medias/flash/mediaplayer/video.flv' }
    },
    { version: '9.0' }
);
//]]>
</script>
</div>
"""

# Macro 'googlemap'
GMAP_TEST_CASE = u"""{% googlemap "6 rue Auber, 93150 Le Blanc Mesnil" %}__Sveetch.Biz,__

6 rue Auber,

93150 Le Blanc Mesnil
{% endgooglemap %}
"""

GMAP_TEST_ATTEMPT = u"""coco"""

# Macro 'pygments'
PYGMENTS_TEST_CASE = u"""{% pygments javascript withlineos %}
/**
** Un faux script Javascript
** ________________________________________
**/
$(document).ready(function(){
    alert("Hello World");
});
{% endpygments %}
"""

PYGMENTS_TEST_ATTEMPT = u"""<table class="highlighttable"><tr><td class="linenos"><pre>1
2
3
4
5
6
7</pre></td><td class="code"><div class="highlight"><pre><span style="color: #408080; font-style: italic">/**</span>
<span style="color: #408080; font-style: italic">** Un faux script Javascript</span>
<span style="color: #408080; font-style: italic">** ________________________________________</span>
<span style="color: #408080; font-style: italic">**/</span>
$(<span style="color: #008000">document</span>).ready(<span style="color: #008000; font-weight: bold">function</span>(){
    alert(<span style="color: #BA2121">&quot;Hello World&quot;</span>);
});
</pre></div>
</td></tr></table>"""

# Macro 'pygments'
HELLOWORLDS_TEST_CASE = u"""{% helloworld2 %}
Lorem ipsum salace,
nec vergiture.
{% endhelloworld2 %}

* Turlu tutu
* Chapeau pointu

{% helloworld %}foo __bar__ et pouet{% endhelloworld %}
"""

HELLOWORLDS_TEST_ATTEMPT = u"""<p class="helloworld2">Hello World : 
Lorem ipsum salace,
nec vergiture.
</p>

<ul>
<li>Turlu tutu</li>
<li>Chapeau pointu</li>
</ul>

<p><ins>Hello World&#160;: foo <strong>bar</strong> et pouet</ins></p>"""

# Macro 'pygments'
ALL_MACROS_TEST_CASE = u"""!!! Intro

Les macros doivent permettre d'inclure un système de plugin
accessibles et __utilisables par les utilisateurs__.

{% helloworld2 %}
Lorem ipsum salace,
nec vergiture.
{% endhelloworld2 %}

Le but est que get_macros soit instancier avant toute recherche sur le 
texte dans le vrai parser wiki, que tout les motifs de macro start/end soit 

{% htmlpass %}<div class="prout">
    <p>FOO!</p>
</div>{% endhtmlpass %}

remplacé par un code de macro avec un serial et d'associer à ce serial le 
contenu de la macro. 

{% pygments javascript withlineos %}
/**
** Hack CSS dégueux via Javascript
** ________________________________________
**/
$(document).ready(function(){
    $("#body_content div.content_container, #submenu div.container").equalizeCols();
});
{% endpygments %}

{% prout %}tupu{% endprout %}

{% mediaplayer %}
file: cam_live_svee.flv
streamer: rtmp://192.168.0.101:1935/mgpC1
width: 450
height: 350
{% endmediaplayer %}

{% helloworld %}foo __bar__ et pouet{% endhelloworld %}

Fin du texte.
"""

ALL_MACROS_TEST_ATTEMPT = u"""<h3 id="wikititle_1">Intro</h3>


<p>Les macros doivent permettre d'inclure un système de plugin
accessibles et <strong>utilisables par les utilisateurs</strong>.</p>

<p class="helloworld2">Hello World : 
Lorem ipsum salace,
nec vergiture.
</p>


<p>Le but est que get_macros soit instancier avant toute recherche sur le
texte dans le vrai parser wiki, que tout les motifs de macro start/end soit</p>

<div class="macro_htmlpass"><div class="prout">
    <p>FOO!</p>
</div></div>


<p>remplacé par un code de macro avec un serial et d'associer à ce serial le
contenu de la macro.</p>

<table class="highlighttable"><tr><td class="linenos"><pre>1
2
3
4
5
6
7</pre></td><td class="code"><div class="highlight"><pre><span style="color: #408080; font-style: italic">/**</span>
<span style="color: #408080; font-style: italic">** Hack CSS dégueux via Javascript</span>
<span style="color: #408080; font-style: italic">** ________________________________________</span>
<span style="color: #408080; font-style: italic">**/</span>
$(<span style="color: #008000">document</span>).ready(<span style="color: #008000; font-weight: bold">function</span>(){
    $(<span style="color: #BA2121">&quot;#body_content div.content_container, #submenu div.container&quot;</span>).equalizeCols();
});
</pre></div>
</td></tr></table>


<p>{% prout %}tupu{% endprout %}</p>

<div class="macro_mediaplayer">
<div id="mediaplayer_1" class="player_container"></div>
<script type="text/javascript">
//<![CDATA[
$('#mediaplayer_1').flash({
        'width': '450', 'allowfullscreen': 'true', 'src': 'player.swf', 'allowscriptaccess': 'always', 'height': '350',
        'flashvars': { 'streamer': 'rtmp://192.168.0.101:1935/mgpC1', 'file': 'cam_live_svee.flv' }
    },
    { version: '9.0' }
);
//]]>
</script>
</div>



<p><ins>Hello World&#160;: foo <strong>bar</strong> et pouet</ins></p>


<p>Fin du texte.</p>"""

# Paquet des macros disponibles
ACTIVE_MACROS = {
    'htmlpass' : [
        u"Insertion de html",
        HTMLPASS_TEST_CASE,
    ],
    'mediaplayer' : [
        u"Insertion d'un player audio/vidéo",
        MEDIAPLAYER_TEST_CASE,
    ],
    'pygments' : [
        u"Coloration syntaxique de code par Pygments",
        PYGMENTS_TEST_CASE,
    ],
    'attach' : [
        u"Gestion d'attachement de fichiers",
        ATTACH_TEST_CASE,
    ],
    'googlemap' : [
        u"Insertion d'une carte de localisation graphique avec GoogleMap",
        GMAP_TEST_CASE,
    ],
}
