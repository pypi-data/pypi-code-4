from abjad import *


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___01():

    prefix_talea, prefix_lengths = [-8], [0, 1]
    suffix_talea, suffix_lengths = [-1], [1]
    talea_denominator = 32
    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea, prefix_lengths, suffix_talea, suffix_lengths, talea_denominator)

    divisions = [(5, 8), (5, 8), (5, 8), (5, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 5/8
            c'2 ~
            c'16.
            r32
        }
        {
            \time 5/8
            r4
            c'4 ~
            c'16.
            r32
        }
        {
            \time 5/8
            c'2 ~
            c'16.
            r32
        }
        {
            \time 5/8
            r4
            c'4 ~
            c'16.
            r32
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 5/8\n\t\tc'2 ~\n\t\tc'16.\n\t\tr32\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tc'4 ~\n\t\tc'16.\n\t\tr32\n\t}\n\t{\n\t\t\\time 5/8\n\t\tc'2 ~\n\t\tc'16.\n\t\tr32\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tc'4 ~\n\t\tc'16.\n\t\tr32\n\t}\n}"


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___02():

    prefix_talea, prefix_lengths = [-8], [1, 2, 3, 4]
    suffix_talea, suffix_lengths = [-1], [1]
    talea_denominator = 32
    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea, prefix_lengths, suffix_talea, suffix_lengths, talea_denominator)

    divisions = [(5, 8), (5, 8), (5, 8), (5, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 5/8
            r4
            c'4 ~
            c'16.
            r32
        }
        {
            \time 5/8
            r4
            r4
            c'16.
            r32
        }
        {
            \time 5/8
            r4
            r4
            r8
        }
        {
            \time 5/8
            r4
            r4
            r8
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tc'4 ~\n\t\tc'16.\n\t\tr32\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tr4\n\t\tc'16.\n\t\tr32\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tr4\n\t\tr8\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr4\n\t\tr4\n\t\tr8\n\t}\n}"


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___03():

    prefix_talea, prefix_lengths = [-1], [1]
    suffix_talea, suffix_lengths = [-8], [1, 2, 3]
    talea_denominator = 32
    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea, prefix_lengths, suffix_talea, suffix_lengths, talea_denominator)

    divisions = [(5, 8), (5, 8), (5, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 5/8
            r32
            c'4 ~
            c'16.
            r4
        }
        {
            \time 5/8
            r32
            c'16.
            r4
            r4
        }
        {
            \time 5/8
            r32
            r4
            r4
            r16.
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 5/8\n\t\tr32\n\t\tc'4 ~\n\t\tc'16.\n\t\tr4\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr32\n\t\tc'16.\n\t\tr4\n\t\tr4\n\t}\n\t{\n\t\t\\time 5/8\n\t\tr32\n\t\tr4\n\t\tr4\n\t\tr16.\n\t}\n}"


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___04():

    prefix_talea, prefix_lengths = [], [0]
    suffix_talea, suffix_lengths = [], [0]
    talea_denominator = 8
    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea, prefix_lengths, suffix_talea, suffix_lengths, talea_denominator)

    divisions = [(5, 8), (5, 8), (5, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 5/8
            c'2 ~
            c'8
        }
        {
            \time 5/8
            c'2 ~
            c'8
        }
        {
            \time 5/8
            c'2 ~
            c'8
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 5/8\n\t\tc'2 ~\n\t\tc'8\n\t}\n\t{\n\t\t\\time 5/8\n\t\tc'2 ~\n\t\tc'8\n\t}\n\t{\n\t\t\\time 5/8\n\t\tc'2 ~\n\t\tc'8\n\t}\n}"


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___05():

    prefix_talea, prefix_lengths = [-1], [1]
    suffix_talea, suffix_lengths = [-1], [1]
    talea_denominator = 8
    prolation_addenda = [1, 0, 3]
    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea, prefix_lengths, suffix_talea, suffix_lengths, talea_denominator,
        prolation_addenda = prolation_addenda)

    divisions = [(4, 8), (4, 8), (4, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 4/8
            \times 4/5 {
                r8
                c'4.
                r8
            }
        }
        {
            \time 4/8
            {
                r8
                c'4
                r8
            }
        }
        {
            \time 4/8
            \times 4/7 {
                r8
                c'2 ~
                c'8
                r8
            }
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 4/8\n\t\t\\times 4/5 {\n\t\t\tr8\n\t\t\tc'4.\n\t\t\tr8\n\t\t}\n\t}\n\t{\n\t\t\\time 4/8\n\t\t{\n\t\t\tr8\n\t\t\tc'4\n\t\t\tr8\n\t\t}\n\t}\n\t{\n\t\t\\time 4/8\n\t\t\\times 4/7 {\n\t\t\tr8\n\t\t\tc'2 ~\n\t\t\tc'8\n\t\t\tr8\n\t\t}\n\t}\n}"


# TODO: change all calls to explicit keyword calls
def test_DivisionIncisedNoteRhythmMaker___call___06():

    maker = rhythmmakertools.DivisionIncisedNoteRhythmMaker(
        prefix_talea=[-1], 
        prefix_lengths=[1],
        suffix_talea=[], 
        suffix_lengths=[0], 
        talea_denominator=32, 
        prolation_addenda=[2, 0], 
        secondary_divisions=[20])

    divisions = [(4, 8), (4, 8), (4, 8)]
    leaf_lists = maker(divisions)
    leaves = sequencetools.flatten_sequence(leaf_lists)

    staff = Staff(measuretools.make_measures_with_full_measure_spacer_skips(divisions))
    measuretools.replace_contents_of_measures_in_expr(staff, leaves)
    measuretools.set_always_format_time_signature_of_measures_in_expr(staff)

    r'''
    \new Staff {
        {
            \time 4/8
            \times 8/9 {
                r32
                c'2 ~
                c'32
            }
        }
        {
            \time 4/8
            {
                r32
                c'16.
            }
            \fraction \times 6/7 {
                r32
                c'4. ~
                c'32
            }
        }
        {
            \time 4/8
            {
                r32
                c'8..
            }
            \times 4/5 {
                r32
                c'4 ~
                c'32
            }
        }
    }
    '''

    assert staff.lilypond_format == "\\new Staff {\n\t{\n\t\t\\time 4/8\n\t\t\\times 8/9 {\n\t\t\tr32\n\t\t\tc'2 ~\n\t\t\tc'32\n\t\t}\n\t}\n\t{\n\t\t\\time 4/8\n\t\t{\n\t\t\tr32\n\t\t\tc'16.\n\t\t}\n\t\t\\fraction \\times 6/7 {\n\t\t\tr32\n\t\t\tc'4. ~\n\t\t\tc'32\n\t\t}\n\t}\n\t{\n\t\t\\time 4/8\n\t\t{\n\t\t\tr32\n\t\t\tc'8..\n\t\t}\n\t\t\\times 4/5 {\n\t\t\tr32\n\t\t\tc'4 ~\n\t\t\tc'32\n\t\t}\n\t}\n}"
