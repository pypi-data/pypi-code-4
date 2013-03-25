from abjad import *


def test_pitchtools_calculate_melodic_chromatic_interval_01():

    pitch_1 = pitchtools.NamedChromaticPitch(10)
    pitch_2 = pitchtools.NamedChromaticPitch(12)

    mci = pitchtools.calculate_melodic_chromatic_interval(
        pitch_1, pitch_2)
    assert mci == pitchtools.MelodicChromaticInterval(2)

    mci = pitchtools.calculate_melodic_chromatic_interval(
        pitch_2, pitch_1)
    assert mci == pitchtools.MelodicChromaticInterval(-2)

    mci = pitchtools.calculate_melodic_chromatic_interval(
        pitch_1, pitch_1)
    assert mci == pitchtools.MelodicChromaticInterval(0)

    mci = pitchtools.calculate_melodic_chromatic_interval(
        pitch_2, pitch_2)
    assert mci == pitchtools.MelodicChromaticInterval(0)


def test_pitchtools_calculate_melodic_chromatic_interval_02():
    '''Works with quartertones.'''

    mci = pitchtools.calculate_melodic_chromatic_interval(
        pitchtools.NamedChromaticPitch(12), pitchtools.NamedChromaticPitch(9.5))
    assert mci == pitchtools.MelodicChromaticInterval(-2.5)
