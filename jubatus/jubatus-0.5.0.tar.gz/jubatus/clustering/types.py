# This file is auto-generated from clustering.idl(0.4.5-350-g9c67807) with jenerator version 0.4.5-375-g07d06b7/develop
# *** DO NOT EDIT ***


import sys
import msgpack
import jubatus.common
from jubatus.common.types import *

class WeightedDatum:
  TYPE = TTuple(TFloat(), TDatum())

  def __init__(self, weight, point):
    self.weight = weight
    self.point = point

  def to_msgpack(self):
    t = (self.weight, self.point)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return WeightedDatum(*val)

  def __str__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("weighted_datum")
    gen.add("weight", self.weight)
    gen.add("point", self.point)
    gen.close()
    return gen.to_string()

