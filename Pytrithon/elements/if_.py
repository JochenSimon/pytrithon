from .transition import Transition
from .python import ExceptionHandler
from ..utils import sanitize

class If(Transition):
  type = "if"
  def fire(self):
    bindings = {}
    bindings.update(self.parent.env)
    bindings.update(self.bindings)
    with ExceptionHandler(self, sanitize(self.inscr)):
      value = eval(compile(sanitize(self.inscr), "\nIf\n", "eval"), globals(), bindings)
      if value is not None:
        if value:
          for link in self.gives + self.writes:
            if not link.alias:
              self.parent[link.place].give(())
            elif link.alias in bindings:
              self.parent[link.place].give(bindings[link.alias])
        else:
          for link in self.gives + self.writes:
            if link.alias == "~":
              self.parent[link.place].give(())
            elif link.alias and link.alias.startswith("~") and link.alias[1:] in bindings:
              self.parent[link.place].give(bindings[link.alias[1:]])
  
  def distribute(self):
    return {self.parent[p] for p in {l.place for l in self.gives + self.writes}}
