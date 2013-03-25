from abjad.tools import containertools


def iterate_containers_in_expr(expr, reverse=False, start=0, stop=None):
    r'''.. versionadded:: 2.10

    Iterate containers forward in `expr`:

    ::

        >>> staff = Staff([Voice("c'8 d'8"), Voice("e'8 f'8 g'8")])
        >>> Tuplet(Fraction(2, 3), staff[1][:])
        Tuplet(2/3, [e'8, f'8, g'8])
        >>> staff.is_parallel = True

    ::

        >>> f(staff)
        \new Staff <<
            \new Voice {
                c'8
                d'8
            }
            \new Voice {
                \times 2/3 {
                    e'8
                    f'8
                    g'8
                }
            }
        >>

    ::

        >>> for x in iterationtools.iterate_containers_in_expr(staff):
        ...   x
        Staff<<2>>
        Voice{2}
        Voice{1}
        Tuplet(2/3, [e'8, f'8, g'8])

    Iterate containers backward in `expr`:

    ::

        >>> for x in iterationtools.iterate_containers_in_expr(staff, reverse=True):
        ...   x
        Staff<<2>>
        Voice{1}
        Tuplet(2/3, [e'8, f'8, g'8])
        Voice{2}

    Ignore threads.

    Return generator.
    '''
    from abjad.tools import iterationtools

    return iterationtools.iterate_components_in_expr(
        expr, klass=containertools.Container, reverse=reverse, start=start, stop=stop)
