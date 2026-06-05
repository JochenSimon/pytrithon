from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class ListWidget(Gadget, QListWidget):
  def __init__(self, items=None, **kwargs):
    self.qrow = self.row
    Gadget.__init__(self, **kwargs)
    QLineEdit.__init__(self)
    self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    if items is None:
      items = []
    self.items = items
    for item in self.items:
      self.addItem(item)

  def sizeHint(self):
    return QSize(128, 0)

  def update(self, alias, token):
    if alias == "items":
      for item in self.items:
        items = self.findItems(item, Qt.MatchExactly)
        if items:
          self.takeItem(self.qrow(items[0]))
      self.items = token
      for item in self.items:
        self.addItem(item)
