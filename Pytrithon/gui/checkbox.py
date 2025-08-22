from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class CheckBox(Gadget, QCheckBox):
  def __init__(self, text="", enabled=True, checked=0, **kwargs):
    Gadget.__init__(self, **kwargs)
    QCheckBox.__init__(self, text)
    self.enabled = enabled
    self.checked = checked
    self.inhibited = False
    self.setCheckState(Qt.Checked if self.checked else Qt.Unchecked)
    self.stateChanged.connect(self.checked_)

  def update(self, alias, token):
    if alias == "enable":
      self.enabled = bool(token)
      self.setEnabled(self.enabled)
    elif alias == "check":
      if token in (True, False):
        self.checked = 2 if token else 0
      else:
        self.checked = token
      self.setCheckState(Qt.Checked if self.checked else Qt.Unchecked)
    elif alias == "text":
      self.setText(str(token))

  def inhibition(self, inhibited, alias):
    if alias == "checked":
      self.inhibited = inhibited
      self.setEnabled(self.enabled and not self.inhibited)

  def checked_(self, checked):
    self.checked = checked
    self.socket.put("checked", checked)
