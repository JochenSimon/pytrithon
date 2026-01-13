from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class Label(Gadget, QLabel):
  def __init__(self, text="", align="left", fontsize=None, **kwargs):
    Gadget.__init__(self, **kwargs)
    QLabel.__init__(self, text)
    self.fontsize = "font-size: {}px; ".format(fontsize) if fontsize else ""
    self.setStyleSheet(self.fontsize)
    if align == "center":
      self.setAlignment(Qt.AlignCenter)
    elif align == "right":
      self.setAlignment(Qt.AlignRight)
    self.inhibited = False

  def update(self, alias, token):
    if alias == "text":
      self.setText(str(token))
    elif alias == "color":
      self.setStyleSheet(self.fontsize + "color: {}".format(str(token))) 
