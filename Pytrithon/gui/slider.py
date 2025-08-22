from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from .gadget import Gadget

class Slider(Gadget, QSlider):
  def __init__(self, vertical=False, min=0, max=10, step=1, **kwargs):
    Gadget.__init__(self, **kwargs)
    QSlider.__init__(self, Qt.Vertical if vertical else Qt.Horizontal)
    self.setMinimum(int(min//step))
    self.setMaximum(int(max//step))
    self.setSingleStep(1)
    self.setTickPosition(QSlider.TicksBelow)
    self.step = step
    self.valueChanged.connect(self.valueChanged_)

  def valueChanged_(self):
    self.socket.put("value", self.value() * self.step)
