# This file is auto-generated from regression.idl(0.4.5-347-g86989a6) with jenerator version 0.4.5-375-g07d06b7/develop
# *** DO NOT EDIT ***


import msgpackrpc
import jubatus.common
from types import *
from jubatus.common.types import *

class Regression(jubatus.common.ClientBase):
  def __init__(self, host, port, name, timeout=10):
    super(Regression, self).__init__(host, port, name, timeout)

  def train(self, train_data):
    return self.jubatus_client.call("train", [train_data], TInt(True, 4),
        [TList(TUserDef(ScoredDatum))])

  def estimate(self, estimate_data):
    return self.jubatus_client.call("estimate", [estimate_data], TList(TFloat(
        )), [TList(TDatum())])

  def clear(self):
    return self.jubatus_client.call("clear", [], TBool(), [])
