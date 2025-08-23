import re
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ..pytriontology import *

class OpenDialog(QDialog):
  def __init__(self, moni, names):
    super().__init__(moni)
    self.moni = moni

    self.setWindowTitle("Open Agent")

    self.pick_button = QPushButton("Pick")
    self.agent_lineedit = QLineEdit()
    self.arguments_lineedit = QLineEdit()
    self.dest_combobox = QComboBox()
    for name in names:
      self.dest_combobox.addItem(name)
    self.delay_spinbox = QSpinBox()
    self.poll_spinbox = QSpinBox()
    self.edit_checkbox = QCheckBox()
    self.halt_checkbox = QCheckBox()
    self.secret_checkbox = QCheckBox()
    self.mute_checkbox = QCheckBox()
    self.errors_checkbox = QCheckBox()
    self.open_button = QPushButton("Open Agent")

    self.agent_lineedit.setMinimumWidth(237)
    self.arguments_lineedit.setMinimumWidth(237)
    self.dest_combobox.setMinimumWidth(237)

    self.layout = QGridLayout(self)
    for col, (label, widget) in enumerate(zip(["", "agent", "arguments", "delay (ms)", "poll (ms)", "edit", "halt", "secret", "mute", "errors", "destination", ""], [self.pick_button, self.agent_lineedit, self.arguments_lineedit, self.delay_spinbox, self.poll_spinbox, self.edit_checkbox, self.halt_checkbox, self.secret_checkbox, self.mute_checkbox, self.errors_checkbox, self.dest_combobox, self.open_button])):
      if label:
        self.layout.addWidget(QLabel(label), 0, col)
      self.layout.addWidget(widget, 1, col)

    self.setLayout(self.layout)  

    self.delay_spinbox.setSuffix("ms")
    self.delay_spinbox.setRange(0, 60000)
    self.delay_spinbox.setSingleStep(100)
    self.delay_spinbox.setValue(moni.config["delay"] if moni.config and "delay" in moni.config else 0)

    self.poll_spinbox.setSuffix("ms")
    self.poll_spinbox.setRange(0, 100)
    self.poll_spinbox.setSingleStep(1)
    self.poll_spinbox.setValue(moni.config["poll"] if moni.config and "poll" in moni.config else 10)

    self.edit_checkbox.setCheckState(Qt.Checked if moni.config and "edit" in moni.config and moni.config["edit"] else Qt.Unchecked)
    self.halt_checkbox.setCheckState(Qt.Checked if moni.config and "halt" in moni.config and moni.config["halt"] else Qt.Unchecked)
    self.secret_checkbox.setCheckState(Qt.Checked if moni.config and "secret" in moni.config and moni.config["secret"] else Qt.Unchecked)
    self.mute_checkbox.setCheckState(Qt.Checked if moni.config and "mute" in moni.config and moni.config["mute"] else Qt.Unchecked)
    self.errors_checkbox.setCheckState(Qt.Checked if moni.config and "errors" in moni.config and moni.config["errors"] or not moni.config or "errors" not in moni.config else Qt.Unchecked)

    self.edit_checkbox.setShortcut(QKeySequence("Ctrl+E"))
    self.halt_checkbox.setShortcut(QKeySequence("Ctrl+H"))
    self.secret_checkbox.setShortcut(QKeySequence("Ctrl+S"))
    self.mute_checkbox.setShortcut(QKeySequence("Ctrl+M"))
    self.errors_checkbox.setShortcut(QKeySequence("Ctrl+R"))
    
    self.edit_checkbox.stateChanged.connect(lambda c: self.agent_lineedit.setFocus())
    self.halt_checkbox.stateChanged.connect(lambda c: self.agent_lineedit.setFocus())
    self.secret_checkbox.stateChanged.connect(lambda c: self.agent_lineedit.setFocus())
    self.mute_checkbox.stateChanged.connect(lambda c: self.agent_lineedit.setFocus())
    self.errors_checkbox.stateChanged.connect(lambda c: self.agent_lineedit.setFocus())

    self.agent_lineedit.textEdited.connect(self.edited)
    self.open_button.clicked.connect(self.do_open)

    self.pick_button.clicked.connect(self.do_pick)
    
    self.pick_button.setShortcut(QKeySequence("Ctrl+O"))

    self.pick_dialog = QFileDialog(self, "Pick agent")
    self.pick_dialog.setFileMode(QFileDialog.ExistingFiles)
    self.pick_dialog.setAcceptMode(QFileDialog.AcceptOpen)
    self.pick_dialog.setNameFilter("Pytrithon Agent file (*.pta)")
    self.pick_dialog.directoryEntered.connect(self.keep_origin)

    self.agent_lineedit.setFocus()
    self.open_button.setEnabled(False)

  def edited(self, text):
    if not text or text == "$" or text.startswith("$") and (re.sub(r"[\w.]", "", text[1:]) or text[1:].startswith(".") or text[1:].endswith(".")) or not text.startswith("$") and (re.sub(r"[\w.]", "", text) or text.startswith(".") or text.endswith(".")) or ".." in text:
      self.agent_lineedit.setStyleSheet("background-color: #420000")
      self.open_button.setEnabled(False)
    else:  
      self.agent_lineedit.setStyleSheet("")
      self.open_button.setEnabled(True)

  def keep_origin(self, directory):
    if not directory.replace("\\", "/").startswith(os.path.abspath("workbench/agents").replace("\\", "/")):
      self.pick_dialog.setDirectory(os.path.abspath("workbench/agents"))

  def do_pick(self, checked):
    self.pick_dialog.setDirectory(os.path.abspath("workbench/agents"))
    if self.pick_dialog.exec():
      self.agent_lineedit.setText(os.path.relpath(self.pick_dialog.selectedFiles()[0], start="workbench/agents").replace("\\", "/").replace("/", ".").rstrip("\\.pta"))
      self.agent_lineedit.setStyleSheet("")
      self.open_button.setEnabled(True)
    self.activateWindow()
    self.agent_lineedit.setFocus()

  def do_open(self, checked):
    agent = self.agent_lineedit.text()
    if agent.startswith("$"):
      self.moni.open_fragment(agent[1:])
    else:
      self.moni.nexus.send(OpenAgent(self.dest_combobox.currentText(), agent, self.arguments_lineedit.text().split(" ") if self.arguments_lineedit.text() else [], self.delay_spinbox.value(), self.poll_spinbox.value(), self.edit_checkbox.checkState() == Qt.Checked, self.halt_checkbox.checkState() == Qt.Checked, self.secret_checkbox.checkState() == Qt.Checked, self.mute_checkbox.checkState() == Qt.Checked, self.errors_checkbox.checkState() == Qt.Checked))

class PushDialog(QDialog):
  def __init__(self, moni, agent, names):
    super().__init__(moni)
    self.moni = moni
    self.agent = agent
    self.names = names

    self.setWindowTitle("Push Agent")

    self.agent_lineedit = QLineEdit(agent)
    self.dest_combobox = QComboBox()
    self.dest_combobox.addItem("(everywhere)")
    for name in names:
      self.dest_combobox.addItem(name)
    self.push_button = QPushButton("Push Agent")

    self.agent_lineedit.setMinimumWidth(237)
    self.dest_combobox.setMinimumWidth(237)

    self.layout = QGridLayout(self)
    for col, (label, widget) in enumerate(zip(["agent", "destination", ""], [self.agent_lineedit, self.dest_combobox, self.push_button])):
      if label:
        self.layout.addWidget(QLabel(label), 0, col)
      self.layout.addWidget(widget, 1, col)

    self.setLayout(self.layout)  

    self.agent_lineedit.textEdited.connect(self.edited)
    self.push_button.clicked.connect(self.do_push)

  def edited(self, text):  
    if not text or text == "$" or text.startswith("$") and (re.sub(r"[\w.]", "", text[1:]) or text[1:].startswith(".") or text[1:].endswith(".")) or not text.startswith("$") and (re.sub(r"[\w.]", "", text) or text.startswith(".") or text.endswith(".")) or ".." in text:
      self.agent_lineedit.setStyleSheet("background-color: #420000")
      self.push_button.setEnabled(False)
    else:  
      self.agent_lineedit.setStyleSheet("")
      self.push_button.setEnabled(True)

  def do_push(self, checked):
    dest = "" if self.dest_combobox.currentText() == "(everywhere)" else self.dest_combobox.currentText()
    agent = self.agent_lineedit.text()
    if self.agent.startswith("$"):
      if agent.startswith("$"):
        print("Fragment '{}' pushed to nexi '{}' as fragment '{}'".format(self.agent[1:], ",".join(self.names) if not dest else dest, agent[1:]))
      else:
        print("Fragment '{}' pushed to nexi '{}' as agent '{}'".format(self.agent[1:], ",".join(self.names) if not dest else dest, agent))
    else:
      if agent.startswith("$"):
        print("Agent '{}' pushed to nexi '{}' as fragment '{}'".format(self.agent, ",".join(self.names) if not dest else dest, agent[1:]))
      else:
        print("Agent '{}' pushed to nexi '{}' as agent '{}'".format(self.agent, ",".join(self.names) if not dest else dest, agent))
    self.moni.nexus.send(PushAgent(dest, agent, str(self.moni.central_widget.canvas)))
    self.hide()

class PushFileDialog(QDialog):
  def __init__(self, moni, names):
    super().__init__(moni)
    self.moni = moni
    self.names = names

    self.setWindowTitle("Push File")

    self.pick_button = QPushButton("Pick")
    self.file_lineedit = QLineEdit()
    self.dest_combobox = QComboBox()
    self.dest_combobox.addItem("(elsewhere)")
    for name in names:
      self.dest_combobox.addItem(name)
    self.push_button = QPushButton("Push File")

    self.file_lineedit.setMinimumWidth(423)
    self.dest_combobox.setMinimumWidth(237)

    self.layout = QGridLayout(self)
    for col, (label, widget) in enumerate(zip(["", "file", "destination", ""], [self.pick_button, self.file_lineedit, self.dest_combobox, self.push_button])):
      if label:
        self.layout.addWidget(QLabel(label), 0, col)
      self.layout.addWidget(widget, 1, col)

    self.setLayout(self.layout)  

    self.file_lineedit.textChanged.connect(self.changed)
    self.pick_button.clicked.connect(self.do_pick)
    self.push_button.clicked.connect(self.do_push)
    
    self.pick_button.setShortcut(QKeySequence("Ctrl+F"))

    self.push_button.setEnabled(False)
    self.push_button.setDefault(True)
    self.push_button.setAutoDefault(True)
    self.file_lineedit.setFocus()

    self.pick_dialog = QFileDialog(self, "Pick File")
    self.pick_dialog.setFileMode(QFileDialog.ExistingFiles)
    self.pick_dialog.setAcceptMode(QFileDialog.AcceptOpen)
    self.pick_dialog.directoryEntered.connect(self.keep_origin)

  def changed(self, text):  
    files = [os.path.abspath("workbench/"+t).replace("\\", "/") for t in text.split(" ")]
    root = os.path.abspath("workbench").replace("\\", "/")
    for absfile,file in zip(files, text.split(" ")):
      if not file or ".." in file or not absfile.startswith(root) or absfile == root or not os.path.exists("workbench/" + file) or len(files) != 1 and not os.path.isfile("workbench/" + file):
        self.file_lineedit.setStyleSheet("background-color: #420000")
        self.push_button.setEnabled(False)
        break
    else:  
      self.file_lineedit.setStyleSheet("")
      self.push_button.setEnabled(True)

  def keep_origin(self, directory):
    if not directory.replace("\\", "/").startswith(os.path.abspath("workbench").replace("\\", "/")):
      self.pick_dialog.setDirectory(os.path.abspath("workbench"))

  def do_pick(self, checked):
    self.pick_dialog.setDirectory(os.path.abspath("workbench"))
    if self.pick_dialog.exec():
      self.file_lineedit.setText(" ".join(os.path.relpath(f, start="workbench").replace("\\", "/") for f in self.pick_dialog.selectedFiles()))
    self.activateWindow()
    self.file_lineedit.setFocus()

  def do_push(self, checked):
    dest = ",".join(self.names) if self.dest_combobox.currentText() == "(elsewhere)" else self.dest_combobox.currentText()
    filenames = self.file_lineedit.text()
    files = []
    if " " in filenames:
      files = filenames.split(" ")
    elif os.path.isfile("workbench/" + filenames):
      files = [filenames]
    elif filenames:  
      for root, _, fs in os.walk("workbench/" + filenames):
        for file in fs:
          files.append(os.path.relpath(root, start="workbench").replace("\\", "/") + "/" + file)
    print("Files '{}' pushed to nexi '{}'".format(" ".join(files), dest))      
    for file in files:
      with open("workbench/"+file, "rb") as f:
        data = f.read()
      if not data.strip():
        os.remove("workbench/"+file)
      self.moni.nexus.send(PushFile(dest, file, data))
    self.hide()
