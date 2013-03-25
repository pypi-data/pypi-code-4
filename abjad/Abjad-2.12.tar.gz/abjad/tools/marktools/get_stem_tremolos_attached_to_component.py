def get_stem_tremolos_attached_to_component(component, tremolo_flags=None):
    r'''.. versionadded:: 2.3

    Get stem tremolos attached to `component`::

        >>> staff = Staff("c'8 d'8 e'8 f'8")
        >>> marktools.StemTremolo(16)(staff[0])
        StemTremolo(16)(c'8)

    ::

        >>> f(staff)
        \new Staff {
            c'8 :16
            d'8
            e'8
            f'8
        }

    ::

        >>> marktools.get_stem_tremolos_attached_to_component(staff[0])
        (StemTremolo(16)(c'8),)

    Return tuple of zero or more stem tremolos.
    '''
    from abjad.tools import marktools

    result = []
    for mark in component._marks_for_which_component_functions_as_start_component:
        if isinstance(mark, marktools.StemTremolo):
            if tremolo_flags is None or mark.tremolo_flags == tremolo_flags:
                result.append(mark)

    result = tuple(result)
    return result
