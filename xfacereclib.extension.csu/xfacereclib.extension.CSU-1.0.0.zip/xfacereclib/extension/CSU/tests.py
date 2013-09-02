#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 10:12:23 CET 2012
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


import unittest
import os
import numpy
import tempfile
import facereclib
import facerec2010
import xfacereclib.extension.CSU
import bob
from nose.plugins.skip import SkipTest

import pkg_resources

regenerate_refs = False

class PythonFaceEvaluationTest(unittest.TestCase):

  def input(self, dir, file):
    test_file = pkg_resources.resource_filename('xfacereclib.extension.CSU', os.path.join('testdata', dir, file))
    facereclib.utils.ensure_dir(os.path.dirname(test_file))
    return test_file


  def train_set(self, feature, count = 50, a = 0, b = 1, as_int = False, seed = True):
    # generate a random sequence of features
    if seed:
      numpy.random.seed(42)
    train_set = [numpy.random.random(feature.shape) * (b - a) + a for i in range(count)]
    if as_int:
      train_set = [f.astype(int) for f in train_set]
    return train_set

  def train_set_by_id(self, feature, count = 7, a = 0, b = 1, as_int = False):
    # generate a random sequence of features
    numpy.random.seed(42)
    return [self.train_set(feature, count, a, b, as_int, seed = False) for i in range(count)]


  def execute_preprocessor(self, preprocessor, image, annotations, reference):
    # execute the preprocessor
    preprocessed = preprocessor(image, annotations)
    if regenerate_refs:
      preprocessor.save_data(preprocessed, self.input('preprocessing', reference))

    self.assertTrue((numpy.abs(preprocessor.read_data(self.input('preprocessing', reference)) - preprocessed) < 1e-5).all())


  def execute_extractor(self, extractor, image, reference):
    # execute the preprocessor
    feature = extractor(image)
    if regenerate_refs:
      bob.io.save(feature, self.input('features', reference))

    self.assertTrue((numpy.abs(bob.io.load(self.input('features', reference)) - feature) < 1e-5).all())
    return feature



  def test01_ldair_preprocessing(self):
    # generate face cropper
    preprocessor = facereclib.utils.tests.configuration_file('lda-ir', 'preprocessor', 'xfacereclib.extension.CSU')

    # load image
    image = preprocessor.read_original_data(self.input(".", "testimage.png"))
    annotation = facereclib.utils.read_annotations(self.input(".", "testimage.pos"), 'named')

    # execute face cropper
    self.execute_preprocessor(preprocessor, image, annotation, 'ldair.hdf5')


  def test02_ldair_features(self):
    # read input
    image = bob.io.load(self.input('preprocessing', 'ldair.hdf5'))
    extractor = facereclib.utils.tests.configuration_file('lda-ir', 'feature_extractor', 'xfacereclib.extension.CSU')
    self.assertTrue(extractor.requires_training)
    self.assertTrue(extractor.split_training_data_by_client)


    # we have to train the eigenface extractor, so we generate some data
    train_data = self.train_set_by_id(image, 10, 0, 255, True)

    t = tempfile.mkstemp('ldair.pkl')[1]
    extractor.train(train_data, t)

    if regenerate_refs:
      import shutil
      shutil.copy2(t, self.input('features', 'ldair_extractor.pkl'))

    extractor.load(self.input('features', 'ldair_extractor.pkl'))

    # TODO: compare the resulting extractors
    #import pickle
    #f = open(t, "rb")
    #new_ldair = pickle.load(f)
    #f.close()
    #self.assertEqual(extractor.m_ldair, new_ldair)

    os.remove(t)

    # now, we can execute the extractor and check that the feature is still identical
    feature = extractor(image)
    if regenerate_refs:
      extractor.save_feature(feature, self.input('features', 'ldair.pkl'))

    # TODO: check the reference feature
    reference = extractor.read_feature(self.input('features', 'ldair.pkl'))
    #self.assertEqual(feature, reference)


  def test03_ldair_tool(self):
    # read feature using the extractor
    extractor = facereclib.utils.tests.configuration_file('lda-ir', 'feature_extractor', 'xfacereclib.extension.CSU')
    feature = extractor.read_feature(self.input('features', 'ldair.pkl'))

    # use the registered tool
    tool = facereclib.utils.tests.configuration_file('lda-ir', 'tool')
    self.assertFalse(tool.performs_projection)
    self.assertFalse(tool.requires_enroller_training)

    # just enroll the model
    model = tool.enroll([feature])
    if regenerate_refs:
      tool.save_model(model, self.input('tool', 'ldair_model.pkl'))
    # TODO: compare reference model with new one
    reference_model = tool.read_model(self.input('tool', 'ldair_model.pkl'))
    #self.assertEqual(model, reference_model)

    # Read probe; should be identical to the feature
    reference_probe = tool.read_probe(self.input('features', 'ldair.pkl'))
    #self.assertEqual(feature, reference_probe)

    # score
    sim = tool.score(model, reference_probe)
    # LDA-IR by default returns the negative L2 distance, which is 0 in this case
    self.assertAlmostEqual(sim, 0.)


  def test04_lrpca_preprocessing(self):
    # generate face cropper
    preprocessor = facereclib.utils.tests.configuration_file('lrpca', 'preprocessor', 'xfacereclib.extension.CSU')

    # load image
    image = preprocessor.read_original_data(self.input('.', 'testimage.png'))
    annotations = facereclib.utils.read_annotations(self.input('.', 'testimage.pos'), 'named')

    # execute face cropper
    self.execute_preprocessor(preprocessor, image, annotations, 'lrpca.hdf5')


  def test05_lrpca_features(self):
    # read input
    image = bob.io.load(self.input('preprocessing', 'lrpca.hdf5'))

    # check that the configuration file is read properly
    extractor = facereclib.utils.tests.configuration_file('lrpca', 'feature_extractor', 'xfacereclib.extension.CSU')

    # for testing purposes, we use a smaller number of kept fisher faces
    TUNING = facerec2010.baseline.lrpca.GBU_TUNING
    TUNING['fisher_thresh'] = 20
    extractor = xfacereclib.extension.CSU.lrpca.Features(TUNING)
    self.assertTrue(extractor.requires_training)
    self.assertTrue(extractor.split_training_data_by_client)

    # we have to train the extractor, so we generate some data
    train_data = self.train_set_by_id(image, 10, 0, 255, True)
    t = tempfile.mkstemp('lrpca.pkl')[1]
    extractor.train(train_data, t)
    if regenerate_refs:
      import shutil
      shutil.copy2(t, self.input('features','lrpca_extractor.pkl'))

    extractor.load(self.input('features', 'lrpca_extractor.pkl'))
    # TODO: compare the resulting extractors
    #import pickle
    #f = open(t, "rb")
    #new_lrpca = pickle.load(f)
    #f.close()
    #self.assertEqual(extractor.m_lrpca, new_lrpca)
    os.remove(t)

    # now, we can execute the extractor and check that the feature is still identical
    feature = self.execute_extractor(extractor, image, 'lrpca.hdf5')
    self.assertEqual(len(feature.shape), 1)



  def test06_lrpca_tool(self):
    feature = bob.io.load(self.input('features', 'lrpca.hdf5'))
    tool = facereclib.utils.tests.configuration_file('lrpca', 'tool', 'xfacereclib.extension.CSU')

    # enroll model
    model = tool.enroll([feature])
    if regenerate_refs:
      tool.save_model(model, self.input('tool', 'lrpca_model.pkl'))
    # TODO: compare reference model with new one
    reference_model = tool.read_model(self.input('tool', 'lrpca_model.pkl'))
    #self.assertEqual(model, reference_model)

    # Read probe; should be identical to the feature
    probe = tool.read_probe(self.input('features', 'lrpca.hdf5'))
    #self.assertEqual(feature, probe)

    # score
    sim = tool.score(model, feature)
    # LRPCA by default computes the correlation between model and probe, which is 1 in this case
    # weirdly, the similarity is not exactly one for some reason...
    self.assertAlmostEqual(sim, 1., places=4)


