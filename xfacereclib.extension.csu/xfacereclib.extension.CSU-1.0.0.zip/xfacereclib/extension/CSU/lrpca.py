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
  """This class defines a wrapper for the facerec2010.baseline.lrpca.LRPCA class to be used as an image preprocessor in the FaceRecLib."""

  def __init__(self, TUNING):
    """Constructor Documentation:

    TUNING
      The tuning for the LRPCA algorithm as taken from the facerec2010.baseline.lrpca.GBU_TUNING
    """
    facereclib.preprocessing.Preprocessor.__init__(self, **TUNING)
    self.m_lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)


  def __call__(self, image, annotations):
    """Preprocesses the image using the facerec2010.baseline.lrpca.LRPCA.preprocess function"""

    # assure that the eye positions are in the set of annotations
    if annotations is None or 'leye' not in annotations or 'reye' not in annotations:
      raise ValueError("The LDA-IR image cropping needs eye positions, but they are not given.")

    # Warning! Left and right eye are mixed up here!
    # The lrpca preprocess expects left_eye_x < right_eye_x
    tile = self.m_lrpca.preprocess(
        image,
        rect=None,
        leye = pyvision.Point(annotations['reye'][1], annotations['reye'][0]),
        reye = pyvision.Point(annotations['leye'][1], annotations['leye'][0])
    )

    # pyvision used images in (x,y)-order.
    # To be consistent to the (y,x)-order in Bob, we have to transpose
    return tile.asMatrix2D().transpose().astype(numpy.float64)


  def read_original_data(self, image_file):
    """Reads the original images using functionality from pyvision."""
    # we use pyvision to read the images. Hence, we don't have to struggle with conversion here
    return pyvision.Image(str(image_file))


class Features (facereclib.features.Extractor):
  """This class defines a wrapper for the facerec2010.baseline.lrpca.LRPCA class to be used as a feature extractor in the FaceRecLib."""

  def __init__(self, TUNING):
    """Constructor Documentation:

    TUNING
      The tuning for the LRPCA algorithm as taken from the facerec2010.baseline.lrpca.GBU_TUNING
    """
    facereclib.features.Extractor.__init__(self, requires_training=True, split_training_data_by_client=True, **TUNING)
    self.m_lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)


  def _py_image(self, image):
    """Converts the given image to pyvision images."""
    pil_image = PIL.Image.new("L",(image.shape[1],image.shape[0]))
    # TODO: Test if there is any faster method to convert the image type
    for y in range(image.shape[0]):
      for x in range(image.shape[1]):
        # copy image content (re-order [y,x] to (x,y))
        pil_image.putpixel((x,y),image[y,x])

    # convert to pyvision image
    py_image = pyvision.Image(pil_image)
    return py_image


  def train(self, image_list, extractor_file):
    """Trains the LRPCA module with the given image list and saves the result into the given extractor file using the pickle module."""
    train_count = 0
    for client_index in range(len(image_list)):
      for image in image_list[client_index]:

        # convert the image into a data type that is understood by FaceRec2010
        pyimage = self._py_image(image)

        # append training data to the LRPCA training
        # (the None parameters are due to the fact that preprocessing happened before)
        self.m_lrpca.addTraining(str(client_index), pyimage, None, None, None),

        train_count += 1

    facereclib.utils.info("  -> Training LRPCA with %d images" % train_count)
    self.m_lrpca.train()

    # and write the result to file, which in this case simply used pickle
    with open(extractor_file, "wb") as f:
      pickle.dump(self.m_lrpca, f)


  def load(self, extractor_file):
    """Loads the trained LRPCA feature extractor from the given extractor file using the pickle module."""
    # read LRPCA projector
    with open(extractor_file, "rb") as f:
      self.m_lrpca = pickle.load(f)


  def __call__(self, image):
    """Projects the image data using the LRPCA projector and returns a numpy.ndarray."""
    # create pvimage
    pyimage = self._py_image(image)
    # Projects the data by creating a "FaceRecord"
    face_record = self.m_lrpca.getFaceRecord(pyimage, None, None, None)
    # return the projected data, which is stored as a numpy.ndarray
    return face_record.feature



class Tool (facereclib.tools.Tool):
  """This class defines a wrapper for the facerec2010.baseline.lrpca.LRPCA class to be used as a face recognition tool in the FaceRecLib."""

  def __init__(
      self,
      TUNING,
      multiple_model_scoring = 'average', # by default, compute the average between several models and the probe
      multiple_probe_scoring = 'average'  # by default, compute the average between the model and several probes
  ):
    """Constructor Documentation:

    TUNING
      The tuning for the LRPCA algorithm as taken from the facerec2010.baseline.lrpca.GBU_TUNING

    multiple_model_scoring
      The scoring strategy if models are enrolled from several images, see facereclib.tools.Tool for more information.

    multiple_probe_scoring
      The scoring strategy if a score is computed from several probe images, see facereclib.tools.Tool for more information.
    """

    facereclib.tools.Tool.__init__(self, multiple_model_scoring=multiple_model_scoring, multiple_probe_scoring=multiple_probe_scoring, **TUNING)
    # initialize LRPCA (not sure if this is really required)
    self.m_lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)


  def enroll(self, enroll_features):
    """Enrolls a model from features from several images by simply storing all given features."""
    # no rule to enroll features in the LRPCA setup, so we just store all features
    # create model Face records
    model_records = []
    for feature in enroll_features:
      model_record = facerec2010.baseline.pca.FaceRecord(None,None,None)
      model_record.feature = feature[:]
      model_records.append(model_record)
    return model_records


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


  def score(self, model, probe):
    """Computes the score for the given model (a list of FaceRecords) and a probe feature (a numpy.ndarray)"""
    if isinstance(model, list):
      # compute score fusion strategy with several model features (which is implemented in the base class)
      return self.score_for_multiple_models(model, probe)
    else:
      assert isinstance(model, facerec2010.baseline.pca.FaceRecord)
      # compute score for one model and one probe
      probe_record = facerec2010.baseline.pca.FaceRecord(None,None,None)
      probe_record.feature = probe

      return self.m_lrpca.similarityMatrix([probe_record], [model])[0,0]

