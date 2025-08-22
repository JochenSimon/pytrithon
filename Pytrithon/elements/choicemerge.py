from .transition import Transition
from .python import ExceptionHandler
from ..utils import sanitize

class Choice(Transition):
  type = "choice"
  def fire(self):
    bindings = {}
    bindings.update(self.parent.env)
    bindings.update(self.bindings)
    with ExceptionHandler(self, sanitize(self.inscr)):
      if sanitize(self.inscr):
        value = eval(compile(sanitize(self.inscr), "\nChoice\n", "eval"), globals(), bindings)
      for link in self.gives + self.writes:
        if "->" in link.alias:
          expression, aliases = link.alias.split("->")
          aliases = [alias.strip() for alias in aliases.split(",")]
        else:
          expression = link.alias.strip()
          aliases = []
        token = [bindings[alias] if alias in bindings else () for alias in aliases]
        if sanitize(self.inscr):
          if eval(compile(expression, "\nChoice\n", "eval"), globals(), bindings) == value:
            if token:
              self.parent[link.place].give(token[0] if len(token) == 1 else tuple(token))
            else:
              self.parent[link.place].give(())
        else:      
          if eval(compile(expression, "\nChoice\n", "eval"), globals(), bindings):
            if token:
              self.parent[link.place].give(token[0] if len(token) == 1 else tuple(token))
            else:
              self.parent[link.place].give(())

  def distribute(self):
    return {self.parent[p] for p in {l.place for l in self.gives + self.writes}}

class Merge(Transition):
  type = "merge"
  priority = -0.5

  def init(self):
    for link in self.links:
      link.connect(self)
    self.needs = {link for link in self.gives}
    for link in self.gives:
      for clear in self.clears:
        if clear.place == link.place:
          self.needs.discard(link)
    self.available = set()      

  def offer(self, link):
    if link in self.takes:
      self.available.add(link)
      if not self.needs:
        self.parent.core.ready(self)
    if link in self.gives:
      self.needs.discard(link)

  def retract(self, link):
    if link in self.takes:
      if not self.available:
        self.parent.core.doze(self)
      self.available.discard(link)
    if link in self.gives:
      if not self.needs:
        self.parent.core.doze(self)
      self.needs.add(link)

  def collect(self):
    self.bindings = {}
    for link in self.clears:
      self.parent[link.place].clear()
    for link in self.takes:
      if link in self.available:
        token = self.parent[link.place].take()
        if link.alias:
          self.bindings[link.alias] = token
    return {self.parent[p] for p in {l.place for l in self.takes + self.writes}}

  def fire(self):
    if not self.available:
      self.parent.core.doze(self)
