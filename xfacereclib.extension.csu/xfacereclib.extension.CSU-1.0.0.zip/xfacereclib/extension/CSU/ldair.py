#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 09:27:59 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import facerec2010
import pyvision
import pickle
import PIL
import numpy
import facereclib


class ImageCrop (facereclib.preprocessing.Preprocessor):
  """This class defines a wrapper for the facerec2010.baseline.lda.LRLDA class to be used as an image preprocessor in the FaceRecLib."""

  def __init__(self, REGION_ARGS, REGION_KEYWORDS):
    """Constructor Documentation:

    REGION_ARGS
      The region arguments as taken from facerec2010.baseline.lda.CohortLDA_REGIONS

    REGION_KEYWORDS
      The region keywords as taken from facerec2010.baseline.lda.CohortLDA_KEYWORDS
    """

    facereclib.preprocessing.Preprocessor.__init__(self, **REGION_KEYWORDS)
    self.m_ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.m_layers = len(REGION_ARGS)


  def __call__(self, image, annotations):
    """Preprocesses the image using the LDA-IR preprocessor facerec2010.baseline.lda.LRLDA.preprocess"""

    # assure that the eye positions are in the set of annotations
    if annotations is None or 'leye' not in annotations or 'reye' not in annotations:
      raise ValueError("The LDA-IR image cropping needs eye positions, but they are not given.")

    # Warning! Left and right eye are mixed up here!
    # The ldair preprocess expects left_eye_x < right_eye_x
    tiles = self.m_ldair.preprocess(
        image,
        leye = pyvision.Point(annotations['reye'][1], annotations['reye'][0]),
        reye = pyvision.Point(annotations['leye'][1], annotations['leye'][0])
    )

    # LDAIR preprocessing spits out 4D structure, i.e., [Matrix]
    # with each element of the outer list being identical
    # so we just have to copy the first image

    assert len(tiles) == self.m_layers
    assert (tiles[0].asMatrix3D() == tiles[1].asMatrix3D()).all()

    # Additionally, pyvision used images in (x,y)-order.
    # To be consistent to the (y,x)-order in the facereclib, we have to transpose
    color_image = tiles[0].asMatrix3D()
    out_images = numpy.ndarray((color_image.shape[0], color_image.shape[2], color_image.shape[1]), dtype = numpy.uint8)

    # iterate over color layers
    for j in range(color_image.shape[0]):
      out_images[j,:,:] = color_image[j].transpose()[:,:]

    # WARNING! This contradicts the default way, images are written. Here, we write full color information!
    return out_images


  def read_original_data(self, image_file):
    """Reads the original images using functionality from pyvision."""
    # we use pyvision to read the images. Hence, we don't have to struggle with conversion here
    return pyvision.Image(str(image_file))


class Features (facereclib.features.Extractor):
  """This class defines a wrapper for the facerec2010.baseline.lda.LRLDA class to be used as a feature extractor in the FaceRecLib."""

  def __init__(self, REGION_ARGS, REGION_KEYWORDS):
    """Constructor Documentation:

    REGION_ARGS
      The region arguments as taken from facerec2010.baseline.lda.CohortLDA_REGIONS

    REGION_KEYWORDS
      The region keywords as taken from facerec2010.baseline.lda.CohortLDA_KEYWORDS
    """
    facereclib.features.Extractor.__init__(self, requires_training=True, split_training_data_by_client=True, **REGION_KEYWORDS)
    self.m_ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.m_layers = len(REGION_ARGS)
    self.m_use_cohort = 'cohort_adjust' not in REGION_ARGS[0] or REGION_ARGS[0]['cohort_adjust']

    # overwrite the training image list generation from the file selector
    # since LRPCA needs training data to be split up into identities
    self.use_training_images_sorted_by_identity = True


  def _py_image(self, image):
    """Generates a 4D structure used for LDA-IR feature extraction"""

    pil_image = PIL.Image.new("RGB",(image.shape[2], image.shape[1]))
    # TODO: Test if there is any faster method to convert the image type
    for y in range(image.shape[1]):
      for x in range(image.shape[2]):
        # copy image content (re-order [y,x] to (x,y) and add the colors as (r,g,b))
        pil_image.putpixel((x,y),(image[0,y,x], image[1,y,x], image[2,y,x]))

    # convert to pyvision image
    py_image = pyvision.Image(pil_image)
    # generate some copies of the image
    return [py_image.copy() for i in range(self.m_layers)]


  def train(self, image_list, extractor_file):
    """Trains the LDA-IR module with the given image list and saves its result into the given extractor file using the pickle module."""
    train_count = 0
    for client_index in range(len(image_list)):
      # Initializes an arrayset for the data
      for image in image_list[client_index]:
        # create PIL image (since there are differences in the
        # implementation of pyvision according to different image types)
        # Additionally, PIL used pixels in (x,y) order
        pyimage = self._py_image(image)

        # append training data to the LDA-IR training
        # (the None parameters are due to the fact that preprocessing happened before)
        self.m_ldair.addTraining(str(client_index), pyimage, None, None, None)

        train_count += 1

    facereclib.utils.info("  -> Training LDA-IR with %d images" % train_count)
    self.m_ldair.train()

    if self.m_use_cohort:
      facereclib.utils.info("  -> Adding cohort images")
      # add image cohort for score normalization
      for client_images in image_list:
        # Initializes an arrayset for the data
        for image in client_images:
          pyimage = self._py_image(image)
          self.m_ldair.addCohort(pyimage, None, None, None)


    # and write the result to file, which in this case simply used pickle
    with open(extractor_file, "wb") as f:
      pickle.dump(self.m_ldair, f, protocol=2)

    # remember the length of the produced feature
    self.m_feature_length = self.m_ldair.regions[0][2].lda_vecs.shape[1]
    for r in self.m_ldair.regions: assert r[2].lda_vecs.shape[1] == self.m_feature_length


  def load(self, extractor_file):
    """Loads the LDA-IR from the given extractor file using the pickle module."""
    # read LDA-IR extractor
    with open(extractor_file, "rb") as f:
      self.m_ldair = pickle.load(f)
    # remember the length of the produced feature
    self.m_feature_length = self.m_ldair.regions[0][2].lda_vecs.shape[1]
    for r in self.m_ldair.regions: assert r[2].lda_vecs.shape[1] == self.m_feature_length


  def __call__(self, image):
    """Projects the data using LDA-IR."""
    # create pvimage
    pyimage = self._py_image(image)
    # Projects the data (by creating a "Face Record"
    face_record = self.m_ldair.getFaceRecord(pyimage, None, None, None, compute_cohort_scores = self.m_use_cohort)

    return face_record


  def save_feature(self, feature, feature_file):
    """Saves the projected LDA-IR feature to file using the pickle module."""
    # write the feature to a .pkl file
    # (since FaceRecord does not have a save method)
    with open(feature_file, "wb") as f:
      pickle.dump(feature, f)


  def read_feature(self, feature_file):
    """Reads the projected LDA-IR feature from file using the pickle module."""
    # read the feature from .pkl file
    with open(feature_file, "rb") as f:
      face_record = pickle.load(f)
    return face_record


class Tool (facereclib.tools.Tool):
  """This class defines a wrapper for the facerec2010.baseline.lda.LRLDA class to be used as a face recognition tool in the FaceRecLib."""

  def __init__(
      self,
      REGION_ARGS,
      REGION_KEYWORDS,
      multiple_model_scoring = 'average', # by default, compute the average between several models and the probe
      multiple_probe_scoring = 'average'  # by default, compute the average between the model and several probes
  ):
    """Constructor Documentation:

    REGION_ARGS
      The region arguments as taken from facerec2010.baseline.lda.CohortLDA_REGIONS

    REGION_KEYWORDS
      The region keywords as taken from facerec2010.baseline.lda.CohortLDA_KEYWORDS

    multiple_model_scoring
      The scoring strategy if models are enrolled from several images, see facereclib.tools.Tool for more information.

    multiple_probe_scoring
      The scoring strategy if a score is computed from several probe images, see facereclib.tools.Tool for more information.
    """
    facereclib.tools.Tool.__init__(self, multiple_model_scoring=multiple_model_scoring, multiple_probe_scoring=multiple_probe_scoring, **REGION_KEYWORDS)
    self.m_ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.m_use_cohort = 'cohort_adjust' not in REGION_ARGS[0] or REGION_ARGS[0]['cohort_adjust']


  def load_projector(self, projector_file):
    """This function loads the Projector from the given projector file.
    This is only required when the cohort adjustment is enabled.
    """
    # To avoid re-training the Projector, we load the Extractor file instead.
    # This is only required when the cohort adjustment is enabled, otherwise the default parametrization of LRLDA should be sufficient.
    # Be careful, THIS IS A HACK and it might not work in all circumstances!
    if self.m_use_cohort:
      extractor_file = projector_file.replace("Projector", "Extractor")
      with open(extractor_file, "rb") as f:
        self.m_ldair = pickle.load(f)


  def enroll(self, enroll_features):
    """Enrolls a model from features from several images by simply storing all given features."""
    # just store all features (should be of type FaceRecord)
    # since the given features are already in the desired format, there is nothing to do.
    return enroll_features

  def save_model(self, model, model_file):
    """Saves the enrolled model to file using the pickle module."""
    # just dump the model to .pkl file
    with open(model_file, "wb") as f:
      pickle.dump(model, f)

  def read_model(self, model_file):
    """Loads an enrolled model from file using the pickle module."""
    # just read the model from .pkl file
    with open(model_file, "rb") as f:
      model = pickle.load(f)
    return model

  # probe and model are identically stored in a .pkl file
  read_probe = read_model

  def score(self, model, probe):
    """Compute the score for the given model (a list of FaceRecords) and a probe (a FaceRecord)"""
    if isinstance(model, list):
      # compute score fusion strategy with several model features (which is implemented in the base class)
      return self.score_for_multiple_models(model, probe)
    else:
      assert isinstance(model, facerec2010.baseline.common.FaceRecord)
      assert isinstance(probe, facerec2010.baseline.common.FaceRecord)

      return self.m_ldair.similarityMatrix([probe], [model])[0,0]

