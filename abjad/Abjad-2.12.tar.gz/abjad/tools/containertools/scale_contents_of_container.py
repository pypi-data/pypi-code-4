def scale_contents_of_container(container, multiplier):
    r'''.. versionadded:: 1.1

    Scale contents of `container` by dot `multiplier`::

        >>> staff = Staff("c'8 d'8")
        >>> beamtools.BeamSpanner(staff.leaves)
        BeamSpanner(c'8, d'8)

    ::

        >>> f(staff)
        \new Staff {
            c'8 [
            d'8 ]
        }

    ::

        >>> containertools.scale_contents_of_container(staff, Duration(3, 2))
        Staff{2}

    ::

        >>> f(staff)
        \new Staff {
            c'8. [
            d'8. ]
        }

    Scale contents of `container` by tie `multiplier`::

        >>> staff = Staff("c'8 d'8")
        >>> beamtools.BeamSpanner(staff.leaves)
        BeamSpanner(c'8, d'8)

    ::

        >>> f(staff)
        \new Staff {
            c'8 [
            d'8 ]
        }

    ::

        >>> containertools.scale_contents_of_container(staff, Duration(5, 4))
        Staff{4}

    ::

        >>> f(staff)
        \new Staff {
            c'8 [ ~
            c'32
            d'8 ~
            d'32 ]
        }

    Scale contents of `container` by `multiplier` without power-of-two denominator::

        >>> staff = Staff("c'8 d'8")
        >>> beamtools.BeamSpanner(staff.leaves)
        BeamSpanner(c'8, d'8)

    ::

        >>> f(staff)
        \new Staff {
            c'8 [
            d'8 ]
        }

    ::

        >>> containertools.scale_contents_of_container(staff, Duration(4, 3))
        Staff{2}

    ::

        >>> f(staff)
        \new Staff {
            \times 2/3 {
                c'4 [
            }
            \times 2/3 {
                d'4 ]
            }
        }

    Return `container`.
    '''
    from abjad.tools import iterationtools
    from abjad.tools import measuretools
    from abjad.tools import tietools
    from abjad.tools import tuplettools

    for expr in tietools.iterate_topmost_tie_chains_and_components_in_expr(container[:]):
        if isinstance(expr, tietools.TieChain):
            tietools.add_or_remove_tie_chain_notes_to_achieve_scaled_written_duration(expr, multiplier)
        elif isinstance(expr, tuplettools.FixedDurationTuplet):
            tuplettools.scale_contents_of_tuplets_in_expr_by_multiplier(expr, multiplier)
        elif isinstance(expr, measuretools.Measure):
            measuretools.scale_contents_of_measures_in_expr(expr, multiplier)
        else:
            raise Exception(NotImplemented)

    return container
