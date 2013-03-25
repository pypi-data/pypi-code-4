from abjad.tools import sequencetools


def list_harmonic_diatonic_intervals_in_expr(expr):
    '''.. versionadded:: 2.0

    List harmonic diatonic intervals in `expr`::

        >>> staff = Staff("c'8 d'8 e'8 f'8")
        >>> for interval in sorted(pitchtools.list_harmonic_diatonic_intervals_in_expr(staff)):
        ...     interval
        ...
        HarmonicDiatonicInterval('m2')
        HarmonicDiatonicInterval('M2')
        HarmonicDiatonicInterval('M2')
        HarmonicDiatonicInterval('m3')
        HarmonicDiatonicInterval('M3')
        HarmonicDiatonicInterval('P4')

    Return unordered set.
    '''
    from abjad.tools import pitchtools

    diatonic_intervals = []
    pitches = pitchtools.list_named_chromatic_pitches_in_expr(expr)
    unordered_pitch_pairs = sequencetools.yield_all_unordered_pairs_of_sequence(pitches)
    for first_pitch, second_pitch in unordered_pitch_pairs:
        diatonic_interval = first_pitch - second_pitch
        diatonic_interval = abs(diatonic_interval)
        diatonic_intervals.append(diatonic_interval)

    return diatonic_intervals
