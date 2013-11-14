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
        ab = b-a
        ac = c-a
        area += np.dot(ab, ac)
    return area

def find_neighbors(structure, max_dist=6):
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

    neighbors = {}
    for i, atom in enumerate(structure.uniq_sites):
        print atom

def find_neighbors2(structure):
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
    carts = np.dot(x8, cell)
    for i, atom in enumerate(structure.atoms):
        # recenter cell
        coords = carts - atom.cart_coord
        tess = Voronoi(coords)
        n = 0
        for j, r in enumerate(tess.ridge_points):
            if not i in r:
                continue
            inds = tess.ridge_vertices[j]
            verts = tess.vertices[inds]
            area = get_facet_area(verts)
            if area < 2e-2:
                continue
            print area
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

