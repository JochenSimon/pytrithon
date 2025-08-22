from collections import defaultdict
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class NightMode:
  background = QColor(0,0,0)
  editbackground = QColor(0,23,0)
  haltbackground = QColor(42,0,0)
  secretbackground = QColor(0,0,42)
  fragbackground = QColor(37,37,0)
  consolebackground = QColor(0,0,0)
  consoletext = QColor(255,255,255)
  consoleerror = QColor(255,0,0)
  consolefatal = QColor(255,0,255)
  consolemoni = QColor(0,255,0)
  comment = QColor(255,255,255)
  gradient0 = QColor(23,23,23)
  gradient1 = QColor(120,120,120)
  transborder = [QColor(77,77,77), QColor(200,200,0), QColor(255,0,0), QColor(255,127,0),
                 QColor(0,0,255), QColor(200,200,255), QColor(255,0,255), QColor(255,127,255)]
  arc = QColor(142,142,142)
  inscription = QColor(255,255,255)
  typing = QColor(127,127,127)
  priority = QColor(200,200,200)
  flow = QColor(255,255,255)
  flowtoken = QColor(255,255,255)
  flowempty = QColor(0,0,0)
  alias = QColor(255,255,255)
  aliasbackground = QColor(0,0,0)
  element = defaultdict(lambda: QColor(127,127,127))
  element.update({"self": QColor(0,127,255), "module": QColor(127,0,160), "ontology": QColor(0,255,0), "know": QColor(0,127,255), "pool": QColor(0,177,0), "queue": QColor(0,177,0), "stack": QColor(0,177,0), "heap": QColor(0,177,0), "set": QColor(0,177,0), "phantom": QColor(137,0,137), "if": QColor(127,0,255), "choice": QColor(255,127,0), "merge": QColor(160,255,0), "timer": QColor(255,0,0), "iterator": QColor(127,0,255), "signal": QColor(255,127,0), "slot": QColor(127,255,0), "nethod": QColor(0,255,255), "call": QColor(255,0,255), "return": QColor(127,0,255), "raise": QColor(255,0,0), "out": QColor(255,127,0), "in": QColor(127,255,0), "task": QColor(0,255,255), "invoke": QColor(255,0,255), "result": QColor(127,0,255), "fail": QColor(255,0,0), "spawn": QColor(127,0,255), "terminate": QColor(255,0,0), "frag": QColor(255,255,0)})

class LightMode:
  background = QColor(255,255,255)
  editbackground = QColor(200,255,200)
  haltbackground = QColor(255,200,200)
  secretbackground = QColor(200,200,255)
  fragbackground = QColor(255,255,200)
  consolebackground = QColor(255,255,255)
  consoletext = QColor(0,0,0)
  consoleerror = QColor(255,0,0)
  consolefatal = QColor(255,0,255)
  consolemoni = QColor(0,255,0)
  comment = QColor(0,0,0)
  gradient0 = QColor(111,111,111)
  gradient1 = QColor(255,255,255)
  transborder = [QColor(77,77,77), QColor(200,200,0), QColor(255,0,0), QColor(255,127,0),
                 QColor(0,0,255), QColor(200,200,255), QColor(255,0,255), QColor(255,127,255)]
  arc = QColor(50,50,50)
  inscription = QColor(0,0,0)
  typing = QColor(127,127,127)
  priority = QColor(55,55,55)
  flow = QColor(127,127,127)
  flowtoken = QColor(0,0,0)
  flowempty = QColor(255,255,255)
  alias = QColor(0,0,0)
  aliasbackground = QColor(255,255,255)
  element = defaultdict(lambda: QColor(127,127,127))
  element.update({"self": QColor(0,127,255), "module": QColor(127,0,160), "ontology": QColor(0,255,0), "know": QColor(0,127,255), "pool": QColor(0,177,0), "queue": QColor(0,177,0), "stack": QColor(0,177,0), "heap": QColor(0,177,0), "set": QColor(0,177,0), "phantom": QColor(137,0,137), "if": QColor(127,0,255), "choice": QColor(255,127,0), "merge": QColor(160,255,0), "timer": QColor(255,0,0), "iterator": QColor(127,0,255), "signal": QColor(255,127,0), "slot": QColor(127,255,0), "nethod": QColor(0,255,255), "call": QColor(255,0,255), "return": QColor(127,0,255), "raise": QColor(255,0,0), "out": QColor(255,127,0), "in": QColor(127,255,0), "task": QColor(0,255,255), "invoke": QColor(255,0,255), "result": QColor(127,0,255), "fail": QColor(255,0,0), "spawn": QColor(127,0,255), "terminate": QColor(255,0,0), "frag": QColor(255,255,0)})

def colormix_rgb(*colors):
  red, green, blue = 0, 0, 0
  for color in colors:
    red += color.red()
    green += color.green()
    blue += color.blue()
  return QColor(red // len(colors), green // len(colors), blue // len(colors))

def colormix(*colors):
  hue, saturation, value = 0, 0, 0
  for color in colors:
    if color.hue() != -1:
      hue += color.hue()
    saturation += color.saturation()
    value += color.value()
  return QColor.fromHsv(hue % 360, saturation // len(colors), value // len(colors))
