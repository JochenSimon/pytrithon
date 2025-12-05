import re
from collections import OrderedDict
from collections.abc import Mapping
import yaml
from string import Template
from itertools import dropwhile
from . import *
from ..utils import linker, sanitize
from ..pml import parse, parselinks

class Fragment(Transition):
  type = "frag"
  istrans = False
  isfrag = True

  def __init__(self, inscription, args, pos):
    super().__init__(inscription, args, pos)

  def __setitem__(self, key, value):
    value.own(self, key)
    self.elements[key] = value

  def __getitem__(self, key):
    return self.parent[key]

  def __contains__(self, key):
    return key in self.elements or key in self.parent.elements

  @property
  def agentname(self):
    return self.parent.agentname

  @property
  def core(self):
    return self.parent.core
  
  @property
  def env(self):
    return self.parent.env
  
  def load(self):
    self.elements = OrderedDict()
    self.globallinks = []
    inscr = sanitize(self.inscr)
    if "\n" in inscr:
      name, inscr = inscr.split("\n", 1)
    else:
      name, inscr = inscr, ""
    try:
      subs = yaml.safe_load(inscr)
    except Exception:
      print("Corrupt fragment mapping in '{}'".format(self.name), file=sys.stderr, hide=True)
      subs = ""
    subs = {k: str(v) for k,v in subs.items()} if isinstance(subs, Mapping) else {}
    try:
      with open(self.core.workbench + "/fragments/"+name.replace(".", "/")+".ptf", encoding="utf-8") as f:
        root = parse(Template(f.read()).safe_substitute(subs))
        for node in root.children:
          self[self.name+"."+node.name] = assoc[node.keyword](node.suite, node.args, node.pos)
          for kind,alias,place,hidden in node.links:
            self[self.name+"."+node.name].links.append(Link(self, linkmap[kind], alias, self.name+"."+place, hidden))
    except FileNotFoundError:
      pass
  
  def init(self):
    for link in self.links:
      link.connect(self)
    for element in self.elements.values():
      element.init()
    for phantom in (p for p in self.elements.values() if p.type == "phantom"):
      for inner in phantom.links:
        changed = False
        for outer in self.links:
          if inner.alias == outer.alias and inner.kind == outer.kind:
            inner.place = outer.place
            changed = True
        if changed:
          self[inner.trans].init()

  def create(self):
    for element in self.elements.values():
      element.create()

  def prime(self):
    for element in self.elements.values():
      element.prime()

  def offer(self, link):
    pass

  def retract(self, link):
    pass

  def delete_link(self, link):
    self.links.remove(link)

  def create_links(self, inscr):
    links, self.inscr, errors = parselinks(inscr)
    for hidden in [link for link in self.links if link.hidden == True]:
      self.links.remove(hidden)
    for kind,alias,place,hidden in links:
      if place in self.parent and self.parent[place].isplace:
        link = Link(self.parent, linkmap[kind], alias, place, hidden)
        link.connect(self)
        self.links.append(link)

  def __repr__(self):
    return "\n".join(str(e) for e in self.elements.values()) + "\n"

assoc = {"self": Self, "module": Module, "ontology": Ontology, "var": Variable, "know": Knowledge, "flow": Flow, "pool": Pool, "queue": Queue, "stack": Stack, "heap": Heap, "set": Set, "phantom": Phantom, "python": Python, "if": If, "choice": Choice, "merge": Merge, "timer": Timer, "iterator": Iterator, "signal": Signal, "slot": Slot, "nethod": Nethod, "call": Call, "return": Return, "raise": Raise, "out": Out, "in": In, "task": Task, "invoke": Invocation, "result": Result, "fail": Fail, "spawn": Spawn, "terminate": Terminate, "gadget": Socket, "frag": Fragment, "comment": Comment}
linkmap = {"clears": Link.Clear, "reads": Link.Read, "takes": Link.Take, "gives": Link.Give, "writes": Link.Write}
