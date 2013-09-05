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


# We here only specify the non-default configurations
# For the default ones, please check the configurations directory from the facereclib package

import facereclib
import xfacereclib.extension.CSU
import bob
import math

import xbob.db.banca
import xbob.db.gbu

########### The Databases #################

# BANCA
banca = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.banca.Database(),
    name = "banca",
    original_directory = "/idiap/group/biometric/databases/banca/english/images/images/",
    original_extension = ".ppm",
    has_internal_annotations = True,
    protocol = 'P'
)

# the Good, the Bad & the Ugly
gbu_x2 = facereclib.databases.DatabaseXBob(
    database = xbob.db.gbu.Database(),
    name = "gbu",
    original_directory = "/idiap/resource/database/MBGC-V1",
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'Good',

    # the 'x2' training list is used for ISV
    all_files_options = { 'subworld': 'x2' },
    extractor_training_options = { 'subworld': 'x2' },
    projector_training_options = { 'subworld': 'x2' },
    enroller_training_options = { 'subworld': 'x2' }
)

gbu_x8 = facereclib.databases.DatabaseXBob(
    database = xbob.db.gbu.Database(),
    name = "gbu",
    original_directory = "/idiap/resource/database/MBGC-V1",
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'Good',

    # the 'x8' training list is used LDA-IR
    all_files_options = { 'subworld': 'x8' },
    extractor_training_options = { 'subworld': 'x8' },
    projector_training_options = { 'subworld': 'x8' },
    enroller_training_options = { 'subworld': 'x8' }
)


########### The Image Preprocessors #################

# image resolution of the preprocessed images
CROPPED_IMAGE_HEIGHT = 80
CROPPED_IMAGE_WIDTH = 64

# eye positions for frontal images
RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT / 5, CROPPED_IMAGE_WIDTH / 4 - 1)
LEFT_EYE_POS  = (CROPPED_IMAGE_HEIGHT / 5, CROPPED_IMAGE_WIDTH / 4 * 3)


# for ISV and Gabor Graphs, we use the Tan-Triggs preprocessor with default options
tan_triggs_preprocessor = facereclib.preprocessing.TanTriggs(
    cropped_image_size = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
    cropped_positions = {'leye' : LEFT_EYE_POS, 'reye' : RIGHT_EYE_POS}
)

# for LGBPHS, we need a preprocessor that includes an offset of two positions
tan_triggs_offset_preprocessor = facereclib.preprocessing.TanTriggs(
    cropped_image_size = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
    cropped_positions = {'leye' : LEFT_EYE_POS, 'reye' : RIGHT_EYE_POS},
    offset = 2
)

# for LDA-IR, we use the preprocessor as defined by LDA-IR
ldair_preprocessor = xfacereclib.extension.CSU.configurations.ldair_preprocessor


########### The Feature Extractors #################

# LGBPHS:
lgbphs_feature_extractor = facereclib.features.LGBPHS(
    # block setup
    block_size = 8,
    block_overlap = 0,
    # Gabor parameters
    gabor_sigma = math.sqrt(2.) * math.pi,
    # LBP setup (we use the defaults)
    # histogram setup
    sparse_histogram = True
)

# Gabor grid graphs for the Gabor graphs algorithm:
gabor_graph_feature_extractor = facereclib.features.GridGraph(
    # Gabor parameters
    gabor_sigma = math.sqrt(2.) * math.pi,
    # what kind of information to extract
    normalize_gabor_jets = True,
    extract_gabor_phases = True,
    # setup of the fixed grid
    first_node = (4, 4),
    image_resolution = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
    node_distance = (8, 8)
)

# DCT blocks for ISV
isv_feature_extractor = facereclib.features.DCTBlocks(
    # block size and overlap
    block_size = 12,
    block_overlap = 11,
    # DCT coefficients
    number_of_dct_coefficients = 45
)

# for LDA-IR, we use the feature extractor as defined by LDA-IR
ldair_feature_extractor = xfacereclib.extension.CSU.configurations.ldair_feature_extractor


########### The Recognition Algorithms #################

# LGBPHS
lgbphs_tool = facereclib.tools.LGBPHS(
    # Distance function: \Chi^2
    distance_function = bob.math.chi_square,
    is_distance_function = True
)

# Gabor graphs: Use the similarity function incorporating the Gabor phase difference and the Canberra distance
gabor_graph_tool = facereclib.tools.GaborJets(
    # Gabor jet comparison
    gabor_jet_similarity_type = bob.machine.gabor_jet_similarity_type.PHASE_DIFF_PLUS_CANBERRA,
    # Gabor wavelet setup; needs to be identical to the feature extractor
    gabor_sigma = math.sqrt(2.) * math.pi
)

# ISV
isv_tool = facereclib.tools.ISV(
    # ISV subspace dimension
    subspace_dimension_of_u = 160,
    # GMM parameters
    number_of_gaussians = 512,
    # by default, our features are normalized, so it does not need to be done here
    normalize_before_k_means = False
)

# for LDA-IR, we use the algorithm as defined by LDA-IR
ldair_tool = xfacereclib.extension.CSU.configurations.ldair_tool


################ Configurations for GridTK  #################

# setup for simple algorithms that do not require too much
grid_simple = facereclib.utils.GridParameters(
    # parameters for the splitting of jobs into array jobs
    number_of_preprocessings_per_job = 500,
    number_of_extracted_features_per_job = 500,
    number_of_projected_features_per_job = 500,
    number_of_enrolled_models_per_job = 50,
    number_of_models_per_scoring_job = 50,

    # queue setup for the SGE grid
    training_queue = '8G',
    preprocessing_queue = 'default',
    extraction_queue = 'default',
    projection_queue = 'default',
    enrollment_queue = 'default',
    scoring_queue = 'default',
)

# setup for algorithms or databases that require more memory and fast network access
grid_demanding = facereclib.utils.GridParameters(
    # parameters for the splitting of jobs into array jobs
    number_of_preprocessings_per_job = 200,
    number_of_extracted_features_per_job = 200,
    number_of_projected_features_per_job = 200,
    number_of_enrolled_models_per_job = 20,
    number_of_models_per_scoring_job = 20,

    # queue setup for the SGE grid
    training_queue = '32G',
    preprocessing_queue = '8G-io-big',
    extraction_queue = '8G-io-big',
    projection_queue = '8G-io-big',
    enrollment_queue = '8G-io-big',
    scoring_queue = '8G-io-big',
)

# setup for running jobs locally in parallel processes
grid_local = facereclib.utils.GridParameters(
    # parameters for the splitting of jobs into array jobs
    number_of_preprocessings_per_job = 500,
    number_of_extracted_features_per_job = 500,
    number_of_projected_features_per_job = 500,
    number_of_enrolled_models_per_job = 50,
    number_of_models_per_scoring_job = 50,

    # setup for the local execution
    grid = 'local',
    number_of_parallel_processes = 4,
    scheduler_sleep_time = 5.0,
)

