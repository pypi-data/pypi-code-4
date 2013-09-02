#!/usr/bin/env python

try:
  import facerec2010
except ImportError:
  raise "Unable to import the facerec2010 tools. Please install the facerec2010 libraries."


import xfacereclib.extension.CSU


# I don't know if this is still required, but in any case:
# LDA-IR regions as defaulted by facerec2010
REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS
REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS

# LRPCA tuning as defaulted by facerec2010
TUNING = facerec2010.baseline.lrpca.GBU_TUNING



# LDA-IR image preprocessing
ldair_preprocessor = xfacereclib.extension.CSU.ldair.ImageCrop(REGION_ARGS, REGION_KEYWORDS)
# LRPCA preprocessing
lrpca_preprocessor = xfacereclib.extension.CSU.lrpca.ImageCrop(TUNING)


# LDA-IR feature extraction
ldair_feature_extractor = xfacereclib.extension.CSU.ldair.Features(REGION_ARGS, REGION_KEYWORDS)
# LRPCA feature extraction
lrpca_feature_extractor = xfacereclib.extension.CSU.lrpca.Features(TUNING)

# LDA-IR tool
ldair_tool = xfacereclib.extension.CSU.ldair.Tool(REGION_ARGS, REGION_KEYWORDS)
# LRPCA tool
lrpca_tool = xfacereclib.extension.CSU.lrpca.Tool(TUNING)



