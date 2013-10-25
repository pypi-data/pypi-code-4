# algorithm.py
# KMB 09/07/07

import multiprocessing
import os
from Queue import Empty as QueueEmpty
import sys
from threading import Timer
import time

import numpy as num

import numpy as num
import wx
from wx import xrc

from version import DEBUG, DEBUG_TRACKINGSETTINGS
import annfiles as annot
import ellipsesk as ell
import hindsight
import setarena
import chooseorientations
from params import params
import setarena
import settings
from version import DEBUG

import codedir
SETTINGS_RSRC_FILE = os.path.join(codedir.codedir,'xrc','tracking_settings.xrc')

if DEBUG: import pdb
DEBUG_LEVEL = 2
if not DEBUG:
    DEBUG_LEVEL = 0

PRINT_COUNTS = False


# CtraxApp.Track #################################################
class CtraxAlgorithm (settings.AppWithSettings):
    """Cannot be used alone -- this class only exists
    to keep algorithm code together in one file."""
    def Track( self ):
        """Run the tracker."""

        ## initialization ##
        if DEBUG: print "Tracking from frame %d..."%self.start_frame
        if DEBUG: print "Last frame tracked = %d"%self.ann_file.lastframetracked

        # maximum number of frames we will look back to fix errors
        self.maxlookback = max(params.lostdetection_length,
                               params.spuriousdetection_length,
                               params.mergeddetection_length,
                               params.splitdetection_length)

        if params.interactive:
            wx.Yield()

        # initialize hindsight data structures
        self.hindsight = hindsight.Hindsight(self.ann_file,self.bg_imgs)

        # initialize dfore and connected component buffer
        self.bg_imgs.set_buffer_maxnframes()

        self.track_timer_start_time = time.time()
        self.update_track_time()

        self.break_flag = False

        for self.start_frame in range(self.start_frame,self.movie.get_n_frames()):
            if DEBUG or DEBUG_TRACKINGSETTINGS: print "frame", self.start_frame

            # KB 20120109 added last_frame command-line option
            if self.start_frame >= self.last_frame:
                break

            if DEBUG_LEVEL > 0: print "Tracking frame %d / %d"%(self.start_frame,self.movie.get_n_frames()-1)

            if self.break_flag:
                break

            last_time = time.time()

            # perform background subtraction
            (dfore, isfore, cc, ncc) = self.bg_imgs.sub_bg( self.start_frame )
            if DEBUG_LEVEL > 1: print ncc, "connected components"

            # write to sbfmf
            if self.dowritesbfmf:
                self.movie.writesbfmf_writeframe(isfore,
                                                 self.bg_imgs.curr_im,
                                                 self.bg_imgs.curr_stamp,
                                                 self.start_frame)

            # process gui events
            if params.interactive:
                wx.Yield()
            if self.break_flag:
                break

            # find observations
            ellipses = ell.find_ellipses( dfore, cc, ncc )
            if DEBUG_LEVEL > 1: print len( ellipses ), "ellipses"

            # process gui events
            if params.interactive:
                wx.Yield()
            if self.break_flag:
                break

            # match target identities to observations
            if DEBUG_LEVEL > 0: print "matching identities"
            if len( self.ann_file ) > 1:
                flies = ell.find_flies( self.ann_file[-2],
                                        self.ann_file[-1],
                                        ellipses,
                                        self.ann_file)
            elif len( self.ann_file ) == 1:
                flies = ell.find_flies( self.ann_file[-1],
                                        self.ann_file[-1],
                                        ellipses,
                                        self.ann_file )
            else:
                flies = ell.TargetList()
                for i,obs in enumerate(ellipses):
                    if obs.isEmpty():
                        if DEBUG: print 'empty observation'
                    else:
                        newid = self.ann_file.GetNewId()
                        obs.identity = newid
                        flies.append(obs)
            if DEBUG_LEVEL > 1: print len( flies ), "flies"

            if DEBUG_LEVEL > 0: print "Done with frame %d, appending to ann_file"%self.start_frame

            # save to ann_data
            self.ann_file.append( flies )

            # fix any errors using hindsight
            if DEBUG_LEVEL > 0: print "Added to ann_file, now running fixerrors"
            self.hindsight.fixerrors()

            # draw?
            if self.request_refresh or (self.do_refresh and ((self.start_frame % self.framesbetweenrefresh) == 0)):
                if params.interactive:
                    if self.start_frame:
                        self.ShowCurrentFrame()
                else:
                    print "    Frame %d / %d"%(self.start_frame,self.movie.get_n_frames() - 1)
                self.request_refresh = False
            if DEBUG_LEVEL > 1: print len( self.ann_file[-1] ), "flies in last frame"

            # process gui events
            if params.interactive:
                wx.Yield()
            if self.break_flag:
                break

            if (self.start_frame % 100) == 0 and self.has( 'diagnostics_filename' ):
                self.write_diagnostics() # save ongoing

        if hasattr( self, 'timer' ):
            self.timer.cancel()

        self.Finish()


    def write_diagnostics( self ):
        """Safely write diagnostics file."""
        if not self.has( 'diagnostics_filename' ):
            self.diagnostics_filename = self.get_filename_with_extension( '_ctraxdiagnostics.txt' )
        annot.WriteDiagnostics( self.diagnostics_filename )


    def update_track_time( self ):
        """Update the time shown in the timer box."""
        elapsed = time.time() - self.track_timer_start_time
        h = int( (elapsed - (elapsed % (60.*60.)))/60./60. )
        elapsed -= h*60.*60.
        m = int( (elapsed - (elapsed % 60.))/60. )
        elapsed -= m*60.
        s = int( round( elapsed ) )

        # show m:s up to 100 min, then show h:m with blinking colon
        if h == 0:
            time_str = '%02d:%02d' % (m, s)
        elif h == 1 and m < 40:
            time_str = '%02d:%02d' % (m + 60, s)
        elif s % 2 == 0:
            time_str = '%02d:%02d' % (h, m)
        else:
            time_str = '%02d %02d' % (h, m)

        try:
            self.time_text.SetValue( time_str )
        except wx.PyDeadObjectError:
            return
        except AttributeError:
            return

        # set a timer to call this function again a second from now
        self.timer = Timer( 1., self.update_track_time )
        self.timer.start()


    def Finish(self):

        # write the rest of the frames to file
        #self.ann_file.finish_writing()
        self.ann_file.write_all_frames_to_disk()
        if self.has( 'diagnostics_filename' ):
            self.write_diagnostics()


    def StopThreads( self ):
        # stop algorithm
        self.break_flag = True


    def DoAllPreprocessing(self):

        # estimate the background
        if (not self.IsBGModel()) or params.batch_autodetect_bg_model:
            print "Estimating background model"
            if not params.batch_autodetect_bg_model:
                print "**autodetecting background because no existing model is loaded"
            print "BG Modeling parameters:"
            print "n_bg_frames = " + str(self.bg_imgs.n_bg_frames)
            print "use_median = " + str(self.bg_imgs.use_median)
            print "bg_firstframe = " + str(self.bg_imgs.bg_firstframe)
            print "bg_lastframe = " + str(self.bg_imgs.bg_lastframe)
            if not self.OnComputeBg(): return
            self.bg_imgs.updateParameters()
        else:
            print "Not estimating background model"

        # detect arena if it has not been set yet
        if params.do_set_circular_arena and params.batch_autodetect_arena:
            print "Auto-detecting circular arena"
            setarena.doall(self.bg_imgs.center)
        else:
            print "Not detecting arena"

        self.bg_imgs.UpdateIsArena()

        # estimate the shape
        if params.batch_autodetect_shape and params.enforce_minmax_shape:
            print "Estimating shape model"
            self.OnComputeShape()
        else:
            print "Not estimating shape model"

    def DoAll(self):

        if not params.interactive:
            self.RestoreStdio()

        print "Performing preprocessing...\n"
	self.DoAllPreprocessing()

        # initialize ann files

        # if resuming tracking, we will keep the tracks from 
        # frames firstframetracked to lastframetracked-1 
        # (remove last frame in case writing the last frame 
        # was interrupted)
        if params.noninteractive_resume_tracking and self.ann_file.lastframetracked > 0:
            print "resuming at", self.ann_file.lastframetracked
            self.start_frame = self.ann_file.lastframetracked
            if DEBUG_LEVEL > 0: print "start_frame = " + str(self.start_frame)
            if DEBUG_LEVEL > 0: print "cropping annotation file to frames %d through %d"%(self.ann_file.firstframetracked,self.ann_file.lastframetracked-1)
            self.ann_file.InitializeData( self.ann_file.firstframetracked,
                                          self.ann_file.lastframetracked - 1,
                                          bg_model=self.bg_imgs )
            print "initialized...", self.ann_file.lastframetracked

        else:
            print "Initializing annotation file...\n"
            self.ann_file.InitializeData( self.start_frame, bg_model=self.bg_imgs )

        print "Done preprocessing, beginning tracking...\n"

        # begin tracking
        if params.interactive:
            self.UpdateToolBar('started')

        # write sbfmf header
        if self.dowritesbfmf:
            # open an sbfmf file if necessary
            self.movie.writesbfmf_start(self.bg_imgs,
                                        self.writesbfmf_filename)

        print "Tracking..."
        try:
            self.Track()
        except:
            print "Error during Track"
            raise
        print "Done tracking"

        # write the sbfmf index and close the sbfmf file
        if self.dowritesbfmf and self.movie.writesbfmf_isopen():
            self.movie.writesbfmf_close(self.start_frame)
        
        print "Choosing Orientations..."
        # choose orientations
        choose_orientations = chooseorientations.ChooseOrientations(self.frame,interactive=False)
        self.ann_file = choose_orientations.ChooseOrientations( self.ann_file, bg_model=self.bg_imgs )

        # save to a .mat file
        if self.has( 'matfilename' ):
            savename = self.matfilename
        else:
            savename = self.get_filename_with_extension( '.mat' )
        print "Saving to mat file "+savename+"...\n"
        self.ann_file.WriteMAT( self.movie, savename )

        print "Done\n"

