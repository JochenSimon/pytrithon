import re
from .transition import Transition
from ..pml import parselinks
from ..pytriontology import *
from ..utils import sanitize

matcher = r"^(\w+) *= *\[(\w+) +for +(\w+) +in +(\w+)\]$"

class Iterator(Transition):
  type = "iterator"

  def init(self):
    for link in self.links:
      link.connect(self)
    self.setup()  
    self.sequence = None
    self.towork = -1
    self.result = None
    self.inputavailable = False
    self.available = False
    self.hasroom = False
    self.outputroom = False

  def setup(self):  
    try:
      self.output, self.new, self.old, self.input = re.match(matcher, sanitize(self.inscr)).groups()  
    except AttributeError:
      self.output, self.new, self.old, self.input = "res", "new", "old", "seq"

  def offer(self, link):
    if link.alias.startswith("*"):
      alias = link.alias[1:]
    else:
      alias = link.alias
    if link in self.takes:
      if alias == self.input:
        self.inputavailable = True
        if self.sequence is None:
          self.parent.core.ready(self)
      elif alias == self.new:
        self.available = True
        self.parent.core.ready(self)
    if link in self.gives:
      if alias == self.output:
        self.outputroom = True
        if self.towork == 0:
          self.parent.core.ready(self)
      elif alias == self.old:
        self.hasroom = True
        if self.sequence is not None:
          self.parent.core.ready(self)

  def retract(self, link):
    if link.alias.startswith("*"):
      alias = link.alias[1:]
    else:
      alias = link.alias
    if link in self.takes:
      if alias == self.input:
        self.inputavailable = False
        if self.sequence is None:
          self.parent.core.doze(self)
      elif alias == self.new:
        self.available = False
        if not self.hasroom:
          self.parent.core.doze(self)
    if link in self.gives:
      if alias == self.output:
        self.outputroom = False
      elif alias == self.old:
        self.hasroom = False
        self.parent.core.doze(self)

  def collect(self):  
    return set()

  def distribute(self):  
    return set()
        
  def fire(self):
    for link in self.links:
      if link.alias.startswith("*"):
        total = True
        alias = link.alias[1:]
      else:
        total = False
        alias = link.alias
      if self.sequence is None and self.inputavailable:
        if alias == self.input:
          self.sequence = []
          if total:
            self.sequence = list(t for t in self.parent[link.place].takeall())
          else:  
            self.sequence = list(self.parent[link.place].take())
          self.towork = len(self.sequence)
          self.result = []
          break
      elif self.available:
        if alias == self.new:
          self.result.append(self.parent[link.place].take())
          self.towork -= 1
          break
      elif self.sequence is not None and self.towork == 0:
        if alias == self.output:
          if self.outputroom:
            if all(r == () for r in self.result):
              if total:
                self.parent[link.place].giveall(tuple([()]))
              else:
                self.parent[link.place].give(())
            else:
              if total:
                self.parent[link.place].giveall(tuple(r for r in self.result))
              else:
                self.parent[link.place].give(tuple(self.result))
            if not self.inputavailable:
              self.parent.core.doze(self)
            self.sequence = None
            break
          else:
            self.parent.core.doze(self)
            break
      elif self.hasroom:
        if alias == self.old:
          if self.sequence:
            self.parent[link.place].give(self.sequence.pop(0))
          else:
            self.parent.core.doze(self)
          break
      else:
        assert False, "fifth case in elif chain"
    self.parent.core.places_changed({self.parent[l.place] for l in self.takes + self.gives + self.writes})

  def delete_link(self, link):
    self.links.remove(link)
    if link.alias.startswith("*"):
      alias = link.alias[1:]
    else:
      alias = link.alias
    if alias == self.output:
      self.outputroom = False
    elif alias == self.new:
      self.available = False
    elif alias == self.old:
      self.hasroom = False
    elif alias == self.input:
      self.inputavailable = False

  def create_links(self, inscr):
    links, self.inscr, _ = parselinks(inscr)
    self.setup()    
    for hidden in [link for link in self.links if link.hidden == True]:
      self.links.remove(hidden)
      if hidden.alias.startswith("*"):
        alias = hidden.alias[1:]
      else:
        alias = hidden.alias
      if alias == self.output:
        self.outputroom = False
      elif alias == self.new:
        self.available = False
      elif alias == self.old:
        self.hasroom = False
      elif alias == self.input:
        self.inputavailable = False
    for kind,alias,place,hidden in links:
      link = Link(self.parent, linkmap[kind], alias, place, hidden)
      link.connect(self)
      self.links.append(link)
      if self.parent[link.place].offers(link):
        if link.alias.startswith("*"):
          alias = link.alias[1:]
        else:
          alias = link.alias
        if alias == self.output:
          self.outputroom = True
        elif alias == self.new:
          self.available = True
        elif alias == self.old:
          self.hasroom = True
        elif alias == self.input:
          self.inputavailable = True
    if self.sequence is None and self.inputavailable:
      self.parent.core.ready(self)
