# This file is auto-generated from classifier.idl(0.4.5-347-g86989a6) with jenerator version 0.4.5-375-g07d06b7/develop
# *** DO NOT EDIT ***


import sys
import msgpack
import jubatus.common
from jubatus.common.types import *

class EstimateResult:
  TYPE = TTuple(TString(), TFloat())

  def __init__(self, label, score):
    self.label = label
    self.score = score

  def to_msgpack(self):
    t = (self.label, self.score)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return EstimateResult(*val)

  def __str__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("estimate_result")
    gen.add("label", self.label)
    gen.add("score", self.score)
    gen.close()
    return gen.to_string()

class LabeledDatum:
  TYPE = TTuple(TString(), TDatum())

  def __init__(self, label, data):
    self.label = label
    self.data = data

  def to_msgpack(self):
    t = (self.label, self.data)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return LabeledDatum(*val)

  def __str__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("labeled_datum")
    gen.add("label", self.label)
    gen.add("data", self.data)
    gen.close()
    return gen.to_string()

