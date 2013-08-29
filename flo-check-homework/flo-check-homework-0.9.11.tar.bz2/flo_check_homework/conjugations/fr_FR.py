# -*- coding: utf-8 -*-

# fr_FR.py --- Conjugation of some French verbs
# Copyright (c) 2011, 2012, 2013 Florent Rougon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA.


conj_subjects = [ "1re pers. sing.",
                  "2e pers. sing.",
                  "3e pers. sing.",
                  "1re pers. plur.",
                  "2e pers. plur.",
                  "3e pers. plur." ]

valid_tenses = { "présent de l'indicatif": "au ",
                 "passé composé de l'indicatif": "au ",
                 "imparfait de l'indicatif": "à l'",
                 "plus-que-parfait de l'indicatif": "au ",
                 "passé simple de l'indicatif": "au ",
                 "passé antérieur de l'indicatif": "au ",
                 "futur simple de l'indicatif": "au ",
                 "futur antérieur de l'indicatif": "au ",
                 "présent du subjonctif": "au ",
                 "passé du subjonctif": "au ",
                 "imparfait du subjonctif": "à l'",
                 "plus-que-parfait du subjonctif": "au ",
                 "présent de l'impératif": "au ",
                 "passé de l'impératif": "au ",
                 "présent du conditionnel": "au ",
                 "passé 1re forme du conditionnel": "au ",
                 "passé 2de forme du conditionnel": "au " }

instructions = {
    "standard": "Conjuguer le verbe {verb} {tense_spec}",
    "Qt rich text":
        "Mot de passe <i>conjugaisons</i> : verbe <i>{verb}</i> {tense_spec}" }

conj = {
    "trouver": {"présent de l'indicatif":
                    [ "je trouve",
                      "tu trouves",
                      "il trouve",
                      "nous trouvons",
                      "vous trouvez",
                      "ils trouvent" ],
                "futur simple de l'indicatif":
                    [ "je trouverai",
                      "tu trouveras",
                      "il trouvera",
                      "nous trouverons",
                      "vous trouverez",
                      "ils trouveront" ],
                "imparfait de l'indicatif":
                    [ "je trouvais",
                      "tu trouvais",
                      "il trouvait",
                      "nous trouvions",
                      "vous trouviez",
                      "ils trouvaient" ],
                "passé composé de l'indicatif":
                    [ "j'ai trouvé",
                      "tu as trouvé",
                      "il a trouvé",
                      "nous avons trouvé",
                      "vous avez trouvé",
                      "ils ont trouvé" ],
                "passé simple de l'indicatif":
                    [ "je trouvai",
                      "tu trouvas",
                      "il trouva",
                      "nous trouvâmes",
                      "vous trouvâtes",
                      "ils trouvèrent" ]
                },
    "finir": {"présent de l'indicatif":
                  [ "je finis",
                    "tu finis",
                    "il finit",
                    "nous finissons",
                    "vous finissez",
                    "ils finissent" ],
              "futur simple de l'indicatif":
                  [ "je finirai",
                    "tu finiras",
                    "il finira",
                    "nous finirons",
                    "vous finirez",
                    "ils finiront" ],
              "imparfait de l'indicatif":
                  [ "je finissais",
                    "tu finissais",
                    "il finissait",
                    "nous finissions",
                    "vous finissiez",
                    "ils finissaient" ],
              "passé composé de l'indicatif":
                  [ "j'ai fini",
                    "tu as fini",
                    "il a fini",
                    "nous avons fini",
                    "vous avez fini",
                    "ils ont fini" ],
              "passé simple de l'indicatif":
                  [ "je finis",
                    "tu finis",
                    "il finit",
                    "nous finîmes",
                    "vous finîtes",
                    "ils finirent" ]
              },
    "pouvoir": {"présent de l'indicatif":
                    [ "je peux",
                      "tu peux",
                      "il peut",
                      "nous pouvons",
                      "vous pouvez",
                      "ils peuvent" ],
                "futur simple de l'indicatif":
                    [ "je pourrai",
                      "tu pourras",
                      "il pourra",
                      "nous pourrons",
                      "vous pourrez",
                      "ils pourront" ],
                "imparfait de l'indicatif":
                    [ "je pouvais",
                      "tu pouvais",
                      "il pouvait",
                      "nous pouvions",
                      "vous pouviez",
                      "ils pouvaient" ],
                "passé composé de l'indicatif":
                    [ "j'ai pu",
                      "tu as pu",
                      "il a pu",
                      "nous avons pu",
                      "vous avez pu",
                      "ils ont pu" ],
                "passé simple de l'indicatif":
                    [ "je pus",
                      "tu pus",
                      "il put",
                      "nous pûmes",
                      "vous pûtes",
                      "ils purent" ]
                },
    "prendre": {"présent de l'indicatif":
                    [ "je prends",
                      "tu prends",
                      "il prend",
                      "nous prenons",
                      "vous prenez",
                      "ils prennent" ],
                "futur simple de l'indicatif":
                    [ "je prendrai",
                      "tu prendras",
                      "il prendra",
                      "nous prendrons",
                      "vous prendrez",
                      "ils prendront" ],
                "imparfait de l'indicatif":
                    [ "je prenais",
                      "tu prenais",
                      "il prenait",
                      "nous prenions",
                      "vous preniez",
                      "ils prenaient" ],
                "passé composé de l'indicatif":
                    [ "j'ai pris",
                      "tu as pris",
                      "il a pris",
                      "nous avons pris",
                      "vous avez pris",
                      "ils ont pris" ],
                "passé simple de l'indicatif":
                    [ "je pris",
                      "tu pris",
                      "il prit",
                      "nous prîmes",
                      "vous prîtes",
                      "ils prirent" ]
                },
    "apprendre": {"présent de l'indicatif":
                      [ "j'apprends",
                        "tu apprends",
                        "il apprend",
                        "nous apprenons",
                        "vous apprenez",
                        "ils apprennent" ],
                  "futur simple de l'indicatif":
                      [ "j'apprendrai",
                        "tu apprendras",
                        "il apprendra",
                        "nous apprendrons",
                        "vous apprendrez",
                        "ils apprendront" ],
                  "imparfait de l'indicatif":
                      [ "j'apprenais",
                        "tu apprenais",
                        "il apprenait",
                        "nous apprenions",
                        "vous appreniez",
                        "ils apprenaient" ],
                  "passé composé de l'indicatif":
                      [ "j'ai appris",
                        "tu as appris",
                        "il a appris",
                        "nous avons appris",
                        "vous avez appris",
                        "ils ont appris" ],
                  "passé simple de l'indicatif":
                      [ "j'appris",
                        "tu appris",
                        "il apprit",
                        "nous apprîmes",
                        "vous apprîtes",
                        "ils apprirent" ]
                  },
    "être": {"présent de l'indicatif":
                 [ "je suis",
                   "tu es",
                   "il est",
                   "nous sommes",
                   "vous êtes",
                   "ils sont" ],
             "futur simple de l'indicatif":
                 [ "je serai",
                   "tu seras",
                   "il sera",
                   "nous serons",
                   "vous serez",
                   "ils seront" ],
             "imparfait de l'indicatif":
                 [ "j'étais",
                   "tu étais",
                   "il était",
                   "nous étions",
                   "vous étiez",
                   "ils étaient" ],
             "passé composé de l'indicatif":
                 [ "j'ai été",
                   "tu as été",
                   "il a été",
                   "nous avons été",
                   "vous avez été",
                   "ils ont été" ],
             "passé simple de l'indicatif":
                 [ "je fus",
                   "tu fus",
                   "il fut",
                   "nous fûmes",
                   "vous fûtes",
                   "ils furent" ] },
    "avoir": {"présent de l'indicatif":
                  [ "j'ai",
                    "tu as",
                    "il a",
                    "nous avons",
                    "vous avez",
                    "ils ont" ],
              "futur simple de l'indicatif":
                  [ "j'aurai",
                    "tu auras",
                    "il aura",
                    "nous aurons",
                    "vous aurez",
                    "ils auront" ],
              "imparfait de l'indicatif":
                  [ "j'avais",
                    "tu avais",
                    "il avait",
                    "nous avions",
                    "vous aviez",
                    "ils avaient" ],
              "passé composé de l'indicatif":
                  [ "j'ai eu",
                    "tu as eu",
                    "il a eu",
                    "nous avons eu",
                    "vous avez eu",
                    "ils ont eu" ],
              "passé simple de l'indicatif":
                  [ "j'eus",
                    "tu eus",
                    "il eut",
                    "nous eûmes",
                    "vous eûtes",
                    "ils eurent" ] },
    "aller": {"présent de l'indicatif":
                  [ "je vais",
                    "tu vas",
                    "il va",
                    "nous allons",
                    "vous allez",
                    "ils vont" ],
              "futur simple de l'indicatif":
                  [ "j'irai",
                    "tu iras",
                    "il ira",
                    "nous irons",
                    "vous irez",
                    "ils iront" ],
              "imparfait de l'indicatif":
                  [ "j'allais",
                    "tu allais",
                    "il allait",
                    "nous allions",
                    "vous alliez",
                    "ils allaient" ],
              "passé composé de l'indicatif":
                  [ "je suis allé",
                    "tu es allé",
                    "il est allé",
                    "nous sommes allés",
                    "vous êtes allés",
                    "ils sont allés" ],
              "passé simple de l'indicatif":
                  [ "j'allai",
                    "tu allas",
                    "il alla",
                    "nous allâmes",
                    "vous allâtes",
                    "ils allèrent" ] },
    "dire": {"présent de l'indicatif":
                 [ "je dis",
                   "tu dis",
                   "il dit",
                   "nous disons",
                   "vous dites",
                   "ils disent" ],
             "futur simple de l'indicatif":
                 [ "je dirai",
                   "tu diras",
                   "il dira",
                   "nous dirons",
                   "vous direz",
                   "ils diront" ],
             "imparfait de l'indicatif":
                 [ "je disais",
                   "tu disais",
                   "il disait",
                   "nous disions",
                   "vous disiez",
                   "ils disaient" ],
             "passé composé de l'indicatif":
                 [ "j'ai dit",
                   "tu as dit",
                   "il a dit",
                   "nous avons dit",
                   "vous avez dit",
                   "ils ont dit" ],
             "passé simple de l'indicatif":
                 [ "je dis",
                   "tu dis",
                   "il dit",
                   "nous dîmes",
                   "vous dîtes",
                   "ils dirent" ] },
    "faire": {"présent de l'indicatif":
                  [ "je fais",
                    "tu fais",
                    "il fait",
                    "nous faisons",
                    "vous faites",
                    "ils font" ],
              "futur simple de l'indicatif":
                  [ "je ferai",
                    "tu feras",
                    "il fera",
                    "nous ferons",
                    "vous ferez",
                    "ils feront" ],
              "imparfait de l'indicatif":
                  [ "je faisais",
                    "tu faisais",
                    "il faisait",
                    "nous faisions",
                    "vous faisiez",
                    "ils faisaient" ],
              "passé composé de l'indicatif":
                  [ "j'ai fait",
                    "tu as fait",
                    "il a fait",
                    "nous avons fait",
                    "vous avez fait",
                    "ils ont fait" ],
              "passé simple de l'indicatif":
                  [ "je fis",
                    "tu fis",
                    "il fit",
                    "nous fîmes",
                    "vous fîtes",
                    "ils firent" ] },
    "partir": {"présent de l'indicatif":
                   [ "je pars",
                     "tu pars",
                     "il part",
                     "nous partons",
                     "vous partez",
                     "ils partent" ],
               "futur simple de l'indicatif":
                   [ "je partirai",
                     "tu partiras",
                     "il partira",
                     "nous partirons",
                     "vous partirez",
                     "ils partiront" ],
               "imparfait de l'indicatif":
                   [ "je partais",
                     "tu partais",
                     "il partait",
                     "nous partions",
                     "vous partiez",
                     "ils partaient" ],
               "passé composé de l'indicatif":
                   [ "je suis parti",
                     "tu es parti",
                     "il est parti",
                     "nous sommes partis",
                     "vous êtes partis",
                     "ils sont partis" ],
               "passé simple de l'indicatif":
                   [ "je partis",
                     "tu partis",
                     "il partit",
                     "nous partîmes",
                     "vous partîtes",
                     "ils partirent" ] },
    "venir": {"présent de l'indicatif":
                  [ "je viens",
                    "tu viens",
                    "il vient",
                    "nous venons",
                    "vous venez",
                    "ils viennent" ],
              "futur simple de l'indicatif":
                  [ "je viendrai",
                    "tu viendras",
                    "il viendra",
                    "nous viendrons",
                    "vous viendrez",
                    "ils viendront" ],
              "imparfait de l'indicatif":
                  [ "je venais",
                    "tu venais",
                    "il venait",
                    "nous venions",
                    "vous veniez",
                    "ils venaient" ],
              "passé composé de l'indicatif":
                  [ "je suis venu",
                    "tu es venu",
                    "il est venu",
                    "nous sommes venus",
                    "vous êtes venus",
                    "ils sont venus" ],
              "passé simple de l'indicatif":
                  [ "je vins",
                    "tu vins",
                    "il vint",
                    "nous vînmes",
                    "vous vîntes",
                    "ils vinrent" ] },
    "voir": {"présent de l'indicatif":
                 [ "je vois",
                   "tu vois",
                   "il voit",
                   "nous voyons",
                   "vous voyez",
                   "ils voient" ],
             "futur simple de l'indicatif":
                 [ "je verrai",
                   "tu verras",
                   "il verra",
                   "nous verrons",
                   "vous verrez",
                   "ils verront" ],
             "imparfait de l'indicatif":
                 [ "je voyais",
                   "tu voyais",
                   "il voyait",
                   "nous voyions",
                   "vous voyiez",
                   "ils voyaient" ],
             "passé composé de l'indicatif":
                 [ "j'ai vu",
                   "tu as vu",
                   "il a vu",
                   "nous avons vu",
                   "vous avez vu",
                   "ils ont vu" ],
             "passé simple de l'indicatif":
                 [ "je vis",
                   "tu vis",
                   "il vit",
                   "nous vîmes",
                   "vous vîtes",
                   "ils virent" ] },
    "vouloir": {"présent de l'indicatif":
                    [ "je veux",
                      "tu veux",
                      "il veut",
                      "nous voulons",
                      "vous voulez",
                      "ils veulent" ],
                "futur simple de l'indicatif":
                    [ "je voudrai",
                      "tu voudras",
                      "il voudra",
                      "nous voudrons",
                      "vous voudrez",
                      "ils voudront" ],
                "imparfait de l'indicatif":
                    [ "je voulais",
                      "tu voulais",
                      "il voulait",
                      "nous voulions",
                      "vous vouliez",
                      "ils voulaient" ],
                "passé composé de l'indicatif":
                    [ "j'ai voulu",
                      "tu as voulu",
                      "il a voulu",
                      "nous avons voulu",
                      "vous avez voulu",
                      "ils ont voulu" ],
                "passé simple de l'indicatif":
                    [ "je voulus",
                      "tu voulus",
                      "il voulut",
                      "nous voulûmes",
                      "vous voulûtes",
                      "ils voulurent" ] }
    }

#     "": {"présent de l'indicatif":
#               [ "je ",
#                 "tu ",
#                 "il ",
#                 "nous ",
#                 "vous ",
#                 "ils " ],
#           "futur simple de l'indicatif":
#               [ "je rai",
#                 "tu ras",
#                 "il ra",
#                 "nous rons",
#                 "vous rez",
#                 "ils ront" ],
#           "imparfait de l'indicatif":
#               [ "je ais",
#                 "tu ais",
#                 "il ait",
#                 "nous ions",
#                 "vous iez",
#                 "ils aient" ],
#           "passé composé de l'indicatif":
#               [ "j'ai ",
#                 "tu as ",
#                 "il a ",
#                 "nous avons ",
#                 "vous avez ",
#                 "ils ont " ],
#           "passé simple de l'indicatif":
#               [ "je ",
#                 "tu ",
#                 "il ",
#                 "nous ",
#                 "vous ",
#                 "ils " ] }


def tense_spec(tense):
    return "{0}{1}".format(valid_tenses[tense], tense)

def instruction(instr_type, verb, tense):
     return instructions[instr_type].format(verb=verb,
                                            tense_spec=tense_spec(tense))

def sanity_checks():
    for verb, t in conj.items():
        assert verb.strip() == verb, \
            "verb %s has leading or trailing whitespace" % repr(self.result)

        for tense, l in t.items():
            assert tense in valid_tenses, \
                "tense %s for verb %s not in valid_tenses" % (repr(tense),
                                                               repr(verb))
            for i, c in enumerate(l):
                assert c.strip() == c, \
                    ("conjugation %s (verb=%s, tense=%s, person=%u) "\
                         "has leading or trailing whitespace") \
                         % (repr(c), repr(verb), repr(tense), i+1)


def print_stuff():
    print(repr(list(conj.keys())))
    print(repr(list(valid_tenses.keys())))
    print(repr(used_tenses))

sanity_checks()
used_tenses = frozenset((tense for verb in conj for tense in conj[verb]))

# print_stuff()
