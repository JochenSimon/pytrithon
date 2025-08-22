import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Pytrithon import Gadget

def room(agent):
  return "".join(agent.split("#")[1].split("@")[::-1])

class JoinDialog(Gadget, QDialog):
  embed = False
  def __init__(self, parent, **kwargs):
    Gadget.__init__(self, **kwargs)
    QDialog.__init__(self, parent)

    self.servers = {}

    self.setWindowTitle("Join Server")

    self.name_lineedit = QLineEdit()
    self.password_lineedit = QLineEdit()
    self.server_combobox = QComboBox()
    self.join_button = QPushButton("Join")

    self.layout = QGridLayout(self)
    self.layout.addWidget(QLabel("Name"), 0, 0)
    self.layout.addWidget(QLabel("Password"), 0, 1)
    self.layout.addWidget(QLabel("Server"), 0, 2)
    self.layout.addWidget(self.name_lineedit, 1, 0)
    self.layout.addWidget(self.password_lineedit, 1, 1)
    self.layout.addWidget(self.server_combobox, 1, 2)
    self.layout.addWidget(self.join_button, 1, 3)

    self.password_lineedit.setEchoMode(QLineEdit.Password)
    self.server_combobox.sizeHint = lambda: QSize(128, 12)

    self.setLayout(self.layout)

    self.join_button.clicked.connect(self.join)

  def sizeHint(self):
    return QSize(640, 64)

  def update(self, alias, token):
    if alias == "servers":
      for server in sorted(token):
        name = room(server)
        if name not in self.servers:
          self.server_combobox.addItem(name)
          self.servers[name] = server
      self.show()  
    elif alias == "reappear":
      self.show()

  def join(self, checked):
    if re.sub(r"[\w]", "", self.name_lineedit.text()) or not self.name_lineedit.text():
      self.name_lineedit.setStyleSheet("background-color: #420000")
      return
    if len(self.password_lineedit.text()) < 6:
      self.password_lineedit.setStyleSheet("background-color: #420000")
      return
    self.name_lineedit.setStyleSheet("")
    self.password_lineedit.setStyleSheet("")
    self.socket.put("name", self.name_lineedit.text())
    self.socket.put("password", self.password_lineedit.text())
    self.socket.put("server", self.servers[self.server_combobox.currentText()])
    self.hide()
