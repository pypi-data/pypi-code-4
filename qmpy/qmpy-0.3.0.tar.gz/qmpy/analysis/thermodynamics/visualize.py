# thermopy.visualize

from qmpy.utils import *
import networkx as nx
import sys
if not 'matplotlib' in sys.modules:
    import matplotlib
    try:
        import backend_wx
        matplotlib.use('WXAgg')
    except ImportError:
        matplotlib.use('Agg')
import matplotlib.pylab as plt

def phase_diagram(space, unstable=False, axes=None, **kwargs):
    '''
    Makes an xwindow with an appropriate phase diagram

    Example:
    >>> space = PhaseSpace('Fe-Li-O')
    >>> space.phase_diagram()
    '''
    if len(space.bounds) == 1:
        raise NotImplementedError
    elif len(space.bounds) == 2:
        hull_plot(space, unstable=unstable, axes=axes, **kwargs)
    elif len(space.bounds) == 3:
        gtri_plot(space, unstable=unstable, axes=axes, **kwargs)
    elif len(space.bounds) == 4:
        gtet_plot(space, unstable=unstable, axes=axes, **kwargs)
    else:
        graph_plot(space, unstable=unstable, axes=axes, **kwargs)

def print_script(space, unstable=False, axes=None, **kwargs):
    '''
    Returns a string which is a pyhon script that generates a phase 
    diagram. Useful for moving labels around to make a graph look better

    Example:
    >>> space = PhaseSpace('Fe-Li-O')
    >>> space.print_script()
    '''

    if len(space.bounds) == 1:
        raise NotImplementedError
    elif len(space.bounds) == 2:
        hull_script(space, unstable=unstable, axes=None, **kwargs)
    elif len(space.bounds) == 3:
        gtri_script(space, unstable=unstable, axes=None, **kwargs)
    elif len(space.bounds) == 4:
        gtet_script(space, unstable=unstable, axes=None, **kwargs)
    else:
        graph_script(space, unstable=unstable, axes=None, **kwargs)

def hull_plot(space, axes=None, unstable=False, **kwargs):
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(111)

    axes.set_xlim([0,1])

    plt.ylabel('$\\rm{\Delta H [eV/atom]}$')
    plt.xlabel('$\\rm{%s_{x}%s_{1-x}}$' % (
        format_comp(space.bounds[0]),
        format_comp(space.bounds[1])))
    
    #plot tie lines
    for p1, p2 in space.tie_lines:
        c1 = space.coord(p1)
        c2 = space.coord(p2)
        if abs(c1[1]) < 1e-6 or abs(c2[1]) < 1e-6:
            if abs(c1[1] - 1) < 1e-6 or abs(c2[1] - 1) < 1e-6:
                if len(space.tie_lines) > 1:
                    continue
        axes.plot([c1[1],c2[1]], [p1.energy, p2.energy], 'k')

    #plot compounds
    for phase in space.stable:
        if not space.in_bounds(phase):
            continue
        x = space.coord(phase.unit_comp)[1]
        axes.plot(x, phase.energy, 'ro')
        axes.annotate('$\\rm{%s}$' % phase.latex, xy=(x, phase.energy))

    if unstable:
        for phase in space.unstable:
            if not space.in_bounds(phase):
                continue
            x = space.coord(phase.unit_comp)[1]
            axes.plot(x, phase.energy, 'bo')
            axes.annotate('$\\rm{%s}$' % phase.latex, xy=(x, phase.energy))
    if axes is None:
        plt.show()

def hull_script(space, axes=None, unstable=False, **kwargs):
    print 'import matplotlib'
    print 'matplotlib.rcParams.update({"font.size": 16})'
    print 'import matplotlib.pylab as plt'
    print
    print 'fig = plt.figure()'
    print 'axes = fig.add_subplot(111)'
    print 'axes.set_xlim([0,1])'
    print 'plt.ylabel("$\\\\rm{\\Delta H [eV/atom]}$")'
    print 'plt.xlabel("$\\\\rm{%s_{x}%s_{1-x}}$")' % (
            format_comp(space.bounds[0]),
            format_comp(space.bounds[1]))
    print
    for p1, p2 in space.tie_lines:
        c1 = space.coord(p1)
        c2 = space.coord(p2)
        if abs(c1[1]) < 1e-6 or abs(c2[1]) < 1e-6:
            if abs(c1[1] - 1) < 1e-6 or abs(c2[1] - 1) < 1e-6:
                if len(space.tie_lines) > 1:
                    continue
        print 'axes.plot([%s, %s], [%s, %s], "k")' % (
                c1[1], c2[1], p1.energy, p2.energy )

    for p in space.stable:
        if not space.in_bounds(p):
            continue
        x = space.coord(p.unit_comp)[1]
        print 'axes.plot(%s, %s, "ro")' % (
                x, p.energy)
        print 'axes.annotate( "$\\\\rm{%s}$", xy=( %s, %s) )' % (
                p.latex, x, p.energy )

def gtri_plot(space, axes=None, unstable=False, labels=True, **kwargs):
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(111)

    axes.axis([-0.1,1.1,-0.1,1.1])
    axes.axis('off')
    axes.set_aspect('equal')

    #plot lines
    for p1, p2 in space.tie_lines:
        x1, y1 = coord_to_gtri(space.coord(p1))
        x2, y2 = coord_to_gtri(space.coord(p2))
        axes.plot([x1, x2], [y1, y2], 'k')

    #plot compounds 
    for p in space.stable:
        if not space.in_bounds(p):
            continue
        x,y = coord_to_gtri(space.coord(p))
        axes.plot(x, y, 'ro')
        if labels:
            axes.annotate('$\\rm{%s}$' % p.latex, xy=(x, y), color='red')

    if unstable:
        for p in space.unstable:
            if not space.in_bounds(p):
                continue
            x,y = coord_to_gtri(space.coord(p))
            axes.plot(x, y, 'bo')
            if labels:
                axes.annotate('$\\rm{%s}$' % p.latex, xy=(x, y))
    if axes is None:
        plt.show()

def gtri_script(space, axes=None, unstable=False, labels=True, **kwargs):
    print 'import matplotlib.pylab as plt'
    print
    print 'axes = plt.axes()'
    print 'axes.axis([-0.1,1.1,-0.1,1.1])'
    print 'axes.axis("off")'
    print 'axes.set_aspect("equal")'
    print
    
    #plot lines
    for p1, p2 in space.tie_lines:
        x1, y1 = coord_to_gtri(space.coord(p1))
        x2, y2 = coord_to_gtri(space.coord(p2))
        print 'axes.plot([%s, %s], [%s, %s], "k")' % (
                x1, x2, y1, y2)

    #plot compounds 
    for p in space.stable:
        if not space.in_bounds(p):
            continue
        x,y = coord_to_gtri(space.coord(p))
        print 'axes.plot(%s, %s, "ro")' % (x, y)
        if labels:
            print 'axes.annotate("$\\\\rm{%s}$" , xy=(%s, %s))' % (
                    p.latex, x, y)

    if unstable:
        for p in space.unstable:
            if not space.in_bounds(p):
                continue
            x,y = coord_to_gtri(space.coord(p))
            print 'axes.plot(%s, %s, "bo")' % (x, y)
            if labels:
                print 'axes.annotate("$\\rm{%s}$", xy=(%s, %s))' % (p.latex, x, y)

def gtet_plot(space, axes=None, unstable=False, labels=True, **kwargs):
    if axes is None:
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        axes = fig.gca(projection='3d')

    axes.axis('off')
    
    #plot lines
    for p1, p2 in space.tie_lines:
        x1, y1, z1 = coord_to_gtet(space.coord(p1))
        x2, y2, z2 = coord_to_gtet(space.coord(p2))
        axes.plot([x1, x2], [y1, y2], [z1, z2], 'k')

    #plot compounds
    for p in space.stable:
        if not space.in_bounds(p):
            continue
        x,y,z = coord_to_gtet(space.coord(p))
        axes.plot([x], [y], [z], 'ro')
        if labels:
            axes.text( x, y, z, '$\\rm{%s}$' % p.latex)

    if unstable:
        for p in space.unstable:
            if not space.in_bounds(p):
                continue
            x,y,z = coord_to_gtet(space.coord(p))
            axes.plot([x], [y], [z], 'bo')   
            if labels:
                axes.text( x, y, z, '$\\rm{%s}$' % p.latex)
    if axes is None:
        plt.show()

def graph_plot(space, axes=None, unstable=False, labels=True, **kwargs):
    G = space.graph
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(111)

    nx.draw(G, ax=axes, node_size=25, edge_color='k',
            with_labels=labels, 
            **kwargs)

    if axes is None:
        plt.show()
