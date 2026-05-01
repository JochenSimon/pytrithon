import re
import html
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .gadget import Gadget

class TextEdit(Gadget, QTextEdit):
  def __init__(self, text="", height=128, readonly=True, autoscroll=True, **kwargs):
    Gadget.__init__(self, **kwargs)
    QTextEdit.__init__(self, text)
    self.height = height
    self.readonly = readonly
    self.autoscroll = autoscroll
    self.inhibited = False
    self.setReadOnly(self.readonly)
    self.document().setDefaultStyleSheet("p { white-space: pre-wrap; }")

  def minimumSizeHint(self):
    return QSize(0, self.height)

  def update(self, alias, token):
    if alias == "replace":
      self.setPlainText(str(token))
    if alias == "append":
      text = str(token)
      if self.autoscroll:
        scrollbar = self.verticalScrollBar()  
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 4
        position = scrollbar.value()
      self.moveCursor(QTextCursor.End)
      self.insertHtml("<p>"+re.sub("\n", "<br/>", html.escape(text))+"<br/></p>")
      if self.autoscroll:
        self.moveCursor(QTextCursor.End)
        if at_bottom:
          self.ensureCursorVisible()
        else:
          scrollbar.setValue(position)
