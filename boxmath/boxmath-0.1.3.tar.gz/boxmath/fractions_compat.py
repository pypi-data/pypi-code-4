import sys
print(tuple(sys.version_info) < (2, 7))
if tuple(sys.version_info) < (2, 7):
    from fractions27 import Fraction
else:
    print("using system fractions")
    from fractions import Fraction

__all__ = ['Fraction']
