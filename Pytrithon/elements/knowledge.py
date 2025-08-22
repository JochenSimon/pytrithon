from .variable import Variable
from .base import Empty

class Knowledge(Variable):
  type = "know"
  @property
  def empty(self):
    return self._tokens is Empty
