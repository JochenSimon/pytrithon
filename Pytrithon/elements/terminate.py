import sys
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Terminate(Transition):
  type = "terminate"

  def fire(self):
    if not sanitize(self.inscr):
      self.parent.core.nexus.send(TerminatedAgent("", self.parent.name))
    elif sanitize(self.inscr) == "total":
      self.parent.core.nexus.send(TerminatedTotal(""))
    elif sanitize(self.inscr) == "local":
      self.parent.core.nexus.send(TerminatedLocal())
    else:
      print("Illegal inscription in terminate '{}'".format(self.name), file=sys.stderr)
      return
    sys.exit(0)
