from abjad.tools import pitchtools


def analyze_chord(expr):
    '''.. versionadded:: 2.0

    Analyze `expr` and return chord class. ::

        >>> chord = Chord([7, 10, 12, 16], (1, 4))
        >>> tonalitytools.analyze_chord(chord)
        CDominantSeventhInSecondInversion

    Return none when no tonal chord is understood. ::

        >>> chord = Chord(['c', 'cs', 'd'], (1, 4))
        >>> tonalitytools.analyze_chord(chord) is None
        True

    Raise tonal harmony error when chord can not analyze.
    '''
    from abjad.tools import tonalitytools

    pitches = pitchtools.list_named_chromatic_pitches_in_expr(expr)
    npcset = pitchtools.NamedChromaticPitchClassSet(pitches)

    #ordered_npcs = pitchtools.NamedChromaticPitchClassSegment([])
    ordered_npcs = []
    letters = ('c', 'e', 'g', 'b', 'd', 'f', 'a')
    for letter in letters:
        for npc in npcset:
            if npc._diatonic_pitch_class_name == letter:
                ordered_npcs.append(npc)

    ordered_npcs = pitchtools.NamedChromaticPitchClassSegment(ordered_npcs)
    for x in range(len(ordered_npcs)):
        ordered_npcs = ordered_npcs.rotate(1)
        if ordered_npcs.inversion_equivalent_diatonic_interval_class_segment.is_tertian:
            break
    else:
        #raise TonalHarmonyError('expr is not tertian harmony: %s' % str(expr))
        return None

    try:
        root = ordered_npcs[0]
        bass = min(pitches).named_chromatic_pitch_class
        inversion = ordered_npcs.index(bass)
        dic_seg =  ordered_npcs.inversion_equivalent_diatonic_interval_class_segment
        cardinality = len(ordered_npcs)
        extent = tonalitytools.chord_class_cardinality_to_extent(cardinality)
        quality = tonalitytools.diatonic_interval_class_segment_to_chord_quality_string(dic_seg)
    except TonalHarmonyError:
        return None

    return tonalitytools.ChordClass(root, quality, extent, inversion)
