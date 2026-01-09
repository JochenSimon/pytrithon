import re
from collections import OrderedDict, defaultdict
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Pytrithon import Gadget

def room(agent):
  return "".join(agent.split("#")[1].split("@")[::-1])

class Lobby(Gadget, QDialog):
  embed = False
  def __init__(self, parent, **kwargs):
    Gadget.__init__(self, **kwargs)
    QDialog.__init__(self, parent)

    self.servers = OrderedDict()
    self.running = defaultdict(bool)

    parent.sub_windows.append(self)

    self.setWindowTitle("Poker Lobby")

    self.server_combobox = QComboBox()
    self.player_labels = [QLabel("") for _ in range(5)]
    self.name_lineedit = QLineEdit()
    self.start_button = QPushButton("Start")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.server_combobox)
    for l in self.player_labels:
      self.layout.addWidget(l)
    self.layout.addWidget(self.name_lineedit)
    self.layout.addWidget(self.start_button)

    self.start_button.setEnabled(False)

    self.setLayout(self.layout)

    self.name_lineedit.setFocus(True)
    self.start_button.setAutoDefault(False)

    self.server_combobox.activated.connect(self.select_server)
    self.name_lineedit.textChanged.connect(self.name_changed)
    self.name_lineedit.returnPressed.connect(self.name_entered)
    self.start_button.clicked.connect(self.start)

  def sizeHint(self):
    return QSize(640, 320)

  def update(self, alias, token):
    if alias == "session":
      server, players = token
      name = room(server)
      if name not in self.servers:
        self.show()  
        self.server_combobox.addItem(name)
      self.servers[name] = server, players
      if self.server_combobox.currentText() == name:
        for i,p in enumerate(players):
          self.player_labels[i].setText(p)
        self.enable_inputs()  
    elif alias == "taken":
      self.name_lineedit.setEnabled(True)
    elif alias == "running":
      self.running[token] = True
      self.enable_inputs()
    elif alias == "hide":
      self.hide()

  def enable_inputs(self):
    name = self.server_combobox.currentText()
    if self.running[self.servers[name][0]]:
      self.start_button.setEnabled(False)
      self.name_lineedit.setEnabled(False)
    else:
      if len(self.servers[name][1]) >= 2:
        self.start_button.setEnabled(True)
      else:
        self.start_button.setEnabled(False)
      if self.name_lineedit.text() in self.servers[name][1]:
        self.name_lineedit.setEnabled(False)
      else:
        self.name_lineedit.setEnabled(True)

  def select_server(self, index):
    server, players = list(self.servers.values())[index]
    for i in range(5):
      self.player_labels[i].setText(players[i] if len(players) > i else "")
    self.enable_inputs()
    
  def name_changed(self, text):
    if re.sub(r"[\w]", "", text) or not text:
      self.name_lineedit.setStyleSheet("background-color: #420000")
    else:  
      self.name_lineedit.setStyleSheet("")

  def name_entered(self):
    if re.sub(r"[\w]", "", self.name_lineedit.text()) or not self.name_lineedit.text():
      return
    self.enable_inputs()
    self.socket.put("name,agent", (self.name_lineedit.text(), self.servers[self.server_combobox.currentText()][0]))
    self.socket.put("name", self.name_lineedit.text())
    self.socket.put("server", self.servers[self.server_combobox.currentText()][0])

  def start(self, checked):
    self.socket.put("start", self.servers[self.server_combobox.currentText()][0])
