from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .. import __version__

class ConsoleWidget(QTextEdit):
  def __init__(self, moni):
    super().__init__()
    self.setReadOnly(True)
    self.setStyleSheet("background: "+moni.colors.consolebackground.name())
    self.document().setDefaultStyleSheet("p { white-space: pre-wrap; color: "+moni.colors.consoletext.name()+"; } p.error { color: "+moni.colors.consoleerror.name()+"; } p.fatal { color: "+moni.colors.consolefatal.name()+"; } p.moni { color: "+moni.colors.consolemoni.name()+"; }")

class Console(QDockWidget):
  def __init__(self, title, moni):
    super().__init__(title, moni)
    self.setFeatures(QDockWidget.DockWidgetMovable |
                     QDockWidget.DockWidgetFloatable |
                     QDockWidget.DockWidgetClosable |
                     QDockWidget.DockWidgetVerticalTitleBar)
    self.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

    self.moni = moni
    self.consoles = {}
    self.widget = QWidget()

    if self.moni.bundle:
      self.buffer = ConsoleWidget(self.moni)
    else:
      self.buffer = QWidget()
      self.buffer.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    self.layout = QHBoxLayout(self.widget)
    self.layout.addWidget(self.buffer)
    if not self.moni.bundle:
      self.agents = QListWidget()
      self.layout.addWidget(self.agents)
      self.agents.itemClicked.connect(self.select_agent)
      self.agents.sizeHint = lambda: QSize(137, 0)
      self.agents.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    self.setWidget(self.widget)
    self.widget.sizeHint = self.sizeHint

    self.topLevelChanged.connect(self.check_floating)

  def check_floating(self, floating):
    self.adjustSize()

  def sizeHint(self):
    return (QSize(1024, 800) if self.moni.bundle else QSize(1200, 800)) if self.isFloating() else QSize(0, 200)

  def select_agent(self, item):
    if item is not None:
      console = self.consoles[item.text()]
      self.layout.replaceWidget(self.buffer, console)
      self.buffer.setParent(None)
      self.buffer = console

  def print(self, agent, message):
    if self.moni.bundle:
      console = self.buffer
    elif agent not in self.consoles:
      console = ConsoleWidget(self.moni)
      if agent != "<monipulator>":
        self.agents.addItem(agent)
      else:
        self.agents.insertItem(0, agent)
      if not self.consoles:
        self.layout.replaceWidget(self.buffer, console)
        self.buffer.setParent(None)
        self.agents.setCurrentRow(0)
        self.buffer = console
      self.consoles[agent] = console
    else:
      console = self.consoles[agent]

    if not self.moni.bundle and agent == "<monipulator>":
      item = self.agents.findItems(agent, Qt.MatchExactly)[0]
      if self.agents.currentItem() != item:
        self.select_agent(item)
        self.agents.setCurrentItem(item)

    scrollbar = console.verticalScrollBar()  
    at_bottom = scrollbar.value() >= scrollbar.maximum() - 4
    position = scrollbar.value()

    console.moveCursor(QTextCursor.End)
    console.insertHtml(message)
    console.moveCursor(QTextCursor.End)

    if at_bottom:
      console.ensureCursorVisible()
    else:
      scrollbar.setValue(position)
