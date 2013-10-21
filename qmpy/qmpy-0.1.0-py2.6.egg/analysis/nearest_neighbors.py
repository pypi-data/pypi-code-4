#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import numpy.linalg as linalg
from scipy.spatial import Delaunay, Voronoi
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D
import itertools
from qmpy.utils import *

def get_facet_area(vertices):
    area = 0
    vertices = np.sort(vertices)
    #vertices = vertices[np.lexsort(vertices.T)]
    if not vertices.shape[1] == 3:
        raise ValueError('vertices must be an Nx3 array')
    for i in range(len(vertices)-2):
        a = vertices[i]
        b = vertices[i+1]
        c = vertices[i+2]
        ab = a-b
        ac = a-c
        area += np.dot(ab, ac)
    return area

def find_neighbors(structure):
    structure.make_conventional()
    cell = structure.cell
    scaled = structure.scaled_coords
    x8 = np.vstack([ structure.scaled_coords + 
                     i*np.array([1, 0, 0]) + 
                     j*np.array([0, 1, 0]) + 
                     k*np.array([0, 0, 1])
            for i, j, k in itertools.product([0, -1, 1], 
                                             [0, -1, 1], 
                                             [0, -1, 1])])
    nns = {}
    for i, atom in enumerate(structure.atoms):
        # recenter cell
        #coords = x8 - atom.coord
        #coords[ coords < -2.5 ] += 5
        #coords[ coords > 2.5 ] -= 5
        carts = np.dot(x8, cell)
        tess = Voronoi(carts)
        n = 0
        if atom.element_id != 'Al':
            continue
        for j, r in enumerate(tess.ridge_points):
            if not i in r:
                continue
            inds = tess.ridge_vertices[j]
            verts = tess.vertices[inds]
            area = get_facet_area(verts)
            if abs(area) <  5e-2:
                continue
            n += 1
        print '%s nearest neighbors found!' % n
    #for i in range(len(scaled)):
        # recenter cell
        #carts = np.dot(x27 - scaled[i], cell)
        #mask = np.argwhere([(linalg.norm(x) < 3 and not all(x == [0,0,0]))
        #                      for x in carts])
        #potential = np.vstack(carts[mask])
        #print potential
        #kdtree = KDTree(potential)
        #return kdtree

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
