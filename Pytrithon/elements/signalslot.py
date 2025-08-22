from collections import defaultdict
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Signal(Transition):
  type = "signal"
  signals = defaultdict(set)
  def init(self):
    super().init()
    Signal.signals[sanitize(self.inscr)].add(self)

  def offer(self, link):
    self.needs.discard(link)
    if not self.needs and not Slot.noroom[sanitize(self.inscr)]:
      self.parent.core.ready(self)
  
  def retract(self, link):
    if not self.needs and not Slot.noroom[sanitize(self.inscr)]:
      self.parent.core.doze(self)
    self.needs.add(link)

  def room(self, slot):
    Slot.noroom[sanitize(self.inscr)].discard(slot)
    if not self.needs and not Slot.noroom[sanitize(self.inscr)]:
      self.parent.core.ready(self)

  def noroom(self, slot):
    if not self.needs and not Slot.noroom[sanitize(self.inscr)]:
      self.parent.core.doze(self)
    Slot.noroom[sanitize(self.inscr)].add(slot)

  def fire(self):
    for slot in Slot.slots[sanitize(self.inscr)]:
      slot.send(self.bindings)

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    Signal.signals[sanitize(oldinscr)].discard(self)
    Signal.signals[sanitize(self.inscr)].add(self)

class Slot(Transition):
  type = "slot"
  slots = defaultdict(set)
  noroom = defaultdict(set)
  def init(self):
    super().init()
    Slot.slots[sanitize(self.inscr)].add(self)
    Slot.noroom[sanitize(self.inscr)].add(self)
  
  def offer(self, link):
    self.needs.discard(link)
    if not self.needs:
      for signal in Signal.signals[sanitize(self.inscr)]:
        signal.room(self)
      
  def retract(self, link):    
    if not self.needs:
      for signal in Signal.signals[sanitize(self.inscr)]:
        signal.noroom(self)
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
    Slot.slots[sanitize(oldinscr)].discard(self)
    Slot.slots[sanitize(self.inscr)].add(self)
    if self in Slot.noroom[sanitize(oldinscr)]:
      Slot.noroom[sanitize(oldinscr)].discard(self)
      Slot.noroom[sanitize(self.inscr)].add(self)
