import sys
import builtins
import re
import html
from random import choice
from colorama import Fore, init, AnsiToWin32
from collections import defaultdict
from PyQt5.QtCore import QTimer
from .elements import *
from .nexusmediator import *
from .pytriontology import *
from .gui import *
from .utils import WithEnum

def print(*objects, sep=" ", end="\n", file=None, flush=False, hide=False):
  file = file if file is not None else sys.stdout
  hidearg = {"hide": hide} if file is sys.stderr else {}
  file.write(sep.join(str(obj) for obj in objects) + end, **hidearg)
  if flush and file not in (sys.stdout, sys.stderr):
    file.flush()

class PrintStream():
  def __init__(self, core):
    self.core = core

  def write(self, message):
    if not self.core.mute:
      self.core.nexus.send(Print(self.core.agent.name, set(), "<p>"+re.sub("\n", "<br/>", html.escape(message))+"</p>"))
      sys.__stdout__.write(message)
      self.flush()
      return len(message)
    return 0

  def flush(self):
    sys.__stdout__.flush()

class ErrorStream():
  def __init__(self, core):
    self.core = core
    self.errstream = AnsiToWin32(sys.__stderr__).stream

  def write(self, message, hide=False):
    if self.core.errors or not hide:
      if hide:
        self.core.nexus.send(Print(self.core.agent.name, set(), "<p class='error'>"+re.sub("\n", "<br/>", html.escape(message))+"</p>"))
        self.errstream.write(Fore.RED + message + Fore.RESET)
      else:  
        self.core.nexus.send(Print(self.core.agent.name, set(), "<p class='fatal'>"+re.sub("\n", "<br/>", html.escape(message))+"</p>"))
        self.errstream.write(Fore.MAGENTA + message + Fore.RESET)
      self.flush()
      return len(message)
    return 0

  def flush(self):
    sys.__stderr__.flush()

def except_hook(cls, exception, traceback):
  sys.__excepthook__(cls, exception, traceback)

class Core:
  def __init__(self, agent, host, port, delay, poll, timeout, edit, halt, secret, mute, errors, app):
    self.agent = agent
    self.delay = delay
    self.poll = poll
    self.timeout = timeout
    self.edit = edit  
    if halt:
      self.state = 0
      self.halted = True
    else:
      self.state = 1
      self.halted = False
    if edit:
      self.state = 0
    self.secret = secret
    self.mute = mute
    self.errors = errors
    self.domain = None
    self.app = app
    self.agent.core = self
    self.watchers = set()
    self.nexus = NexusMediator(host, port, core=self)
    self.hasgui = False
    self.window = Window(self)
    self.invocations = defaultdict(list)
    self.results = defaultdict(list)
    self.communications = defaultdict(list)
    self.phase = 0

    init(wrap=False)
    sys.stdout = PrintStream(self)
    sys.stderr = ErrorStream(self)
    sys.excepthook = except_hook
    builtins.print = print

  def init(self):
    self.firables = []

    if self.agent.exists:
      self.agent.init(repr(self.agent))
      self.reinit = True
    else:
      self.agent.init()
      self.reinit = False

    if self.reinit:
      self.window.widgets = []
      for i in reversed(range(self.window.layout.count())):
        self.window.layout.itemAt(i).widget().setParent(None)
        self.window.layout.removeItem(self.window.layout.itemAt(i))
      Nethod.nethods = defaultdict(set)
      Nethod.neth = 1
      Nethod.origins = {}
      Call.calls = {}
      Return.returns = {}
      Signal.signals = defaultdict(set)
      Slot.slots = defaultdict(set)
      Slot.noroom = defaultdict(set)
      Invocation.invocations = {}
      Task.tasks = defaultdict(set)
      In.sensors = defaultdict(set)

    elements = self.agent.elements.values()
    for element in elements:
      element.load()
    for element in elements:
      if element.type == "self":
        element.init()
    for element in elements:
      if element.type != "self":
        element.init()

    self.register_listeners()  

    if not self.edit:
      for element in elements:
        element.create()
      if self.hasgui:
        self.window.show()  
      for element in elements:
        element.prime()

      self.populate("agent", self.agent)
      self.populate("args", self.agent.args)
      self.populate("env", self.agent.env)
      self.populate("window", self.window)
      self.populate("app", self.app)

  def populate(self, name, obj):
    fragments = [e for e in self.agent.elements.values() if e.isfrag]
    elements = [name] + [f.name+"."+name for f in fragments]
    for element in elements:
      if element in self.agent and self.agent[element].type == "know":
        if self.agent[element].empty:
          self.agent[element].give(obj)
        else:
          if obj:
            self.agent[element].write(obj)

  def ready(self, trans):
    if trans not in self.firables:
      self.firables.append(trans)

  def doze(self, trans):
    if trans in self.firables:
      self.firables.remove(trans)

  def start(self):
    QTimer().singleShot(0, self.dispatch)  
    QTimer().singleShot(0, self.ping)  
    QTimer().singleShot(0, self.run)  

  def run(self):
    try:
      if not self.edit:
        if self.state:
          if self.state < 0:
            self.state += 1
          if self.firables or self.phase in (1, 2):
            self.step()
            return QTimer().singleShot(int([0.8,0.1,0.1][self.phase] * self.delay), self.run)
      else:
        return QTimer().singleShot(10, self.run)
    except KeyboardInterrupt:
      self.state = 2

    if self.state == 2:
      return
    QTimer().singleShot(self.poll, self.run)  

  def step(self):
    if self.phase == 0:
      priorities = defaultdict(set)
      for element in self.firables:
        priorities[element.priority].add(element)
      for priority in sorted(priorities, reverse=True):
        self.tofire = choice(list(priorities[priority]))
        if self.watchers and not self.tofire.parent.isfrag:
            self.nexus.send(TransitionFiring(self.agent.name, self.watchers, self.tofire.name, True))
        self.places_changed(self.tofire.collect())
        self.phase = 1
        break
    elif self.phase == 1:  
      self.tofire.fire()
      self.phase = 2
    elif self.phase == 2:
      if self.watchers and not self.tofire.parent.isfrag:
          self.nexus.send(TransitionFiring(self.agent.name, self.watchers, self.tofire.name, False))
      self.places_changed(self.tofire.distribute())
      self.phase = 0

  def dispatch(self):
    while 1:
      communication = self.nexus.receive()
      if communication:
        communication.execute(self)
      else:
        return QTimer().singleShot(self.poll, self.dispatch)

  def ping(self):
    self.nexus.send(Ping("", self.agent.name, int(self.timeout)))
    QTimer().singleShot(int(self.timeout * 500), self.ping)

  def give_structure(self, moniid=None, but=None):
    if moniid is None:
      monis = self.watchers
    else:
      monis = {moniid}
    if but is not None:
      monis = {m for m in self.watchers if m != but}
    if monis:
      places = {Content(p.name, p.tokens) for p in self.agent.places} if not self.secret else set()
      self.nexus.send(GiveStructure(self.agent.name, monis, repr(self.agent), places, self.delay, not bool(self.state), self.edit, self.secret))

  def places_changed(self, places):
    if self.watchers and not self.secret:
      contents = {Content(p.name, p.tokens) for p in places if not p.parent.isfrag}
      if contents:
        self.nexus.send(PlacesChanged(self.agent.name, self.watchers, contents))
  
  def state_changed(self, moniid):
    monis = {m for m in self.watchers if m != moniid}
    if monis:
      self.nexus.send(StateChanged(self.agent.name, monis, self.state != 1))

  def register_listeners(self):
    listeners = set()
    for topic in Task.tasks:
      listeners.add(Listener(self.agent.name, "task", topic))
    for topic in Invocation.invocations:
      listeners.add(Listener(self.agent.name, "invocation", topic))
    for topic in In.sensors:
      listeners.add(Listener(self.agent.name, "communication", topic))
    self.nexus.send(RegisterListeners("", listeners))

  def taskpending(self, topic):
    for task in Task.tasks[topic]:
      task.pending()

  def invocationpending(self, topic):
    invocation = Invocation.invocations[topic]
    invocation.pending()

  def inpending(self, topic):
    for sensor in In.sensors[topic]:
      sensor.pending()
  
  def terminate(self):
    self.nexus.send(TerminatedAgent("", self.agent.name))
    sys.exit(0)
