# -*- coding: utf-8 -*-

from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('datepicker', 'resources')

bootstrapdatepicker_css = Resource(
    library, 'bootstrap-datepicker.css',
    depends=[bootstrap_css],
    minified='bootstrap-datepicker.min.css',
    minifier='cssmin',
)

bootstrapdatepicker_js = Resource(
    library, 'bootstrap-datepicker.js',
    depends=[bootstrap_js],
    minified='bootstrap-datepicker.min.js',
    minifier='jsmin',
)

bootstrapdatepicker = Group([
    bootstrapdatepicker_css,
    bootstrapdatepicker_js,
])

bootstrapdatepicker_bg = Resource(
    library, 'locales/bootstrap-datepicker.bg.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.bg.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_ca = Resource(
    library, 'locales/bootstrap-datepicker.ca.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.ca.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_cs = Resource(
    library, 'locales/bootstrap-datepicker.cs.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.cs.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_da = Resource(
    library, 'locales/bootstrap-datepicker.da.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.da.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_de = Resource(
    library, 'locales/bootstrap-datepicker.de.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.de.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_el = Resource(
    library, 'locales/bootstrap-datepicker.el.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.el.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_es = Resource(
    library, 'locales/bootstrap-datepicker.es.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.es.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_et = Resource(
    library, 'locales/bootstrap-datepicker.et.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.et.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_fi = Resource(
    library, 'locales/bootstrap-datepicker.fi.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.fi.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_fr = Resource(
    library, 'locales/bootstrap-datepicker.fr.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.fr.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_he = Resource(
    library, 'locales/bootstrap-datepicker.he.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.he.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_hr = Resource(
    library, 'locales/bootstrap-datepicker.hr.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.hr.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_hu = Resource(
    library, 'locales/bootstrap-datepicker.hu.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.hu.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_id = Resource(
    library, 'locales/bootstrap-datepicker.id.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.id.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_is = Resource(
    library, 'locales/bootstrap-datepicker.is.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.is.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_it = Resource(
    library, 'locales/bootstrap-datepicker.it.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.it.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_ja = Resource(
    library, 'locales/bootstrap-datepicker.ja.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.ja.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_kr = Resource(
    library, 'locales/bootstrap-datepicker.kr.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.kr.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_lt = Resource(
    library, 'locales/bootstrap-datepicker.lt.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.lt.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_lv = Resource(
    library, 'locales/bootstrap-datepicker.lv.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.lv.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_mk = Resource(
    library, 'locales/bootstrap-datepicker.mk.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.mk.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_ms = Resource(
    library, 'locales/bootstrap-datepicker.ms.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.ms.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_nb = Resource(
    library, 'locales/bootstrap-datepicker.nb.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.nb.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_nl = Resource(
    library, 'locales/bootstrap-datepicker.nl.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.nl.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_pl = Resource(
    library, 'locales/bootstrap-datepicker.pl.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.pl.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_pt_BR = Resource(
    library, 'locales/bootstrap-datepicker.pt-BR.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.pt-BR.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_pt = Resource(
    library, 'locales/bootstrap-datepicker.pt.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.pt.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_ro = Resource(
    library, 'locales/bootstrap-datepicker.ro.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.ro.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_rs_latin = Resource(
    library, 'locales/bootstrap-datepicker.rs-latin.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.rs-latin.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_rs = Resource(
    library, 'locales/bootstrap-datepicker.rs.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.rs.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_ru = Resource(
    library, 'locales/bootstrap-datepicker.ru.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.ru.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_sk = Resource(
    library, 'locales/bootstrap-datepicker.sk.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.sk.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_sl = Resource(
    library, 'locales/bootstrap-datepicker.sl.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.sl.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_sq = Resource(
    library, 'locales/bootstrap-datepicker.sq.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.sq.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_sv = Resource(
    library, 'locales/bootstrap-datepicker.sv.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.sv.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_sw = Resource(
    library, 'locales/bootstrap-datepicker.sw.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.sw.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_th = Resource(
    library, 'locales/bootstrap-datepicker.th.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.th.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_tr = Resource(
    library, 'locales/bootstrap-datepicker.tr.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.tr.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_uk = Resource(
    library, 'locales/bootstrap-datepicker.uk.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.uk.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_zh_CN = Resource(
    library, 'locales/bootstrap-datepicker.zh-CN.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.zh-CN.min.js',
    minifier='jsmin',
)

bootstrapdatepicker_zh_TW = Resource(
    library, 'locales/bootstrap-datepicker.zh-TW.js',
    depends=[bootstrapdatepicker_js],
    minified='locales/bootstrap-datepicker.zh-TW.min.js',
    minifier='jsmin',
)


bootstrapdatepicker_locales = {
    "bg": bootstrapdatepicker_bg,
    "ca": bootstrapdatepicker_ca,
    "cs": bootstrapdatepicker_cs,
    "da": bootstrapdatepicker_da,
    "de": bootstrapdatepicker_de,
    "el": bootstrapdatepicker_el,
    "es": bootstrapdatepicker_es,
    "et": bootstrapdatepicker_et,
    "fi": bootstrapdatepicker_fi,
    "fr": bootstrapdatepicker_fr,
    "he": bootstrapdatepicker_he,
    "hr": bootstrapdatepicker_hr,
    "hu": bootstrapdatepicker_hu,
    "id": bootstrapdatepicker_id,
    "is": bootstrapdatepicker_is,
    "it": bootstrapdatepicker_it,
    "ja": bootstrapdatepicker_ja,
    "kr": bootstrapdatepicker_kr,
    "lt": bootstrapdatepicker_lt,
    "lv": bootstrapdatepicker_lv,
    "mk": bootstrapdatepicker_mk,
    "ms": bootstrapdatepicker_ms,
    "nb": bootstrapdatepicker_nb,
    "nl": bootstrapdatepicker_nl,
    "pl": bootstrapdatepicker_pl,
    "pt_BR": bootstrapdatepicker_pt_BR,
    "pt": bootstrapdatepicker_pt,
    "ro": bootstrapdatepicker_ro,
    "rs_latin": bootstrapdatepicker_rs_latin,
    "rs": bootstrapdatepicker_rs,
    "ru": bootstrapdatepicker_ru,
    "sk": bootstrapdatepicker_sk,
    "sl": bootstrapdatepicker_sl,
    "sq": bootstrapdatepicker_sq,
    "sv": bootstrapdatepicker_sv,
    "sw": bootstrapdatepicker_sw,
    "th": bootstrapdatepicker_th,
    "tr": bootstrapdatepicker_tr,
    "uk": bootstrapdatepicker_uk,
    "zh_CN": bootstrapdatepicker_zh_CN,
    "zh_TW": bootstrapdatepicker_zh_TW,
    "zh": bootstrapdatepicker_zh_CN,
}
