import sys
import yaml
import traceback
from .base import Element
from ..stringify import stringify_meta
from ..ontology import Concept, ontologize
from ..utils import format_error

class Meta(Element):
  type = "meta"
  ismeta = True
  def __init__(self, inscription, args, pos):
    super().__init__(args, pos)
    self.inscr = inscription

  def create_links(self, inscr):
    self.inscr = inscr

  def __str__(self):
    return stringify_meta(self)

class Self(Meta):
  type = "self"
  def init(self):
    try:
      config = yaml.safe_load(self.inscr)
      if config and "secret" in config:
        self.parent.core.secret = config["secret"]
      if config and "mute" in config:
        self.parent.core.mute = config["mute"]
      if config and "errors" in config:
        self.parent.core.errors = config["errors"]
      if config and "delay" in config:
        self.parent.core.delay = config["delay"]
      if config and "poll" in config:
        self.parent.core.poll = config["poll"]
      if config and "timeout" in config:
        self.parent.core.timeout = config["timeout"]
      if config and "domain" in config:
        self.parent.core.domain = config["domain"]
    except Exception as exc:
      print(format_error(self, self.inscr, "<string>", type(exc), exc, exc.__traceback__), end="", file=sys.stderr, hide=True)
      print("Corrupt self inscription in '{}'".format(self.name), file=sys.stderr, hide=True)

class Module(Meta):
  type = "module"
  def init(self):
    bindings = {}
    bindings.update({"agent": self.parent, "window": self.parent.core.window, "application": self.parent.core.app})
    bindings.update(self.parent.env)
    try:
      exec(compile(self.inscr, "\nModule\n", "exec"), bindings)
    except Exception as exc:
      print(format_error(self, self.inscr, "\nModule\n", type(exc), exc, exc.__traceback__), end="", file=sys.stderr, hide=True)
      print("Corrupt module inscription in '{}'".format(self.name), file=sys.stderr, hide=True)

    for key,value in bindings.items():
      if key not in globals() and key not in ("agent", "window", "application") or key in sys.modules:
        self.parent.env[key] = value

class Ontology(Meta):
  type = "ontology"
  ismeta = True
  def init(self):
    bindings = {}
    bindings.update({"Concept": Concept})
    bindings.update(self.parent.env)
    try:
      exec(compile(ontologize(self.inscr), "\nOntology\n", "exec"), bindings)
    except Exception as exc:
      print(format_error(self, self.inscr, "\nOntology\n", type(exc), exc, exc.__traceback__), end="", file=sys.stderr, hide=True)
      print("Corrupt ontology inscription in '{}'".format(self.name), file=sys.stderr, hide=True)

    for key,value in bindings.items():
      if key not in globals():
        self.parent.env[key] = value
