import sys
from .base import Empty
from .variable import Variable

class Flow(Variable):
  type = "flow"
  def __init__(self, seed, args, pos):
    super().__init__(seed, args, pos)
    self._tokens = Empty
    self.typing = "tuple"

  @property
  def tokens(self):
    if self._tokens is Empty:
      string = ""
    elif self._tokens == ():
      string = "()"
    return string  
  
  @tokens.setter
  def tokens(self, tokens):
    if not tokens:
      self._tokens = Empty
    elif tokens == "()":
      self._tokens = ()
    else:
      print("Corrupt seed in place '{}'".format(self.name), file=sys.stderr, hide=True)

  def give(self, token):
    token = ()
    super().give(token)

  def write(self, token):
    token = ()
    super().write(token)
