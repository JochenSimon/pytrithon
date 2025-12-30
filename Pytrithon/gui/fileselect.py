from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class FileSelect(Gadget, QPushButton):
  def __init__(self, text="", enabled=True, binary=False, filetype="(*.*)", **kwargs):
    Gadget.__init__(self, **kwargs)
    QPushButton.__init__(self, text)
    self.enabled = enabled
    self.binary = binary
    self.inhibited = False
    self.clicked.connect(self.clicked_)
    self.pick_dialog = QFileDialog(self, text)
    self.pick_dialog.setFileMode(QFileDialog.ExistingFiles)
    self.pick_dialog.setAcceptMode(QFileDialog.AcceptOpen)
    self.pick_dialog.setNameFilter(filetype)

  def clicked_(self, checked):
    if self.pick_dialog.exec():
      file = self.pick_dialog.selectedFiles()[0]
      self.socket.put("file", file)
      if self.socket.outputs("read"):
        with open(file, "rb" if self.binary else "r", **{} if self.binary else {"encoding": "utf-8"}) as f:
          self.socket.put("read", f.read())
