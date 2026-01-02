import sys
from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .. import __version__
from ..pytriontology import *

class Window(QDialog):
  def __init__(self, core):
    super().__init__()
    self.core = core
    self.embed = False
    self.quit_on_close = False

    self.widgets = []

    self.setWindowTitle("Pytrithon v" + __version__)
    self.setWindowIcon(QIcon("../icon.png"))
    self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    self.layout = QGridLayout(self)

    self.row = 0

  def init(self):
    pass

  def sizeHint(self):
    return QSize(480, 64)
  
  def add_gadget(self, gadget):
    self.widgets.append(gadget)
    if gadget.embed:
      if gadget.row is None:
        rows = [g.row for g in self.widgets if g.row is not None]
        gadget.row = max(rows) + 1 if rows else 0
      self.layout.addWidget(gadget, gadget.row, gadget.col, gadget.rows, gadget.cols)
    self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
    elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
      for widget in self.widgets:
        if hasattr(widget, "focus") and widget.focus() or hasattr(widget, "isdefault") and widget.isdefault:
          widget.keyPressEvent(event)
    else:
      QDialog.keyPressEvent(self, event)

  def closeEvent(self, event):
    if hasattr(self, "socket"):
      self.socket.put("closed", ())
    if self.quit_on_close:
      if self.quit_on_close == "agent" or self.quit_on_close is True:
        self.core.nexus.send(TerminatedAgent("", self.parent.name))
      elif self.quit_on_close == "total":
        self.core.nexus.send(TerminatedTotal(""))
      elif self.quit_on_close == "local":
        self.core.nexus.send(TerminatedLocal())
      else:
        print("Illegal value for window.quit_on_close", file=sys.stderr, hide=True)
        return
      sleep(0.1)
      sys.exit(0)  
  
  def __str__(self):
    return 'Window("{}")'.format(self.windowTitle())
