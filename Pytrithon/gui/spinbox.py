from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class SpinBox(Gadget, QSpinBox):
  def __init__(self, value=0, range=(0,1000), step=1, reselect=True, enabled=True, focus=False, **kwargs):
    Gadget.__init__(self, **kwargs)
    QSpinBox.__init__(self)
    self.reselect = reselect
    self.enabled = enabled
    self.dofocus = focus
    self.setRange(*range)
    self.setSingleStep(step)
    self.setValue(value)
    self.setEnabled(self.enabled)
    self.valueChanged.connect(self.value_changed)

  def update(self, alias, token):
    if alias == "enable":
      self.enabled = bool(token)
      self.setEnabled(self.enabled)
      if self.enabled:
        if self.dofocus:
          self.setFocus()
        if self.reselect:
          self.selectAll()
    elif alias == "range":
      if len(token) == 3:
        self.setRange(token[0], token[2])
        self.setValue(token[1])
      else:
        self.setRange(*token)
  
  def value_changed(self, value):
    self.socket.put("value", self.value())
