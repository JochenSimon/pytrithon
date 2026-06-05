from collections import defaultdict
from .transition import Transition
from ..ontology import contains_concept
from ..pytriontology import *
from ..utils import sanitize

class Event(Transition):
  type = "event"
  sensors = defaultdict(set)
  def init(self):
    super().init()
    Event.sensors[sanitize(self.inscr)].add(self)
  
  def offer(self, link):
    self.needs.discard(link)
    if not self.needs and self.parent.core.events[sanitize(self.inscr)]:
      self.parent.core.ready(self)
      
  def retract(self, link):    
    if not self.needs:
      self.parent.core.doze(self)
    self.needs.add(link)    

  def pending(self):
    if not self.needs and self.parent.core.events[sanitize(self.inscr)]:
      self.parent.core.ready(self)

  def fire(self):
    self.bindings.update({a:o for a,o in self.parent.core.events[sanitize(self.inscr)].pop(0).items()})
    if not self.parent.core.events[sanitize(self.inscr)]:
      self.parent.core.doze(self)

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    Event.sensors[sanitize(oldinscr)].discard(self)
    Event.sensors[sanitize(self.inscr)].add(self)
    self.parent.core.nexus.send(RegisterListeners("", {Listener(self.parent.agentname, "event", sanitize(self.inscr), sanitize(oldinscr))}))
