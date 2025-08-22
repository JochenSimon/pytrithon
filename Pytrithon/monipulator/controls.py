import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from ..pytriontology import *
from .check import *

class Controls(QDockWidget):
  def __init__(self, title, moni):
    super().__init__(title, moni)
    self.moni = moni
    self.setFeatures(QDockWidget.DockWidgetMovable |
                     QDockWidget.DockWidgetFloatable)
    self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    self.console_button = QPushButton("co&nsole")
    self.check_button = QPushButton("chec&k")
    self.snapshot_button = QPushButton("sn&apshot")
    self.edit_button = QPushButton("&edit")
    self.init_button = QPushButton("&init")
    self.reset_button = QPushButton("rese&t")
    self.run_button = QPushButton("&run")
    self.step_button = QPushButton("ste&p")
    self.halt_button = QPushButton("&halt")
    self.terminate_button = QPushButton("ter&minate")
    self.delay_label = QLabel("delay")
    self.delay_spinbox = QSpinBox()
    self.agent_selector = QListWidget()

    self.delay_widget = QWidget()
    self.delay_layout = QHBoxLayout()
    self.delay_layout.addWidget(self.delay_label)
    self.delay_layout.addWidget(self.delay_spinbox)
    self.delay_layout.setContentsMargins(0, 0, 0, 0)
    self.delay_layout.setSpacing(0)
    self.delay_widget.setLayout(self.delay_layout)

    self.widget = QWidget()
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.console_button)
    self.layout.addWidget(self.check_button)
    self.layout.addWidget(self.snapshot_button)
    self.layout.addWidget(self.edit_button)
    self.layout.addWidget(self.init_button)
    self.layout.addWidget(self.reset_button)
    self.layout.addWidget(self.run_button)
    self.layout.addWidget(self.step_button)
    self.layout.addWidget(self.halt_button)
    self.layout.addWidget(self.terminate_button)
    self.layout.addWidget(self.delay_widget)
    self.layout.addWidget(self.agent_selector)
    self.widget.setLayout(self.layout)
    self.setWidget(self.widget)

    self.setMaximumWidth(400)
    self.setMinimumWidth(200)
    
    self.widget.sizeHint = lambda: QSize(200,0)

    self.delay_spinbox.setSuffix("ms")
    self.delay_spinbox.setRange(0, 60000)
    self.delay_spinbox.setSingleStep(100)

    self.console_button.clicked.connect(self.do_console)
    self.check_button.clicked.connect(self.do_check)
    self.snapshot_button.clicked.connect(self.do_snapshot)
    self.edit_button.clicked.connect(self.do_edit)
    self.init_button.clicked.connect(self.do_init)
    self.reset_button.clicked.connect(self.do_reset)
    self.run_button.clicked.connect(self.do_run)
    self.step_button.clicked.connect(self.do_step)
    self.halt_button.clicked.connect(self.do_halt)
    self.terminate_button.clicked.connect(self.do_terminate)

    self.oldSpinboxKeyPressEvent = self.delay_spinbox.keyPressEvent
    self.delay_spinbox.keyPressEvent = self.spinboxKeyPressEvent

    self.agent_selector.itemClicked.connect(self.do_select_agent)

    self.disable_buttons()

    self.console_button.setShortcut(QKeySequence("Ctrl+N"))
    self.check_button.setShortcut(QKeySequence("Ctrl+K"))
    self.snapshot_button.setShortcut(QKeySequence("Ctrl+A"))
    self.edit_button.setShortcut(QKeySequence("Ctrl+E"))
    self.init_button.setShortcut(QKeySequence("Ctrl+I"))
    self.reset_button.setShortcut(QKeySequence("Ctrl+T"))
    self.run_button.setShortcut(QKeySequence("Ctrl+R"))
    self.step_button.setShortcut(QKeySequence("Ctrl+P"))
    self.halt_button.setShortcut(QKeySequence("Ctrl+H"))
    self.terminate_button.setShortcut(QKeySequence("Ctrl+M"))
    self.delay_action = QShortcut(QKeySequence("Ctrl+D"), self, lambda: (self.delay_spinbox.setFocus(), self.delay_spinbox.selectAll()))

  def disable_buttons(self):  
    self.edit_button.setEnabled(False)
    self.init_button.setEnabled(False)
    self.reset_button.setEnabled(False)
    self.run_button.setEnabled(False)
    self.step_button.setEnabled(False)
    self.halt_button.setEnabled(False)
    self.terminate_button.setEnabled(False)

  def do_console(self, checked):
    if self.moni.console.isVisible():
      self.moni.console.hide()
    else:  
      self.moni.console.show()

  def do_check(self, checked):
    check(self.moni, {name.split("#")[0]: repr(self.moni.central_widget.canvases[name]) if name in self.moni.central_widget.canvases else None for name in self.moni.agents})

  def do_snapshot(self, checked):
    canvas = self.moni.central_widget.canvas
    image = QImage(canvas.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
    image.fill(canvas.colors.background)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    canvas.scene.render(painter)
    painter.end()
    image.save("workbench/snapshots/" + canvas.agent.split("#")[0] + ".png")
    print("Snapshot '{}' saved".format(canvas.agent.split("#")[0] + ".png"))

  def do_edit(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.disable_buttons()
      self.moni.nexus.send(CoreEdit(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_init(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.disable_buttons()
      self.moni.nexus.send(CoreInit(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_reset(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.disable_buttons()
      self.moni.nexus.send(CoreReset(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_run(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.moni.central_widget.canvas.halted = False
      self.moni.central_widget.canvas.enable_buttons()
      self.moni.nexus.send(CoreRun(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_step(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.moni.nexus.send(CoreStep(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_halt(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.moni.central_widget.canvas.halted = True
      self.moni.central_widget.canvas.enable_buttons()
      self.moni.nexus.send(CoreHalt(self.moni.central_widget.canvas.agent, self.moni.id))

  def do_terminate(self, checked):
    if self.moni.central_widget.canvas is not None:
      self.disable_buttons()
      agent = self.moni.central_widget.canvas.agent
      selector = self.moni.controls.agent_selector
      if agent.startswith("$"):
        selector.takeItem(selector.row(selector.findItems(agent, Qt.MatchExactly)[0]))
      else:  
        self.moni.nexus.send(TriggerTerminate(agent, self.moni.id))

  def spinboxKeyPressEvent(self, event):
    if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
      self.set_delay(self.delay_spinbox.value())
    else:
      self.oldSpinboxKeyPressEvent(event)

  def set_delay(self, value):
    self.moni.central_widget.canvas.delay = value
    self.moni.nexus.send(SetDelay(self.moni.central_widget.canvas.agent, self.moni.id, value))

  def do_select_agent(self, item):
    if item is not None:
      if item.text() not in self.moni.central_widget.canvases:
        self.moni.nexus.send(RequestStructure(item.text(), self.moni.id))
      else:
        self.moni.central_widget.select_canvas(item.text())
        self.delay_spinbox.setValue(self.moni.central_widget.canvas.delay)
