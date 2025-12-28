import sys
from .variable import Variable


class Phantom(Variable):
  type = "phantom"

  @Variable.tokens.setter
  def tokens(self, tokens):
    Variable.tokens.__set__(self, tokens)
    if self.parent.isfrag and tokens:
      print("Phantom '{}' in fragment '{}' must not have seed".format(self.name.split(".")[1], self.parent.name), file=sys.stderr, hide=True)

  def give(self, token):
    pass
