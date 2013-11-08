import numpy as np
import numpy.linalg as linalg
import itertools
import matplotlib
matplotlib.rcParams.update({'font.size': 22,
    'font.serif':['Century']})
import matplotlib.pylab as plt
from collections import defaultdict
from StringIO import StringIO

def get_pair_distances(structure, max_dist=10):
    '''
    Loops over pairs of atoms that are within radius max_dist of one another.
    Returns a dict of (atom1, atom2):[list of distances].

    '''
    dists = []
    structure.symmetrize()
    cell = structure.cell
    coords = structure.cartesian_coords.copy()
    lat_params = structure.lat_params
    limits = [ int(np.ceil(max_dist/lat_params[i])) for i in range(3) ]
    ranges = [ range(-l, l+1) for l in limits ]
    sc = np.vstack([ coords+np.dot(ijk, cell) for ijk in itertools.product(*ranges)])
    elts = [ a.element_id for a in structure ]
    n_cells = len(ranges[0])*len(ranges[1])*len(ranges[2])
    elt_list = list(set(elts))
    elts = n_cells*elts

    pairs = list(itertools.combinations(elt_list, r=2))
    dists = defaultdict(list)
        
    for a1 in structure.uniq_sites:
        c1 = a1.cart_coord
        e1 = a1.label
        for c2, e2 in zip(sc, elts):
            vec = c1 - c2
            if all([ v == 0 for v in vec ]):
                continue
            dists[frozenset([e1,e2])] += [linalg.norm(vec)]*a1.multiplicity
    return dists

def get_pdf_uri(structure, max_dist=5, smearing=0.1):
    '''
    Return a uri of pair distribution function for the input structure. Ranges
    from 0 to max_dist, with pair distances smeared into gaussians of width
    "smearing".

    '''
    distances = get_pair_distances(structure, max_dist=max_dist)
    elts = list(set([ a.element_id for a in structure ]))
    rhos = dict((elt, structure.comp[elt]/structure.volume) for elt in elts)

    xs = np.mgrid[0:max_dist:200j]
    dr = xs[1] - xs[0]
    ideals = dict((elt, 4.0*np.pi*rhos[elt]/3.0) for elt in elts)

    for pair, dists in distances.items():
        pair = list(pair)
        if len(pair) == 1:
            pair *= 2
        e1, e2 = pair

        vals = np.zeros(xs.shape)
        prefactor = 1.0/(smearing*np.sqrt(2*np.pi))
        norms = [ ( (x+dr/2)**3 - (x-dr/2)**3) for x in xs ]
        for d in dists:
            vals += np.exp(-(d-xs)**2/(2*smearing**2))
            #vals += prefactor*np.exp(-(d-xs)**2/(2*smearing**2))
        vals = vals/norms
        plt.plot(xs, vals, lw=3, label="%s-%s" % (e1, e2))

    plt.legend(loc=2)
    plt.xlabel('interatomic distance [$\\AA$]')
    img = StringIO()
    plt.savefig(img, dpi=75, bbox_inches='tight')
    data_uri = 'data:image/jpg;base64,'
    data_uri += img.getvalue().encode('base64').replace('\n', '')
    plt.close()
    return data_uri

def get_pdf(structure, ind=None):
    result = []
    for atom1 in structure:
        dists = []
        for atom2 in structure:
            dists.append(structure.get_distance(atom1, atom2))
        result.append(dists)
    kernel = gaussian_kde(result[0])
    kernel.covariance_factor = lambda : .25
    kernel._compute_covariance()
    xs = np.linspace(1, max(result[0]), 1000)
    plt.plot(xs, kernel(xs))
    plt.hist(result[0], normed=True)
    plt.show()
    return result
