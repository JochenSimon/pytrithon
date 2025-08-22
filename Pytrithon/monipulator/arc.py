import re
import math
from PyQt5.QtWidgets import *
from .colors import *
from ..utils import WithEnum
from ..pytriontology import *

class Alias(QGraphicsTextItem):
  def __init__(self, parent):
    super().__init__(parent.alias, parent)
    self.parent = parent
    self.setDefaultTextColor(self.parent.canvas.colors.alias)
  
  def paint(self, painter, option, widget):
    painter.setBrush(QBrush(self.parent.canvas.colors.aliasbackground))
    painter.setPen(Qt.NoPen)
    painter.drawRect(self.boundingRect().adjusted(3, 3, -3, -3))
    super().paint(painter, option, widget)

  @property
  def context(self):
    return [("edit alias", self.edit_alias), ("delete link", self.delete_link)] if not self.parent.canvas.figures[self.parent.trans].isfrag or self.parent.canvas.edit else []

  def edit_alias(self):
    self.setTextInteractionFlags(Qt.TextEditorInteraction)
    textcursor = self.textCursor()
    textcursor.select(QTextCursor.Document)
    self.setTextCursor(textcursor)
    self.setFocus()

  def delete_link(self):
    self.parent.figure.arcs.remove(self.parent)  
    self.parent.canvas.scene.removeItem(self.parent)
    if not self.parent.canvas.frag:
      self.parent.canvas.moni.nexus.send(DeleteLinkManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.serial))
  
  def focusOutEvent(self, event):
    self.setTextInteractionFlags(Qt.NoTextInteraction)
    newtext = re.sub("[:;\n]", "", self.toPlainText())
    if self.parent.alias != newtext:
      if not self.parent.canvas.frag:
        self.parent.canvas.moni.nexus.send(AliasManipulation(self.parent.canvas.agent, self.parent.canvas.moni.id, self.parent.serial, newtext))
      self.setPlainText(newtext)
      self.parent.alias = newtext
    else:
      self.setPlainText(self.parent.alias)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.setPlainText(self.parent.alias)
      self.setTextInteractionFlags(Qt.NoTextInteraction)
    elif event.key() == Qt.Key_Return:
      self.focusOutEvent(None)
    else:
      super().keyPressEvent(event)

@WithEnum('Clear Read Take Give Write')
class Arc(QGraphicsLineItem):
  hidden = False
  def __init__(self, canvas, figure, kind, alias, place, trans):
    super().__init__()
    self.serial = len(canvas.arcs)
    canvas.arcs.append(self)
    self.figure = figure

    self.kind = kind
    self.alias = alias
    self.place = place
    self.trans = trans
    self.canvas = canvas
    self.canvas.scene.addItem(self)

    self.text = Alias(self)

  def paint(self, painter, option, widget):
    zoom = self.canvas.zoom
    trans = self.canvas.figures[self.trans]
    place = self.canvas.figures[self.place]
    self.setLine(QLineF(trans.pos[0]*zoom, trans.pos[1]*zoom, place.pos[0]*zoom, place.pos[1]*zoom))
    pen = QPen(Qt.SolidLine)
    pen.setWidth(1)
    pen.setColor(self.canvas.colors.arc)
    painter.setBrush(QBrush(self.canvas.colors.arc))
    painter.setPen(pen)
    painter.drawLine(self.line())
    self.text.setPos(self.boundingRect().center().x()-self.text.boundingRect().width() / 2,
                     self.boundingRect().center().y()-self.text.boundingRect().height() / 2)
    if self.kind in {Arc.Take, Arc.Write, Arc.Clear}:
      diff = place.pos[0]*zoom - trans.pos[0]*zoom, place.pos[1]*zoom - trans.pos[1]*zoom
      angle = -int(math.degrees(math.atan2(diff[1], diff[0])))
      point = trans.touch_point((place.pos[0]*zoom, place.pos[1]*zoom))
      if self.kind is Arc.Clear:
        painter.drawEllipse(int(point.x()-3), int(point.y()-3), 6, 6)
      else:  
        painter.drawPie(int(point.x()-7), int(point.y()-7), 14, 14, (angle-30)*16, 60*16)
    if self.kind in {Arc.Give, Arc.Write}:
      diff = trans.pos[0]*zoom - place.pos[0]*zoom, trans.pos[1]*zoom - place.pos[1]*zoom
      angle = -int(math.degrees(math.atan2(diff[1], diff[0])))
      point = place.touch_point((trans.pos[0]*zoom, trans.pos[1]*zoom))
      painter.drawPie(int(point.x()-7), int(point.y()-7), 14, 14, (angle-30)*16, 60*16)
  
class HiddenArc:
  hidden = True
  def __init__(self, canvas, figure, kind, alias, place, trans):
    self.serial = len(canvas.arcs)
    canvas.arcs.append(self)
    self.figure = figure

    self.kind = kind
    self.alias = alias
    self.place = place
    self.trans = trans
