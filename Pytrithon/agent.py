from collections import OrderedDict
from .elements import *
from .pml import *
from .utils import *

class Agent:
  isfrag = False
  def __init__(self, name, args, structure):
    self.name = name
    self.args = tuple(args)
    self.structure = structure
    self.exists = False

  @property
  def agentname(self):
    return self.name

  @property  
  def places(self):
    return [e for e in self.elements.values() if e.isplace]

  def __setitem__(self, key, value):
    value.own(self, key)
    self.elements[key] = value

  def __getitem__(self, key):
    if "." in key:
      for frag in (e.name for e in self.elements.values() if e.isfrag):
        if key.split(".")[0] == frag:
          return self.elements[frag].elements[key]
    return self.elements[key]
  
  def __contains__(self, key):
    if "." in key:
      for frag in (e.name for e in self.elements.values() if e.isfrag):
        if key.split(".")[0] == frag:
          return key in self.elements[frag].elements
    return key in self.elements

  def init(self, structure=None):
    if structure is not None:
      self.structure = structure
    self.exists = True  

    self.elements = OrderedDict()
    self.globallinks = []
    self.env = {}

    root = parse(self.structure)

    for node in root.children:
      self[node.name] = assoc[node.keyword](node.suite, node.args, node.pos)
      for kind,alias,place,hidden in node.links:
        self[node.name].links.append(Link(self, linkmap[kind], alias, place, hidden))
    
  def create_element(self, type, name, typing, pos):
    self[name] = assoc[type]("" if type != "comment" else "<comment>", typing, pos)
    self[name].load()
    self[name].init()

  def change_to(self, name, type):
    links = self[name].links
    self[name] = assoc[type](self[name].seed, "" if self[name].type == "flow" else self[name].typing, self[name].pos)
    self[name].links = links
    self[name].init()

  def delete_element(self, name):
    if self.elements[name].isplace:
      for link in self.elements[name].links:
        self.elements[link.trans].links.remove(link)
    elif self.elements[name].istrans or self.elements[name].isgadget:
      for link in self.elements[name].links:
        self.elements[link.place].links.remove(link)
    del self.elements[name]    
    flood(self.elements, self.globallinks)

  def __repr__(self):
    return "\n".join(str(e) for e in self.elements.values()) + "\n"

  def __str__(self):
    return self.name
