#
# ColorManager.py -- Abstraction of an generic data image.
#
# Eric Jeschke (eric@naoj.org) 
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import time
import numpy
import os
import hashlib

# Do we have color management (ICC profile) support?
try:
    import PIL.ImageCms as ImageCms
    have_cms = True
except ImportError:
    have_cms = False

try:
    basedir = os.environ['GINGA_HOME']
except KeyError:
    basedir = os.path.join(os.environ['HOME'], '.ginga')


class ColorManager(object):

    def __init__(self, logger, settings):
        self.logger = logger
        self.settings = settings

        # Color Management configuration
        self.profile = {}
        for filename in ('working.icc', 'monitor.icc', 'sRGB.icc',
                         'AdobeRGB.icc'):
            profname, ext = os.path.splitext(filename)
            self.profile[profname] = os.path.join(basedir, "profiles", filename)

        self.rendering_intent = ImageCms.INTENT_PERCEPTUAL

        # Prepare common transforms
        self.transform = {}
        # Build transforms for profile conversions for which we have profiles
        if have_cms:
            for inprof, outprof in [('sRGB', 'working'),
                                    ('AdobeRGB', 'working'),
                                    ('working', 'monitor')]:
                if os.path.exists(self.profile[inprof]) and os.path.exists(self.profile[outprof]):
                    self.transform[(inprof, outprof)] = ImageCms.buildTransform(self.profile[inprof],
                                                                           self.profile[outprof],
                                                                           'RGB', 'RGB',
                                                                           renderingIntent=rendering_intent,
                                                                           flags=0)


    def convertToWorking(self, image):
        """Load an image file, guessing the format, and return a numpy
        array containing an RGB image.  If EXIF keywords can be read
        they are returned in the dict _kwds_.
        """
        start_time = time.time()
        
        # If we have a working color profile then handle any embedded
        # profile or color space information, if possible
        if have_cms and os.path.exists(self.profile['working']):
            # Assume sRGB image, unless we learn to the contrary
            in_profile = 'sRGB'
            try:
                if image.info.has_key('icc_profile'):
                    self.logger.debug("image has embedded color profile")
                    buf_profile = image.info['icc_profile']
                    # Write out embedded profile (if needed)
                    prof_md5 = hashlib.md5(buf_profile).hexdigest()
                    in_profile = "/tmp/_image_%d_%s.icc" % (
                        os.getpid(), prof_md5)
                    if not os.path.exists(in_profile):
                        with open(in_profile, 'w') as icc_f:
                            icc_f.write(buf_profile)

                # see if there is any EXIF tag about the colorspace
                elif kwds.has_key('ColorSpace'):
                    csp = kwds['ColorSpace']
                    iop = kwds.get('InteroperabilityIndex', None)
                    if (csp == 0x2) or (csp == 0xffff):
                        # NOTE: 0xffff is really "undefined" and should be
                        # combined with a test of EXIF tag 0x0001
                        # ('InteropIndex') == 'R03', but PIL _getexif()
                        # does not return the InteropIndex
                        in_profile = 'AdobeRGB'
                        self.logger.debug("hmm..this looks like an AdobeRGB image")
                    elif csp == 0x1:
                        self.logger.debug("hmm..this looks like a sRGB image")
                        in_profile = 'sRGB'
                    else:
                        self.logger.debug("no color space metadata, assuming this is an sRGB image")

                # if we have a valid profile, try the conversion
                tr_key = (in_profile, 'working')
                if tr_key in self.transform:
                    # We have am in-core transform already for this (faster)
                    image = convert_profile_pil_transform(image, self.transform[tr_key],
                                                          inPlace=True)
                else:
                    # Convert using profiles on disk (slower)
                    if in_profile in profile:
                        in_profile = self.profile[in_profile]
                    image = convert_profile_pil(image, in_profile,
                                                self.profile['working'])
                self.logger.info("converted from profile (%s) to profile (%s)" % (
                    in_profile, self.profile['working']))
            except Exception, e:
                self.logger.error("Error converting from embedded color profile: %s" % (str(e)))
                self.logger.warn("Leaving image unprofiled.")

        data_np = numpy.array(image)

        end_time = time.time()
        self.logger.debug("loading (%s) time %.4f sec" % (
            means, end_time - start_time))
        return data_np

    def have_monitor_profile(self):
        return ('working', 'monitor') in self.transform

    def convert_profile_monitor(self, image_np):
        output_transform = self.transform[('working', 'monitor')]
        out_np = convert_profile_numpy_transform(image_np, output_transform)
        return out_np

# --- Color Management conversion functions ---

def convert_profile_pil(image_pil, inprof_path, outprof_path, inPlace=False):
    if not have_cms:
        return image_pil
    
    image_out = ImageCms.profileToProfile(image_pil, inprof_path,
                                          outprof_path, 
                                          renderingIntent=rendering_intent,
                                          outputMode='RGB', inPlace=inPlace,
                                          flags=0)
    if inPlace:
        return image_pil
    return image_out

def convert_profile_pil_transform(image_pil, transform, inPlace=False):
    if not have_cms:
        return image_pil
    
    image_out = ImageCms.applyTransform(image_pil, transform, inPlace)
    if inPlace:
        return image_pil
    return image_out

def convert_profile_numpy(image_np, inprof_path, outprof_path):
    if (not have_pilutil) or (not have_cms):
        return image_np

    in_image_pil = pilutil.toimage(image_np)
    out_image_pil = convert_profile_pil(in_image_pil,
                                        inprof_path, outprof_path)
    image_out = pilutil.fromimage(out_image_pil)
    return image_out

def convert_profile_numpy_transform(image_np, transform):
    if (not have_pilutil) or (not have_cms):
        return image_np

    in_image_pil = pilutil.toimage(image_np)
    convert_profile_pil_transform(in_image_pil, transform, inPlace=True)
    image_out = pilutil.fromimage(in_image_pil)
    return image_out

#END
