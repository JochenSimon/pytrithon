from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class Label(Gadget, QLabel):
  def __init__(self, text="", align="left", fontsize=None, **kwargs):
    Gadget.__init__(self, **kwargs)
    QLabel.__init__(self, text)
    if fontsize is not None:
      self.setStyleSheet("font-size: {}px".format(fontsize))
    if align == "center":
      self.setAlignment(Qt.AlignCenter)
    elif align == "right":
      self.setAlignment(Qt.AlignRight)
    self.inhibited = False

  def update(self, alias, token):
    if alias == "text":
      self.setText(str(token))
