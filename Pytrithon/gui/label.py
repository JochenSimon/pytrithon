from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class Label(Gadget, QLabel):
  def __init__(self, text="", center=False, fontsize=None, **kwargs):
    Gadget.__init__(self, **kwargs)
    QLabel.__init__(self, text)
    ss = ""
    if fontsize is not None:
      ss += "font-size: {}px;".format(fontsize)
    if center:
      ss += "qproperty-alignment: AlignCenter;"
    self.setStyleSheet(ss)
    self.inhibited = False

  def update(self, alias, token):
    if alias == "text":
      self.setText(str(token))
