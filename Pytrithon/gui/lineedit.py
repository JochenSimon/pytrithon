from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class LineEdit(Gadget, QLineEdit):
  def __init__(self, text="", clear=False, reselect=True, history=False, enabled=True, focus=False, tooltip="", **kwargs):
    Gadget.__init__(self, **kwargs)
    QLineEdit.__init__(self, text)
    self.clear = clear
    self.reselect = reselect
    self.history = [] if history else None
    self.historyindex = 0
    self.enabled = enabled
    self.dofocus = focus
    self.tooltip = tooltip
    self.inhibited = False
    self.setEnabled(self.enabled)
    self.setToolTip(self.tooltip)
    self.returnPressed.connect(self.returnPressed_)

  def update(self, alias, token):
    if alias == "enable":
      self.enabled = bool(token)
      self.setEnabled(self.enabled and not self.inhibited)
      if self.dofocus:
        self.setFocus()
    elif alias == "text":
      self.setText(str(token))
  
  def inhibition(self, inhibited, alias):
    if alias == "return":
      self.inhibited = inhibited
      self.setEnabled(self.enabled and not self.inhibited)
      if not self.inhibited:
        self.setFocus()
        if self.reselect:
          self.selectAll()

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Up:
      if self.history is not None:
        if self.historyindex < len(self.history):
          self.historyindex += 1
          self.setText(self.history[-self.historyindex])
    elif event.key() == Qt.Key_Down:
      if self.history is not None:
        if self.historyindex > 1:
          self.historyindex -= 1
          self.setText(self.history[-self.historyindex])
    else:      
      super().keyPressEvent(event)      

  def returnPressed_(self):
    if self.history is not None:
      self.history.append(self.text())
      self.historyindex = 1
    for widget in self.window.widgets:
      if isinstance(widget, QPushButton):
        if widget.isDefault():
          widget.setFocus()
    self.socket.put("return", self.text())
    if self.clear:
      self.setText("")
