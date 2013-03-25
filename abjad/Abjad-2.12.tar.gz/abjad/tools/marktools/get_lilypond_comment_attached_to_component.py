def get_lilypond_comment_attached_to_component(component):
    r'''.. versionadded:: 2.0

    Get exactly one LilyPond comment attached to `component`::

        >>> staff = Staff("c'8 d'8 e'8 f'8")
        >>> marktools.LilyPondComment('comment')(staff[0])
        LilyPondComment('comment')(c'8)

    ::

        >>> f(staff)
        \new Staff {
            % comment
            c'8
            d'8
            e'8
            f'8
        }

    ::

        >>> marktools.get_lilypond_comment_attached_to_component(staff[0])
        LilyPondComment('comment')(c'8)

    Return one LilyPond comment.

    Raise missing mark error when no LilyPond comment is attached.

    Raise extra mark error when more than one LilyPond comment is attached.
    '''
    from abjad.tools import marktools

    lilypond_comments = marktools.get_lilypond_comments_attached_to_component(component)
    if not lilypond_comments:
        raise MissingMarkError
    elif 1 < len(lilypond_comments):
        raise ExtraMarkError
    else:
        return lilypond_comments[0]
