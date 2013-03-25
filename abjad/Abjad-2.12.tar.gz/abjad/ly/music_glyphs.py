lilypond_version = "2.17.9"

music_glyphs = set([
    "accidentals.doublesharp",
    "accidentals.flat",
    "accidentals.flat.arrowboth",
    "accidentals.flat.arrowdown",
    "accidentals.flat.arrowup",
    "accidentals.flat.slash",
    "accidentals.flat.slashslash",
    "accidentals.flatflat",
    "accidentals.flatflat.slash",
    "accidentals.hufnagelM1",
    "accidentals.kievan1",
    "accidentals.kievanM1",
    "accidentals.leftparen",
    "accidentals.medicaeaM1",
    "accidentals.mensural1",
    "accidentals.mensuralM1",
    "accidentals.mirroredflat",
    "accidentals.mirroredflat.backslash",
    "accidentals.mirroredflat.flat",
    "accidentals.natural",
    "accidentals.natural.arrowboth",
    "accidentals.natural.arrowdown",
    "accidentals.natural.arrowup",
    "accidentals.rightparen",
    "accidentals.sharp",
    "accidentals.sharp.arrowboth",
    "accidentals.sharp.arrowdown",
    "accidentals.sharp.arrowup",
    "accidentals.sharp.slashslash.stem",
    "accidentals.sharp.slashslash.stemstemstem",
    "accidentals.sharp.slashslashslash.stem",
    "accidentals.sharp.slashslashslash.stemstem",
    "accidentals.vaticana0",
    "accidentals.vaticanaM1",
    "accordion.bayanbass",
    "accordion.discant",
    "accordion.dot",
    "accordion.freebass",
    "accordion.oldEE",
    "accordion.pull",
    "accordion.push",
    "accordion.stdbass",
    "arrowheads.close.01",
    "arrowheads.close.0M1",
    "arrowheads.close.11",
    "arrowheads.close.1M1",
    "arrowheads.open.01",
    "arrowheads.open.0M1",
    "arrowheads.open.11",
    "arrowheads.open.1M1",
    "brackettips.down",
    "brackettips.up",
    "clefs.C",
    "clefs.C_change",
    "clefs.F",
    "clefs.F_change",
    "clefs.G",
    "clefs.G_change",
    "clefs.blackmensural.c",
    "clefs.blackmensural.c_change",
    "clefs.hufnagel.do",
    "clefs.hufnagel.do.fa",
    "clefs.hufnagel.do.fa_change",
    "clefs.hufnagel.do_change",
    "clefs.hufnagel.fa",
    "clefs.hufnagel.fa_change",
    "clefs.kievan.do",
    "clefs.kievan.do_change",
    "clefs.medicaea.do",
    "clefs.medicaea.do_change",
    "clefs.medicaea.fa",
    "clefs.medicaea.fa_change",
    "clefs.mensural.c",
    "clefs.mensural.c_change",
    "clefs.mensural.f",
    "clefs.mensural.f_change",
    "clefs.mensural.g",
    "clefs.mensural.g_change",
    "clefs.neomensural.c",
    "clefs.neomensural.c_change",
    "clefs.percussion",
    "clefs.percussion_change",
    "clefs.petrucci.c1",
    "clefs.petrucci.c1_change",
    "clefs.petrucci.c2",
    "clefs.petrucci.c2_change",
    "clefs.petrucci.c3",
    "clefs.petrucci.c3_change",
    "clefs.petrucci.c4",
    "clefs.petrucci.c4_change",
    "clefs.petrucci.c5",
    "clefs.petrucci.c5_change",
    "clefs.petrucci.f",
    "clefs.petrucci.f_change",
    "clefs.petrucci.g",
    "clefs.petrucci.g_change",
    "clefs.tab",
    "clefs.tab_change",
    "clefs.vaticana.do",
    "clefs.vaticana.do_change",
    "clefs.vaticana.fa",
    "clefs.vaticana.fa_change",
    "comma",
    "custodes.hufnagel.d0",
    "custodes.hufnagel.d1",
    "custodes.hufnagel.d2",
    "custodes.hufnagel.u0",
    "custodes.hufnagel.u1",
    "custodes.hufnagel.u2",
    "custodes.medicaea.d0",
    "custodes.medicaea.d1",
    "custodes.medicaea.d2",
    "custodes.medicaea.u0",
    "custodes.medicaea.u1",
    "custodes.medicaea.u2",
    "custodes.mensural.d0",
    "custodes.mensural.d1",
    "custodes.mensural.d2",
    "custodes.mensural.u0",
    "custodes.mensural.u1",
    "custodes.mensural.u2",
    "custodes.vaticana.d0",
    "custodes.vaticana.d1",
    "custodes.vaticana.d2",
    "custodes.vaticana.u0",
    "custodes.vaticana.u1",
    "custodes.vaticana.u2",
    "dots.dot",
    "dots.dotkievan",
    "dots.dotvaticana",
    "eight",
    "f",
    "five",
    "flags.d3",
    "flags.d4",
    "flags.d5",
    "flags.d6",
    "flags.d7",
    "flags.dgrace",
    "flags.mensurald03",
    "flags.mensurald04",
    "flags.mensurald05",
    "flags.mensurald06",
    "flags.mensurald13",
    "flags.mensurald14",
    "flags.mensurald15",
    "flags.mensurald16",
    "flags.mensurald23",
    "flags.mensurald24",
    "flags.mensurald25",
    "flags.mensurald26",
    "flags.mensuralu03",
    "flags.mensuralu04",
    "flags.mensuralu05",
    "flags.mensuralu06",
    "flags.mensuralu13",
    "flags.mensuralu14",
    "flags.mensuralu15",
    "flags.mensuralu16",
    "flags.mensuralu23",
    "flags.mensuralu24",
    "flags.mensuralu25",
    "flags.mensuralu26",
    "flags.u3",
    "flags.u4",
    "flags.u5",
    "flags.u6",
    "flags.u7",
    "flags.ugrace",
    "four",
    "hyphen",
    "m",
    "nine",
    "noteheads.d0doFunk",
    "noteheads.d0fa",
    "noteheads.d0faFunk",
    "noteheads.d0faThin",
    "noteheads.d0miFunk",
    "noteheads.d0reFunk",
    "noteheads.d0tiFunk",
    "noteheads.d1do",
    "noteheads.d1doFunk",
    "noteheads.d1doThin",
    "noteheads.d1doWalker",
    "noteheads.d1fa",
    "noteheads.d1faFunk",
    "noteheads.d1faThin",
    "noteheads.d1faWalker",
    "noteheads.d1miFunk",
    "noteheads.d1re",
    "noteheads.d1reFunk",
    "noteheads.d1reThin",
    "noteheads.d1reWalker",
    "noteheads.d1ti",
    "noteheads.d1tiFunk",
    "noteheads.d1tiThin",
    "noteheads.d1tiWalker",
    "noteheads.d1triangle",
    "noteheads.d2do",
    "noteheads.d2doFunk",
    "noteheads.d2doThin",
    "noteheads.d2doWalker",
    "noteheads.d2fa",
    "noteheads.d2faFunk",
    "noteheads.d2faThin",
    "noteheads.d2faWalker",
    "noteheads.d2kievan",
    "noteheads.d2re",
    "noteheads.d2reFunk",
    "noteheads.d2reThin",
    "noteheads.d2reWalker",
    "noteheads.d2ti",
    "noteheads.d2tiFunk",
    "noteheads.d2tiThin",
    "noteheads.d2tiWalker",
    "noteheads.d2triangle",
    "noteheads.d3kievan",
    "noteheads.dM2",
    "noteheads.dM2blackmensural",
    "noteheads.dM2mensural",
    "noteheads.dM2neomensural",
    "noteheads.dM2semimensural",
    "noteheads.dM3blackmensural",
    "noteheads.dM3mensural",
    "noteheads.dM3neomensural",
    "noteheads.dM3semimensural",
    "noteheads.drM2mensural",
    "noteheads.drM2neomensural",
    "noteheads.drM2semimensural",
    "noteheads.drM3mensural",
    "noteheads.drM3neomensural",
    "noteheads.drM3semimensural",
    "noteheads.s0",
    "noteheads.s0blackmensural",
    "noteheads.s0blackpetrucci",
    "noteheads.s0cross",
    "noteheads.s0diamond",
    "noteheads.s0do",
    "noteheads.s0doThin",
    "noteheads.s0doWalker",
    "noteheads.s0faWalker",
    "noteheads.s0harmonic",
    "noteheads.s0kievan",
    "noteheads.s0la",
    "noteheads.s0laFunk",
    "noteheads.s0laThin",
    "noteheads.s0laWalker",
    "noteheads.s0mensural",
    "noteheads.s0mi",
    "noteheads.s0miMirror",
    "noteheads.s0miThin",
    "noteheads.s0miWalker",
    "noteheads.s0neomensural",
    "noteheads.s0petrucci",
    "noteheads.s0re",
    "noteheads.s0reThin",
    "noteheads.s0reWalker",
    "noteheads.s0slash",
    "noteheads.s0sol",
    "noteheads.s0solFunk",
    "noteheads.s0ti",
    "noteheads.s0tiThin",
    "noteheads.s0tiWalker",
    "noteheads.s0triangle",
    "noteheads.s1",
    "noteheads.s1blackpetrucci",
    "noteheads.s1cross",
    "noteheads.s1diamond",
    "noteheads.s1kievan",
    "noteheads.s1la",
    "noteheads.s1laFunk",
    "noteheads.s1laThin",
    "noteheads.s1laWalker",
    "noteheads.s1mensural",
    "noteheads.s1mi",
    "noteheads.s1miMirror",
    "noteheads.s1miThin",
    "noteheads.s1miWalker",
    "noteheads.s1neomensural",
    "noteheads.s1petrucci",
    "noteheads.s1slash",
    "noteheads.s1sol",
    "noteheads.s1solFunk",
    "noteheads.s2",
    "noteheads.s2blackpetrucci",
    "noteheads.s2cross",
    "noteheads.s2diamond",
    "noteheads.s2harmonic",
    "noteheads.s2la",
    "noteheads.s2laFunk",
    "noteheads.s2laThin",
    "noteheads.s2laWalker",
    "noteheads.s2mensural",
    "noteheads.s2mi",
    "noteheads.s2miFunk",
    "noteheads.s2miMirror",
    "noteheads.s2miThin",
    "noteheads.s2miWalker",
    "noteheads.s2neomensural",
    "noteheads.s2petrucci",
    "noteheads.s2slash",
    "noteheads.s2sol",
    "noteheads.s2solFunk",
    "noteheads.s2xcircle",
    "noteheads.sM1",
    "noteheads.sM1blackmensural",
    "noteheads.sM1double",
    "noteheads.sM1kievan",
    "noteheads.sM1mensural",
    "noteheads.sM1neomensural",
    "noteheads.sM1semimensural",
    "noteheads.sM2blackligmensural",
    "noteheads.sM2kievan",
    "noteheads.sM2ligmensural",
    "noteheads.sM2semiligmensural",
    "noteheads.sM3blackligmensural",
    "noteheads.sM3ligmensural",
    "noteheads.sM3semiligmensural",
    "noteheads.shufnagel.lpes",
    "noteheads.shufnagel.punctum",
    "noteheads.shufnagel.virga",
    "noteheads.smedicaea.inclinatum",
    "noteheads.smedicaea.punctum",
    "noteheads.smedicaea.rvirga",
    "noteheads.smedicaea.virga",
    "noteheads.sr1kievan",
    "noteheads.srM1mensural",
    "noteheads.srM1neomensural",
    "noteheads.srM1semimensural",
    "noteheads.srM2ligmensural",
    "noteheads.srM2semiligmensural",
    "noteheads.srM3ligmensural",
    "noteheads.srM3semiligmensural",
    "noteheads.ssolesmes.auct.asc",
    "noteheads.ssolesmes.auct.desc",
    "noteheads.ssolesmes.incl.auctum",
    "noteheads.ssolesmes.incl.parvum",
    "noteheads.ssolesmes.oriscus",
    "noteheads.ssolesmes.stropha",
    "noteheads.ssolesmes.stropha.aucta",
    "noteheads.svaticana.cephalicus",
    "noteheads.svaticana.epiphonus",
    "noteheads.svaticana.inclinatum",
    "noteheads.svaticana.inner.cephalicus",
    "noteheads.svaticana.linea.punctum",
    "noteheads.svaticana.linea.punctum.cavum",
    "noteheads.svaticana.lpes",
    "noteheads.svaticana.plica",
    "noteheads.svaticana.punctum",
    "noteheads.svaticana.punctum.cavum",
    "noteheads.svaticana.quilisma",
    "noteheads.svaticana.reverse.plica",
    "noteheads.svaticana.reverse.vplica",
    "noteheads.svaticana.upes",
    "noteheads.svaticana.vepiphonus",
    "noteheads.svaticana.vlpes",
    "noteheads.svaticana.vplica",
    "noteheads.svaticana.vupes",
    "noteheads.u0doFunk",
    "noteheads.u0fa",
    "noteheads.u0faFunk",
    "noteheads.u0faThin",
    "noteheads.u0miFunk",
    "noteheads.u0reFunk",
    "noteheads.u0tiFunk",
    "noteheads.u1do",
    "noteheads.u1doFunk",
    "noteheads.u1doThin",
    "noteheads.u1doWalker",
    "noteheads.u1fa",
    "noteheads.u1faFunk",
    "noteheads.u1faThin",
    "noteheads.u1faWalker",
    "noteheads.u1miFunk",
    "noteheads.u1re",
    "noteheads.u1reFunk",
    "noteheads.u1reThin",
    "noteheads.u1reWalker",
    "noteheads.u1ti",
    "noteheads.u1tiFunk",
    "noteheads.u1tiThin",
    "noteheads.u1tiWalker",
    "noteheads.u1triangle",
    "noteheads.u2do",
    "noteheads.u2doFunk",
    "noteheads.u2doThin",
    "noteheads.u2doWalker",
    "noteheads.u2fa",
    "noteheads.u2faFunk",
    "noteheads.u2faThin",
    "noteheads.u2faWalker",
    "noteheads.u2kievan",
    "noteheads.u2re",
    "noteheads.u2reFunk",
    "noteheads.u2reThin",
    "noteheads.u2reWalker",
    "noteheads.u2ti",
    "noteheads.u2tiFunk",
    "noteheads.u2tiThin",
    "noteheads.u2tiWalker",
    "noteheads.u2triangle",
    "noteheads.u3kievan",
    "noteheads.uM2",
    "noteheads.uM2blackmensural",
    "noteheads.uM2mensural",
    "noteheads.uM2neomensural",
    "noteheads.uM2semimensural",
    "noteheads.uM3blackmensural",
    "noteheads.uM3mensural",
    "noteheads.uM3neomensural",
    "noteheads.uM3semimensural",
    "noteheads.urM2mensural",
    "noteheads.urM2neomensural",
    "noteheads.urM2semimensural",
    "noteheads.urM3mensural",
    "noteheads.urM3neomensural",
    "noteheads.urM3semimensural",
    "one",
    "p",
    "pedal.*",
    "pedal..",
    "pedal.M",
    "pedal.P",
    "pedal.Ped",
    "pedal.d",
    "pedal.e",
    "period",
    "plus",
    "r",
    "rests.0",
    "rests.0mensural",
    "rests.0neomensural",
    "rests.0o",
    "rests.1",
    "rests.1mensural",
    "rests.1neomensural",
    "rests.1o",
    "rests.2",
    "rests.2classical",
    "rests.2mensural",
    "rests.2neomensural",
    "rests.3",
    "rests.3mensural",
    "rests.3neomensural",
    "rests.4",
    "rests.4mensural",
    "rests.4neomensural",
    "rests.5",
    "rests.6",
    "rests.7",
    "rests.M1",
    "rests.M1mensural",
    "rests.M1neomensural",
    "rests.M1o",
    "rests.M2",
    "rests.M2mensural",
    "rests.M2neomensural",
    "rests.M3",
    "rests.M3mensural",
    "rests.M3neomensural",
    "s",
    "scripts.arpeggio",
    "scripts.arpeggio.arrow.1",
    "scripts.arpeggio.arrow.M1",
    "scripts.augmentum",
    "scripts.barline.kievan",
    "scripts.caesura.curved",
    "scripts.caesura.straight",
    "scripts.circulus",
    "scripts.coda",
    "scripts.daccentus",
    "scripts.dfermata",
    "scripts.dlongfermata",
    "scripts.dmarcato",
    "scripts.downbow",
    "scripts.downmordent",
    "scripts.downprall",
    "scripts.dpedalheel",
    "scripts.dpedaltoe",
    "scripts.dportato",
    "scripts.dsemicirculus",
    "scripts.dshortfermata",
    "scripts.dsignumcongruentiae",
    "scripts.dstaccatissimo",
    "scripts.dverylongfermata",
    "scripts.espr",
    "scripts.flageolet",
    "scripts.halfopen",
    "scripts.halfopenvertical",
    "scripts.ictus",
    "scripts.lcomma",
    "scripts.lineprall",
    "scripts.lvarcomma",
    "scripts.mordent",
    "scripts.open",
    "scripts.prall",
    "scripts.pralldown",
    "scripts.prallmordent",
    "scripts.prallprall",
    "scripts.prallup",
    "scripts.rcomma",
    "scripts.reverseturn",
    "scripts.rvarcomma",
    "scripts.segno",
    "scripts.sforzato",
    "scripts.snappizzicato",
    "scripts.staccato",
    "scripts.stopped",
    "scripts.tenuto",
    "scripts.thumb",
    "scripts.tickmark",
    "scripts.trilelement",
    "scripts.trill",
    "scripts.trill_element",
    "scripts.turn",
    "scripts.uaccentus",
    "scripts.ufermata",
    "scripts.ulongfermata",
    "scripts.umarcato",
    "scripts.upbow",
    "scripts.upedalheel",
    "scripts.upedaltoe",
    "scripts.upmordent",
    "scripts.uportato",
    "scripts.upprall",
    "scripts.usemicirculus",
    "scripts.ushortfermata",
    "scripts.usignumcongruentiae",
    "scripts.ustaccatissimo",
    "scripts.uverylongfermata",
    "scripts.varcoda",
    "scripts.varsegno",
    "seven",
    "six",
    "space",
    "three",
    "ties.lyric.default",
    "ties.lyric.short",
    "timesig.C22",
    "timesig.C44",
    "timesig.mensural22",
    "timesig.mensural24",
    "timesig.mensural32",
    "timesig.mensural34",
    "timesig.mensural44",
    "timesig.mensural48",
    "timesig.mensural64",
    "timesig.mensural68",
    "timesig.mensural68alt",
    "timesig.mensural94",
    "timesig.mensural98",
    "timesig.neomensural22",
    "timesig.neomensural24",
    "timesig.neomensural32",
    "timesig.neomensural34",
    "timesig.neomensural44",
    "timesig.neomensural48",
    "timesig.neomensural64",
    "timesig.neomensural68",
    "timesig.neomensural68alt",
    "timesig.neomensural94",
    "timesig.neomensural98",
    "two",
    "z",
    "zero",
])
