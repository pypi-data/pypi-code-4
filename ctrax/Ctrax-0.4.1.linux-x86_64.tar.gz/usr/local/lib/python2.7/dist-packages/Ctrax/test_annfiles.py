#!/usr/bin/env python

# annfiles unit tests
# JAB 8/18/12

import multiprocessing
import os
import Queue
import random
import shutil
import stat
import struct
from subprocess import call
import sys
import tempfile
import threading
import time
import traceback

import numpy as num

import annfiles_pre4 as oldann
import annfiles as ann
from chooseorientations import ChooseOrientations
import ellipsesk as ell
from params import params
params.interactive = False
params.enable_feedback( False )
import test_filelist
import bg
import movies
from version import __version__


REAL_ANN_DIR = "/home/jbender/data/ctrax-data/playdata/batch-test"
TEST_ANN_DIR = "/home/jbender/ann_data_test"

REAL_ANN = "movie20100707_141914_trimmed3.fmf.ann.keep"
TEST_MOVIE = "movie20100707_141914_trimmed3.fmf"


def prepare_test_ann():
    """Create test annotation files with known content; back them up."""
    if os.access( TEST_ANN_DIR, os.F_OK ):
        os.chmod( TEST_ANN_DIR, 0755 )
    else:
        os.mkdir( TEST_ANN_DIR )

    global REAL_ANN, TEST_MOVIE

    shutil.copyfile( os.path.join( REAL_ANN_DIR, TEST_MOVIE ),
                     os.path.join( TEST_ANN_DIR, TEST_MOVIE ) )
    shutil.copyfile( os.path.join( REAL_ANN_DIR, REAL_ANN ),
                     os.path.join( TEST_ANN_DIR, REAL_ANN ) )

    REAL_ANN = os.path.join( TEST_ANN_DIR, REAL_ANN )
    TEST_MOVIE = os.path.join( TEST_ANN_DIR, TEST_MOVIE )
    
    shutil.copyfile( REAL_ANN, TEST_MOVIE + ".ann" )
    shutil.copyfile( TEST_MOVIE + ".ann", TEST_MOVIE + ".ann_anntest" )

def reset_test_ann():
    """Copy backups of test annotation files back into place."""
    initial_permissions = stat.S_IMODE( os.lstat( TEST_ANN_DIR ).st_mode )
    os.chmod( TEST_ANN_DIR, 0755 )
    shutil.copyfile( TEST_MOVIE + ".ann_anntest", TEST_MOVIE + ".ann" )
    os.chmod( TEST_ANN_DIR, initial_permissions )

def delete_test_ann():
    """Delete test annotation file."""
    try:
        os.remove( TEST_MOVIE + ".ann" )
    except OSError:
        pass


#######################################################################
# test_object_creation()
#######################################################################
def test_object_creation( n_err ):
    """Test with all combinations of input parameters."""
    movie = movies.Movie( TEST_MOVIE, interactive=False )
    initial_dir_permissions = stat.S_IMODE( os.lstat( TEST_ANN_DIR ).st_mode )

    file_exists_vals = [True, False]
    dir_readonly_vals = [True, False]
    filename_vals = [None, TEST_MOVIE + ".ann"]
    bg_model_vals = [None, bg.BackgroundCalculator( movie )]
    justreadheader_vals = [False, True]
    readbgmodel_vals = [False, True]
    readonly_vals = [False, True]
    bg_img_shape_vals = [None, (10,10), (movie.get_height(), movie.get_width())]
    
    n_tests = len( file_exists_vals ) * len( dir_readonly_vals ) * len( filename_vals ) * len( bg_model_vals ) * len( justreadheader_vals ) * len( readbgmodel_vals ) * len( readonly_vals ) * len( bg_img_shape_vals )
    cur_test = 1

    for file_exists in file_exists_vals:
     for dir_readonly in dir_readonly_vals:
        for filename in filename_vals:
         for bg_model in bg_model_vals:
          for justreadheader in justreadheader_vals:
           for readbgmodel in readbgmodel_vals:
            for readonly in readonly_vals:
             for bg_img_shape in bg_img_shape_vals:

                 print "running object creation test %d/%d" % (cur_test, n_tests)

                 if file_exists:
                     reset_test_ann()
                 else:
                     delete_test_ann()
                 if dir_readonly:
                     os.chmod( TEST_ANN_DIR, 0555 )
                 else:
                     os.chmod( TEST_ANN_DIR, 0755 )

                 # set test parameters to see if header is being read
                 params.n_bg_std_thresh = None
                 if bg_model is not None:
                     bg_model.med = None
                 
                 try:
                     obj = ann.AnnotationFile( filename=filename,
                                               bg_model=bg_model,
                                               justreadheader=justreadheader,
                                               readbgmodel=readbgmodel,
                                               readonly=readonly,
                                               bg_img_shape=bg_img_shape )

                     if filename is None:
                         if readonly:
                             # should have raised an exception
                             # if this executes, the test failed
                             assert( False )
                         
                     if file_exists:
                         if justreadheader:
                             assert( len( obj ) == 0 )
                         elif filename is not None:
                             assert( len( obj ) > 0 )
                             arr = range( len( obj ) )

                             # test slice operator
                             new = obj[:10]
                             assert( len( new ) == 10 )
                             assert( len( new ) == len( arr[:10] ) )
                             new = obj[5:]
                             assert( len( new ) == len( obj ) - 5 )
                             assert( len( new ) == len( arr[5:] ) )
                             new = obj[5:10]
                             assert( len( new ) == 5 )
                             assert( len( new ) == len( arr[5:10] ) )
                             new = obj[1:10:2]
                             assert( len( new ) == 5 )
                             assert( len( new ) == len( arr[1:10:2] ) )
                             new = obj[:-1]
                             assert( len( new ) == len( obj ) - 1 )
                             assert( len( new ) == len( arr[:-1] ) )
                             new = obj[-1:]
                             assert( len( new ) == 1 )
                             assert( len( new ) == len( arr[-1:] ) )
                             new = obj[:-10:-1]
                             assert( len( new ) == 9 )
                             assert( len( new ) == len( arr[:-10:-1] ) )
                             new = obj[-5:-10:-1]
                             assert( len( new ) == 5 )
                             assert( len( new ) == len( arr[-5:-10:-1] ) )
                             new = obj[::-1]
                             assert( len( new ) == len( obj ) )
                             assert( len( new ) == len( arr[::-1] ) )
                             new = obj[-10::-1]
                             assert( len( new ) == len( obj ) - 9 )
                             assert( len( new ) == len( arr[-10::-1] ) )

                         if bg_model is not None and \
                                bg_img_shape is not None and \
                                bg_img_shape[0] == movie.get_height():
                             if filename is not None and readbgmodel:
                                 assert( bg_model.med is not None )
                                 assert( bg_model.med.shape[0] == bg_img_shape[0] and bg_model.med.shape[1] == bg_img_shape[1] )
                             else:
                                 assert( bg_model.med is None )

                         if (filename is not None) and (not dir_readonly) and (not readonly):
                             assert( os.access( obj._backup_filename, os.F_OK ) )

                     else:
                         if readonly:
                             assert( False )
                         if justreadheader:
                             assert( params.n_bg_std_thresh is None )
                         if bg_model is not None and readbgmodel:
                             assert( bg_model.med is None )

                     if filename is None:
                         assert( os.access( obj._filename, os.F_OK ) )
                     else:
                         assert( os.access( TEST_MOVIE + ".ann", os.F_OK ) )

                 except AssertionError:
                     # test failed by not raising an exception
                     print "object creation failed with", file_exists, dir_readonly, filename, bg_model, justreadheader, readbgmodel, readonly, bg_img_shape
                     print traceback.format_exc()
                     n_err.value += 1
                     
                 except Exception, details:
                     # exception was expected in a few cases...
                     if not file_exists and readonly and filename is not None:
                         pass
                     elif filename is None and (readonly or readbgmodel):
                         pass
                     elif dir_readonly and not readonly:
                         pass

                     else:
                         # exception was unexpected -- test failed
                         print "object creation failed with", file_exists, dir_readonly, filename, bg_model, justreadheader, readbgmodel, readonly, bg_img_shape
                         print traceback.format_exc()
                         n_err.value += 1

                 finally:
                     cur_test += 1

                 if n_err.value > 0: return

    os.chmod( TEST_ANN_DIR, initial_dir_permissions )


#######################################################################
# test_backward_compatibility_read()
#######################################################################
def test_backward_compatibility_read( n_err ):
    """Comparison test with all available file versions and contents."""
    filelist = test_filelist.CtraxFileList()
    
    movie_files = filelist.movie_files()
    annfiles = filelist.ann_files()

    n_tests = len( movie_files )
    cur_test = 1

    for moviefile, annfile in zip( movie_files, annfiles ):
        print "running read comparison test %d/%d" % (cur_test, n_tests)
        
        movie = movies.Movie( moviefile, interactive=False )
        bg_model = bg.BackgroundCalculator( movie )
        bg_img_shape = (movie.get_height(), movie.get_width())

        try:
            obj = ann.AnnotationFile( annfile,
                                      bg_model,
                                      readonly=True,
                                      bg_img_shape=bg_img_shape )

            old_bg_model = bg.BackgroundCalculator( movie )
            params.movie = movie
            params.movie_size = bg_img_shape
            oldobj = oldann.AnnotationFile( annfile, old_bg_model,
                                            doreadtrx=True, readonly=True )

            # test bg model reading
            for field in ann.BG_MODEL_FIELDS + ann.IMAGE_DATA_FIELDS:
                if hasattr( bg_model, field ) and hasattr( old_bg_model, field ):
                    try:
                        assert( getattr( bg_model, field ) == getattr( old_bg_model, field ) )
                    except ValueError:
                        new = getattr( bg_model, field )
                        old = getattr( bg_model, field )
                        try:
                            assert( (new == old).all() )
                        except AssertionError:
                            print "error comparing image field %s" % field
                            raise
                    except AssertionError:
                        print "error comparing field %s" % field
                        raise
                elif (not hasattr( bg_model, field )) and \
                         (not hasattr( old_bg_model, field )):
                    pass
                else:
                    raise AttributeError( "error comparing field %s: new has field? %s; old has field? %s" % (field, str( hasattr( bg_model, field ) ), str( hasattr( old_bg_model, field ) )) )

            # test data reading
            for i, (new, old) in enumerate( zip( obj, oldobj ) ):
                try:
                    assert( all( new == old ) )
                except TypeError:
                    try:
                        assert( new == old )
                    except AssertionError:
                        print "data comparison error in frame", i
                        raise
                except AssertionError:
                    print "data comparison error in frame", i
                    raise
                
        except:
            print "error with backward-compatibility test reading", annfile
            print traceback.format_exc()
            n_err.value += 1
        finally:            
            cur_test += 1

        if n_err.value > 0: return


#######################################################################
# test_weird_headers()
#######################################################################
def test_weird_headers( n_err ):
    """Test graceful handling of invalid header data."""
    reset_test_ann()

    movie = movies.Movie( TEST_MOVIE, interactive=False )
    bg_img_shape = (movie.get_height(), movie.get_width())
    
    def do_read( filename, readonly ):
        """Read a file."""
        bg_model = bg.BackgroundCalculator( movie )
        obj = ann.AnnotationFile( filename, bg_model, readonly=readonly,
                                  bg_img_shape=bg_img_shape )
        return obj, bg_model

    def test_fail( filename, test_name ):
        """Run a test that's supposed to fail."""
        try:
            do_read( filename, True )
            assert( False )
        except ValueError:
            try:
                do_read( filename, False )
                assert( False )
            except ValueError:
                pass
        except:
            print "error", test_name
            print traceback.format_exc()
            return 1
        finally:
            os.remove( filename )
        return 0

    def test_pass( filename, test_name ):
        """Run a test that's supposed to pass."""
        stuff = None
        try:
            do_read( filename, True )
            stuff = do_read( filename, False )
        except:
            print "error", test_name
            print traceback.format_exc()
            return 1, stuff
        finally:
            os.remove( filename )
        return 0, stuff

    # test read empty
    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.close()
    n_err.value += test_fail( fp.name, "reading empty file" )

    # test only header start
    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.write( "Ctrax header\n" )
    fp.close()
    n_err.value += test_fail( fp.name, "reading start-header only" )

    # test empty header
    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.write( "Ctrax header\n" )
    fp.write( "end header\n" )
    fp.close()
    new_err, annobj = test_pass( fp.name, "reading empty header" )
    n_err.value += new_err

    # test weird crap in header
    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.write( "Ctrax header\n" )
    fp.write( "fff" ) # no newline
    fp.write( "end header\n" )
    fp.close()
    n_err.value += test_fail( fp.name, "reading weird header 1" )

    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.write( "Ctrax header\n" )
    fp.write( "fff\n" )
    fp.write( "end header\n" )
    fp.close()
    n_err.value += test_fail( fp.name, "reading weird header 2" )

    fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
    fp.write( "Ctrax header\n" )
    fp.write( "foo:123\n" )
    fp.write( "end header\n" )
    fp.close()
    new_err, annobj = test_pass( fp.name, "reading weird header 3" )
    n_err.value += new_err

    # test varying image sizes
    def write_bg_med( size_nominal, size_actual, write_version=False ):
        """Write a header with a phony background median image."""
        n_bytes_nominal = 8*size_nominal
        n_bytes_actual = 8*size_actual
        
        fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
        fp.write( "Ctrax header\n" )
        if write_version:
            fp.write( "version:%s\n" % __version__ )
        fp.write( "background median:%d\n" % n_bytes_nominal )
        data = [127. for i in range( size_actual )]
        binary = struct.pack( '%dd' % size_actual, *data )
        assert( len( binary ) == n_bytes_actual )
        fp.write( binary )
        if write_version:
            fp.write( "\n" )
        fp.write( "end header\n" )
        fp.close()

        return fp.name

    filename = write_bg_med( 10, 10 )
    print "testing image size 1"
    new_err, annobj = test_pass( filename, "reading image size 1" )
    n_err.value += new_err

    filename = write_bg_med( 10, bg_img_shape[0]*bg_img_shape[1] )
    print "testing image size 2"
    n_err.value += test_fail( filename, "reading image size 2" )

    filename = write_bg_med( bg_img_shape[0]*bg_img_shape[1], 10 )
    print "testing image size 3"
    n_err.value += test_fail( filename, "reading image size 3" )

    filename = write_bg_med( bg_img_shape[0]*bg_img_shape[1],
                             bg_img_shape[0]*bg_img_shape[1] )
    print "testing image size 4"
    new_err, annobj = test_pass( filename, "reading image size 4" )
    n_err.value += new_err

    filename = write_bg_med( bg_img_shape[0]*bg_img_shape[1],
                             bg_img_shape[0]*bg_img_shape[1],
                             write_version=True )
    print "testing image size 5"
    new_err, annobj = test_pass( filename, "reading image size 5" )
    n_err.value += new_err

    try:
        assert( annobj is not None )
        annfile, bg_model = annobj
        assert( hasattr( bg_model, 'med' ) )
        assert( bg_model.med.shape[0] == bg_img_shape[0] )
        assert( bg_model.med.shape[1] == bg_img_shape[1] )
        assert( num.all( bg_model.med == 127. ) )
    except AssertionError:
        print "error reading background median image"
        n_err.value += 1
    except Exception, details:
        print "error reading background median image:", details
        n_err.value += 1


#######################################################################
# test_weird_data()
#######################################################################
def test_weird_data( n_err ):
    """Test graceful handling of invalid track data."""
    reset_test_ann()

    movie = movies.Movie( TEST_MOVIE, interactive=False )
    bg_img_shape = (movie.get_height(), movie.get_width())

    def write_header():
        fp = tempfile.NamedTemporaryFile( mode='wb+', suffix='.ann', delete=False )
        fp.write( "Ctrax header\n" )
        fp.write( "version:%s\n" % __version__ )
        fp.write( "end header\n" )
        return fp

    def test_read( filename ):
        bg_model = bg.BackgroundCalculator( movie )
        obj = None

        try:
            obj = ann.AnnotationFile( filename, bg_model, readonly=True,
                                      bg_img_shape=bg_img_shape )
        except Exception, details:
            print "read error:", details
            print traceback.format_exc()
            return obj, bg_model, 1
        finally:
            os.remove( filename )
            
        return obj, bg_model, 0

    def test_length( annfile, expected_n_frames, expected_n_flies ):
        if annfile is None:
            try:
                assert( expected_n_frames == 0 )
            except:
                print "annfile was none -- has 0 frames, not", expected_n_frames
                return 1
            else:
                return 0
            
        n = 0
        try:
            assert( len( annfile ) == expected_n_frames )
        except AssertionError:
            print "expected file to have %d frames, but it has %d" % (expected_n_frames, len( annfile ))
            n += 1
        except Exception, details:
            print "error testing length of annfile:", details
            n += 1
            
        try:
            for f, frame in enumerate( annfile ):
                assert( len( frame ) == expected_n_flies[f] )
        except AssertionError:
            print "frame", f, "didn't have the expected number of flies (%d not %d)" % (len( frame ), expected_n_flies[f])
            n += 1
        except Exception, details:
            print "error reading annfile data:", details
            print traceback.format_exc()
            n += 1
        return n

    # test empty data
    print "test empty"
    fp = write_header()
    fp.write( "\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [0] )

    # test one number
    print "test one number"
    fp = write_header()
    fp.write( "1\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [0] )

    # test two numbers
    print "test two numbers"
    fp = write_header()
    fp.write( "1 2\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [0] )

    # test two numbers on two lines
    print "test two numbers multiline"
    fp = write_header()
    fp.write( "1 2\n" )
    fp.write( "3 4\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 2, [0,0] )

    # test one fly with spaces
    print "test one fly with spaces"
    fp = write_header()
    fp.write( "1 2 3 4 5 6\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [1] )

    # test one fly with tabs
    print "test one fly with tabs"
    fp = write_header()
    fp.write( "1\t2\t3\t4\t5\t6\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [1] )

    # test 1.5 flies
    print "test 1.5 flies"
    fp = write_header()
    fp.write( "1 2 3 4 5 6 1 2 3\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [0] )

    # test 3 flies
    print "test 3 flies"
    fp = write_header()
    three_flies = [1,2,3,4,5,6, 11,22,33,44,55,66, 111,222,333,444,555,666]
    for d in three_flies:
        fp.write( "%d " % d )
    fp.write( "\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 1, [3] )

    # test some text
    for n in range( 3 ):
        for i in range( len( three_flies ) ):
            print "test 3 flies", n*len( three_flies ) + i + 1, "/", 3*len( three_flies )
            fp = write_header()
            for j in range( i ):
                fp.write( "%d " % three_flies[j] )
            fp.write( "garbage " )
            for j in range( i + 1, len( three_flies ) ):
                fp.write( "%d " % three_flies[j] )
            fp.write( "\n" )
            for extra in range( n ):
                for d in three_flies:
                    fp.write( "%d " % d )
                fp.write( "\n" )
            fp.close()
            annfile, bg_model, new_errs = test_read( fp.name )
            n_err.value += new_errs
            n_err.value += test_length( annfile, n + 1, [3]*(n + 1) )

            if n_err.value != 0: return

    # test truncated lines
    print "test truncated lines 1"
    fp = write_header()
    for d in three_flies:
        fp.write( "%d " % d )
    fp.write( "\n" )
    for d in three_flies[:-1]:
        fp.write( "%d " % d )
    fp.write( "\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 2, [3,0] )

    print "test truncated lines 2"
    fp = write_header()
    for d in three_flies:
        fp.write( "%d " % d )
    fp.write( "\n" )
    for d in three_flies[:-1]:
        fp.write( "%d " % d )
    fp.write( "\n" )
    for d in three_flies:
        fp.write( "%d " % d )
    fp.write( "\n" )
    fp.close()
    annfile, bg_model, new_errs = test_read( fp.name )
    n_err.value += new_errs
    n_err.value += test_length( annfile, 3, [3,0,3] )


#######################################################################
# test_backward_compatibility_write()
#######################################################################
def test_backward_compatibility_write( n_err ):
    """Test that files can be read in older Ctrax."""
    reset_test_ann()

    movie = movies.Movie( TEST_MOVIE, interactive=False )
    bg_img_shape = (movie.get_height(), movie.get_width())

    old_bg_model = bg.BackgroundCalculator( movie )
    params.movie = movie
    params.movie_size = bg_img_shape
    existing_ann = oldann.AnnotationFile( TEST_MOVIE + ".ann", old_bg_model,
                                          doreadtrx=True, readonly=True )

    def read_test( filename ):
        test_bg_model = bg.BackgroundCalculator( movie )
        try:
            oldtest = oldann.AnnotationFile( filename, test_bg_model,
                                             doreadtrx=True, readonly=True )
            assert( oldtest is not None )
        except Exception, details:
            print "error reading new annotation file:", details
            print traceback.format_exc()
            return 1
        else:
            return 0

    # test with no bg model
    print "testing with no bg model"
    newann = ann.AnnotationFile()
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )
    newann.close()
    n_err.value += read_test( newann._filename )
    if n_err.value != 0: return

    # test with empty bg model
    print "test with empty bg model"
    newann = ann.AnnotationFile()
    newann.bg_model = bg.BackgroundCalculator( movie )
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )
    newann.close()
    n_err.value += read_test( newann._filename )
    if n_err.value != 0: return

    # test with bg model
    print "testing with read bg model"
    newann = ann.AnnotationFile()
    newann.bg_model = old_bg_model
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )
    newann.close()
    newerr = read_test( newann._filename )
    n_err.value += newerr
    if n_err.value != 0: return
    
    # test values of read bg model
    print "testing bg model values"
    def compare_values( img0, img1 ):
        try:
            assert( (img0 == img0).all() )
        except AssertionError:
            return 1
        except Exception, details:
            print "error comparing images:", details
            return 1
        else:
            return 0

    test_bg_model = bg.BackgroundCalculator( movie )
    oldtest = oldann.AnnotationFile( newann._filename, test_bg_model,
                                     doreadtrx=True, readonly=True )

    for attr in ann.IMAGE_DATA_FIELDS:
        if hasattr( old_bg_model, attr ) and hasattr( test_bg_model, attr ):
            n_err.value += compare_values( getattr( old_bg_model, attr ),
                                     getattr( test_bg_model, attr ) )
        elif (not hasattr( old_bg_model, attr )) and (not hasattr( test_bg_model, attr )):
            pass
        else:
            print "error retrieving bg model attribute", attr, hasattr( old_bg_model, attr ), hasattr( test_bg_model, attr )
            n_err.value += 1
    if n_err.value != 0: return    

    # test values of bg algorithm strings
    print "testing bg algorithm values"
    for use_median in (True, False):
        newann = ann.AnnotationFile()
        test_bg_model = bg.BackgroundCalculator( movie )
        test_bg_model.use_median = use_median
        newann.bg_model = test_bg_model
        newann.InitializeData( existing_ann.firstframetracked,
                               existing_ann.firstframetracked - 1 )
        newann.close()
        test_bg_model.use_median = not use_median
        oldtest = oldann.AnnotationFile( newann._filename, test_bg_model,
                                         doreadtrx=True, readonly=True )
        try:
            assert( test_bg_model.use_median == use_median )
        except AssertionError:
            print "read bg algorithm didn't match for", use_median
            n_err.value += 1
    if n_err.value != 0: return

    # test with data
    print "testing with data"
    newann = ann.AnnotationFile()
    newann.bg_model = old_bg_model
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )
    for frame in existing_ann:
        newann.append( frame )

    try:
        assert( len( newann ) == len( existing_ann ) )
    except AssertionError:
        print "existing annotation had %d frames, new had %d" % (len( existing_ann ), len( newann ))
        n_err.value += 1

    newann.write_all_frames_to_disk()
    newerr = read_test( newann._filename )
    n_err.value += newerr
    if n_err.value != 0: return

    # test data values
    print "testing data values"
    oldtest = oldann.AnnotationFile( newann._filename,
                                     doreadtrx=True, readonly=True )
    try:
        assert( len( oldtest ) == len( existing_ann ) )
    except AssertionError:
        print "existing annotation had %d frames, written had %d" % (len( existing_ann ), len( oldtest ))
        n_err.value += 1
    else:
        try:
            assert( newann.firstframetracked == oldtest.firstframetracked )
            assert( newann.firstframetracked == existing_ann.firstframetracked )
            assert( newann.lastframetracked == oldtest.lastframetracked )
            assert( newann.lastframetracked == existing_ann.lastframetracked )
        except AssertionError:
            print "firstframes %d %d %d, lastframes %d %d %d" % (newann.firstframetracked, oldtest.firstframetracked, existing_ann.firstframetracked, newann.lastframetracked, oldtest.lastframetracked, existing_ann.lastframetracked)
            n_err.value += 1
        else:
            for i, (written, read) in enumerate( zip( existing_ann, oldtest ) ):
                try:
                    assert( all( written == read ) )
                except AssertionError:
                    print "data comparison error in frame", i
                    n_err.value += 1
                    break
            try:
                assert( i == len( existing_ann ) - 1 )
            except AssertionError:
                print "didn't iterate over all annotation", i
                n_err.value += 1
    if n_err.value != 0: return

    # test with non-zero start frame
    print "testing with non-zero start frame"
    newann = ann.AnnotationFile()
    newann.bg_model = old_bg_model
    newann.InitializeData( 10 )
    for frame in existing_ann[10:]:
        newann.append( frame )
    newann.write_all_frames_to_disk()
    n_err.value += read_test( newann._filename )

    try:
        assert( newann.firstframetracked == 10 )
        assert( newann.lastframetracked == existing_ann.lastframetracked )
    except AssertionError:
        print "failed setting tracked frame #s in new annotation:", newann.firstframetracked, newann.lastframetracked, existing_ann.lastframetracked
        n_err.value += 1

    try:
        assert( len( newann ) == len( existing_ann ) - 10 )
    except AssertionError:
        print "length of newann %d, old ann %d" % (len( newann ), len( existing_ann ))
        n_err.value += 1

    oldtest = oldann.AnnotationFile( newann._filename,
                                     doreadtrx=True, readonly=True )
    newtest = ann.AnnotationFile( newann._filename, readonly=True )
    for i, (written, readold, readnew) in enumerate( zip( existing_ann[10:], oldtest, newtest ) ):
        try:
            assert( all( written == readold ) )
            assert( all( written == readnew ) )
        except AssertionError:
            print "data comparison error in frame", i
            n_err.value += 1
            break
    
    if n_err.value != 0: return

    # test assignment
    print "testing assignment"
    newann = ann.AnnotationFile()
    newann.bg_model = old_bg_model

    try:
        newann[0] = existing_ann[0]
    except IndexError:
        pass
    else:
        print "should not allow assignment to uninitialized annfile"
        n_err.value += 1
        return

    try:
        newann[0] = None
    except TypeError:
        pass
    else:
        print "should not allow assignment of non-ellipses"
        n_err.value += 1
        return

    try:
        newann.append( existing_ann[0] )
    except IOError:
        pass
    else:
        print "should not allow appending to unintialized annfile"
        n_err.value += 1
        return

    try:
        newann.append( None )
    except TypeError:
        pass
    else:
        print "should not allow appending non-ellipses"
        n_err.value += 1
        return
    
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )

    try:
        newann[0] = existing_ann[0]
    except IndexError:
        pass
    else:
        print "should not allow assignment beyond bounds of annfile"
        n_err.value += 1
        return

    try:
        newann[0] = None
    except TypeError:
        pass
    else:
        print "should not allow assignment of non-ellipses"
        n_err.value += 1
        return

    try:
        newann.append( existing_ann[5] )
        # file now [5]
    except:
        print "error appending to initialized annfile"
        n_err.value += 1
        return

    try:
        newann.append( None )
    except TypeError:
        pass
    else:
        print "should not allow appending non-ellipses"
        n_err.value += 1
        return

    newann.append( existing_ann[6] )
    # file now [5, 6]

    try:
        newann[0] = existing_ann[7]
        # file now [7, 6]
    except IndexError:
        print "error reassigning value"
        n_err.value += 1
        return

    try:
        newann[0] = None
    except TypeError:
        pass
    else:
        print "should not allow assignment of non-ellipses"
        n_err.value += 1
        return

    try:
        newann.append( existing_ann[5] )
        # file now [7, 6, 5]
    except:
        print "error appending to initialized annfile"
        n_err.value += 1
        return

    try:
        newann.append( None )
    except TypeError:
        pass
    else:
        print "should not allow appending non-ellipses"
        n_err.value += 1
        return

    try:
        assert( newann[0] == existing_ann[7] )
        assert( newann[1] == existing_ann[6] )
        assert( newann[2] == existing_ann[5] )
    except AssertionError:
        print "incorrect values stored:", newann[0], newann[1], newann[2]
        n_err.value += 1
        return

    newann.close()

##    try:
##        assert( newann[0] == existing_ann[7] )
##        assert( newann[1] == existing_ann[6] )
##        assert( newann[2] == existing_ann[5] )
##    except AssertionError:
##        print "incorrect values retrieved after closing file:", newann[0], newann[1], newann[2]
##        n_err.value += 1
##        return

    try:
        newann[0] = existing_ann[0]
    except IOError:
        pass
    else:
        print "should not allow altering frame after closing file"
        n_err.value += 1
        return

    try:
        newann.append( existing_ann[4] )
    except IOError:
        pass
    else:
        print "should not allow appending frame after closing file"
        n_err.value += 1
        return
    
    newerr = read_test( newann._filename )
    n_err.value += newerr
    if n_err.value != 0: return

    # test slices
    print "testing slices"
    newann = ann.AnnotationFile()
    newann.bg_model = old_bg_model

    try:
        newann[0:1] = existing_ann[0]
    except TypeError:
        pass
    else:
        print "should not allow slice assignment to uninitialized annfile with non-iterable"
        n_err.value += 1
        return

    try:
        newann[0:1] = existing_ann[0:1]
        assert( len( newann ) == 0 )
    except AssertionError:
        print "slice assignment to uninitialized annfile should do nothing"
        n_err.value += 1
        return

    try:
        newann.extend( existing_ann[0:1] )
    except IOError:
        pass
    else:
        print "should not allow extending unintialized annfile"
        n_err.value += 1
        return
    
    newann.InitializeData( existing_ann.firstframetracked,
                           existing_ann.firstframetracked - 1 )

    try:
        newann[0:2] = existing_ann[0]
    except TypeError:
        pass
    else:
        print "should not allow slice assignment with non-iterable"
        n_err.value += 1
        return

    try:
        newann[0:2] = existing_ann[0:2]
        assert( len( newann ) == 0 )
    except AssertionError:
        print "slice assignment beyond bounds of annfile should do nothing"
        n_err.value += 1
        return

    try:
        newann.extend( existing_ann[5] )
    except TypeError:
        pass
    else:
        print "should not allow extending with a single item"
        n_err.value += 1
        return

    try:
        newann.extend( [existing_ann[5], existing_ann[6]] )
        # file now [5, 6]
    except:
        print "failed extending using list"
        n_err.value += 1
        return

    try:
        newann.extend( existing_ann[7:9] )
        # file now [5, 6, 7, 8]
    except:
        print "failed extending using slice"
        n_err.value += 1
        return

    try:
        newann.extend( existing_ann[9:10] )
        # file now [5, 6, 7, 8, 9]
    except:
        print "failed extending using slice with length 1"
        n_err.value += 1
        return

    try:
        newann[0:2] = existing_ann[0]
    except TypeError:
        pass
    else:
        print "should not allow slice assignment with mismatched sizes"
        n_err.value += 1
        return

    try:
        newann[0:2] = existing_ann[10:12]
        # file now [10, 11, 7, 8, 9]
    except IndexError:
        print "error reassigning slice"
        n_err.value += 1
        return

    try:
        for fnew, fold in enumerate( [10, 11, 7, 8, 9] ):
            assert( newann[fnew] == existing_ann[fold] )
    except AssertionError:
        print "incorrect values stored:", newann
        n_err.value += 1
        return

    newann.close()

    newerr = read_test( newann._filename )
    n_err.value += newerr
    if n_err.value != 0: return


#######################################################################
# test_buffering()
#######################################################################
def test_buffering( n_err ):
    """Test reading/writing extremely large datasets."""
    n_flies = 500
    n_frames = 10000

    print "test writing %d frames of %d flies" % (n_frames, n_flies)
    writeann = ann.AnnotationFile()
    writeann.InitializeData()

    for fr in xrange( n_frames ):
        flies = ell.TargetList()
        for fl in xrange( n_flies ):
            width = random.random()*5.
            flies.append( ell.Ellipse( random.random()*1000.,
                                       random.random()*1000.,
                                       width, width*2.,
                                       random.random()*2*num.pi,
                                       fl ) )
        writeann.append( flies )

    try:
        assert( len( writeann ) == n_frames )
    except AssertionError:
        print "written file only had", len( writeann ), "frames"
        n_err.value += 1

    writeann.write_all_frames_to_disk()

    print "test reading %d frames of %d flies" % (n_frames, n_flies)
    readann = ann.AnnotationFile( writeann._filename )
    try:
        assert( len( readann ) == len( writeann ) )
    except AssertionError:
        print "read file had", len( readann ), "frames"
        n_err.value += 1
    else:
        for i in xrange( len( writeann ) ):
            written = writeann[i]
            read = readann[i]
            try:
                assert( len( written ) == len( read ) )
                assert( all( written == read ) )
            except AssertionError:
                print "data comparison error in frame", i
                n_err.value += 1
                break
        try:
            assert( i == n_frames - 1 )
        except AssertionError:
            print "didn't iterate over all annotation", i
            n_err.value += 1


#######################################################################
# test_threading()
#######################################################################
def test_threading( n_err ):
    """Test reading/writing annfile in multiple threads simultaneously."""
    n_read_threads = 8
    n_write_threads = 8

    n_flies = 50
    n_frames = 1000
    n_repeats = 100

    def flies_with_pos( pos ):
        flies = ell.TargetList()
        for fl in range( n_flies ):
            width = random.random()*5.
            flies.append( ell.Ellipse( pos, pos, width, width*2.,
                                       random.random()*2*num.pi,
                                       fl ) )
        return flies

    class AnnWriteThread (threading.Thread):
        """Read frame # from read queue, create data for frame and write to annfile, write frame # to write queue."""
        def __init__( self, annfile, read_queue, write_queue ):
            threading.Thread.__init__( self )
            self.annfile = annfile
            self.read_queue = read_queue
            self.write_queue = write_queue
            self.quit = False
            self.n_err = 0

        def run( self ):
            while not self.quit:
                try:
                    frame = self.read_queue.get( True, 0.001 )
                except Queue.Empty:
                    continue

                fly_pos = random.random()
                flies = flies_with_pos( fly_pos )
                try:
                    self.annfile[frame] = flies
                except:
                    print "error writing data to frame", frame
                    print traceback.format_exc()
                    self.n_err += 1
                    self.read_queue.task_done()
                    break
                
                self.write_queue.put( (frame, fly_pos) )
                self.read_queue.task_done()

    class AnnReadThread (threading.Thread):
        """Read frame # from queue, get frame data from annfile, verify it."""
        def __init__( self, annfile, read_queue ):
            threading.Thread.__init__( self )
            self.annfile = annfile
            self.read_queue = read_queue
            self.quit = False
            self.n_err = 0

        def run( self ):
            while not self.quit:
                try:
                    (frame, fly_pos) = self.read_queue.get( True, 0.001 )
                except Queue.Empty:
                    continue

                flies = self.annfile[frame]
                try:
                    assert( len( flies ) == n_flies )
                except AssertionError:
                    print "length error reading frame", frame, len( flies )
                    self.n_err += 1
                else:
                    for f, fly in flies.iteritems():
                        try:
                            assert( fly.center.x == fly_pos )
                            assert( fly.center.y == fly.center.x )
                            assert( fly.identity == f )
                        except AssertionError:
                            print "fly data error in frame", frame, "fly", f, fly
                            self.n_err += 1
                finally:
                    self.read_queue.task_done()

    print "test writing and writing %d frames of %d flies in %d read/%d write threads" % (n_frames, n_flies, n_read_threads, n_write_threads)

    # write initial data into annfile
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    for fr in range( n_frames ):
        annfile.append( flies_with_pos( fr ) )

    for repeat in range( n_repeats ):
        sys.stdout.write( '.' )
        sys.stdout.flush()
        
        queue0 = Queue.Queue()
        queue1 = Queue.Queue()

        read_threads = [AnnReadThread( annfile, queue1 ) for i in range( n_read_threads )]
        write_threads = [AnnWriteThread( annfile, queue0, queue1 ) for i in range( n_write_threads )]

        # threads start and wait for frame numbers
        for read_thread in read_threads:
            read_thread.daemon = True
            read_thread.start()
        for write_thread in write_threads:
            write_thread.daemon = True
            write_thread.start()

        # feed frame numbers to write threads --
        # one will grab the number and overwrite its frame in annfile,
        # then the frame data will be put in the other queue,
        # finally a read thread will read the data and verify it
        for frame in range( n_frames ):
            queue0.put( frame )

        # stop the threads
        queue0.join()
        for write_thread in write_threads:
            write_thread.quit = True
            write_thread.join()
            n_err.value += write_thread.n_err

        queue1.join()
        for read_thread in read_threads:
            read_thread.quit = True
            read_thread.join()
            n_err.value += read_thread.n_err

    print


#######################################################################
# test_first_last_frames()
#######################################################################
def test_first_last_frames( n_err ):
    """Test that firstframetracked and lastframetracked are accurate."""
    n_new_fr = 10

    def extra_data():
        """Return a list of TargetLists, X frames of new data to write."""
        n_flies = 10
        data = []
        for fr in range( n_new_fr ):
            flies = ell.TargetList()
            for fl in range( n_flies ):
                width = random.random()*5.
                flies.append( ell.Ellipse( fr, fr, width, width*2.,
                                           random.random()*2*num.pi, fl ) )
            data.append( flies )
        return data

    def check_first_last( annfile, expected_first, expected_last ):
        """Assert that the first and last frames are known."""
        try:
            assert( annfile.firstframetracked == expected_first )
            assert( annfile.lastframetracked == expected_last )
            assert( len( annfile ) == annfile.lastframetracked - annfile.firstframetracked + 1 )
        except AssertionError:
            return 1
        return 0

    def check_read_true( annfile, frame ):
        """Assert we can read a frame."""
        try:
            x = annfile[frame]
        except:
            return 1
        else:
            return 0

    def check_read_false( annfile, frame ):
        """Assert we can't read a frame."""
        try:
            x = annfile[frame]
        except IndexError:
            return 0
        else:
            return 1

    def check_read_slice( annfile, first, last_plus_one, length ):
        """Assert that a slice has a particular length."""
        try:
            x = annfile[first:last_plus_one]
            assert( len( x ) == length )
        except AssertionError:
            print "%d:%d should have length of %d, but has %d" % (first, last_plus_one, length, len( x ))
            return 1
        else:
            return 0

    # open, read
    print "testing open, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )

    new_err = check_first_last( annfile, 0, len( annfile ) - 1 )
    if new_err != 0:
        print "read file with %d frames, but firstframe %d lastframe %d" % (len( annfile ), annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += 1
        return

    # open, write
    print "testing open, write"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    old_last = annfile.lastframetracked
    annfile.extend( extra_data() )

    new_err = check_first_last( annfile, 0, old_last + n_new_fr )
    if new_err != 0:
        print "after adding %d frames, last went from %d to %d" % (n_new_fr, old_last, annfile.lastframetracked)
        n_err.value += new_err
        return

    # open, clear, read
    print "testing open, clear, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData()

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "after clearing file, still read frame 0"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, -1 )
    if new_err != 0:
        print "after clearing file, first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # open, clear, write
    print "testing open, clear, write"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData()
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "cleared, then wrote, should be able to read frame 0"
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr )
    if new_err != 0:
        print "cleared, then wrote %d frames, still read frame %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_slice( annfile, 0, n_new_fr, n_new_fr )
    if new_err != 0:
        print "cleared, then wrote %d frames, slice %d:%d should have length %d" % (n_new_fr, 0, n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_slice( annfile, 0, 2*n_new_fr, n_new_fr )
    if new_err != 0:
        print "cleared, then wrote %d frames, slice %d:%d should have length %d" % (n_new_fr, 0, 2*n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_slice( annfile, 5, n_new_fr, n_new_fr - 5 )
    if new_err != 0:
        print "cleared, then wrote %d frames, slice %d:%d should have length %d" % (n_new_fr, 5, n_new_fr, n_new_fr - 5)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr - 1 )
    if new_err != 0:
        print "cleared, then wrote %d frames, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # open, clear, close, open, read
    print "testing open, clear, close, open, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "cleared, closed, opened, still read frame 0"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, -1 )
    if new_err != 0:
        print "cleared, closed, opened, now first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # open, crop, read
    print "testing open, crop, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData( 0, 9 )

    new_err = check_read_true( annfile, 9 )
    if new_err != 0:
        print "cropped to 10 frames, can't read frame 9"
        n_err.value += new_err
        
    new_err = check_read_false( annfile, 10 )
    if new_err != 0:
        print "cropped to 10 frames, still read frame 10"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, 9 )
    if new_err != 0:
        print "cropped to 10 frames, now first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # open, crop, write
    print "testing open, crop, write"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData( 0, 9 )
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, n_new_fr + 9 )
    if new_err != 0:
        print "cropped to 10 frames, then wrote %d, can't read %d" % (n_new_fr, n_new_fr + 9)
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr + 10 )
    if new_err != 0:
        print "cropped to 10 frames, then wrote %d, still read frame %d" % (n_new_fr, n_new_fr + 10)
        n_err.value += new_err

    new_err = check_read_slice( annfile, 0, n_new_fr, n_new_fr )
    if new_err != 0:
        print "cleared, then wrote %d frames, slice %d:%d should have length %d" % (n_new_fr, 0, n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_slice( annfile, n_new_fr, 2*n_new_fr, n_new_fr )
    if new_err != 0:
        print "cleared, then wrote %d frames, slice %d:%d should have length %d" % (n_new_fr, n_new_fr, 2*n_new_fr, n_new_fr + 9)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr + 9 )
    if new_err != 0:
        print "cropped to 10 frames, wrote %d frames, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # open, crop, close, open, read
    print "testing open, crop, close, open, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData( 0, 9 )
    del annfile # make it get garbage-collected immediately (data written)
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "cropped to 10 frames, closed, opened, but couldn't read frame 0"
        n_err.value += new_err

    new_err = check_read_false( annfile, 10 )
    if new_err != 0:
        print "cropped to 10 frames, closed, opened, still read frame 10"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, 9 )
    if new_err != 0:
        print "cropped to 10 frames, closed, opened, now first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # crop keep center
    print "testing open, crop keep center, close, open, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    annfile.InitializeData( 10, 19 )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "cropped to center but still read frame 0"
        n_err.value += new_err

    new_err = check_read_true( annfile, 10 )
    if new_err != 0:
        print "cropped to center but couldn't read frame 10"
        n_err.value += new_err

    new_err = check_read_false( annfile, 20 )
    if new_err != 0:
        print "cropped to center but still read frame 20"
        n_err.value += new_err

    new_err = check_first_last( annfile, 10, 19 )
    if new_err != 0:
        print "cropped to center, now first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    del annfile # make it get garbage-collected immediately (data written)
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "cropped to center, closed, opened, but still read frame 0"
        n_err.value += new_err

    new_err = check_read_true( annfile, 10 )
    if new_err != 0:
        print "cropped to center, closed, opened, but couldn't read frame 10"
        n_err.value += new_err

    new_err = check_read_false( annfile, 20 )
    if new_err != 0:
        print "cropped to center, closed, opened, but still read frame 20"
        n_err.value += new_err

    new_err = check_first_last( annfile, 10, 19 )
    if new_err != 0:
        print "cropped to center, closed, opened, now first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # crop keep end
    print "testing open, crop keep end, close, open, read"
    reset_test_ann()
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )
    last_frame = annfile.lastframetracked
    annfile.InitializeData( last_frame - 9, last_frame + 10 )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "cropped to end but still read frame 0"
        n_err.value += new_err

    new_err = check_read_true( annfile, last_frame )
    if new_err != 0:
        print "cropped to end but couldn't read frame", last_frame
        n_err.value += new_err

    new_err = check_read_false( annfile, last_frame + 1 )
    if new_err != 0:
        print "cropped to end but can now read past end??"
        n_err.value += new_err

    new_err = check_read_slice( annfile, 0, n_new_fr, 0 )
    if new_err != 0:
        print "cropped to end, so %d:%d should raise error" % (0, n_new_fr)
        n_err.value += new_err

    new_err = check_read_slice( annfile, last_frame - 9, last_frame + 1, 10 )
    if new_err != 0:
        print "cropped to end, slice %d:%d should have length %d" % (last_frame - 9, last_frame + 1, 10)
        n_err.value += new_err

    new_err = check_first_last( annfile, last_frame - 9, last_frame )
    if new_err != 0:
        print "cropped to end (%d), now first %d last %d" % (last_frame, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    del annfile # make it get garbage-collected immediately (data written)
    annfile = ann.AnnotationFile( TEST_MOVIE + ".ann" )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "cropped to end but still read frame 0"
        n_err.value += new_err

    new_err = check_read_true( annfile, last_frame )
    if new_err != 0:
        print "cropped to end but couldn't read frame", last_frame
        n_err.value += new_err

    new_err = check_read_false( annfile, last_frame + 1 )
    if new_err != 0:
        print "cropped to end but can now read past end??"
        n_err.value += new_err

    new_err = check_first_last( annfile, last_frame - 9, last_frame )
    if new_err != 0:
        print "cropped to end (%d), now first %d last %d" % (last_frame, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, read
    print "testing new, read"
    annfile = ann.AnnotationFile()

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "new annotation file still read frame 0"
        n_err.value += new_err

    try:
        assert( not hasattr( annfile, 'firstframetracked' ) )
        assert( not hasattr( annfile, 'lastframetracked' ) )
    except AssertionError:
        print "new uninitialized annotation file has firstframetracked or lastframetracked"
        n_err.value += 1

    annfile.close()

    # new, initialize, read
    print "testing new, init, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "new annotation file, init, still read frame 0"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, -1 )
    if new_err != 0:
        print "new annotation file has first %d last %d" % (last_frame, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    annfile.write_all_frames_to_disk()

    new_err = check_first_last( annfile, 0, -1 )
    if new_err != 0:
        print "new annotation file, init, closed, has first %d last %d" % (last_frame, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, read
    print "testing new, write, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "new annotation file, wrote %d, can't read %d" % (n_new_fr, 0)
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr )
    if new_err != 0:
        print "new annotation file, wrote %d, read frame %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr - 1 )
    if new_err != 0:
        print "new annotation file, wrote %d, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, clear, read
    print "testing new, write, clear, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.InitializeData()

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "after clearing file, still read frame 0"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, -1 )
    if new_err != 0:
        print "after clearing file, first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, clear, write, read
    print "testing new, write, clear, write, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.InitializeData()
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "new annotation file, cleared, wrote %d, can't read %d" % (n_new_fr, 0)
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr )
    if new_err != 0:
        print "new annotation file, cleared, wrote %d, read frame %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr - 1 )
    if new_err != 0:
        print "new annotation file, cleared, wrote %d, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, crop, read
    print "testing new, write, crop, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.InitializeData( 0, 4 )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "after cropping file, couldn't read frame 0"
        n_err.value += new_err

    new_err = check_read_false( annfile, 5 )
    if new_err != 0:
        print "after cropping file, still read frame 5"
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, 4 )
    if new_err != 0:
        print "after clearing file, first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, crop, write, read
    print "testing new, write, crop, write, read"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.InitializeData( 0, 4 )
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, 5 )
    if new_err != 0:
        print "after cropping file and appending, couldn't read frame 5"
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr + 5 )
    if new_err != 0:
        print "after cropping file, still read frame %d" % n_new_fr + 5
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr + 4 )
    if new_err != 0:
        print "after cropping file, first %d last %d" % (annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, reopen
    print "testing new, write, reopen"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.close()
    annfile = ann.AnnotationFile( annfile._filename )

    new_err = check_read_true( annfile, 0 )
    if new_err != 0:
        print "reopened annotation file, wrote %d, can't read %d" % (n_new_fr, 0)
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr )
    if new_err != 0:
        print "reopened annotation file, wrote %d, read frame %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, n_new_fr - 1 )
    if new_err != 0:
        print "reopened annotation file, wrote %d, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, write, reopen, append
    print "testing new, write, reopen, append"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( extra_data() )
    annfile.close()
    annfile = ann.AnnotationFile( annfile._filename )
    annfile.extend( extra_data() )

    new_err = check_read_true( annfile, n_new_fr )
    if new_err != 0:
        print "reopened annotation file, wrote %d, can't read %d" % (2*n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_false( annfile, 2*n_new_fr )
    if new_err != 0:
        print "reopened annotation file, wrote %d, read frame %d" % (2*n_new_fr, 2*n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, 0, 2*n_new_fr - 1 )
    if new_err != 0:
        print "new annotation file, wrote %d, now first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10
    print "testing start after 0"
    annfile = ann.AnnotationFile()
    annfile.InitializeData( n_new_fr )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "when starting at frame %d, still read frame 0" % n_new_fr
        n_err.value += new_err

    new_err = check_first_last( annfile, n_new_fr, n_new_fr - 1 )
    if new_err != 0:
        print "started at %d, but first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10, write
    print "testing start after 0 and appending"
    annfile = ann.AnnotationFile()
    annfile.InitializeData( n_new_fr )
    annfile.extend( extra_data() )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "when starting at frame %d, still read frame 0" % n_new_fr
        n_err.value += new_err

    new_err = check_read_true( annfile, n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should be able to read %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_false( annfile, 2*n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should not be able to read %d" % (n_new_fr, 2*n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, n_new_fr, 2*n_new_fr - 1 )
    if new_err != 0:
        print "started at %d, but first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10, write, reopen
    print "testing start after 0 and reopening"
    annfile = ann.AnnotationFile()
    annfile.InitializeData( n_new_fr )
    annfile.extend( extra_data() )
    annfile.close()
    annfile = ann.AnnotationFile( annfile._filename )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "when starting at frame %d, still read frame 0" % n_new_fr
        n_err.value += new_err

    new_err = check_read_true( annfile, n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should be able to read %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_false( annfile, 2*n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should not be able to read %d" % (n_new_fr, 2*n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, n_new_fr, 2*n_new_fr - 1 )
    if new_err != 0:
        print "started at %d, but first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10, write, reopen, append
    print "testing start after 0 and reopening"
    annfile = ann.AnnotationFile()
    annfile.InitializeData( n_new_fr )
    annfile.extend( extra_data() )
    annfile.close()
    annfile = ann.AnnotationFile( annfile._filename )
    annfile.extend( extra_data() )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "when starting at frame %d, still read frame 0" % n_new_fr
        n_err.value += new_err

    new_err = check_read_true( annfile, 2*n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should be able to read %d" % (n_new_fr, 2*n_new_fr)
        n_err.value += new_err

    new_err = check_read_false( annfile, 3*n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should not be able to read %d" % (n_new_fr, 3*n_new_fr)
        n_err.value += new_err

    new_err = check_first_last( annfile, n_new_fr, 3*n_new_fr - 1 )
    if new_err != 0:
        print "started at %d, but first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10, write, reopen, truncate
    print "testing start after 0, reopen, truncate"
    annfile = ann.AnnotationFile()
    annfile.InitializeData( n_new_fr )
    annfile.extend( extra_data() )
    annfile.close()
    annfile = ann.AnnotationFile( annfile._filename )
    annfile.InitializeData( annfile.firstframetracked, annfile.firstframetracked + n_new_fr/2 )

    new_err = check_read_false( annfile, 0 )
    if new_err != 0:
        print "when starting at frame %d, still read frame 0" % n_new_fr
        n_err.value += new_err

    new_err = check_read_true( annfile, n_new_fr )
    if new_err != 0:
        print "after starting at %d and appending, should be able to read %d" % (n_new_fr, n_new_fr)
        n_err.value += new_err

    new_err = check_read_false( annfile, n_new_fr + n_new_fr/2 + 1 )
    if new_err != 0:
        print "after starting at %d and appending, should not be able to read %d" % (n_new_fr, n_new_fr + n_new_fr/2 + 1)
        n_err.value += new_err

    new_err = check_first_last( annfile, n_new_fr, n_new_fr + n_new_fr/2 )
    if new_err != 0:
        print "started at %d, but first %d last %d" % (n_new_fr, annfile.firstframetracked, annfile.lastframetracked)
        n_err.value += new_err

    if n_err.value != 0: return

    # new, firstframe 10, write, reopen, truncate, append
    print "testing start after 0, reopen, truncate, append"


#######################################################################
# test_fly_IDs()
#######################################################################
def test_fly_IDs( n_err ):
    """Test that fly IDs are assigned, reassigned, and recycled correctly."""
    n_new_flies = 5

    def annfile_to_use( annfile, use_annfile_ids ):
        if use_annfile_ids:
            return annfile
        return None

    def new_frame( annfile, add_current_flies=True, new_flies_born=True ):
        """Create a new frame of data, with X new flies."""
        flies = ell.TargetList()

        if add_current_flies:
            for fly_id in range( params.nids ):
                width = random.random()*5.
                flies.append( ell.Ellipse( fly_id, fly_id, width, width*2.,
                                           random.random()*2*num.pi, fly_id ) )

        if new_flies_born:
            for i in range( n_new_flies ):
                width = random.random()*5.
                if annfile is None:
                    new_id = params.nids
                    params.nids += 1
                else:
                    new_id = annfile.GetNewId()
                    
                flies.append( ell.Ellipse( new_id, new_id, width, width*2.,
                                           random.random()*2*num.pi, new_id ) )
            
        return flies

    def check_nids( val ):
        """Check if params.nids matches the number we've added."""
        try:
            assert( params.nids == val )
            return 0
        except AssertionError:
            return 1

    for use_annfile_ids in [False, True]:
        print "using annfile's GetNewId():", use_annfile_ids
        
        # test in a new annotation file
        print "test new file"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()

        for f in range( 10 ):
            annfile.append( new_frame( use_annfile ) )

            n_err.value += check_nids( n_new_flies*(f + 1) )
            if n_err.value != 0:
                print "ID count error after writing frame", f
                return

        for f in range( 10 ):
            annfile.append( new_frame( use_annfile, add_current_flies=False ) )

            n_err.value += check_nids( n_new_flies*(f + 11) )
            if n_err.value != 0:
                print "ID count error after writing frame (no old flies)", f
                return

        for f in range( 10 ):
            annfile.append( new_frame( use_annfile, new_flies_born=False ) )

            n_err.value += check_nids( n_new_flies*20 )
            if n_err.value != 0:
                print "ID count error after writing frame (no new flies)", f
                return

        # test clearing
        print "test clear"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        annfile.InitializeData()

        new_err = check_nids( 0 )
        if new_err != 0:
            print "ID count error after clearing", params.nids
            n_err.value += new_err

        if n_err.value != 0: return

        # test clearing, rewriting
        print "test clear, rewrite"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )

        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after clearing and rewriting", params.nids, 10*n_new_flies
            n_err.value += new_err

        if n_err.value != 0: return

        # test cropping
        print "test crop"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        annfile.InitializeData( 0, 4 )

        new_err = check_nids( 5*n_new_flies )
        if new_err != 0:
            print "ID count error after cropping", params.nids, 5*n_new_flies
            n_err.value += new_err

        if n_err.value != 0: return

        # test crop keep end
        def check_id_values( startvalue, endvalue ):
            """Check for specific ID values anywhere in the annfile."""
            for test_id in range( startvalue, endvalue ):
                found_id = False
                for ells in annfile:
                    for ellipse in ells.itervalues():
                        if ellipse.identity == test_id:
                            found_id = True

                try:
                    assert( found_id )
                except AssertionError:
                    print "couldn't find id %d in annfile after cropping" % test_id
                    return 1
            return 0

        print "test crop keep end"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        annfile.InitializeData( 5, 9 )

        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after crop keep end", params.nids, 10*n_new_flies
            n_err.value += new_err

        new_err = check_id_values( 5*n_new_flies, 10*n_new_flies )
        if new_err != 0:
            n_err.value += new_err

        if n_err.value != 0: return

        # test crop, write
        print "test crop, write"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        annfile.InitializeData( 5, 9 )

        annfile.extend( [new_frame( use_annfile, new_flies_born=False ) for f in range( 10 )] )
        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after cropping, writing (no new flies)", params.nids, 10*n_new_flies
            n_err.value += new_err

        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )
        new_err = check_nids( 20*n_new_flies )
        if new_err != 0:
            print "ID count error after cropping, writing (new flies)", params.nids, 20*n_new_flies
            n_err.value += new_err

        if n_err.value != 0: return

        # test re-opening
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile ) for f in range( 10 )] )

        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after initializing", params.nids, 10*n_new_flies
            n_err.value += new_err

        annfile.close()
        new_err = check_nids( 0 )
        if new_err != 0:
            print "ID count error after closing", params.nids, 0
            n_err.value += new_err

        annfile = ann.AnnotationFile( annfile._filename )
        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after reopening", params.nids, 10*n_new_flies
            n_err.value += new_err

        if n_err.value != 0: return

        # test ID reduction
        print "test reducing IDs"
        annfile = ann.AnnotationFile()
        use_annfile = annfile_to_use( annfile, use_annfile_ids )
        annfile.InitializeData()
        annfile.extend( [new_frame( use_annfile, add_current_flies=False ) for f in range( 10 )] )

        new_err = check_nids( 10*n_new_flies )
        if new_err != 0:
            print "ID count error after writing without current flies", params.nids, 10*n_new_flies
            n_err.value += new_err

        annfile.InitializeData( 5, 9 )
        new_err = check_nids( 5*n_new_flies )
        if new_err != 0:
            print "ID count error after cropping without current flies", params.nids, 5*n_new_flies
            n_err.value += new_err

        new_err = check_id_values( 0, 5*n_new_flies )
        if new_err != 0:
            print "ID value error after cropping without current flies"
            n_err.value += new_err

        if n_err.value != 0: return

    # test ID recycling
    print "test ID recycling"
    annfile = ann.AnnotationFile()
    annfile.InitializeData()

    try:
        annfile.RecycleId( 0 )
    except ValueError:
        pass
    else:
        print "should have raised an error when attempting to recycle a non-existent ID"
        n_err.value += 1

    annfile.append( new_frame( annfile ) )
    new_err = check_nids( n_new_flies )
    if new_err != 0:
        print "ID count error after adding one frame", params.nids, n_new_flies
        n_err.value += new_err
    new_err = check_id_values( 0, n_new_flies )
    if new_err != 0:
        print "ID value error after adding one frame"
        n_err.value += new_err

    annfile.append( new_frame( annfile, add_current_flies=False ) )
    new_err = check_nids( 2*n_new_flies )
    if new_err != 0:
        print "ID count error after adding two frames", params.nids, 2*n_new_flies
        n_err.value += new_err
    new_err = check_id_values( 0, 2*n_new_flies )
    if new_err != 0:
        print "ID value error after adding two frames"
        n_err.value += new_err

    annfile.RecycleId( 0 )
    try:
        assert( annfile.GetNewId() == 0 )
    except AssertionError:
        print "ID 0 didn't get recycled"
        n_err.value += 1
    else:
        annfile.RecycleId( 0 )
    
    annfile.append( new_frame( annfile, add_current_flies=False ) )
    new_err = check_nids( 3*n_new_flies - 1 )
    if new_err != 0:
        print "ID count error after recycling", params.nids, 3*n_new_flies - 1
        n_err.value += new_err
    new_err = check_id_values( 0, 3*n_new_flies - 1 )
    if new_err != 0:
        print "ID value error after recycling"
        n_err.value += new_err

    # test double ID recycling
    print "test double recycling"
    annfile.InitializeData()
    annfile.append( new_frame( annfile ) )
    annfile.RecycleId( 0 )
    annfile.RecycleId( 0 )
    try:
        assert( annfile.GetNewId() == 0 )
    except AssertionError:
        print "ID 0 didn't get recycled"
        n_err.value += 1
    else:
        try:
            new_id = annfile.GetNewId()
            assert( new_id == n_new_flies )
        except AssertionError:
            print "new ID should have been %d: %d" % (n_new_flies, new_id)
            n_err.value += 1


#######################################################################
# test_choose_orientations()
#######################################################################
def test_choose_orientations( n_err ):
    """Test that the orientations_chosen state is accurate."""
    chooser = ChooseOrientations( None, False )
    n_new_fr = 10
    
    def new_data():
        """Return a list of TargetLists, X frames of new data to write."""
        n_flies = 10
        data = []
        for fr in range( n_new_fr ):
            flies = ell.TargetList()
            for fl in range( n_flies ):
                width = random.random()*5.
                flies.append( ell.Ellipse( fr, fr, width, width*2.,
                                           random.random()*2*num.pi, fl ) )
            data.append( flies )
        return data

    def check_state( annfile, expected ):
        """Check that the file is in a known state."""
        try:
            assert( annfile.orientations_chosen == expected )
        except AssertionError:
            return 1
        return 0

    # new file
    print "test new file"
    annfile = ann.AnnotationFile()
    new_err = check_state( annfile, False )
    if new_err != 0:
        print "new file should not say orientations were chosen"
        n_err.value += new_err

    annfile.InitializeData()
    new_err = check_state( annfile, False )
    if new_err != 0:
        print "newly initialized file should not say orientations were chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # write data
    print "test with data"
    annfile.extend( new_data() )
    new_err = check_state( annfile, False )
    if new_err != 0:
        print "file with new data should not say orientations were chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # choose orientations
    print "test choosing orientations"
    annfile = chooser.ChooseOrientations( annfile )

    new_err = check_state( annfile, True )
    if new_err != 0:
        print "orientations have been chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # clear
    print "test clear"
    annfile.InitializeData()
    # TODO: shouldn't this set state to False?
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "file re-initialized, orientations_chosen should not change"
        n_err.value += new_err

    annfile.extend( new_data() )
    # TODO: shouldn't state be False now?
    
    annfile = chooser.ChooseOrientations( annfile )
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "orientations have been chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    def print_orientations( annfile ):
        for f, ells in enumerate( annfile ):
            s = '%2d:\t' % f
            for ell in ells.itervalues():
                s += '%d:%.3f\t' % (ell.identity, ell.angle)
            print s

    # crop
    print "test crop"
    annfile.InitializeData( 5, 9 )
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "orientations should still be chosen after crop"
        n_err.value += new_err

    annfile.extend( new_data() )
    annfile = chooser.ChooseOrientations( annfile )
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "orientations have been chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # add data
    print "test adding data"
    annfile.extend( new_data() )
    new_err = check_state( annfile, False )
    if new_err != 0:
        print "new data added, orientations_chosen should be false"
        n_err.value += new_err

    if n_err.value != 0: return

    # close, reopen
    print "test closing, reopening"
    annfile = ann.AnnotationFile( annfile._filename )
    new_err = check_state( annfile, False )
    if new_err != 0:
        print "reopened file, new data was added, orientations should be unchosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # choose, close, reopen
    print "test choose, close, reopen"
    annfile = chooser.ChooseOrientations( annfile )
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "orientations have been chosen"
        n_err.value += new_err

    annfile = ann.AnnotationFile( annfile._filename )
    new_err = check_state( annfile, True )
    if new_err != 0:
        print "reopened file, orientations should be chosen"
        n_err.value += new_err

    if n_err.value != 0: return

    # write bg model
    print "test writing bg model"
    movie = movies.Movie( TEST_MOVIE, interactive=False )
    bg_model = bg.BackgroundCalculator( movie )
    bg_model.medmad()
    bg_img_shape = (movie.get_height(), movie.get_width())

    annfile = ann.AnnotationFile()
    annfile.InitializeData()
    annfile.extend( new_data() )
    annfile = chooser.ChooseOrientations( annfile, bg_model )
    annfile.close()

    bg_model.med = None
    annfile = ann.AnnotationFile( annfile._filename, bg_model, bg_img_shape=bg_img_shape )

    try:
        assert( bg_model.med is not None )
    except AssertionError:
        print "error reading bg model field from file after choosing orientations"
        n_err.value += 1

    if n_err.value != 0: return
    

#######################################################################
# test_save_as()
#######################################################################
def test_save_as( n_err ):
    """Test saving annotation as CSV and for MATLAB."""
    movie = movies.Movie( TEST_MOVIE, interactive=False )

    # write test data
    n_frames = 10
    n_flies = 5

    annfile = ann.AnnotationFile()
    annfile.InitializeData()

    for fr in range( n_frames ):
        flies = ell.TargetList()
        for fl in range( n_flies ):
            width = 10*(fl + 1)
            if fr == 0:
                fly_id = annfile.GetNewId()
            else:
                fly_id = fl
            flies.append( ell.Ellipse( fl + fr, fl + fr, width, width*2.,
                                       random.random()*2*num.pi, fly_id ) )
        annfile.append( flies )

    # write CSV
    print "test writing CSV"
    csv_path = os.path.join( TEST_ANN_DIR, "test.csv" )
    annfile.WriteCSV( csv_path )

    print "test re-reading CSV"
    data = num.loadtxt( csv_path, delimiter=',' )

    try:
        assert( data.shape[0] == n_frames )
        assert( data.shape[1] == n_flies*6 )
    except AssertionError:
        print "read data should have %d rows and %d cols, actually" % (n_frames, n_flies), data.shape
        n_err.value += 1

    for fr, frame in enumerate( annfile ):
        for fl, fly in enumerate( frame.itervalues() ):
            try:
                assert( fly.identity == data[fr,fl*6] )
                assert( fly.center.x == data[fr,fl*6 + 1] )
                assert( fly.center.y == data[fr,fl*6 + 2] )
                assert( fly.height == data[fr,fl*6 + 3] )
                assert( fly.width == data[fr,fl*6 + 4] )
                assert( fly.angle == data[fr,fl*6 + 5] )
            except AssertionError:
                print "data error frame %d fly %d:" % (fr, fl), fly, data[fr,fl*6:(fl + 1)*6]
                n_err.value += 1
                break

    if n_err.value != 0: return

    # write MAT
    print "test writing MAT-file"
    mat_path = os.path.join( TEST_ANN_DIR, "test.mat" )
    annfile.WriteMAT( movie, mat_path )

    print "test re-reading MAT-file"
    success_path = os.path.join( TEST_ANN_DIR, "mat_test_success.txt" )
    if os.access( success_path, os.W_OK ):
        os.remove( success_path )
    elif os.access( success_path, os.F_OK ):
        print "couldn't delete success file"
        n_err.value += 1
        return
    
    call( "matlab -nodisplay -nojvm -nosplash -r 'test_annfiles_read; exit'", shell=True )

    if os.access( success_path, os.R_OK ):
        with open( success_path, 'r' ) as fp:
            success = int( fp.readline().strip() )
            try:
                assert( success == 1 )
            except AssertionError:
                print "MAT-file not read successfully"
                n_err.value += 1
    else:
        print "success file not written"
        n_err.value += 1

    # copy to .sbfmf.ann
    print "test copying to .sbfmf.ann"
    shutil.copyfile( TEST_MOVIE, TEST_MOVIE[:-len( '.fmf' )] + '.sbfmf' )
    annfile = ann.AnnotationFile( TEST_MOVIE + '.ann' )
    annfile.CopyToSBFMF()

    try:
        assert( os.access( annfile._filename[:-len( '.fmf.ann' )] + '.sbfmf.ann', os.F_OK ) )
    except AssertionError:
        print "SBFMF annotation file not found based on", annfile._filename
        print annfile._filename[:-len( '.ann' )] + '.fmf.ann'
        n_err.value += 1
    

# run all tests if ALL_ENABLED, or selectively enable some tests below
ALL_ENABLED = False
TEST_OBJECT_CREATION               = ALL_ENABLED or False
TEST_BACKWARD_COMPATIBILITY_READ   = ALL_ENABLED or False
TEST_WEIRD_HEADERS                 = ALL_ENABLED or False
TEST_WEIRD_DATA                    = ALL_ENABLED or False
TEST_BACKWARD_COMPATIBILITY_WRITE  = ALL_ENABLED or False
TEST_BUFFERING                     = ALL_ENABLED or False
TEST_THREADING                     = ALL_ENABLED or False
TEST_FIRST_LAST_FRAMES             = ALL_ENABLED or False
TEST_ASSIGN_IDS                    = ALL_ENABLED or True
TEST_CHOOSE_ORIENTATIONS           = ALL_ENABLED or True
TEST_SAVE_AS                       = ALL_ENABLED or True

if __name__ == '__main__':
    prepare_test_ann()

    def run_func( func ):
        """Do test in a separate subprocess so all memory is fully freed."""
        print "running", func
        n_err = multiprocessing.Value( 'i', 0 )
        st = time.time()
        proc = multiprocessing.Process( target=func, args=(n_err,) )
        proc.start()
        proc.join()
        try:
            assert( proc.exitcode == 0 )
        except AssertionError:
            print "...crashed"
            exit( 1 )
        try:
            assert( n_err.value == 0 )
        except AssertionError:
            print "...errors raised"
            exit( 2 )
        print "elapsed", time.time() - st, "s\n"

    if TEST_OBJECT_CREATION:
        run_func( test_object_creation )

    if TEST_BACKWARD_COMPATIBILITY_READ:
        run_func( test_backward_compatibility_read )

    if TEST_WEIRD_HEADERS:
        run_func( test_weird_headers )

    if TEST_WEIRD_DATA:
        run_func( test_weird_data )

    if TEST_BACKWARD_COMPATIBILITY_WRITE:
        run_func( test_backward_compatibility_write )

    if TEST_BUFFERING:
        run_func( test_buffering )

    if TEST_THREADING:
        run_func( test_threading )

    if TEST_FIRST_LAST_FRAMES:
        run_func( test_first_last_frames )

    if TEST_ASSIGN_IDS:
        run_func( test_fly_IDs )

    if TEST_CHOOSE_ORIENTATIONS:
        run_func( test_choose_orientations )

    if TEST_SAVE_AS:
        run_func( test_save_as )

    print "\n...all tests passed"
