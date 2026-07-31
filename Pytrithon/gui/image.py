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
      if len(token.shape) == 3 and token.shape[2] == 3:
        channels = QImage.Format_RGB888
      elif len(token.shape) == 3 and token.shape[2] == 4:
        channels = QImage.Format_RGBA8888
      else:
        print("Unsupported image depth in '{}'".format(self.name), file=sys.stderr, hide=True)
        return
      self.image = QImage(token.data, w, h, channels)
      self.repaint()
    elif alias == "size":
      self.window.sizeHint = lambda: QSize(token[0], token[1])
      self.sizeHint = lambda: QSize(token[0], token[1])
      self.setFixedWidth(token[0])
      self.setFixedHeight(token[1])
      self.resize(token[0], token[1])
      self.adjustSize()
      self.window.adjustSize()

  def paintEvent(self, event):
    if self.image is not None:
      painter = QPainter(self)
      painter.drawImage(self.rect(), self.image, self.image.rect())
