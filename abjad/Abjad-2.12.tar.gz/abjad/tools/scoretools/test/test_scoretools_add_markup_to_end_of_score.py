from abjad import *


def test_scoretools_add_markup_to_end_of_score_01():

    staff = Staff("c'4 d'4 e'4 f'4")
    markup = r'\italic \right-column { "Bremen - Boston - Los Angeles." "Jul 2010 - May 2011." }'
    markup = markuptools.Markup(markup, Down)
    scoretools.add_markup_to_end_of_score(staff, markup, (4, -2))

    r'''
    \new Staff {
        c'4
        d'4
        e'4
        \once \override TextScript #'extra-offset = #'(4 . -2)
        f'4
            _ \markup {
                \italic
                    \right-column
                        {
                            "Bremen - Boston - Los Angeles."
                            "Jul 2010 - May 2011."
                        }
                }
    }
    '''

    assert staff.lilypond_format == '\\new Staff {\n\tc\'4\n\td\'4\n\te\'4\n\t\\once \\override TextScript #\'extra-offset = #\'(4 . -2)\n\tf\'4\n\t\t_ \\markup {\n\t\t\t\\italic\n\t\t\t\t\\right-column\n\t\t\t\t\t{\n\t\t\t\t\t\t"Bremen - Boston - Los Angeles."\n\t\t\t\t\t\t"Jul 2010 - May 2011."\n\t\t\t\t\t}\n\t\t\t}\n}'

