import re
import sys
from traceback import extract_tb, format_list, format_exception_only
from collections import OrderedDict
from itertools import count
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

def restore_cursor():
  QApplication.restoreOverrideCursor()

def wait_cursor():
  QApplication.setOverrideCursor(Qt.BusyCursor)
  QTimer.singleShot(200, restore_cursor)

linker = r"^(clears|reads|takes|gives|writes): *(.*)$"
matcher = r"^(?:(.*?) )?\((.+,.+)\)$"

def format_error(element, code, check, exc_type, exc, exc_tb):
  eledesc = '{} "{}"'.format(element.__class__.__name__, element.name)
  error = 'Traceback (most recent call last):\n'
  for tb in extract_tb(exc_tb)[1:]:
    if tb[0] == check:
      error += '  {}, line {}, in "{}"\n    {}\n'.format(eledesc, tb[1], element.parent.name, code.split('\n')[tb[1]-1])
    else:
      error += "\n".join(format_list([tb]))
  if issubclass(exc_type, SyntaxError):
    error += '  {}, line {}, in "{}"\n    {}\n'.format(eledesc, exc.lineno, element.parent.name, exc.text)
    error += ' ' * (exc.offset + 3) + '^\n'
    error += '{}: {}\n'.format(exc_type.__name__, exc.msg)
  else:
    error += "\n".join(format_exception_only(exc_type, exc))
  return error


def sanitize(inscr):
  return "\n".join(line for line in inscr.split("\n") if not re.match(linker, line))

def renamekey(dict, oldkey, newkey):
  updated = OrderedDict()
  for key, value in dict.items():
    if key == oldkey:
      updated[newkey] = value
    else:
      updated[key] = value
  dict.clear()    
  dict.update(updated)    

def flood(elements, links, trans=None):
  changes = {old: "#{}".format(count) for old, count in zip((num for num in elements if "#" in num), count(1))}
  updated = OrderedDict()
  for key, value in elements.items():
    updated[changes.get(key, key)] = value
    value.name = changes.get(key, key)
  elements.clear()
  elements.update(updated)
  for link in links:
    link.trans = changes.get(link.trans, link.trans)
  if trans:
    return changes.get(trans, trans)

def purgekeys(dict, keys):
  for key in keys:
    if key in dict:
      del dict[key]

class Enum(frozenset):
  def __new__(cls, iterable):
    return frozenset.__new__(cls, iterable)

  def __init__(self, iterable):
    self.sorted_values = tuple(sorted(iterable))

  def __iter__(self):
    return self.sorted_values.__iter__()

  def __contains__(self, enum):
    return isinstance(enum, EnumValue) and frozenset.__contains__(self, enum)

class EnumValue(int):
  def __new__(cls, klass, name, value):
    return int.__new__(cls, value)

  def __init__(self, klass, name, value):
    self.klass = klass
    self.name = name

  def __repr__(self):
    return "{}.{}.{}: {}".format(self.klass.__module__,
                                 self.klass.__name__,
                                 self.name,
                                 self.__int__())

  def __str__(self):
    return "{}.{}: {}".format(self.klass.__name__, self.name, self.__int__())

def WithEnum(enumstring, **kwenums):
  def enumize(klass):
    assert not hasattr(klass, "enum")
    enumlist = []
    for value,name in (list(enumerate(enumstring.replace(",", " ").split())) +
                       list((value,name) for (name,value) in kwenums.items())):
      assert not hasattr(klass, name)
      enum_value = EnumValue(klass, name, value)
      setattr(klass, name, enum_value)
      enumlist.append(enum_value)
    enum = Enum(enumlist)
    klass.enum = enum
    return klass
  return enumize
