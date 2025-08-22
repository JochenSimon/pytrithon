import os
import sys
import re
import html
import builtins
from colorama import Fore, init, AnsiToWin32
from time import sleep
from collections import OrderedDict
from threading import Thread
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .colors import *
from .controls import *
from .console import *
from .dialogs import *
from .canvas import *
from ..pytriontology import *
from ..nexusmediator import NexusMediator
from ..utils import wait_cursor
from .. import __version__

def print(*objects, sep=" ", end="\n", file=None, flush=False):
  file = file if file is not None else sys.stdout
  file.write(sep.join(str(obj) for obj in objects) + end)
  if flush and file is not sys.stdout:
    file.flush()

class PrintStream():
  def __init__(self, console):
    self.console = console
    self.printstream = AnsiToWin32(sys.__stdout__).stream

  def write(self, message):
    if self.console.info:
      self.console.print("<monipulator>", "<p class='moni'>"+re.sub("\n", "<br/>", html.escape(message))+"</p>")
      self.printstream.write(Fore.GREEN + message + Fore.RESET)
      self.flush()
      return len(message)
    return 0

  def flush(self):
    sys.__stdout__.flush()

class CentralWidget(QWidget):
  def __init__(self, moni):
    super().__init__(moni)
    self.moni = moni
    self.canvas = None
    self.canvases = OrderedDict()
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)
  def add_canvas(self, agent, canvas):
    if self.canvas:
      self.canvas.hide()
    self.canvas = canvas
    self.canvases[agent] = canvas
    self.layout.addWidget(canvas)
    self.canvas.agent = agent
  def select_canvas(self, agent):
    self.moni.push_action.setEnabled(True)
    self.moni.pushto_action.setEnabled(True)
    self.moni.save_action.setEnabled(True)
    self.moni.saveas_action.setEnabled(True)
    for name, canvas in self.canvases.items():
      if agent == name:
        canvas.show()
        canvas.enable_buttons()
        self.canvas = canvas
      else:
        canvas.hide()

class Monipulator(QMainWindow):
  def __init__(self, app, host, port, console, bundle, info, open, quit, lightmode, zoom, config):
    QMainWindow.__init__(self, None)
    self.agents = OrderedDict()
    self.connected = False
    self.nexus = NexusMediator(host, port, moni=self)

    self.app = app

    self.open = open
    self.quit = quit
    self.zoom = zoom
    self.colors = LightMode if lightmode else NightMode
    self.bundle = bundle
    self.config = config

    self.file_menu = QMenu("File")
    self.open_action = QAction("Open...")
    self.open_action.setShortcut(QKeySequence("Ctrl+O"))
    self.open_action.triggered.connect(self.do_open)
    self.push_action = QAction("Push Everywhere")
    self.push_action.setShortcut(QKeySequence("Shift+Ctrl+U"))
    self.push_action.triggered.connect(self.do_push)
    self.pushto_action = QAction("Push To...")
    self.pushto_action.setShortcut(QKeySequence("Ctrl+U"))
    self.pushto_action.triggered.connect(self.do_pushto)
    self.pushfile_action = QAction("Push File...")
    self.pushfile_action.setShortcut(QKeySequence("Ctrl+F"))
    self.pushfile_action.triggered.connect(self.do_pushfile)
    self.save_action = QAction("Save")
    self.save_action.setShortcut(QKeySequence("Ctrl+S"))
    self.save_action.triggered.connect(self.do_save)
    self.saveas_action = QAction("Save As...")
    self.saveas_action.setShortcut(QKeySequence("F12"))
    self.saveas_action.triggered.connect(self.do_saveas)
    self.quit_action = QAction("Quit")
    self.quit_action.setShortcut(QKeySequence("Ctrl+Q"))
    self.quit_action.triggered.connect(self.do_quit)
    self.file_menu.addAction(self.open_action)
    self.file_menu.addAction(self.push_action)
    self.file_menu.addAction(self.pushto_action)
    self.file_menu.addAction(self.pushfile_action)
    self.file_menu.addAction(self.save_action)
    self.file_menu.addAction(self.saveas_action)
    self.file_menu.addAction(self.quit_action)
    self.menu_bar = QMenuBar()
    self.menu_bar.addMenu(self.file_menu)
    self.setMenuBar(self.menu_bar)

    self.push_action.setEnabled(False)
    self.pushto_action.setEnabled(False)
    self.save_action.setEnabled(False)
    self.saveas_action.setEnabled(False)

    self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
    self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
    self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
    self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

    self.central_widget = CentralWidget(self)
    self.setCentralWidget(self.central_widget)
    self.controls = Controls("controls", self)
    self.console = Console("console", self)

    self.console.info = info
    init(wrap=False)
    sys.stdout = PrintStream(self.console)
    builtins.print = print

    self.addDockWidget(Qt.BottomDockWidgetArea, self.console)
    if not console:
      self.console.hide()
    self.addDockWidget(Qt.RightDockWidgetArea, self.controls)
    self.setWindowTitle("Pytrithon Monipulator v" + __version__)
    self.setWindowIcon(QIcon("moni.png"))

  def do_open(self):
    self.nexus.send(TriggerOpen(self.id, []))

  def show_open(self, names):
    open_dialog = OpenDialog(self, names)
    open_dialog.show()

  def do_push(self):
    wait_cursor()
    agentname = self.central_widget.canvas.agent.split("#")[0]
    if agentname.startswith("$"):
      print("Fragment '{}' pushed to everywhere".format(agentname[1:]))
    else:
      print("Agent '{}' pushed to everywhere".format(agentname))
    self.nexus.send(PushAgent("", agentname, str(self.central_widget.canvas)))

  def do_pushto(self):
    self.nexus.send(TriggerPush(self.id, [], self.central_widget.canvas.agent.split("#")[0]))

  def do_pushfile(self):
    self.nexus.send(TriggerPushFile(self.id, []))

  def show_push(self, agent, names):
    push_dialog = PushDialog(self, agent, names)
    push_dialog.show()
  
  def show_pushfile(self, names):
    pushfile_dialog = PushFileDialog(self, names)
    pushfile_dialog.show()

  def do_save(self):
    wait_cursor()
    agentname = self.central_widget.canvas.agent.split("#")[0]
    if "$" not in agentname:
      if "." in agentname:
        os.makedirs("workbench/agents/" + "/".join(agentname.replace(".", "/").split("/")[:-1]), exist_ok=True) 
      with open("workbench/agents/" + agentname.replace(".", "/") + ".pta", "w", encoding="utf-8") as f:
        f.write(str(self.central_widget.canvas))
      print("Agent '{}' saved locally".format(agentname))
    else:
      if "." in agentname:
        os.makedirs("workbench/fragments/" + "/".join(agentname[1:].replace(".", "/").split("/")[:-1]), exist_ok=True) 
      with open("workbench/fragments/" + agentname[1:].replace(".", "/") + ".ptf", "w", encoding="utf-8") as f:
        f.write(str(self.central_widget.canvas))
      print("Fragment '{}' saved locally".format(agentname[1:]))

  def do_saveas(self):
    agentname = self.central_widget.canvas.agent.split("#")[0]
    if not agentname.startswith("$"):
      directory = "workbench/agents" + ("/" if "." in agentname else "")
      filetype = ".pta"
      filetypehint = "Pytrithon Agent File (*.pta);;Pytrithon Fragment File (*.ptf)"
    else:
      agentname = agentname[1:]
      directory = "workbench/fragments" + ("/" if "." in agentname else "")
      filetype = ".ptf"
      filetypehint = "Pytrithon Fragment File (*.ptf);;Pytrithon Agent File (*.pta)"
    agentfile, filetype = QFileDialog.getSaveFileName(self, "Save",  directory + "/".join(agentname.replace(".", "/").split("/")[:-1]) + "/" + agentname.rsplit(".", 1)[-1] + filetype, filetypehint)
    if agentfile:
      with open(agentfile, "w", encoding="utf-8") as f:
        f.write(str(self.central_widget.canvas))

  def give_agent_list(self, agents):
    if self.open and not self.agents:
      if agents:
        self.nexus.send(RequestStructure(agents[0], self.id))
    for agent in self.agents:
      if agent not in agents and not agent.startswith("$"):
        items = self.controls.agent_selector.findItems(agent, Qt.MatchExactly)
        if items:
          self.controls.agent_selector.takeItem(self.controls.agent_selector.row(items[0]))
    for agent in agents:
      if agent not in self.agents:
        self.agents[agent] = None
        self.controls.agent_selector.addItem(agent)
        self.controls.check_button.setEnabled(True)
      elif not self.controls.agent_selector.findItems(agent, Qt.MatchExactly):
        self.controls.agent_selector.addItem(agent)

  def give_structure(self, agent, structure, contents, delay, halted, editmode, secret):
    canvas = Canvas(self, structure, delay, halted, editmode, secret, False, self.zoom, self.colors)
    self.agents[agent] = canvas
    self.central_widget.add_canvas(agent, canvas)
    if self.controls.agent_selector.currentItem() is None or self.controls.agent_selector.currentItem().text() == agent:
      self.central_widget.select_canvas(agent)
      items = self.controls.agent_selector.findItems(agent, Qt.MatchExactly)
      if items:
        self.controls.agent_selector.setCurrentItem(items[0])
      self.controls.delay_spinbox.setValue(delay)
    for content in contents:
      self.agents[agent].figures[content.place].change(content.content)

  def open_fragment(self, frag):
    items = self.controls.agent_selector.findItems("$"+frag, Qt.MatchExactly)
    if not items:
      try:
        with open("workbench/fragments/"+frag.replace(".", "/")+".ptf", encoding="utf-8") as f:
          structure = f.read()
      except FileNotFoundError:
        structure = ""
      canvas = Canvas(self, structure, 0, False, True, False, True, self.zoom, self.colors)
      self.agents["$"+frag] = canvas
      self.controls.agent_selector.addItem("$"+frag)
      self.central_widget.add_canvas("$"+frag, canvas)
    self.controls.agent_selector.setCurrentItem(self.controls.agent_selector.findItems("$"+frag, Qt.MatchExactly)[0])
    self.central_widget.select_canvas("$"+frag)

  def closeEvent(self, event):
    if self.quit:
      self.nexus.send(TerminatedLocal())
    event.accept()

  def do_quit(self):
    self.close()

  def start(self):
    QTimer().singleShot(0, self.run)

  def run(self):
    for _ in range(17):
      communication = self.nexus.receive()
      if communication:
        communication.execute(self)
      else:
        break
    if communication:    
      return QTimer().singleShot(0, self.run)
    QTimer().singleShot(10, self.run)
