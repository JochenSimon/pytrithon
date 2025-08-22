from collections import defaultdict
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Nethod(Transition):
  type = "nethod"
  nethods = defaultdict(set)
  neth = 1
  origins = {}
  def init(self):
    Nethod.nethods[sanitize(self.inscr)].add(self)
    for link in self.links:
      link.connect(self)
    self.needs = {link for link in self.reads + self.takes}  
    self.rooms = {link for link in self.gives}  

  def pending(self):  
    if not self.needs:
      self.parent.core.ready(self)
  
  def blocked(self):  
    self.parent.core.doze(self)

  def offer(self, link):
    if link in self.reads + self.takes:
      self.needs.discard(link)
      if not self.needs and Call.calls[sanitize(self.inscr)].hasroom:
        self.parent.core.ready(self)
    elif link in self.gives:
      self.rooms.discard(link)
      if not self.rooms:
        Return.returns[sanitize(self.inscr)].pending()
    else:
      assert False, "illegal write in nethod"
  
  def retract(self, link):
    if link in self.reads + self.takes:
      if not self.needs or Call.calls[sanitize(self.inscr)].hasroom:
        self.parent.core.doze(self)
      self.needs.add(link)
    elif link in self.gives:
      self.rooms.add(link)
    else:
      assert False, "illegal write in nethod"

  def fire(self):
    Nethod.origins[Nethod.neth] = self
    self.bindings["neth"] = Nethod.neth
    Nethod.neth += 1
    call = Call.calls[sanitize(self.inscr)]
    call.send(self.bindings)

  def send(self, bindings):
    self.bindings = bindings
    self.distribute()
    self.parent.core.places_changed({self.parent[l.place] for l in self.takes + self.gives + self.writes})
  
  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    Nethod.nethods[sanitize(oldinscr)].discard(self)
    Nethod.nethods[sanitize(self.inscr)].add(self)
      
class Call(Transition):
  type = "call"
  calls = {}
  def init(self):
    super().init()
    Call.calls[sanitize(self.inscr)] = self
    self.hasroom = False
  
  def offer(self, link):
    self.needs.discard(link)
    if not self.needs:
      self.hasroom = True
      for nethod in Nethod.nethods[sanitize(self.inscr)]:
        nethod.pending()
      
  def retract(self, link):    
    if not self.needs:
      self.hasroom = False
      for nethod in Nethod.nethods[sanitize(self.inscr)]:
        nethod.blocked()
    self.needs.add(link)    

  def send(self, bindings):
    self.collect()
    bindings.update(self.bindings)
    self.bindings = bindings
    self.distribute()
    self.parent.core.places_changed({self.parent[l.place] for l in self.takes + self.gives + self.writes})

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    del Call.calls[sanitize(oldinscr)]
    Call.calls[sanitize(self.inscr)] = self
      
class Return(Transition):
  type = "return"
  returns = {}
  def init(self):
    Return.returns[sanitize(self.inscr)] = self
    for link in self.links:
      link.connect(self)
    self.needs = {link for link in self.reads + self.takes}  

  def pending(self):
    if not self.needs:
      match = None
      for link in self.takes:
        token = self.parent[link.place].read()
        if "," in link.alias:
          aliases = link.alias.split(",")
          for alias in aliases:
            neth = token[aliases.index(alias.strip())]
        elif link.alias == "neth":
          neth = token
        if match is None:
          match = neth
        if match != neth:  
          assert False, "nonmatching neth"
      if not Nethod.origins[neth].rooms:  
        self.parent.core.ready(self)

  def offer(self, link):
    self.needs.discard(link)
    self.pending()
  
  def retract(self, link):
    if not self.needs:
      self.parent.core.doze(self)
    self.needs.add(link)

  def fire(self):
    Nethod.origins[self.bindings["neth"]].send(self.bindings)

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    del Return.returns[sanitize(oldinscr)]
    Return.returns[sanitize(self.inscr)] = self

class Raise(Return):
  type = "raise"
