from collections import OrderedDict, defaultdict
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ..pml import *
from .figure import *
from .arc import *
from ..utils import *

assoc = {"self": SelfFigure, "module": ModuleFigure, "ontology": OntologyFigure, "var": VariableFigure, "know": KnowledgeFigure, "flow": FlowFigure, "pool": PoolFigure, "queue": QueueFigure, "stack": StackFigure, "heap": HeapFigure, "set": SetFigure, "phantom": PhantomFigure, "python": PythonFigure, "if": IfFigure, "choice": ChoiceFigure, "merge": MergeFigure, "timer": TimerFigure, "iterator": IteratorFigure, "signal": SignalFigure, "slot": SlotFigure, "nethod": NethodFigure, "call": CallFigure, "return": ReturnFigure, "raise": RaiseFigure, "out": OutFigure, "in": InFigure, "task": TaskFigure, "invoke": InvocationFigure, "result": ResultFigure, "fail": FailFigure, "spawn": SpawnFigure, "terminate": TerminateFigure, "gadget": SocketFigure, "frag": FragmentFigure, "comment": CommentFigure}
arcmap = {"clears": Arc.Clear, "reads": Arc.Read, "takes": Arc.Take, "gives": Arc.Give, "writes": Arc.Write}
insides = defaultdict(str)
insides.update({"self": "self", "module": "mod", "ontology": "ont", "know": "k", "pool": "p", "queue": "q", "stack": "s", "heap": "h", "set": "{}", "phantom": "ph", "if": "if", "choice": "ch", "merge": "mr", "timer": "tim", "iterator": "itr", "signal": "sig", "slot": "slot", "nethod": "nth", "call": "call", "return": "ret", "raise": "rs", "out": "out", "in": "in", "task": "tsk", "invoke": "inv", "result": "res", "fail": "fai", "spawn": "sp", "terminate": "ter", "frag": "frag"})


class Canvas(QGraphicsView):
  def __init__(self, moni, structure, delay, halted, edit, secret, frag, zoom, colors):
    super().__init__(moni)
    self.moni = moni
    self.delay = delay
    self.halted = halted
    self.edit = edit
    self.secret = secret
    self.frag = frag
    self.zoom = zoom
    self.colors = colors
    self.figures = OrderedDict()
    self.arcs = []
    self.firing = None
    self.zoom_factor = 1

    root = parse(structure)

    self.scene = QGraphicsScene(self)
    self.setScene(self.scene)

    for node in root.children:
      self.figures[node.name] = assoc[node.keyword](self, node.name, insides[node.keyword], node.suite, node.args, node.pos)
      for kind,alias,place,hidden in node.links:
        if not hidden:
          self.figures[node.name].arcs.append(Arc(self, self.figures[node.name], arcmap[kind], alias, place, node.name))
        else:  
          self.figures[node.name].arcs.append(HiddenArc(self, self.figures[node.name], arcmap[kind], alias, place, node.name))

    self.contextMenu = QMenu(self)
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self.on_context_menu)

    self.reset_zoom_sc = QShortcut(QKeySequence("Ctrl+0"), self)
    self.reset_zoom_sc.activated.connect(self.reset_zoom)
    self.zoom_in_sc = QShortcut(QKeySequence("Ctrl+="), self)
    self.zoom_in_sc.activated.connect(self.zoom_in)
    self.zoom_out_sc = QShortcut(QKeySequence("Ctrl+-"), self)
    self.zoom_out_sc.activated.connect(self.zoom_out)

  def reset_zoom(self):
    self.zoom_factor = 1
    self.setTransform(QTransform())
    self.scene.update()

  def zoom_in(self):
    self.zoom_factor *= 1.05
    transform = QTransform()
    transform.scale(self.zoom_factor, self.zoom_factor)
    self.setTransform(transform)
    self.scene.update()

  def zoom_out(self):
    self.zoom_factor /= 1.05
    transform = QTransform()
    transform.scale(self.zoom_factor, self.zoom_factor)
    self.setTransform(transform)
    self.scene.update()

  def wheelEvent(self, event):
    if QApplication.keyboardModifiers() == Qt.ControlModifier:
      if event.angleDelta().y() > 0:
        self.zoom_in()
      elif event.angleDelta().y() < 0:
        self.zoom_out()
    else:
      super().wheelEvent(event)

  def enable_buttons(self):
    self.moni.controls.terminate_button.setEnabled(True)
    if self.frag:
      self.setBackgroundBrush(QBrush(self.colors.fragbackground))
      self.moni.controls.edit_button.setEnabled(False)
      self.moni.controls.init_button.setEnabled(False)
      self.moni.controls.reset_button.setEnabled(False)
      self.moni.controls.run_button.setEnabled(False)
      self.moni.controls.step_button.setEnabled(False)
      self.moni.controls.halt_button.setEnabled(False)
    elif self.edit:  
      self.setBackgroundBrush(QBrush(self.colors.editbackground))
      self.moni.controls.edit_button.setEnabled(False)
      self.moni.controls.init_button.setEnabled(True)
      self.moni.controls.reset_button.setEnabled(False)
      if self.halted:
        self.moni.controls.run_button.setEnabled(True)
      else:  
        self.moni.controls.run_button.setEnabled(False)
      self.moni.controls.step_button.setEnabled(False)
      if self.halted:
        self.moni.controls.halt_button.setEnabled(False)
      else:
        self.moni.controls.halt_button.setEnabled(True)
    else:
      self.moni.controls.edit_button.setEnabled(True)
      self.moni.controls.init_button.setEnabled(False)
      self.moni.controls.reset_button.setEnabled(True)
      if self.halted:
        self.setBackgroundBrush(QBrush(self.colors.haltbackground))
        self.moni.controls.run_button.setEnabled(True)
        self.moni.controls.step_button.setEnabled(True)
        self.moni.controls.halt_button.setEnabled(False)
      else:  
        if self.secret:
          self.setBackgroundBrush(QBrush(self.colors.secretbackground))
        else:  
          self.setBackgroundBrush(QBrush(self.colors.background))
        self.moni.controls.run_button.setEnabled(False)
        self.moni.controls.step_button.setEnabled(False)
        self.moni.controls.halt_button.setEnabled(True)

  def on_context_menu(self, point):
    self.hascontext = False
    self.submenus = {}
    self.metamenu = None
    self.placemenu = None
    self.transmenu = None
    self.contextMenu.clear()
    for item in self.items(point):
      if hasattr(item, "context"):
        for text, action in item.context:
          if "." in text:
            submenu, subtext = text.split(".")
            if submenu not in self.submenus:
              self.submenus[submenu] = self.contextMenu.addMenu(submenu)
            self.submenus[submenu].addAction(subtext, action)
            self.hascontext = True
          else:  
            self.contextMenu.addAction(text, action)
            self.hascontext = True
        break
    else:
      if self.edit:
        for element in assoc:
          if assoc[element].ismeta:
            if self.metamenu is None:
              self.metamenu = self.contextMenu.addMenu("create meta")
            self.metamenu.addAction(element, lambda t=element,p=point: self.on_new_element(t,p))
          if assoc[element].isplace:
            if self.placemenu is None:
              self.placemenu = self.contextMenu.addMenu("create place")
            self.placemenu.addAction(element, lambda t=element,p=point: self.on_new_element(t,p))
          if assoc[element].istrans:
            if self.transmenu is None:
              self.transmenu = self.contextMenu.addMenu("create transition")
            self.transmenu.addAction(element, lambda t=element,p=point: self.on_new_element(t,p))
          if assoc[element].isgadget:
            self.contextMenu.addAction("create gadget", lambda t=element,p=point: self.on_new_element(t,p))
          if assoc[element].isfrag:
            self.contextMenu.addAction("embed fragment", lambda t=element,p=point: self.on_new_element(t,p))
          if assoc[element].iscomment:
            self.contextMenu.addAction("add comment", lambda t=element,p=point: self.on_new_element(t,p))
        self.hascontext = True
        
    if self.hascontext:    
      self.contextMenu.exec(self.mapToGlobal(point))    

  def on_new_element(self, type, point):
    zoom = self.zoom
    if not self.figures:
      point = QPoint(0, 0)
    else:
      point = self.mapToScene(point)
    if type == "comment":  
      x, y = round(point.x()/zoom*10)*zoom/10, round(point.y()/zoom*10)*zoom/10
    else:  
      x, y = round(point.x()/zoom)*zoom, round(point.y()/zoom)*zoom
    if type in named_els:
      nextname = next(str(i) for i in count() if i not in {int(name) for name in self.figures if name.isdigit()})
      figure = assoc[type](self, nextname, insides[type], "", "", (x/zoom, y/zoom))
      self.figures[nextname] = figure
    else:
      serialnames = {int(name.split("#")[1]) for name in self.figures if name.startswith("#")}
      nextserial = "#{}".format((max(serialnames) if serialnames else 0) + 1)
      figure = assoc[type](self, nextserial, insides[type], "<comment>" if type == "comment" else "frag" if type == "frag" else "", "", (x/zoom, y/zoom))
      self.figures[nextserial] = figure
    if not self.frag:
      self.moni.nexus.send(CreateManipulation(self.agent, self.moni.id, type, figure.name, "", (x/zoom, y/zoom)))

  def change_to(self, place, type):
    self.scene.removeItem(place)
    self.figures[place.name] = assoc[type](self, place.name, insides[type], place.inscr, "" if isinstance(place, FlowFigure) else place.typing, place.pos)
    if not self.frag:
      self.moni.nexus.send(ChangeManipulation(self.agent, self.moni.id, place.name, type))

  def __repr__(self):
    return "\n".join(str(fig) for fig in self.figures.values()) + "\n"
