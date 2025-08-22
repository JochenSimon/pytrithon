from .base import Element
from ..utils import WithEnum

@WithEnum('Clear Read Take Give Write')
class Link(Element):
  serial = 0
  def __init__(self, frag, kind, alias, place, hidden):
    self.frag = frag
    self.kind = kind
    self.alias = alias
    self.place = place
    self.hidden = hidden
    self.serial = len(self.frag.globallinks)
    self.frag.globallinks.append(self)

  def connect(self, trans):
    self.parent = trans.parent
    self.trans = trans.name
    trans.parent[self.place].links.append(self)

  def __str__(self):
    return "Link({}, {}, {}, {})".format(self.kind, self.alias, self.place, self.hidden)
  
  def __repr__(self):
    return self.__str__()
