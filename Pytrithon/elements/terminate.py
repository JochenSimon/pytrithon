import sys
from time import sleep
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Terminate(Transition):
  type = "terminate"

  def fire(self):
    if not sanitize(self.inscr) or santitize(self.inscr) == "agent":
      self.parent.core.nexus.send(TerminatedAgent("", self.parent.name))
    elif sanitize(self.inscr) == "total":
      self.parent.core.nexus.send(TerminatedTotal(""))
    elif sanitize(self.inscr) == "local":
      self.parent.core.nexus.send(TerminatedLocal())
    else:
      print("Illegal inscription in terminate '{}'".format(self.name), file=sys.stderr, hide=True)
      return
    sleep(0.1)  
    sys.exit(0)
