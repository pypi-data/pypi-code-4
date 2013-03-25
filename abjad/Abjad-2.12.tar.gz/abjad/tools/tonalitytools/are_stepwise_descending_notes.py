from abjad.tools import componenttools
from abjad.tools import iterationtools
from abjad.tools import pitchtools
from abjad.tools import sequencetools


def are_stepwise_descending_notes(*expr):
    '''.. versionadded:: 2.0

    True when notes in `expr` are stepwise descending:

    ::

        >>> staff = Staff("g'2 f'16 e' d' c'")
        >>> time_signature = contexttools.TimeSignatureMark((3, 4))(staff)

    ::

        >>> show(staff) # doctest: +SKIP

    ::

        >>> tonalitytools.are_stepwise_descending_notes(staff)
        True

    Otherwise false:

        >>> staff[-4:] = "c'16 d' e' f'"

    ::

        >>> show(staff) # doctest: +SKIP

    ::

        >>> tonalitytools.are_stepwise_descending_notes(staff)
        False

    Return boolean.
    '''

    for left, right in sequencetools.iterate_sequence_pairwise_strict(
        iterationtools.iterate_notes_in_expr(expr)):
        try:
            assert not (left.written_pitch == right.written_pitch)
            mdi = pitchtools.calculate_melodic_diatonic_interval(left, right)
            assert mdi.number == -2
        except AssertionError:
            return False

    return True
