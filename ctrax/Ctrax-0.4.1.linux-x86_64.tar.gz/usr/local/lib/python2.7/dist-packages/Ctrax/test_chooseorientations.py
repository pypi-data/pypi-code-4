#!/usr/bin/env python

# choose-orientations unit tests
# JAB 8/19/13

import numpy as num

import annfiles as ann
from chooseorientations import ChooseOrientations
import ellipsesk as ell
from params import params

def init_file():
    chooser = ChooseOrientations( None, False )
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    params.nids = 1
    return chooser, annfile

def add_fly( annfile, x, y, theta ):
    flies = ell.TargetList()
    flies.append( ell.Ellipse( x, y, 5., 10., theta, 25., 0 ) )
    annfile.append( flies )

def test_pi_flip():
    n_err = 0
    n_first_frames = 3
    
    chooser, annfile = init_file()

    # walking in decreasing x with theta=pi
    for fr in range( n_first_frames ):
        add_fly( annfile, 100 - fr, 97., num.pi )
    for fr in range( n_first_frames ):
        add_fly( annfile, 97., 97., 0. )

    try:
        assert( annfile.orientations_chosen == False )
    except AssertionError:
        print "new file should not have orientations chosen"
        n_err += 1
        return
        
    annfile = chooser.ChooseOrientations( annfile )

    def test_annfile( annfile ):
        n_err = 0
        
        try:
            assert( annfile.orientations_chosen == True )
        except AssertionError:
            print "ChooseOrientations should choose orientations"
            n_err += 1
            return

        try:
            assert( len( annfile ) == 2*n_first_frames )
        except AssertionError:
            print "new annotation file has length", len( annfile )
            n_err += 1

        for f, flies in enumerate( annfile ):
            try:
                assert( len( flies ) == 1 )
            except AssertionError:
                print "frame", f, "has", len( flies ), "flies"
                n_err += 1

            if f < n_first_frames:
                for fly in flies.itervalues():
                    try:
                        assert( fly.identity == 0 )
                        assert( fly.area() > 0. )
                    except AssertionError:
                        print "non-angle value changed in fly", f, fly
                        n_err += 1
                    try:
                        assert( abs( fly.angle - num.pi ) < 1e-6 )
                    except AssertionError:
                        print "initial angle error in fly", f, fly
                        n_err += 1
            else:
                for fly in flies.itervalues():
                    try:
                        assert( fly.identity == 0 )
                        assert( fly.area() > 0. )
                    except AssertionError:
                        print "non-angle value changed in fly", f, fly
                        n_err += 1
                    try:
                        assert( abs( fly.angle - num.pi ) % (2.*num.pi) < 1e-6 )
                    except AssertionError:
                        print "altered angle error in fly", f, fly
                        n_err += 1

        return n_err

    n_err += test_annfile( annfile )

    annfile.close()
    new_annfile = ann.AnnotationFile( annfile._filename )

    n_err += test_annfile( new_annfile )

    return n_err


if __name__ == '__main__':
    n_err = test_pi_flip()

    try:
        assert( n_err == 0 )
    except AssertionError:
        print "**errors raised"
    else:
        print "\n...all tests passed"
