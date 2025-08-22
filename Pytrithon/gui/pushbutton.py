from PyQt5.QtWidgets import *
from .gadget import Gadget

class PushButton(Gadget, QPushButton):
  def __init__(self, text="", enabled=True, default=False, **kwargs):
    Gadget.__init__(self, **kwargs)
    QPushButton.__init__(self, text)
    self.enabled = enabled
    self.isdefault = default
    self.inhibited = False
    self.setEnabled(self.enabled)
    self.clicked.connect(self.clicked_)

  def update(self, alias, token):
    if alias == "enable":
      self.enabled = bool(token)
      self.setEnabled(self.enabled and not self.inhibited)
    elif alias == "text":
      text = str(token)
      self.setText(text)

  def inhibition(self, inhibited, alias):
    if alias == "clicked":
      self.inhibited = inhibited
      self.setEnabled(self.enabled and not self.inhibited)

  def clicked_(self, checked):
    self.socket.put("clicked", self.text())
