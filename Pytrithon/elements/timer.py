import time
from math import floor
from PyQt5.QtCore import QTimer
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Timer(Transition):
  type = "timer"

  def __init__(self, inscription, args, pos):
    super().__init__(inscription, args, pos)
    self.last = None

  def delay(self, inscr):  
    delay = inscr
    if delay.endswith("ms"):
      return int(delay[:-2])
    elif delay.endswith("s"):
      return int(float(delay[:-1]) * 1000)
    elif delay.endswith("m"):
      return int(float(delay[:-1]) * 1000 * 60)
    elif delay.endswith("h"):
      return int(float(delay[:-1]) * 1000 * 60 * 60)
    else:
      return 1000

  def distribute(self):
    return set()

  def fire(self):
    if "delay" in self.bindings:
      delay = self.bindings["delay"]
      if isinstance(delay, str):
        delay = self.delay(delay)
      elif isinstance(delay, int):
        delay = self.delay(str(delay)+"ms")
      else:
        delay = self.delay(sanitize(self.inscr))
    else:  
      if sanitize(self.inscr).endswith("hz"):
        rate = int(sanitize(self.inscr)[:-2])
        if self.last is None:
          delay = 0
        else:
          delay = max(0, floor((1 / rate - (time.perf_counter() - self.last)) * 1000))
      else:    
        delay = self.delay(sanitize(self.inscr))
    QTimer.singleShot(delay, lambda bin=self.bindings: self.elapse(bin))
    self.parent.core.doze(self)

  def elapse(self, bindings):
    if sanitize(self.inscr).endswith("hz"):
      self.last = time.perf_counter()
    self.bindings = bindings
    super().distribute()
    if not self.needs:
      self.parent.core.ready(self)
    self.parent.core.places_changed({self.parent[l.place] for l in self.gives + self.writes})
