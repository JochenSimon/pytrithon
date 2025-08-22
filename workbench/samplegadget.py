from PyQt5.QtWidgets import *
from Pytrithon import Gadget

class SampleGadget(Gadget, QComboBox):
  def __init__(self, items=None, enabled=True, **kwargs):
    Gadget.__init__(self, **kwargs)
    QComboBox.__init__(self)
    self.enabled = enabled
    self.inhibited = False
    self.setEnabled(self.enabled)

    for item in items:
      self.addItem(item)

    self.activated.connect(self.activated_)

  def update(self, alias, token):
    if alias == "enable":
      self.enabled = bool(token)
      self.setEnabled(self.enabled and not self.inhibited)
    elif alias == "items":
      self.clear()
      for item in token:
        self.addItem(item)

  def inhibition(self, inhibited, alias):
    if alias == "activated":
      self.inhibited = inhibited
      self.setEnabled(self.enabled and not self.inhibited)

  def activated_(self, index):
    self.socket.put("activated", self.itemText(index))
