import sys
from ..stringify import stringify_transition
from .base import Element
from .link import Link
from ..pml import parselinks
from ..utils import sanitize

linkmap = {"clears": Link.Clear, "reads": Link.Read, "takes": Link.Take, "gives": Link.Give, "writes": Link.Write}

class Transition(Element):
  type = "trans"
  priority = 0
  istrans = True

  def __init__(self, inscription, args, pos):
    super().__init__(args, pos)
    if args.strip():
      self.priority = float(args)
    self.inscr = inscription
    self.links = []
    self.exception = None
    self.errored = False

  @property
  def clears(self):
    return [link for link in self.links if link.kind is Link.Clear]

  @property
  def reads(self):
    return [link for link in self.links if link.kind is Link.Read]

  @property
  def takes(self):
    return [link for link in self.links if link.kind is Link.Take]

  @property
  def gives(self):
    return [link for link in self.links if link.kind is Link.Give]

  @property
  def writes(self):
    return [link for link in self.links if link.kind is Link.Write]
  
  def init(self):
    for link in self.links:
      link.connect(self)
    self.needs = {link for link in self.reads + self.takes + self.gives + self.writes}
    for link in self.gives:
      for clear in self.clears:
        if clear.place == link.place:
          self.needs.discard(link)

  def offer(self, link):
    self.needs.discard(link)
    if not self.needs:
      self.parent.core.ready(self)
  
  def retract(self, link):
    if not self.needs:
      self.parent.core.doze(self)
    self.needs.add(link)

  def changed(self, link):
    pass

  def collect(self):
    self.bindings = {}
    for link in self.clears:
      self.parent[link.place].clear()
    for link in self.reads:
      if "*" in link.alias:
        self.bindings[link.alias[1:]] = [token for token in self.parent[link.place].readall()]
      else:  
        token = self.parent[link.place].read()
        if "," in link.alias:
          for i,alias in enumerate(link.alias.split(",")):
            self.bindings[alias.strip()] = token[i]
        else:
          self.bindings[link.alias] = token
    for link in self.writes + self.takes:
      if link.alias:
        if "*" in link.alias:
          if link.alias[1:]:
            self.bindings[link.alias[1:]] = [token for token in self.parent[link.place].takeall()]
          else:
            self.parent[link.place].takeall()
        else:  
          token = self.parent[link.place].take()
          if "," in link.alias:
            for i,alias in enumerate(link.alias.split(",")):
              self.bindings[alias.strip()] = token[i]
          else:
            self.bindings[link.alias] = token
      else:
        self.parent[link.place].take()
    return {self.parent[p] for p in {l.place for l in self.takes + self.writes}}
  
  def distribute(self):
    for link in self.gives + self.writes:
      if not link.alias:
        self.parent[link.place].give(())
      elif link.alias[0] == "*" and link.alias[1:] in self.bindings:   
        self.parent[link.place].giveall([token for token in self.bindings[link.alias[1:]]])
      elif link.alias in self.bindings:
        self.parent[link.place].give(self.bindings[link.alias])
      elif self.exception is not None and link.alias.strip() == "except":
        self.parent[link.place].give(self.exception)
      elif ',' in link.alias:
        aliases = [a.strip() for a in link.alias.split(",")]
        suppress = False
        if "except" not in aliases:
          for alias in aliases:
            if alias not in self.bindings:
              suppress = True
              break
        else:      
          if self.exception:
            token = [None]*len(aliases)
            for alias in aliases:
              if alias == "except":
                token[aliases.index(alias)] = self.exception
              else:
                token[aliases.index(alias)] = self.bindings[alias] if alias in self.bindings else None
            self.parent[link.place].give(tuple(token) if len(token) > 1 else token[0])
          suppress = True
        if not suppress:
          self.parent[link.place].give(tuple(self.bindings[alias.strip()] for alias in link.alias.split(',')))
    return {self.parent[p] for p in {l.place for l in self.gives + self.writes}}

  def topic(self, inscr=None):
    if inscr is None:
      inscr = self.inscr
    if sanitize(inscr).startswith("."):
      return sanitize(inscr)[1:]
    return self.parent.core.domain + "." + sanitize(inscr) if self.parent.core.domain is not None and "." not in sanitize(inscr) else sanitize(inscr)

  def delete_link(self, link):
    self.links.remove(link)
    if link in self.needs:
      self.needs.discard(link)
      if not self.needs:
        self.parent.core.ready(self)

  def create_links(self, inscr):
    links, self.inscr, errors = parselinks(inscr)
    for hidden in [link for link in self.links if link.hidden == True]:
      self.links.remove(hidden)
      if hidden in self.needs:
        self.needs.discard(hidden)
        if not self.needs:
          self.parent.core.ready(self)
    for kind,alias,place,hidden in links:
      if place in self.parent and self.parent[place].isplace:
        link = Link(self.parent, linkmap[kind], alias, place, hidden)
        link.connect(self)
        self.links.append(link)
        if not self.parent[link.place].offers(link):
          if not self.needs:
            self.parent.core.doze(self)
          self.needs.add(link)
      else:
        print("Illegal link from '{}' to wrong element '{}'".format(self.name, place), file=sys.stderr, hide=True)
    if errors:
      print("\n".join(e+" in element '{}'".format(self.name) for e in errors), file=sys.stderr, hide=True)

  def __str__(self):
    return stringify_transition(self)
