import re
import sys
from .transition import Transition
from ..pytriontology import *
from ..utils import sanitize

class Spawn(Transition):
  type = "spawn"
  def fire(self):
    agent = self.bindings["agent"] if "agent" in self.bindings else ""
    dest = self.bindings["dest"] if "dest" in self.bindings else "(local)"
    args = self.bindings["args"] if "args" in self.bindings else ""
    delay = self.bindings["delay"] if "delay" in self.bindings else None
    edit = self.bindings["edit"] if "edit" in self.bindings else False
    halt = self.bindings["halt"] if "halt" in self.bindings else False
    secret = self.bindings["secret"] if "secret" in self.bindings else False
    mute = self.bindings["mute"] if "mute" in self.bindings else False
    errors = self.bindings["errors"] if "errors" in self.bindings else True

    if not isinstance(agent, str) or not agent or re.sub(r"[\w]", "", agent):
      return print("Illegal agent in spawn '{}'".format(self.name), file=sys.stderr, hide=True)
    if dest != "(local)" and (not isinstance(dest, str) or not dest or re.sub(r"[\w]", "", dest)):
      return print("Illegal dest in spawn '{}'".format(self.name), file=sys.stderr, hide=True)
    if not isinstance(args, str):
      return print("Illegal args in spawn '{}'".format(self.name), file=sys.stderr, hide=True)
    if delay is not None and not isinstance(delay, int):
      return print("Illegal delay in spawn '{}'".format(self.name), file=sys.stderr, hide=True)
    for mode,name in zip([edit, halt, secret, mute, errors], ["edit", "halt", "secret", "mute", "errors"]):
      if not isinstance(mode, bool):
        return print("Illegal {} in spawn '{}'".format(name, self.name), file=sys.stderr, hide=True)

    self.parent.core.nexus.send(OpenAgent(dest, agent, args.split(" ") if args else [], delay, edit, halt, secret, mute, errors)) 
