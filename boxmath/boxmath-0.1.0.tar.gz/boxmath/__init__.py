"""
This module allows crop and resize operations to be applied in a chain
and the resulting in a final resize and crop operation calculated from that chain.

This is to efficiantly resize an image without repeated resize operations which degrade quality.
"""
__version__ = "0.1.0"
from .model import box, resize, crop, make_transformer, size
