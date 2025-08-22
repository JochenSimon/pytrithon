import sys
from traceback import extract_tb, format_list, format_exception_only
from .transition import Transition
from ..utils import format_error, sanitize
from ..pytriontology import *

class Python(Transition):
  type = "python"

  def fire(self):
    bindings = {"Break": Break}
    bindings.update(self.parent.env)
    bindings.update(self.bindings)
    self.bindings = bindings

    code = sanitize(self.inscr)

    self.exception = None

    with ExceptionHandler(self, code):
      exec(compile(code, '\nPython\n', 'exec'), self.bindings)

class ExceptionHandler:
  def __init__(self, element, code, err=None):
    self.element = element
    self.code = code
    self.err = err if err else sys.stderr
    
  def __enter__(self): pass
  def __exit__(self, exc_type, exc, exc_tb):
    if exc_type:
      if not isinstance(exc, Break):
        self.element.exception = exc
        self.err.write(format_error(self.element, self.code, "\nPython\n", exc_type, exc, exc_tb), hide=True)
        if self.element.parent.core.watchers and not self.element.errored and not self.element.parent.isfrag:
          self.element.parent.core.nexus.send(TransitionErrored(self.element.parent.name, self.element.parent.core.watchers, self.element.name, True))
          self.element.errored = True
    else:
      if self.element.parent.core.watchers and self.element.errored and not self.element.parent.isfrag:
        self.element.parent.core.nexus.send(TransitionErrored(self.element.parent.name, self.element.parent.core.watchers, self.element.name, False))
        self.element.errored = False
    return True

class Break(Exception):
  pass
