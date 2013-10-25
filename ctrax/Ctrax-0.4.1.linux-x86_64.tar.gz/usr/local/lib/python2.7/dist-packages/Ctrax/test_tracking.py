#!/usr/bin/env python

# tracking unit tests
# JAB 7/13/13

import multiprocessing
import os
import os.path
from Queue import Empty as QueueEmpty
import random
import shutil
import time
import traceback

import numpy as num

import annfiles as ann
import bg
import bg_pre4
import ellipsesk as ell
import ellipsesk_pre4 as ell_pre4
import hindsight as hs
from params import params, ShapeParams
params.interactive = False
params.enable_feedback( False )
import movies
import test_filelist

num.random.seed( 0 ) # use the same random seed every time...

TEST_ANN_DIR = "/home/jbender/ann_data_test"

AREA_RANGE = range( 1, 10000, 100 )
MAJOR_RANGE = num.arange( 0.5, 10., 0.5 )
MINOR_RANGE = MAJOR_RANGE.copy()
ECC_RANGE = num.arange( 0.1, 1.001, 0.1 )
MINBACKTHRESH_RANGE = num.arange( 0.5, 10., 1. )
MAXCLUSTPER_RANGE = range( 0, 10 )
MAXNCLUST_RANGE = range( 5, 200, 5 )
MAXPENALTYMERGE_RANGE = range( 0, 100, 10 )
MAXAREADELETE_RANGE = range( 0, 50, 5 )
MINAREAIGNORE_RANGE = range( 100, 10000, 500 )
ANGDIST_RANGE = num.arange( 1., 500., 20. )
MAXJUMP_RANGE = num.arange( 10., 500., 25. )
MINJUMP_RANGE = num.arange( 10., 250., 25. )
DAMPEN_RANGE = num.arange( 0., 1.001, 0.1 )
ANGLEDAMP_RANGE = num.arange( 0., 1.001, 0.1 )
# sanity check fails repeatedly:
# movie20071009_164618.sbfmf-pre4h20_l10_min7300.003.505.001.00_mean5900.006.506.000.50_max2800.001.509.000.80_6.50_8.00_30.00_25.00_2600.00_70.00_121.00_60.00_300.00_10.00_0.90_0.10.ann
# movie20071009_164618.sbfmfh20_l10_min9500.007.505.000.90_mean4800.007.504.500.90_max3500.004.003.500.30_9.50_4.00_0.00_5.00_9600.00_190.00_121.00_360.00_350.00_185.00_1.00_0.00.ann

PARAM_NAMES = ['minbackthresh', 'maxclustersperblob', 'maxpenaltymerge', 'maxareadelete', 'minareaignore', 'max_n_clusters', 'ang_dist_wt', 'max_jump', 'min_jump', 'dampen', 'angle_dampen']


def test_movie_for_known_movie( moviefile ):
    dirname, filename = os.path.split( moviefile )
    return os.path.join( TEST_ANN_DIR, filename )

def annname( moviefile, pre4 ):
    string = test_movie_for_known_movie( moviefile )
    if pre4:
        string += "-pre4"
    string += "h%d_l%d_min%.2f%.2f%.2f%.2f_mean%.2f%.2f%.2f%.2f_max%.2f%.2f%.2f%.2f" % (params.n_bg_std_thresh, params.n_bg_std_thresh_low, params.minshape.area, params.minshape.major, params.minshape.minor, params.minshape.ecc, params.meanshape.area, params.meanshape.major, params.meanshape.minor, params.meanshape.ecc, params.maxshape.area, params.maxshape.major, params.maxshape.minor, params.maxshape.ecc)
    for name in PARAM_NAMES:
        string += "_%.2f" % getattr( params, name )
    string += ".ann"
    return string

def print_vals():
    print "thresh low", params.n_bg_std_thresh_low, "hi", params.n_bg_std_thresh
    print "minshape", params.minshape, "meanshape", params.meanshape, "maxshape", params.maxshape
    print ' '.join( ["%s:%.2f" % (name, getattr( params, name )) for name in PARAM_NAMES] )


#######################################################################
# prepare_test_movies()
#######################################################################
def prepare_test_movies( filelist ):
    """Create test movies with known content."""
    if os.access( TEST_ANN_DIR, os.F_OK ):
        os.chmod( TEST_ANN_DIR, 0755 )
    else:
        os.mkdir( TEST_ANN_DIR )

    for moviefile in filelist.movie_files():
        for pre4 in [True, False]:
            destination = test_movie_for_known_movie( moviefile )
            docopy = False
            if not os.access( destination, os.R_OK ):
                docopy = True
            elif os.stat( moviefile ).st_size != os.stat( destination ).st_size:
                docopy = True

            if docopy:
                print "copying", moviefile
                shutil.copyfile( moviefile, destination )

        try:
            os.remove( annname( moviefile, True ) )
            os.remove( annname( moviefile, False ) )
        except OSError: pass


#######################################################################
# setup_tracking()
#######################################################################
def setup_tracking( moviefile, pre4 ):
    """Create all tracking objects."""
    # open movie
    testmovie = test_movie_for_known_movie( moviefile )
    movie = movies.Movie( testmovie, interactive=False )

    # create background model calculator
    if pre4:
        bg_model = bg_pre4.BackgroundCalculator( movie )
    else:
        bg_model = bg.BackgroundCalculator( movie )
    bg_img_shape = (movie.get_height(), movie.get_width())
    bg_model.set_buffer_maxnframes()

    # open annotation file
    ann_file = ann.AnnotationFile( annname( moviefile, pre4 ) )
    ann_file.InitializeData()

    # calculate bg
    bg_model.OnCalculate()

    # estimate fly shapes
    havevalue = (not params.maxshape.area == 9999.)
    haveshape = (not num.isinf( params.maxshape.area ))
    if (not haveshape) or (not havevalue):
        if pre4:
            params.movie = movie
            ell_pre4.est_shape( bg_model )
            params.movie = None
        else:
            ell.est_shape( bg_model )

    hindsight = hs.Hindsight( ann_file, bg_model )

    return movie, bg_model, ann_file, hindsight


#######################################################################
# test_shape_bounds()
#######################################################################
def test_shape_bounds():
    """Test that the current shape boundaries are valid."""
    return
    try:
        assert( params.minshape.area >= AREA_RANGE[0] )
        assert( params.minshape.major >= MAJOR_RANGE[0] )
        assert( params.minshape.minor >= MINOR_RANGE[0] )
        assert( params.minshape.ecc >= ECC_RANGE[0] )
    except AssertionError:
        print "**minshape error"
        raise

    try:
        assert( params.maxshape.area <= AREA_RANGE[-1] )
        assert( params.maxshape.major <= MAJOR_RANGE[-1] )
        assert( params.maxshape.minor <= MINOR_RANGE[-1] )
        assert( params.maxshape.ecc <= ECC_RANGE[-1] )
    except AssertionError:
        print "**maxshape error"
        raise


#######################################################################
# test_ellipses()
#######################################################################
def test_ellipses( ellipses ):
    """Check that all the items in a TargetList are currently valid."""
    if hasattr( ellipses, 'itervalues' ):
        items = ellipses.itervalues()
    else:
        items = ellipses
        
    for ellipse in items:
        try:
            assert( not ellipse.isEmpty() )
            assert( not ellipse.isnan() )
            assert( ellipse.area() > 0. )
        except AssertionError:
            print "**bad ellipse", ellipse
            raise

        try:
            assert( ellipse.major >= params.minshape.major )
            assert( ellipse.minor >= params.minshape.minor )
            assert( ellipse.area() >= params.minshape.area )
            assert( ellipse.eccentricity() >= params.minshape.ecc )
        except AssertionError:
            print "**minshape violation in ellipse", ellipse
            print "minshape", params.minshape
            raise

        try:
            assert( ellipse.major <= params.maxshape.major )
            assert( ellipse.minor <= params.maxshape.minor )
            assert( ellipse.area() <= params.maxshape.area )
            assert( ellipse.eccentricity() <= params.maxshape.ecc )
        except AssertionError:
            print "**maxshape violation in ellipse", ellipse
            print "maxshape", params.maxshape
            raise


#######################################################################
# run_movie_pre4()
#######################################################################
def run_movie_pre4( moviefile, comms ):
    """Run old-style tracking for a test movie."""
    quit_val = comms['quit_val']
    cmp_list = comms['cmp_list']
    shape_dict = comms['shape_dict']

    movie, bg_model, ann_file, hindsight = setup_tracking( moviefile, True )
    params.movie = movie

    if quit_val.value > 0: return

    try:
        test_shape_bounds()
    except:
        print "**aborting pre4 with invalid shape bounds"
        print "minshape", params.minshape
        print "maxshape", params.maxshape
        print_vals()
        quit_val.value = 1
        raise

    if shape_dict is not None:
        while not shape_dict.has_key( 'maxshape' ):
            time.sleep( 0.5 )
            if quit_val.value > 0: return
        try:
            assert( shape_dict['minshape'] == params.minshape )
            assert( shape_dict['meanshape'] == params.meanshape )
            assert( shape_dict['maxshape'] == params.maxshape )
        except AssertionError:
            print "**aborting after shape mismatch"
            print "minshape", shape_dict['minshape']
            print "pre4 minshape", params.minshape
            print "meanshape", shape_dict['meanshape']
            print "pre4 meanshape", params.meanshape
            print "maxshape", shape_dict['maxshape']
            print "pre4 maxshape", params.maxshape
            print_vals()
            quit_val.value = 1
            raise

    fst = time.time()

    params.start_frame = 0
    if MAX_FRAMES is None:
        max_frames = movie.get_n_frames()
    else:
        max_frames = min( movie.get_n_frames(), MAX_FRAMES )
    for frame in range( max_frames ):
        # perform background subtraction
        (dfore, isfore, cc, ncc) = bg_model.sub_bg( frame, dobuffer=True )

        # find observations
        if PRINT_COUNTS: print "pre4", frame, "ncc", ncc
        ellipses = ell_pre4.find_ellipses( dfore, cc, ncc )
        if PRINT_COUNTS: print "pre4", frame, "found ellipses", len( ellipses )
        try:
            test_ellipses( ellipses )
        except AssertionError:
            print "**find_ellipse output error in pre4 frame", frame
            print_vals()
            quit_val.value = 1
            raise

        # match target identities to observations
        if len( ann_file ) > 1:
            flies = ell.find_flies( ann_file[-2],
                                    ann_file[-1],
                                    ellipses,
                                    ann_file)
        elif len( ann_file ) == 1:
            flies = ell.find_flies( ann_file[-1],
                                    ann_file[-1],
                                    ellipses,
                                    ann_file )
        else:
            flies = ell.TargetList()
            for i,obs in enumerate(ellipses):
                newid = ann_file.GetNewId()
                obs.identity = newid
                flies.append(obs)

        try:
            test_ellipses( flies )
        except AssertionError:
            print "**find_flies output error in pre4 frame", frame
            print_vals()
            quit_val.value = 1
            raise

        if PRINT_COUNTS: print "pre4", frame, "found flies", len( flies )
        ann_file.append( flies )

        # fix any errors using hindsight
        if PRINT_COUNTS: print "pre4", frame, "pre-hindsight", len( ann_file[-1] )
        hindsight.fixerrors()
        if PRINT_COUNTS: print "pre4", frame, "post-hindsight", len( ann_file[-1] )

        try:
            test_ellipses( ann_file[-1] )
        except AssertionError:
            print "**hindsight output error in pre4 frame", frame
            print_vals()
            quit_val.value = 1
            raise

        if frame % 100 == 0: print "__pre4 tracking", frame, "/", movie.get_n_frames()

        # compare with newly tracked values
        if cmp_list is not None:
            while len( cmp_list ) <= frame:
                time.sleep( 0.5 )
                if quit_val.value > 0: return

            old = ann_file[-1]
            counts, new = cmp_list[frame]
            if PRINT_COUNTS: print "new counts", counts

            try:
                assert( len( new ) == len( old ) )
            except AssertionError:
                print "**aborting after data length error in frame", frame, "new", len( new ), "old", len( old )
                print moviefile
                print_vals()
                quit_val.value = 1
                raise

            try:
                compare_frames( new, old )
            except AssertionError:
                print "**data comparison error in frame", frame
                print "new", new
                print "old", old
                print moviefile
                print_vals()
                quit_val.value = 1
                raise

        if quit_val.value > 0: return

    ann_file.close()

    at = (time.time() - fst)/max_frames
    print "pre4 avg. per frame: %.3f s" % (at)
    #bt = num.mean( num.array( bgsub_times ) )
    #print "pre4 bg. sub: %.3f (%.1f%%); ellipses: %.3f (%.1f%%); flies: %.3f (%.1f%%); hindsight: %.3f (%.1f%%)" % (bt, 100.*bt/at, et, 100.*et/at, ft, 100.*ft/at, ht, 100.*ht/at)

    params.movie = None


#######################################################################
# run_movie()
#######################################################################
def run_movie( moviefile, comms ):
    """Run new-style tracking for a test movie."""
    quit_val = comms['quit_val']
    cmp_list = comms['cmp_list']
    shape_dict = comms['shape_dict']
    
    movie, bg_model, ann_file, hindsight = setup_tracking( moviefile, False )

    if quit_val.value > 0: return

    try:
        test_shape_bounds()
    except:
        print "**aborting with invalid shape bounds"
        print "minshape", params.minshape
        print "maxshape", params.maxshape
        print_vals()
        quit_val.value = 1
        raise

    shape_dict['minshape'] = params.minshape
    shape_dict['meanshape'] = params.meanshape
    shape_dict['maxshape'] = params.maxshape

    fst = time.time()

    params.start_frame = 0
    if MAX_FRAMES is None:
        max_frames = movie.get_n_frames()
    else:
        max_frames = min( movie.get_n_frames(), MAX_FRAMES )
    for frame in range( max_frames ):
        if cmp_list is not None: counts = []
            
        # perform background subtraction
        (dfore, isfore, cc, ncc) = bg_model.sub_bg( frame )

        # find observations
        if PRINT_COUNTS and (frame == PRINT_FRAME or PRINT_FRAME is None): print frame, "ncc", ncc
        if cmp_list is not None: counts.append( ncc )
        ellipses = ell.find_ellipses( dfore, cc, ncc )
        if PRINT_COUNTS and (frame == PRINT_FRAME or PRINT_FRAME is None): print frame, "found ellipses", len( ellipses )
        if cmp_list is not None: counts.append( len( ellipses ) )

        try:
            test_ellipses( ellipses )
        except AssertionError:
            print "**find_ellipses output error in frame", frame
            print_vals()
            quit_val.value = 1
            raise

        # match target identities to observations
        if len( ann_file ) > 1:
            flies = ell.find_flies( ann_file[-2],
                                    ann_file[-1],
                                    ellipses,
                                    ann_file)
        elif len( ann_file ) == 1:
            flies = ell.find_flies( ann_file[-1],
                                    ann_file[-1],
                                    ellipses,
                                    ann_file )
        else:
            flies = ell.TargetList()
            for i,obs in enumerate(ellipses):
                newid = ann_file.GetNewId()
                obs.identity = newid
                flies.append(obs)

        try:
            test_ellipses( flies )
        except AssertionError:
            print "**find_flies output error in frame", frame
            print_vals()
            quit_val.value = 1
            raise

        if PRINT_COUNTS and (frame == PRINT_FRAME or PRINT_FRAME is None): print frame, "found flies", len( flies )
        if cmp_list is not None: counts.append( len( flies ) )
        ann_file.append( flies )

        # fix any errors using hindsight
        if PRINT_COUNTS and (frame == PRINT_FRAME or PRINT_FRAME is None): print frame, "pre-hindsight", len( ann_file[-1] )
        if cmp_list is not None: counts.append( len( ann_file[-1] ) )
        hindsight.fixerrors()
        if PRINT_COUNTS and (frame == PRINT_FRAME or PRINT_FRAME is None): print frame, "post-hindsight", len( ann_file[-1] )
        if cmp_list is not None: counts.append( len( ann_file[-1] ) )

        try:
            test_ellipses( ann_file[-1] )
        except AssertionError:
            print "**hindsight output error in frame", frame
            print_vals()
            quit_val.value = 1
            raise

        if frame % 500 == 0: print "__tracking", frame, "/", movie.get_n_frames()

        if quit_val.value > 0: return

        if cmp_list is not None:
            cmp_list.append( (counts, ann_file[-1]) )

    ann_file.close()

    at = (time.time() - fst)/max_frames
    print "avg. per frame: %.3f s" % (at)
    #bt = num.mean( num.array( bgsub_times ) )
    #print "bg. sub: %.3f (%.1f%%); ellipses: %.3f (%.1f%%)" % (bt, 100.*bt/at, et, 100.*et/at)


#######################################################################
# compare_frames()
#######################################################################
def compare_frames( newframe, oldframe ):
    def compare_flies( newfly, oldfly ):
        eps = 1.e-5
        #assert( newfly.identity == oldfly.identity )
        assert( abs( newfly.center.x - oldfly.center.x ) < eps )
        assert( abs( newfly.center.y - oldfly.center.y ) < eps )
        assert( abs( newfly.height - oldfly.height ) < eps )
        assert( abs( newfly.width - oldfly.width ) < eps )
        assert( abs( newfly.angle - oldfly.angle ) < eps )

    oldfound = {fly.identity: False for fly in oldframe.itervalues()}

    # make sure every new fly matches some old fly
    for newfly in newframe.itervalues():
        newfound = False
        for oldfly in oldframe.itervalues():
            try:
                compare_flies( newfly, oldfly )
            except AssertionError:
                continue
            else:
                newfound = True
                oldfound[oldfly.identity] = True
                # also match other identical flies
                for otherfly in oldframe.itervalues():
                    try:
                        compare_flies( oldfly, otherfly )
                    except AssertionError:
                        continue
                    else:
                        oldfound[otherfly.identity] = True
                break
        try:
            assert( newfound )
        except Exception as e:
            print "no match for new fly", newfly
            print "in old", oldframe
            for oldfly in oldframe.itervalues():
                print "..comparing with", oldfly
                try:
                    compare_flies( newfly, oldfly )
                except AssertionError:
                    print "False"
                else:
                    print "True"
            raise e

    # make sure every old fly matches some new fly
    for id, truth in oldfound.iteritems():
        try:
            assert( truth )
        except Exception as e:
            oldfly = oldframe[id]
            print "no match for old fly", oldfly
            print "in new", newframe
            for newfly in newframe.itervalues():
                print "..comparing with", newfly
                try:
                    compare_flies( newfly, oldfly )
                except AssertionError:
                    print "False"
                else:
                    print "True"
            raise e

#######################################################################
# compare_test_movie()
#######################################################################
def compare_test_movie( moviefile, n_err ):
    """Compare annotation data from test movie with known movie."""
    newann = ann.AnnotationFile( annname( moviefile, False ), readonly=True )
    oldann = ann.AnnotationFile( annname( moviefile, True ), readonly=True )

    try:
        assert( len( newann ) == len( oldann ) )
    except AssertionError:
        print "**file length error; old", len( oldann ), "new", len( newann )
        print moviefile
        n_err.value += 1
    except:
        n_err.value += 1
        print traceback.format_exc()
        return

    for i, (new, old) in enumerate( zip( newann, oldann ) ):
        try:
            assert( len( new ) == len( old ) )
        except AssertionError:
            print "**data length error in frame", i, "new", len( new ), "old", len( old )
            n_err.value += 1
        except:
            n_err.value += 1
            print traceback.format_exc()
            break

        try:
            compare_frames( new, old )
        except AssertionError:
            print "**data comparison error in frame", i
            print "new", new
            print "old", old
            n_err.value += 1
        except:
            n_err.value += 1
            print traceback.format_exc()
            break

        if n_err.value > 5:
            print "**aborting comparison"
            print moviefile
            break

    if n_err.value > 0:
        print_vals()


#######################################################################
# do_all_for_movie()
#######################################################################
def do_all_for_movie( moviefile, quit_vals ):
    """Run side-by-side tracking comparison for a movie."""
    print "==%s %s" % (os.path.split( moviefile )[1], time.asctime())
    
    def run_func( func, moviefile, comms ):
        proc = multiprocessing.Process( target=func,
                                        args=(moviefile, comms) )
        proc.start()
        return proc

    st = time.time()

    # run pre4 tracking only if necessary
    cmp_list = None
    shape_dict = None
    cmp_list = multiprocessing.Manager().list()
    shape_dict = multiprocessing.Manager().dict()
    comms = {'quit_val': quit_vals[0],
             'cmp_list': cmp_list,
             'shape_dict': shape_dict}
    proc_pre4 = run_func( run_movie_pre4, moviefile, comms )

    comms = {'quit_val': quit_vals[1],
             'cmp_list': cmp_list,
             'shape_dict': shape_dict}
    proc = run_func( run_movie, moviefile, comms )

    while proc.exitcode is None:
        proc.join( 1. )
        if quit_vals[0].value > 0:
            quit_vals[1].value = quit_vals[0].value
            
    if proc.exitcode != 0:
        print "new tracking crashed", proc.exitcode
        print_vals()
        quit_vals[0].value = 1
        proc_pre4.join()
        exit( 1 )
    
    proc_pre4.join()
    if proc_pre4.exitcode != 0:
        print "pre4 tracking crashed", proc_pre4.exitcode
        print_vals()
        exit( 1 )

    if quit_vals[0].value > 0 or quit_vals[1].value > 0:
        print "terminating"
        exit( 1 )

    n_err = multiprocessing.Value( 'i', 0 )
    compare_test_movie( moviefile, n_err )
    if n_err.value != 0:
        print "...errors raised"
        exit( 2 )

    print "elapsed", time.time() - st, "s\n"


#######################################################################
# test_varying_thresholds()
#######################################################################
def test_varying_thresholds( moviefile ):
    """Track a movie repeatedly with varying threshold combinations."""
    def do_movie( moviefile ):
        try:
            os.remove( annname( moviefile, True ) )
            os.remove( annname( moviefile, False ) )
        except OSError: pass

        print "==thresh low", params.n_bg_std_thresh_low, "high", params.n_bg_std_thresh
        do_all_for_movie( moviefile, (multiprocessing.Value( 'i', 0 ),
                                      multiprocessing.Value( 'i', 0 )) )

    def los_for_hi( hi ):
        los = range( 1, 6 )
        [los.append( lo ) for lo in range( 10, int( hi ) + 1, 5 )]
        return los

    hi_jump = 5
    hi_max = 200
    n_proc = 2

    save_lo = params.n_bg_std_thresh_low
    save_hi = params.n_bg_std_thresh

    # optimize parallelization, serially by brute force
    def count_for_rng( lo, hi ):
        count = 0
        for h in range( lo, hi, hi_jump ):
            for l in los_for_hi( h ):
                count += 1
        return count
    
    def score_for_split( split ):
        split.insert( 0, hi_jump )
        split.append( hi_max )
        counts = []
        for s in range( 1, len( split ) ):
            counts.append( count_for_rng( split[s - 1], split[s] ) )
        return max( counts )

    def split_his( hi_range ):
        best_split = []
        if n_proc > 1:
            x = int( len( hi_range )/(n_proc - 1) )
        else:
            x = len( hi_range )
        for p in range( x, len( hi_range ) - 1, x ):
            best_split.append( hi_range[p] )
        best_score = score_for_split( best_split )
        for i in range( 10000 ):
            split = random.sample( hi_range, n_proc - 1 )
            split.sort()
            score = score_for_split( split )
            if score < best_score:
                best_split = split
                best_score = score
        return best_split

    # test in parallel
    def do_hi_range( hi_range ):
        for params.n_bg_std_thresh in hi_range:
            for params.n_bg_std_thresh_low in los_for_hi( params.n_bg_std_thresh ):
                do_movie( moviefile )

    hi_range = range( hi_jump, hi_max, hi_jump )
    hi_split = split_his( hi_range )
    procs = []
    for p in range( n_proc ):
        i = hi_range.index( hi_split[p] )
        if hi_split[p + 1] in hi_range:
            j = hi_range.index( hi_split[p + 1] )
        else:
            j = len( hi_range )
        his = hi_range[i:j]
        proc = multiprocessing.Process( target=do_hi_range, args=(his,) )
        proc.start()
        procs.append( proc )

    active_procs = procs[:]
    crash = False
    while len( active_procs ) > 0 and not crash:
        time.sleep( 1. )
        for proc in active_procs:
            if proc.exitcode is not None:
                active_procs.remove( proc )
                if proc.exitcode != 0:
                    crash = True
                    break

    [proc.terminate() for proc in active_procs]
    [proc.join() for proc in procs]
    if crash: exit( 1 )

    params.n_bg_std_thresh_low = save_lo
    params.n_bg_std_thresh = save_hi


#######################################################################
# test_tracking_settings()
#######################################################################
def test_tracking_settings( moviefile ):
    """Track a movie repeatedly with varying tracking settings."""
    def do_movie( moviefile, quit_flags ):
        try:
            os.remove( annname( moviefile, True ) )
            os.remove( annname( moviefile, False ) )
        except OSError: pass

        print "==minshape", params.minshape, "meanshape", params.meanshape, "maxshape", params.maxshape
        print "==%s" % ' '.join( ["%s:%.2f" % (name, getattr( params, name )) for name in PARAM_NAMES] )
        do_all_for_movie( moviefile, quit_flags )

    save_params = {}
    save_params['minshape'] = params.minshape.copy()
    save_params['meanshape'] = params.meanshape.copy()
    save_params['maxshape'] = params.maxshape.copy()
    for name in PARAM_NAMES:
        save_params[name] = getattr( params, name )

    n_proc = 4
    n_combos = 12
    # short movies: 470 combos/hr
    # long movies: 3 combos/hr

    if True:
        combos = []
        for c in range( n_combos ):
            minshape = ShapeParams( random.choice( MAJOR_RANGE ),
                                    random.choice( MINOR_RANGE ),
                                    random.choice( AREA_RANGE ),
                                    random.choice( ECC_RANGE ) )
            meanshape = ShapeParams( random.choice( MAJOR_RANGE ),
                                     random.choice( MINOR_RANGE ),
                                     random.choice( AREA_RANGE ),
                                     random.choice( ECC_RANGE ) )
            maxshape = ShapeParams( random.choice( MAJOR_RANGE ),
                                    random.choice( MINOR_RANGE ),
                                    random.choice( AREA_RANGE ),
                                    random.choice( ECC_RANGE ) )
            others = {'minbackthresh': random.choice( MINBACKTHRESH_RANGE ),
                      'maxclustersperblob': random.choice( MAXCLUSTPER_RANGE ),
                      'max_n_clusters': random.choice( MAXNCLUST_RANGE ),
                      'maxpenaltymerge': random.choice( MAXPENALTYMERGE_RANGE ),
                      'maxareadelete': random.choice( MAXAREADELETE_RANGE ),
                      'minareaignore': random.choice( MINAREAIGNORE_RANGE ),
                      'ang_dist_wt': random.choice( ANGDIST_RANGE ),
                      'max_jump': random.choice( MAXJUMP_RANGE ),
                      'min_jump': random.choice( MINJUMP_RANGE ),
                      'dampen': random.choice( DAMPEN_RANGE ),
                      'angle_dampen': random.choice( ANGLEDAMP_RANGE )}
            combos.append( (minshape, meanshape, maxshape, others) )
    else:
#min9500.007.505.000.90_mean4800.007.504.500.90_max3500.004.003.500.30_9.50_4.00_0.00_5.00_9600.00_190.00_121.00_360.00_350.00_185.00_1.00_0.00
        minshape = ShapeParams( 7.5, 5., 9500., 0.9 )
        meanshape = ShapeParams( 7.5, 4.5, 4800., 0.9 )
        maxshape = ShapeParams( 4., 3.5, 3500., 0.3 )
        others = {'minbackthresh': 9.5,
                  'maxclustersperblob': 4.,
                  'maxpenaltymerge': 0.,
                  'maxareadelete': 5.,
                  'minareaignore': 9600.,
                  'max_n_clusters': 190.,
                  'ang_dist_wt': 121.,
                  'max_jump': 360.,
                  'min_jump': 185.,
                  'dampen': 1.,
                  'angle_dampen': 0.}
        combos = [(minshape, meanshape, maxshape, others)]

    def do_combos( combos, quit_flags ):
        for vals in combos:
            minshape, meanshape, maxshape, others = vals
            params.minshape = minshape.copy()
            params.meanshape = meanshape.copy()
            params.maxshape = maxshape.copy()
            for key, value in others.iteritems():
                setattr( params, key, value )
            do_movie( moviefile, quit_flags )

    procs = []
    quit_flags = []
    for p in range( n_proc ):
        lo = len( combos )*p/n_proc
        hi = len( combos )*(p + 1)/n_proc
        flags = (multiprocessing.Value( 'i', 0 ),
                 multiprocessing.Value( 'i', 0 ))
        proc = multiprocessing.Process( target=do_combos,
                                        args=(combos[lo:hi], flags) )
        proc.start()
        procs.append( proc )
        quit_flags.append( flags )

    active_procs = procs[:]
    crash = False
    while len( active_procs ) > 0 and not crash:
        time.sleep( 1. )
        for proc in active_procs:
            if proc.exitcode is not None:
                active_procs.remove( proc )
                if proc.exitcode != 0:
                    crash = True
                    break

    for f1, f2 in quit_flags:
        f1.value = 1
        f2.value = 1
    [proc.join() for proc in procs]
    if crash: exit( 1 )

    params.minshape = save_params['minshape']
    params.meanshape = save_params['meanshape']
    params.maxshape = save_params['maxshape']
    for name in PARAM_NAMES:
        setattr( params, name, save_params[name] )
    

# run all tests if ALL_ENABLED, or selectively enable some tests below
ALL_ENABLED = False
TEST_ACCURACY          = ALL_ENABLED or False
TEST_THRESHOLDS        = ALL_ENABLED or True
TEST_TRACKPARAMS       = ALL_ENABLED or False

PRINT_COUNTS = False
PRINT_FRAME = None

MAX_FRAMES = None
MAX_MOVIES = None


if __name__ == '__main__':

    st = time.time()

    filelist = test_filelist.CtraxFileList( ['sample_sbfmf1', 'sample_sbfmf2'] )
    #filelist = test_filelist.CtraxFileList( ['short'] )
    if MAX_MOVIES is not None:
        filelist = filelist[:MAX_MOVIES]

    prepare_test_movies( filelist )

    if TEST_ACCURACY:
        print "==test accuracy"
        for moviefile in filelist.movie_files():
            do_all_for_movie( moviefile, (multiprocessing.Value( 'i', 0 ),
                                          multiprocessing.Value( 'i', 0 )) )
    if TEST_THRESHOLDS:
        print "==test thresholds"
        for moviefile in filelist.movie_files():
            test_varying_thresholds( moviefile )
    if TEST_TRACKPARAMS:
        print "==test parameters"
        for moviefile in filelist.movie_files():
            test_tracking_settings( moviefile )

    print "total", (time.time() - st)/60., "min"
    print "\n...all tests passed"

