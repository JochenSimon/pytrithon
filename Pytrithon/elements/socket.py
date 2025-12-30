import sys
import traceback
from .link import Link
from .transition import Transition
from ..pytriontology import *
from ..gui import allgadgets, Gadget
from ..utils import format_error, sanitize

class Socket(Transition):
  type = "gadget"
  istrans = False
  isgadget = True

  @property
  def gadget(self):
    return self._gadget

  @gadget.setter
  def gadget(self, gadget):
    environment = {}
    environment.update({"window": self.parent.core.window})
    environment.update(allgadgets)
    environment.update(self.parent.env)
    try:
      self._gadget = eval(gadget, globals(), environment)
      self._gadget.socket = self
      self._gadget.window = self.parent.core.window
      self._gadget.init()
      self.parent.core.hasgui = True
    except Exception as exc:
      print(format_error(self, gadget, "<string>", type(exc), exc, exc.__traceback__), end="", file=sys.stderr, hide=True)
      print("Corrupt gadget in socket '{}'".format(self.name), file=sys.stderr, hide=True)
      self._gadget = Gadget()
      self._gadget.embed = False

  def init(self):
    for link in self.links:
      link.connect(self)
    self.observed = set()
    self.needs = set()

  def create(self):
    self.gadget = sanitize(self.inscr)
    self.parent.core.window.add_gadget(self._gadget)
    if hasattr(self._gadget, "inhibition"):
      for link in self.gives:
        self._gadget.inhibition(True, link.alias)

  def offer(self, link):
    if link.kind == Link.Give:
      if hasattr(self._gadget, "inhibition"):
        self._gadget.inhibition(False, link.alias)
    elif link.kind is Link.Take:
      if not self.observed:
        self.parent.core.ready(self)
      self.observed.add(link)
    elif link.kind in (Link.Read, Link.Write):
      if link.alias and link.alias[0] == "*":
        self._gadget.update(link.alias[1:], [t for t in self.parent[link.place].readall()])
      else:  
        self._gadget.update(link.alias, self.parent[link.place].read())

  def retract(self, link):
    if link.kind == Link.Give:
      if hasattr(self._gadget, "inhibition"):
        self._gadget.inhibition(True, link.alias)
    elif link.kind is Link.Take:
      self.observed.discard(link)
      if not self.observed:
        self.parent.core.doze(self)

  def outputs(self, alias):
    return alias in {link.alias for link in self.gives + self.writes}

  def put(self, alias, token):
    links = [link for link in self.gives + self.writes if link.alias == alias]
    if links:
      link, = links
      place = self.parent[link.place]
      if link.kind == Link.Give:
        place.give(token)
      else:
        place.write(token)
      self.parent.core.places_changed({place})

  def collect(self):
    return set()

  def distribute(self):
    return set()

  def fire(self):
    observed = {o for o in self.observed}
    for link in observed:
      if link.kind is Link.Take:
        if link.alias and link.alias[0] == "*":
          self._gadget.update(link.alias[1:], [t for t in self.parent[link.place].takeall()])
        else:
          self._gadget.update(link.alias, self.parent[link.place].take())
    self.parent.core.places_changed({self.parent[l.place] for l in self.takes})
