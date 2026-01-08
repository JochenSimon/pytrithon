import sys
from time import sleep
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Terminate(Transition):
  type = "terminate"

  def fire(self):
    if santitize(self.inscr) == "unseen" and self.parent.core.watchers:
      return
    if not sanitize(self.inscr) or santitize(self.inscr) == "agent":
      self.parent.core.nexus.send(TerminatedAgent("", self.parent.name))
    elif sanitize(self.inscr) in {"local", "unseen"}:
      self.parent.core.nexus.send(TerminatedLocal())
    elif sanitize(self.inscr) == "total":
      self.parent.core.nexus.send(TerminatedTotal(""))
    else:
      print("Illegal inscription in terminate '{}'".format(self.name), file=sys.stderr, hide=True)
      return
    sleep(0.1)  
    sys.exit(0)
