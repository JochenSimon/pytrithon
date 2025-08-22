from collections.abc import Iterable
from PyQt5.QtWidgets import *
from .gadget import Gadget

class PushButtonGroup(Gadget, QWidget):
  def __init__(self, text=None, enabled=None, count=None, column=False, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)
    self.count = count if count is not None else len(text)
    self.column = column
    self.text = list(text) if text is not None else [""]*self.count
    if enabled in (True, False):
      self.enabled = [enabled]*self.count
    else:  
      self.enabled = [bool(en) for en in enabled] if enabled is not None else [True]*self.count
    self.widgets = []
    self.inhibited = False
    self.layout = QVBoxLayout() if self.column else QHBoxLayout()
    self.setLayout(self.layout)
    for i in range(self.count):
      self.widgets.append(QPushButton(self.text[i]))
    for i,widget in enumerate(self.widgets):
      self.layout.addWidget(widget)
      widget.clicked.connect(lambda c,i=i: self.clicked_(i,c))
    for enabled,widget in zip(self.enabled, self.widgets):  
      widget.setEnabled(enabled)

  def update(self, alias, token):
    if isinstance(token, Iterable):
      assert len(token) == len(self.text), "wrong input to " + self.socket.name
    else:
      token = [token]*self.count
    if alias == "enabled":
      for i,(tok,widget) in enumerate(zip(token, self.widgets)):
        self.enabled[i] = bool(tok)
        widget.setEnabled(self.enabled[i] and not self.inhibited)
    elif alias == "text":
      for i,(tok,widget) in enumerate(zip(token, self.widgets)):
        text = str(tok)
        self.text[i] = text
        widget.setText(text)

  def inhibition(self, inhibited, alias):
    if alias == "clicked":
      self.inhibited = inhibited
      for i,(enabled,widget) in enumerate(zip(self.enabled, self.widgets)):
        widget.setEnabled(self.enabled[i] and not self.inhibited)

  def clicked_(self, index, checked):
    self.socket.put("clicked", self.text[index])
