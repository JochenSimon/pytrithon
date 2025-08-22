import sys
from .base import Element
from .link import Link
from ..stringify import stringify_place

class Place(Element):
  type = "place"
  isplace = True

  def __init__(self, seed, args, pos):
    super().__init__(args, pos)
    self.seed = seed
    self.typing = args
    self.links = []

  @property
  def clearers(self):
    return [link for link in self.links if link.kind is Link.Clear]

  @property
  def readers(self):
    return [link for link in self.links if link.kind is Link.Read]

  @property
  def takers(self):
    return [link for link in self.links if link.kind is Link.Take]

  @property
  def givers(self):
    return [link for link in self.links if link.kind is Link.Give]

  @property
  def writers(self):
    return [link for link in self.links if link.kind is Link.Write]

  def __str__(self):
    return stringify_place(self)

  def typecheck(self, token):
    if self.typing:
      try:
        typing = eval("("+self.typing+")", globals(), self.parent.env)
        if "," in self.typing:
          if isinstance(token, str):
            raise Exception("String")
          for i,typ in enumerate(typing):
            self.printcheck(token[i], typ)
        else:
          self.printcheck(token, typing)
      except Exception:
        print("Wrong typing in place '{}'".format(self.name), file=sys.stderr, hide=True)

  def printcheck(self, token, typing):        
    if not isinstance(token, typing):
      print("Wrong type {} in place '{}' expecting type {}".format(type(token), self.name, typing), file=sys.stderr, hide=True)
