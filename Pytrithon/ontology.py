from collections.abc import Iterable, Mapping
from more_itertools import one
from .pml import parse

def issubclass_(type_, class_):
  try:
    return issubclass(type_, class_)
  except TypeError:
    return False

class classproperty:
  def __init__(self, fget):
    self.fget = fget
  def __get__(self, owner_self, owner_cls):
    return self.fget(owner_cls)

class Any:
  def __init__(self, concept):
    self.concept = concept
  def __eq__(self, other):
    return isinstance(other, self.concept)
  def __repr__(self):
    return self.concept.__name__ + ".any"
  def __str__(self):
    return self.__repr__()

class Concept:
  def __init__(self, *args):
    if "_allslots" not in self.__class__.__dict__:
      self.__class__._allslots = []
      for klass in reversed(self.__class__.__mro__):
        if not issubclass(klass, Concept) or klass == Concept:
          continue
        if "_slots" in klass.__dict__:
          for slot in klass._slots:
            assert slot[0] not in {sl[0] for sl in self.__class__._allslots}, \
                "concept {} inherited duplicate slot".format(self.__class__.__name__)
            self.__class__._allslots.append(slot)
    assert len(args) <= len(self.__class__._allslots), \
        "too many arguments for concept {}".format(self.__class__.__name__)
    args += tuple(None for _ in range(len(self.__class__._allslots) - len(args)))
    for i,arg in enumerate(args):
      if isinstance(self._allslots[i][1], list):
        assert isinstance(arg, list), \
            "slot {} of {} not of type {}".format(self._allslots[i][0], self.__class__.__name__, self._allslots[i][1])
        if one(self._allslots[i][1]) == float:
          arg = [float(a) if isinstance(a, int) else a for a in arg]
        assert all(isinstance(a, one(self._allslots[i][1])) for a in arg), \
            "slot {} of {} not of type {}".format(self._allslots[i][0], self.__class__.__name__, self._allslots[i][1])
      elif isinstance(self._allslots[i][1], set):
        assert isinstance(arg, set), \
            "slot {} of {} not of type {}".format(self._allslots[i][0], self.__class__.__name__, self._allslots[i][1])
        if one(self._allslots[i][1]) == float:
          arg = {float(a) if isinstance(a, int) else a for a in arg}
        assert all(isinstance(a, one(self._allslots[i][1])) for a in arg), \
            "slot {} of {} not of type {}".format(self._allslots[i][0], self.__class__.__name__, self._allslots[i][1])
      else:
        if self._allslots[i][1] == float and isinstance(arg, int):
          arg = float(arg)
        assert isinstance(arg, self._allslots[i][1]) or arg is None, \
            "slot {} of {} not of type {}".format(self._allslots[i][0], self.__class__.__name__, self._allslots[i][1])
      setattr(self, self._allslots[i][0], arg)
  def __hash__(self):
    return (self.__class__.__name__, tuple(getattr(self, self._allslots[i][0]) for i in range(len(self._allslots)))).__hash__()
  def __eq__(self, other):
    if isinstance(other, Concept):
      return (self.__class__.__name__, tuple(getattr(self, self._allslots[i][0]) for i in range(len(self._allslots)))) == (other.__class__.__name__, tuple(getattr(other, other._allslots[i][0]) for i in range(len(other._allslots))))
    elif isinstance(other, Any):
      return isinstance(self, other.concept)
    else:
      return False
  def __repr__(self):
    return "{}({})".format(self.__class__.__name__,
        ", ".join(repr(getattr(self, slot[0])) for slot in self._allslots))
  def __str__(self):
    slots = []
    for slot,typ in self._allslots:
      if isinstance(typ, list) or issubclass_(typ, list):
        slots += ["[" + ", ".join([str(item) for item in getattr(self, slot)]) + "]"]
      elif isinstance(typ, set) or issubclass_(typ, set):
        slots += ["{" + ", ".join([str(item) for item in getattr(self, slot)]) + "}"]
      else:
        slots += [str(getattr(self, slot))]
    return "{}({})".format(self.__class__.__name__, ", ".join(slots))
  def __setattr__(self, name, value):
    assert name in {sl[0] for sl in self._allslots}, name + " not in slots"
    slotdict = dict(self._allslots)
    if isinstance(slotdict[name], list):
      assert isinstance(value, list), \
          "slot {} of {} not of type {}".format(name, self.__class__.__name__, slotdict[name])
      if one(slotdict[name]) == float:
        value = [float(v) if isinstance(v, int) else v for v in value]
      assert all(isinstance(v, one(slotdict[name])) for v in value), \
          "slot {} of {} anot of type {}".format(name, self.__class__.__name__, slotdict[name])
    elif isinstance(slotdict[name], set):
      assert isinstance(value, set), \
          "slot {} of {} not of type {}".format(name, self.__class__.__name__, slotdict[name])
      if one(slotdict[name]) == float:
        value = {float(v) if isinstance(v, int) else v for v in value}
      assert all(isinstance(v, one(slotdict[name])) for v in value), \
          "slot {} of {} not of type {}".format(name, self.__class__.__name__, slotdict[name])
    else:
      if slotdict[name] == float and isinstance(value, int):
        value = float(value)
      assert isinstance(value, slotdict[name]) or value is None, \
          "slot {} of {} not of type {}".format(name, self.__class__.__name__, slotdict[name])
    self.__dict__[name] = value
  @classproperty  
  def __match_args__(cls):
    return tuple(slot[0] for slot in cls._allslots)
  def __getstate__(self):
    if "_slots" in self.__class__.__dict__:
      return self.__dict__, self.__class__._slots, self.__class__._allslots
    else:  
      return self.__dict__, [], self.__class__._allslots
  def __setstate__(self, state):
    dict, slots, allslots = state
    super(Concept, self).__setattr__("__dict__", dict)
    if slots:
      setattr(getattr(self, "__class__"), "_slots", slots)
    setattr(getattr(self, "__class__"), "_allslots", allslots)
  @classproperty
  def any(cls):
    return Any(cls)

def ontologize(suite):
  ontology = ""
  ontnode = parse(suite)
  for node in ontnode.children:
    assert node.slots or node.suite, "missing suite in concept {}".format(name)
    if ontology:
      ontology += "\n"
    ontology += "class {}{}:".format(node.name, node.args or "(Concept)") + (("\n  _slots = {}".format('[("' + '), ("'.join( slot[0] + '", ' + slot[1] for slot in node.slots) + ')]')) if node.slots else "")
    ontology += ("\n  " if node.suite else "") + "\n  ".join(node.suite.split("\n"))
  ontology += "\n"  
  return ontology  

def contains_concept(obj):
  if isinstance(obj, Concept):
    return True
  if isinstance(obj, Mapping):
    for o in obj:
      if contains_concept(obj[o]):
        return True
  if not isinstance(obj, str) and not isinstance(obj, bytes) and isinstance(obj, Iterable):
    for o in obj:
      if contains_concept(o):
        return True
  return False
