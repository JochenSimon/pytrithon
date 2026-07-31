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
    self.moveable = False
    self.quit_on_close = False
    self.confirm_quit = None
    self.force_close = False

    self.widgets = []
    self.sub_windows = []

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

  def update(self, alias, token):
    if alias == "close":
      self.force_close = True
      self.close()
  
  def moveEvent(self, event):
    if hasattr(self, "socket") and self.socket.outputs("pos"):
      self.socket.put("pos", (self.frameGeometry().left(), self.frameGeometry().top()))

  def mousePressEvent(self, event):
    if self.moveable:
      self.startPos = event.pos()
    super().mousePressEvent(event)

  def mouseMoveEvent(self, event):
    if self.moveable and event.buttons() == Qt.LeftButton:
      delta = event.pos() - self.startPos
      self.move(self.pos() + delta)
      event.accept()
    super().mouseMoveEvent(event)
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
    elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
      if hasattr(self, "socket"):
        if self.socket.outputs("key"):
          self.socket.put("key", event.key())
        if self.socket.outputs("key, mod"):
          self.socket.put("key, mod", (event.key(), event.modifiers()))
      for widget in self.widgets:
        if hasattr(widget, "focus") and widget.focus() or hasattr(widget, "isdefault") and widget.isdefault:
          widget.keyPressEvent(event)
    else:
      if hasattr(self, "socket"):
        if self.socket.outputs("key"):
          self.socket.put("key", event.key())
        if self.socket.outputs("key, mod"):
          self.socket.put("key, mod", (event.key(), event.modifiers()))
      QDialog.keyPressEvent(self, event)

  def closeEvent(self, event):
    if not self.force_close and self.confirm_quit:
      ret = QMessageBox.warning(self, self.confirm_quit[0], self.confirm_quit[1], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
      match ret:
        case QMessageBox.Yes:
          do_quit = True
        case QMessageBox.No:
          do_quit = False
          event.ignore()
    else:
      do_quit = True
    if do_quit:      
      if hasattr(self, "socket"):
        self.socket.put("closed", ())
      if self.quit_on_close:
        if self.quit_on_close == "unseen" and self.core.watchers:
          return
        if self.quit_on_close == "agent" or self.quit_on_close is True:
          pass
        elif self.quit_on_close in {"local", "unseen"}:
          self.core.nexus.send(TerminatedLocal())
        else:
          print("Illegal value for window.quit_on_close", file=sys.stderr, hide=True)
          return
        sleep(0.1)
        sys.exit(0)  
  
  def __str__(self):
    return 'Window("{}")'.format(self.windowTitle())
