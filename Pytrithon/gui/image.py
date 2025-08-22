from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from .gadget import Gadget

class Image(Gadget, QWidget):
  def __init__(self, width, height, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)
    self.image = None
    self.resize(width, height)
    self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.sizeHint = lambda: QSize(width, height)

  def update(self, alias, token):
    if alias == "image":
      w, h = token.shape[1], token.shape[0]
      self.image = QImage(token.data, w, h, QImage.Format_RGBA8888)
      self.repaint()

  def paintEvent(self, event):
    if self.image is not None:
      painter = QPainter(self)
      painter.drawImage(self.rect(), self.image, self.image.rect())
