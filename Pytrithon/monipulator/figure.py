import re
import math
from itertools import takewhile, dropwhile
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ..utils import *
from ..stringify import *
from ..pml import *
from .arc import *
from ..pytriontology import *

arcmap = {"clears": Arc.Clear, "reads": Arc.Read, "takes": Arc.Take, "gives": Arc.Give, "writes": Arc.Write}

class Inscription(QGraphicsTextItem):
  def __init__(self, parent, text, positor, color):
    super().__init__("", parent)
    self.parent = parent
    self.positor = positor
    self.setDefaultTextColor(color)
    Inscription.change(self, text)
  def change(self, text):  
    self.setPlainText(text)
    self.setPos(*self.positor(self.boundingRect().width(), self.boundingRect().height()))

class NameInscription(Inscription):
  def __init__(self, parent, text, positor, color, optional):
    super().__init__(parent, text, positor, color)
    self.optional = optional
    if "#" in self.parent.name:
      self.setPlainText("")

  def change(self, text, new=False):
    if "#" in text:
      self.setPlainText("")
    else:  
      self.setPlainText(text)
    self.setPos(*self.positor(self.boundingRect().width(), self.boundingRect().height()))
    if new:
      self.parent.name = text

  def focusOutEvent(self, event):
    newtext = re.sub(r"[^\w]", "", self.toPlainText())
    if self.parent.name != newtext:
      if self.toPlainText() == "<taken>":
        self.setFocus()
      elif newtext in self.parent.canvas.figures or not self.optional and newtext == "":
        self.change("<taken>")
        textcursor = self.textCursor()
        textcursor.select(QTextCursor.Document)
        self.setTextCursor(textcursor)
        self.setFocus()
      else:  
        if newtext == "":
          newtext = "#0"
        if not self.parent.canvas.frag:
          self.parent.canvas.moni.nexus.send(NameManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, newtext))
        renamekey(self.parent.canvas.figures, self.parent.name, newtext)
        to_update = set()
        for arc in self.parent.canvas.arcs:
          if arc.place == self.parent.name:
            arc.place = newtext
            to_update.add(self.parent.canvas.figures[arc.trans])
          if arc.trans == self.parent.name:
            arc.trans = newtext
        for trans in to_update:
          trans.update_hidden()
        newname = flood(self.parent.canvas.figures, self.parent.canvas.arcs, newtext)
        self.change(newname, True)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
    else:  
      self.change(self.parent.name)
      self.setTextInteractionFlags(Qt.NoTextInteraction)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.change(self.parent.name)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    elif event.key() == Qt.Key_Return:
      self.focusOutEvent(None)
    else:
      super().keyPressEvent(event)

class InscrInscription(Inscription):
  def __init__(self, parent, text, positor, color, frag):
    super().__init__(parent, text, positor, color)
    self.frag = frag
    
  def change(self, text):
    super().change(text)
    self.parent.inscr = text

  def focusOutEvent(self, event):
    new_text = self.toPlainText()
    if self.parent.inscr != new_text:
      if self.frag:
        arcs = list(takewhile(lambda l: re.match(linker, l), new_text.split("\n")))
        inscr = list(dropwhile(lambda l: re.match(linker, l), new_text.split("\n")))
        if not "".join(inscr).strip():
          inscr = ["frag"]
        elif not re.sub(r"[^\w.]", "", inscr[0]):
          inscr[0] = "frag"
        else:  
          inscr[0] = re.sub(r"[^\w.]", "", inscr[0])
        while ".." in inscr[0]:
          inscr[0] = inscr[0].replace("..", ".")
        if inscr[0] == ".":
          inscr[0] = "frag"
        if inscr[0].startswith("."):
          inscr[0] = inscr[0][1:]
        if inscr[0].endswith("."):
          inscr[0] = inscr[0][:-1]
        new_text = "\n".join(arcs + inscr)
      if not self.parent.canvas.frag:
        self.parent.canvas.moni.nexus.send(InscriptionManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, new_text))
      if self.parent.istrans or self.parent.isgadget or self.parent.isfrag:
        arcs, inscr, _ = parselinks(new_text)
        for hidden in [arc for arc in self.parent.arcs if arc.hidden == True]:
          self.parent.arcs.remove(hidden)
        for kind,alias,place,hidden in arcs:
          if place in self.parent.canvas.figures and self.parent.canvas.figures[place].isplace:
            if not hidden:
              self.parent.arcs.append(Arc(self.parent.canvas, self.parent, arcmap[kind], alias, place, self.parent.name))
            else:  
              self.parent.arcs.append(HiddenArc(self.parent.canvas, self.parent, arcmap[kind], alias, place, self.parent.name))
        self.parent.inscr = inscr
        self.parent.update_hidden()    
      else:
        self.change(new_text)
    self.setTextInteractionFlags(Qt.NoTextInteraction)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      super().change(self.parent.inscr)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    else:
      super().keyPressEvent(event)

class TypeInscription(Inscription):
  def change(self, text):
    super().change(text)
    self.parent.typing = text

  def focusOutEvent(self, event):
    newtext = re.sub(r"[:;\s]", "", self.toPlainText())
    if self.parent.typing != newtext:
      if not self.parent.canvas.frag:
        self.parent.canvas.moni.nexus.send(TypeManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, newtext))
      self.change(newtext)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    else:
      super().change(self.parent.typing)
      self.setTextInteractionFlags(Qt.NoTextInteraction)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      super().change(self.parent.typing)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    elif event.key() == Qt.Key_Return:
      self.focusOutEvent(None)
    else:
      super().keyPressEvent(event)

class PriorityInscription(Inscription):
  def change(self, text):
    super().change(text)
    self.parent.priority = text

  def focusOutEvent(self, event):
    try:
      float(self.toPlainText())
      newtext = self.toPlainText().strip()
    except ValueError:
      newtext = ""
    if self.parent.priority != newtext:
      if not self.parent.canvas.frag:
        self.parent.canvas.moni.nexus.send(PriorityManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, newtext))
      self.change(newtext)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    else:
      super().change(self.parent.priority)
      self.setTextInteractionFlags(Qt.NoTextInteraction)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      super().change(self.parent.priority)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    elif event.key() == Qt.Key_Return:
      self.focusOutEvent(None)
    else:
      super().keyPressEvent(event)

class CommentText(QGraphicsTextItem):
  def __init__(self, parent):
    super().__init__("", parent)
    self.parent = parent

  def edit_comment(self):  
    self.setTextInteractionFlags(Qt.TextEditorInteraction)
    self.setFocus()

  def delete_comment(self):  
    if not self.parent.canvas.frag:
      self.parent.canvas.moni.nexus.send(DeleteElementManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name))
    self.parent.canvas.scene.removeItem(self.parent)
    del self.parent.canvas.figures[self.parent.name]

  def change_color(self):
    color = QColorDialog.getColor()
    font_color = color.name()[1:]
    if font_color != self.parent.font_color:
      if font_color == self.parent.canvas.colors.comment.name()[1:]:
        self.parent.font_color = None
        self.setDefaultTextColor(self.parent.canvas.colors.comment)
      else:  
        self.parent.font_color = font_color
        self.setDefaultTextColor(QColor(int(self.parent.font_color[:2], 16), int(self.parent.font_color[2:4], 16), int(self.parent.font_color[4:6], 16)))
      self.parent.canvas.moni.nexus.send(CommentManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, self.parent.font_color, self.parent.font_size, self.parent.font_type))

  def change_font(self):
    font, ok = QFontDialog.getFont(self.parent.canvas.moni.app.font(), self.parent.canvas.moni)
    if ok:
      default_font = self.parent.canvas.moni.app.font()
      self.setFont(font)
      if font.pointSize() != default_font.pointSize():
        self.parent.font_size = str(font.pointSize())
      else:
        self.parent.font_size = None
      if font.family() != default_font.family():
        self.parent.font_size = str(font.pointSize())
        self.parent.font_type = font.family()
      else:
        self.parent.font_type = None
      self.parent.canvas.moni.nexus.send(CommentManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, self.parent.font_color, self.parent.font_size, self.parent.font_type))

  def focusOutEvent(self, event):
    if re.sub(r"[\s]", "", self.toPlainText()):
      if self.parent.inscr != self.toPlainText():
        if not self.parent.canvas.frag:
          self.parent.canvas.moni.nexus.send(InscriptionManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.name, self.toPlainText()))
        self.parent.inscr = self.toPlainText()
    else:
      self.setPlainText(self.parent.inscr)
    self.setTextInteractionFlags(Qt.NoTextInteraction)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.setPlainText(self.parent.inscr)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    else:
      super().keyPressEvent(event)

  @property
  def context(self):  
    return [("edit comment", self.edit_comment), ("delete comment", self.delete_comment), ("change color", self.change_color), ("change font", self.change_font)]

class CommentFigure(QGraphicsItem):    
  type = "comment"
  ismeta = False
  isplace = False
  istrans = False
  isgadget = False
  isfrag = False
  iscomment = True
  def __init__(self, canvas, name, inside, inscr, args, pos):
    super().__init__(None)
    self.setFlags(QGraphicsItem.ItemIsMovable |
                  QGraphicsItem.ItemIsFocusable |
                  QGraphicsItem.ItemSendsGeometryChanges)
    self.canvas = canvas
    zoom = self.canvas.zoom
    self.name = name
    self.inscr = inscr
    self.pos = pos

    self.created = False

    if args.count(",") == 2:
      self.font_color = args.split(",")[0]
      self.font_size = args.split(",")[1]
      self.font_type = args.split(",")[2]
    elif "," in args:
      self.font_color = args.split(",")[0]
      self.font_size = args.split(",")[1]
      self.font_type = None
    elif args:
      self.font_color = args
      self.font_size = None
      self.font_type = None
    else:  
      self.font_color = None
      self.font_size = None
      self.font_type = None

    self.text = CommentText(self)
    self.text.setPlainText(self.inscr)

    self.setPos(QPointF(self.pos[0]*zoom, self.pos[1]*zoom))
    font = self.canvas.moni.app.font()
    if not self.font_size:
      font_size = font.pointSize()
    else:
      font_size = self.font_size
    if not self.font_type:
      font_type = font.family()
    else:
      font_type = self.font_type
    self.text.setFont(QFont(font_type, int(font_size)))
    if self.font_color:
      self.text.setDefaultTextColor(QColor(int(self.font_color[:2], 16), int(self.font_color[2:4], 16), int(self.font_color[4:6], 16)))
    else:  
      self.text.setDefaultTextColor(self.canvas.colors.comment)
    self.setZValue(2)
    
    self.canvas.scene.clearSelection()
    self.canvas.scene.addItem(self)

  def itemChange(self, change, value):
    if change == QGraphicsItem.ItemPositionChange:
      if self.created:
        zoom = self.canvas.zoom
        x, y = round(value.x()/zoom*10)*zoom/10, round(value.y()/zoom*10)*zoom/10
        if (not math.isclose(x/zoom, self.pos[0])) or (not math.isclose(y/zoom, self.pos[1])):
          self.pos = x/zoom, y/zoom
          if not self.canvas.frag:
            self.canvas.moni.nexus.send(MoveManipulation(self.canvas.agent, self.canvas.moni.id, self.name, self.pos[0], self.pos[1]))
          self.canvas.viewport().repaint()
        return QPointF(x, y)
      else:
        self.created = True
    return QGraphicsItem.itemChange(self, change, value)  

  def boundingRect(self):
    return self.text.boundingRect()

  def paint(self, painter, option, widget):
    pass

  def __str__(self):
    return stringify_comment(self)

class Figure(QGraphicsItem):
  ismeta = False
  isplace = False
  istrans = False
  isgadget = False
  isfrag = False
  iscomment = False
  def __init__(self, canvas, name, inside, inscr, args, pos):
    super().__init__()
    self.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable |
                  QGraphicsItem.ItemIsFocusable |
                  QGraphicsItem.ItemSendsGeometryChanges)
    self.canvas = canvas
    zoom = self.canvas.zoom
    self.name = name
    self.inscr = inscr
    self.pos = pos

    self.created = False

    self.firing = False
    self.errored = False

    self.width, self.height = self.size

    self.rect = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)
    self.setPos(QPointF(self.pos[0]*zoom, self.pos[1]*zoom))
    self.setZValue(1)
    self.style = Qt.SolidLine

    self.canvas.scene.clearSelection()
    self.canvas.scene.addItem(self)

    self.header = NameInscription(self, name, lambda x,y: (-x / 2, -y - self.height / 2), self.canvas.colors.inscription, not self.isplace)
    self.inside = Inscription(self, inside, lambda x,y: (-x / 2, -y / 2), self.canvas.colors.element[self.type]) if inside else None
    self.footer = InscrInscription(self, inscr, lambda x,y: (-x / 2, self.height / 2), self.canvas.colors.inscription, self.isfrag)

  @property
  def context(self):
    return [("delete element", self.delete_element)] if self.canvas.edit else []

  def edit_name(self):
    self.header.setTextInteractionFlags(Qt.TextEditorInteraction)
    textcursor = self.header.textCursor()
    textcursor.select(QTextCursor.Document)
    self.header.setTextCursor(textcursor)
    self.header.setFocus()

  def delete_element(self):
    if not self.canvas.frag:
      self.canvas.moni.nexus.send(DeleteElementManipulation(self.canvas.agent, self.canvas.moni.id, self.name))
    if self.isplace:
      to_update = set()
      for arc in self.canvas.arcs:
        if arc.place == self.name:
          if arc.trans in self.canvas.figures and arc in self.canvas.figures[arc.trans].arcs:
            self.canvas.figures[arc.trans].arcs.remove(arc)
            if not arc.hidden:
              self.canvas.scene.removeItem(arc)
            else:
              to_update.add(self.canvas.figures[arc.trans])
      for trans in to_update:
        trans.update_hidden()
    if self.istrans or self.isgadget:
      for arc in [a for a in self.arcs]:
        self.arcs.remove(arc)
        if not arc.hidden:
          self.canvas.scene.removeItem(arc)
    self.canvas.scene.removeItem(self)
    del self.canvas.figures[self.name]    
    flood(self.canvas.figures, self.canvas.arcs)

  def paint(self, painter, option, widget):
    pen = QPen(self.style)
    pen.setWidth(1)
    is_selected = bool(option.state & QStyle.State_Selected)
    is_firing = self.canvas.firing == self.name
    pen.setColor(self.canvas.colors.transborder[is_firing + self.errored * 2 + is_selected * 4])
    painter.setPen(pen)
  
  def boundingRect(self):
    return self.rect.adjusted(-2, -2, 2, 2)

  def itemChange(self, change, value):
    if change == QGraphicsItem.ItemPositionChange:
      if self.created:
        zoom = self.canvas.zoom
        x, y = round(value.x()/zoom)*zoom, round(value.y()/zoom)*zoom
        if (not math.isclose(x/zoom, self.pos[0])) or (not math.isclose(y/zoom, self.pos[1])):
          self.pos = int(x/zoom), int(y/zoom)
          if not self.canvas.frag:
            self.canvas.moni.nexus.send(MoveManipulation(self.canvas.agent, self.canvas.moni.id, self.name, self.pos[0], self.pos[1]))
          self.canvas.viewport().repaint()
        return QPointF(x, y)
      else:
        self.created = True
    return QGraphicsItem.itemChange(self, change, value)  

class MetaFigure(Figure):
  ismeta = True
  @property
  def context(self):
    return ([("edit name", self.edit_name)] if self.canvas.edit else []) + super().context + ([("edit inscription", self.edit_inscription)] if self.canvas.edit else [])

  def edit_inscription(self):
    self.footer.setTextInteractionFlags(Qt.TextEditorInteraction)
    textcursor = self.footer.textCursor()
    textcursor.select(QTextCursor.Document)
    self.footer.setTextCursor(textcursor)
    self.footer.setFocus()

  def paint(self, painter, option, widget):
    super().paint(painter, option, widget)
    gradient = QLinearGradient(-7.0, -21.0, 7.0, 21.0)
    gradient.setColorAt(0, self.canvas.colors.gradient0)
    gradient.setColorAt(1, self.canvas.colors.gradient1)
    brush = QBrush(gradient)
    painter.setBrush(brush)
    painter.drawPolygon(QPoint(int(self.rect.left()), int(self.rect.bottom())),
                        QPoint(int((self.rect.left()+self.rect.right())//2), int(self.rect.top())),
                        QPoint(int(self.rect.right()), int(self.rect.bottom())),
                        QPoint(int(self.rect.left()), int(self.rect.bottom())))
  
  def __str__(self):
    return stringify_meta(self)

class SelfFigure(MetaFigure):
  type = "self"
  size = 37,27

class ModuleFigure(MetaFigure):
  type = "module"
  size = 37,27

class OntologyFigure(MetaFigure):
  type = "ontology"
  size = 37,27

class PlaceFigure(Figure):
  type = "place"
  isplace = True
  size = 23,23

  def __init__(self, canvas, name, inside, inscr, args, pos):
    super().__init__(canvas, name, inside, inscr, args, pos)
    self.typing = args
    self.typeinscr = TypeInscription(self, self.typing, lambda x,y: (-x / 2, -y / 2), self.canvas.colors.typing)
    self.tokens = Inscription(self, "", lambda x,y: (-x / 2, -y / 2), self.canvas.colors.inscription)
  
  @property
  def context(self):
    return ([("edit name", self.edit_name)] if self.canvas.edit else []) + super().context + [("edit seed", self.edit_seed)] + ([("edit type", self.edit_type)] if not isinstance(self, FlowFigure) else []) + ([("change to.{}".format(t), lambda p=self,t=t: self.canvas.change_to(p,t)) for t in ("var", "know", "flow", "pool", "queue", "stack", "heap", "set", "phantom") if t != self.type] if self.canvas.edit else [])

  def edit_seed(self):
    self.footer.setTextInteractionFlags(Qt.TextEditorInteraction)
    textcursor = self.footer.textCursor()
    textcursor.select(QTextCursor.Document)
    self.footer.setTextCursor(textcursor)
    self.footer.setFocus()

  def edit_type(self):
    self.typeinscr.setTextInteractionFlags(Qt.TextEditorInteraction)
    textcursor = self.typeinscr.textCursor()
    textcursor.select(QTextCursor.Document)
    self.typeinscr.setTextCursor(textcursor)
    self.typeinscr.setFocus()

  @property
  def seed(self):
    return self.inscr

  def change(self, text):
    self.tokens.change(text)

  def shape(self):
    path = QPainterPath()
    path.addEllipse(self.rect)
    return path

  def paint(self, painter, option, widget):
    super().paint(painter, option, widget)
    gradient = QRadialGradient(0.0, 0.0, 21, 5, 15)
    gradient.setColorAt(0, self.canvas.colors.gradient0)
    gradient.setColorAt(1, self.canvas.colors.gradient1)
    brush = QBrush(gradient)
    painter.setBrush(brush)
    painter.drawEllipse(self.rect)

  def touch_point(self, pos):
    zoom = self.canvas.zoom
    x, y = self.pos[0]*zoom, self.pos[1]*zoom
    dx, dy = pos[0] - x, pos[1] - y
    sx, sy = self.size[0] / 2, self.size[1] / 2
    angle = math.atan2(dy, dx)
    return QPointF(sx * math.cos(angle) + x, sy * math.sin(angle) + y)

  def __str__(self):
    return stringify_place(self)

class VariableFigure(PlaceFigure):
  type = "var"
  size = 23,23

class KnowledgeFigure(PlaceFigure):
  type = "know"
  size = 23,23

class FlowFigure(PlaceFigure):
  type = "flow"
  size = 23,23
  def __init__(self, canvas, name, inside, inscr, args, pos):
    super().__init__(canvas, name, inside, inscr, args, pos)
    self.typing = ""
    self.token = False

  def change(self, text):
    self.token = text == "()"
    self.update()

  def paint(self, painter, option, widget):
    super().paint(painter, option, widget)
    if self.token:
      brush = QBrush(self.canvas.colors.flowtoken)
    else:
      brush = QBrush(self.canvas.colors.flowempty)
    pen = QPen(self.canvas.colors.flow)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawEllipse(self.rect.adjusted(8, 8, -8, -8))

class PoolFigure(PlaceFigure):
  type = "pool"
  size = 37,37

class QueueFigure(PlaceFigure):
  type = "queue"
  size = 37,37

class StackFigure(PlaceFigure):
  type = "stack"
  size = 37,37

class HeapFigure(PlaceFigure):
  type = "heap"
  size = 37,37

class SetFigure(PlaceFigure):
  type = "set"
  size = 37,37

class PhantomFigure(PlaceFigure):
  type = "phantom"
  size = 23,23

  def paint(self, painter, option, widget):
    Figure.paint(self, painter, option, widget)
    painter.setBrush(QBrush(self.canvas.colors.fragbackground))
    painter.drawEllipse(self.rect)

class TransFigure(Figure):
  type = "trans"
  istrans = True
  size = 23,17

  def __init__(self, canvas, name, inside, inscr, args, pos):
    super().__init__(canvas, name, inside, inscr, args, pos)
    self.priority = args
    self.prioinscr = PriorityInscription(self, self.priority, lambda x,y: (-x / 2, -y / 2), self.canvas.colors.priority)
    self.arcs = []

  @property
  def context(self):
    return super().context + ([("edit inscription", self.edit_inscription)] if self.type not in {"gadget"} or self.canvas.edit else []) + ([("edit priority", self.edit_priority)] if self.type not in {"frag"} else [])

  def edit_inscription(self):
    self.footer.setTextInteractionFlags(Qt.TextEditorInteraction)
    self.footer.setFocus()

  def edit_priority(self):
    self.prioinscr.setTextInteractionFlags(Qt.TextEditorInteraction)
    self.prioinscr.setFocus()

  @property
  def clears(self):
    return [arc for arc in self.arcs if arc.kind is Arc.Clear]

  @property
  def reads(self):
    return [arc for arc in self.arcs if arc.kind is Arc.Read]

  @property
  def takes(self):
    return [arc for arc in self.arcs if arc.kind is Arc.Take]

  @property
  def gives(self):
    return [arc for arc in self.arcs if arc.kind is Arc.Give]

  @property
  def writes(self):
    return [arc for arc in self.arcs if arc.kind is Arc.Write]

  def update_hidden(self):
    inscr = ""
    if [arc for arc in self.clears if arc.hidden]:
      inscr += "clears: " + "; ".join(":"+arc.place if arc.alias == arc.place else arc.alias+":"+arc.place if arc.alias else arc.place for arc in self.clears if arc.hidden) + "\n"
    if [arc for arc in self.reads if arc.hidden]:
      inscr += "reads: " + "; ".join(":"+arc.place if arc.alias == arc.place else arc.alias+":"+arc.place if arc.alias else arc.place for arc in self.reads if arc.hidden) + "\n"
    if [arc for arc in self.takes if arc.hidden]:
      inscr += "takes: " + "; ".join(":"+arc.place if arc.alias == arc.place else arc.alias+":"+arc.place if arc.alias else arc.place for arc in self.takes if arc.hidden) + "\n"
    if [arc for arc in self.gives if arc.hidden]:
      inscr += "gives: " + "; ".join(":"+arc.place if arc.alias == arc.place else arc.alias+":"+arc.place if arc.alias else arc.place for arc in self.gives if arc.hidden) + "\n"
    if [arc for arc in self.writes if arc.hidden]:
      inscr += "writes: " + "; ".join(":"+arc.place if arc.alias == arc.place else arc.alias+":"+arc.place if arc.alias else arc.place for arc in self.writes if arc.hidden) + "\n"
    inscr += "\n".join(line for line in self.inscr.split("\n") if not re.match(linker, line))
    self.footer.change(inscr)
  
  def shape(self):
    path = QPainterPath()
    path.addRect(self.rect)
    return path

  def paint(self, painter, option, widget):
    super().paint(painter, option, widget)
    gradient = QLinearGradient(-7.0, -21.0, 7.0, 21.0)
    gradient.setColorAt(0, self.canvas.colors.gradient0)
    gradient.setColorAt(1, self.canvas.colors.gradient1)
    brush = QBrush(gradient)
    painter.setBrush(brush)
    painter.drawRect(self.rect)

  def touch_point(self, pos):
    zoom = self.canvas.zoom
    x, y = self.pos[0]*zoom, self.pos[1]*zoom
    dx, dy = pos[0] - x, pos[1] - y
    sx, sy = self.size[0] / 1.5, self.size[1] / 1.5
    angle = math.atan2(dy, dx)
    return QPointF(sx * math.cos(angle) + x, sy * math.sin(angle) + y)

  def __str__(self):
    return stringify_transition(self)

class PythonFigure(TransFigure):
  type = "python"
  size = 17,17

class IfFigure(TransFigure):
  type = "if"
  size = 17,17

class ChoiceFigure(TransFigure):
  type = "choice"
  size = 23,17

class MergeFigure(TransFigure):
  type = "merge"
  size = 23,17

class TimerFigure(TransFigure):
  type = "timer"
  size = 23,17

class IteratorFigure(TransFigure):
  type = "iterator"
  size = 23,17

class SignalFigure(TransFigure):
  type = "signal"
  size = 23,17

class SlotFigure(TransFigure):
  type = "slot"
  size = 23,17

class NethodFigure(TransFigure):
  type = "nethod"
  size = 23,17
  
class CallFigure(TransFigure):
  type = "call"
  size = 23,17
  
class ReturnFigure(TransFigure):
  type = "return"
  size = 23,17
  
class RaiseFigure(TransFigure):
  type = "raise"
  size = 23,17
  
class OutFigure(TransFigure):
  type = "out"
  size = 23,17
  
class InFigure(TransFigure):
  type = "in"
  size = 23,17
  
class TaskFigure(TransFigure):
  type = "task"
  size = 23,17
  
class InvocationFigure(TransFigure):
  type = "invoke"
  size = 23,17
  
class ResultFigure(TransFigure):
  type = "result"
  size = 23,17
  
class FailFigure(TransFigure):
  type = "fail"
  size = 23,17
  
class SpawnFigure(TransFigure):
  type = "spawn"
  size = 23,23

class TerminateFigure(TransFigure):
  type = "terminate"
  size = 23,23

class RoundRectFigure(TransFigure):
  type = "roundrect"
  def shape(self):
     path = QPainterPath()
     path.addRoundedRect(self.rect, 10, 10)
     return path

  def paint(self, painter, option, widget):
    Figure.paint(self, painter, option, widget)
    gradient = QConicalGradient(0, 0, 123)
    gradient.setColorAt(0.0, self.canvas.colors.gradient0)
    gradient.setColorAt(0.5, self.canvas.colors.gradient1)
    gradient.setColorAt(1.0, self.canvas.colors.gradient0)
    brush = QBrush(gradient)
    painter.setBrush(brush)
    painter.drawRoundedRect(self.rect, 10, 10)

  def touch_point(self, pos):
    zoom = self.canvas.zoom
    x, y = self.pos[0]*zoom, self.pos[1]*zoom
    dx, dy = pos[0] - x, pos[1] - y
    sx, sy = self.size[0] / 2, self.size[1] / 2
    angle = math.atan2(dy, dx)
    return QPointF(sx * math.cos(angle) + x, sy * math.sin(angle) + y)

class SocketFigure(RoundRectFigure):
  type = "gadget"
  istrans = False
  isgadget = True
  size = 42,42
  @property
  def context(self):
    return ([("edit name", self.edit_name)] if self.canvas.edit else []) + super().context

class FragmentFigure(RoundRectFigure):
  type = "frag"
  isgadget = False
  isfrag = True
  size = 42,42
  @property
  def context(self):
    return ([("edit name", self.edit_name)] + super().context if self.canvas.edit else []) + [("edit fragment", lambda f=sanitize(self.inscr).split("\n")[0]: self.canvas.moni.open_fragment(f))]
