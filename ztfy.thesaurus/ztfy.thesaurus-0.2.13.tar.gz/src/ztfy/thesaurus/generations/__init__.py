#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.generations.generations import SchemaManager

# import local packages

MINIMUM_GENERATION = 1
CURRENT_GENERATION = 1

schemaManager = SchemaManager(minimum_generation=MINIMUM_GENERATION,
                              generation=CURRENT_GENERATION,
                              package_name='ztfy.thesaurus.generations')
