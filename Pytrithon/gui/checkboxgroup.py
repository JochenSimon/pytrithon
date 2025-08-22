from collections.abc import Iterable
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class CheckBoxGroup(Gadget, QWidget):
  def __init__(self, text=None, enabled=True, checked=False, count=None, column=False, fontsize=None, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)
    self.count = count if count is not None else len(text)
    self.text = text if text is not None else [""]*self.count
    self.column = column
    self.fontsize = fontsize
    if enabled in (True, False):
      self.enabled = [enabled]*self.count
    else:  
      self.enabled = [bool(en) for en in enabled] if enabled is not None else [True]*self.count
    if checked in (True, False):
      self.checked = [2 if checked else 0]*self.count
    else:  
      self.checked = [ch for ch in checked] if checked is not None else [0]*self.count
    self.widgets = []
    self.inhibited = False

    self.layout = QVBoxLayout() if self.column else QHBoxLayout()
    self.setLayout(self.layout)
    for i in range(self.count):
      self.widgets.append(QCheckBox(self.text[i]))
    for i,widget in enumerate(self.widgets):
      self.layout.addWidget(widget)
      widget.stateChanged.connect(lambda c,i=i: self.checked_(i,c))
    for enabled,checked,widget in zip(self.enabled, self.checked, self.widgets):  
      widget.setEnabled(enabled)
      widget.setCheckState(Qt.Checked if checked else Qt.Unchecked)
      if self.fontsize:
        font = widget.font()
        font.setPointSize(self.fontsize)
        widget.setFont(font)

  def update(self, alias, token):
    if isinstance(token, Iterable) and not isinstance(token, str):
      assert len(token) == self.count, "wrong input to " + self.socket.name
    else:
      token = [token]*self.count
    if alias == "enable":
      for i,(tok,widget) in enumerate(zip(token, self.widgets)):
        self.enabled[i] = bool(tok)
        widget.setEnabled(self.enabled[i] and not self.inhibited)
    elif alias == "check":
      for i,(tok,widget) in enumerate(zip(token, self.widgets)):
        if tok in (True, False):
          checked = 2 if tok else 0
        else:  
          checked = tok
        self.checked[i] = checked
        widget.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    elif alias == "text":
      for i,(tok,widget) in enumerate(zip(token, self.widgets)):
        text = str(tok)
        self.text[i] = text
        widget.setText(text)

  def inhibition(self, inhibited, alias):
    if alias == "checked":
      self.inhibited = inhibited
      for i,(enabled,widget) in enumerate(zip(self.enabled, self.widgets)):
        widget.setEnabled(self.enabled[i] and not self.inhibited)

  def checked_(self, index, checked):
    self.checked[index] = checked
    self.socket.put("checked", tuple(self.checked))
