import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Pytrithon import Gadget, Concept, ontologize

exec(ontologize("""
concept Player:
  slot aid: str
  slot name: str
  slot turn: bool
  slot rerolls: int
  slot dice: [int]
  slot keep: [bool]
  slot scores: [int]
  @classmethod
  def new(cls, aid, name):
    return cls(aid, name, False, 2, [0]*5, [False]*5, [-1]*6+[0]+[-1]*7+[0])
"""))

categories = ["Ones", "Twos", "Threes", "Fours", "Fives", "Sixes", "Bonus: 0", "3 of a Kind", "4 of a Kind", "Full House", "Sml. Straight", "Lg. Straight", "Yahtzee", "Chance", "Total: 0"]

def random_dice():
  return [random.randint(1, 6) for _ in range(5)]

def reroll_dice(dice, keep):
  for i,(d,k) in enumerate(zip(list(dice), keep)):
    if not k:
      dice[i] = random.randint(1, 6)

def isofakind(dice, num):
  for v in range(1,7):
    if len([d for d in dice if d == v]) >= num:
      return True

def isfullhouse(dice):
  for v in range(1,7):
    for u in range(1,7):
      if len([d for d in dice if d == v]) == 3 and len([d for d in dice if d == u]) == 2:
        return True

def issmlstraight(dice):
  for v in range(1,4):
    if v in dice and v+1 in dice and v+2 in dice and v+3 in dice:
      return True

def choose(player, choice):
  index = categories.index(choice)
  dice = player.dice
  match index:
    case i if i <= 5:
      player.scores[index] = sum(die for die in dice if die == index+1)
    case 7 | 8:  
      player.scores[index] = sum(die for die in dice) if isofakind(dice, index-4) else 0
    case 9:
      player.scores[index] = 25 if isfullhouse(dice) else 0
    case 10:
      player.scores[index] = 30 if issmlstraight(dice) else 0
    case 11:
      player.scores[index] = 40 if sorted(dice) == [1,2,3,4,5] or sorted(dice) == [2,3,4,5,6] else 0
    case 12:
      player.scores[index] = 50 if len(set(dice)) == 1 else 0
    case 13:
      player.scores[index] = sum(dice)
      

def total(player):
  return sum(s for s in player.scores if s != -1) + (35 if sum(player.scores[:6]) >= 63 else 0)

class Dice(QWidget):
  def __init__(self, parent):
    QWidget.__init__(self)
    self.parent = parent
    self.layout = QHBoxLayout()
    self.setLayout(self.layout)
    self.checked = [False]*5
    self.checkboxes = []
    for i in range(5):
      die = QCheckBox("0")
      font = die.font()
      font.setPointSize(37)
      die.setFont(font)
      die.setEnabled(False)
      self.checkboxes.append(die)
      self.layout.addWidget(die)
      die.stateChanged.connect(lambda c,i=i: self.checked_(i,c))

  def set(self, turn, dice, keep, enabled):
    for i,(cb,d,k) in enumerate(zip(self.checkboxes, dice, keep)):
      cb.setText(str(d) if d else "")
      cb.blockSignals(True)
      cb.setCheckState(Qt.Checked if k else Qt.Unchecked)
      cb.blockSignals(False)
      cb.setEnabled(enabled)
      if turn:
        cb.setStyleSheet("color: #b1b1b1")
      else:
        cb.setStyleSheet("color: #424242")
      self.checked[i] = k

  def checked_(self, index, checked):
    self.checked[index] = bool(checked)
    self.parent.socket.put("checked", self.checked)

class Yahtzee(Gadget, QWidget):
  def __init__(self, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)
    self.name = ""
    self.layout = QGridLayout()
    self.setLayout(self.layout)
    self.prime([Player.new("", "")])

  def prime(self, players):  
    for i in reversed(range(self.layout.count())):
      self.layout.itemAt(i).widget().setParent(None)
    self.widgets = []
    self.dices = []
    self.newgame = QPushButton("New Game")
    self.newgame.clicked.connect(lambda c: self.newgame_(c))
    self.layout.addWidget(self.newgame, 0, 0, 1, len(players))
    for j,p in enumerate(players):
      name_label = QLabel(p.name)
      name_label.setAlignment(Qt.AlignCenter)
      self.layout.addWidget(name_label, 1, j)
      dice = Dice(self)
      self.dices.append(dice)
      self.layout.addWidget(dice, 2, j)
      if self.name == p.name:
        self.reroll = QPushButton("reroll")
        self.reroll.setEnabled(False)
        self.reroll.clicked.connect(lambda c: self.rerolled(c))
        self.layout.addWidget(self.reroll, 3, j)
        self.winner = QLabel("")
        self.winner.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.winner, 4, 0, 1, len(players))
      self.widgets.append([])
      for i,c in enumerate(categories):
        if i in {6, 14} or self.name != p.name:
          label = QLabel(c)
          label.setAlignment(Qt.AlignCenter)
          self.widgets[j].append(label)
        else:  
          self.widgets[j].append(QPushButton(c))
      for i,widget in enumerate(self.widgets[j]):
        self.layout.addWidget(widget, i+5, j)
        if self.name == p.name:
          if i not in {6, 14}:
            widget.clicked.connect(lambda c,i=i: self.clicked_(i,c))
            widget.setEnabled(False)

  def update(self, alias, token):
    match alias:
      case "name":
        self.name = token
        self.window.setWindowTitle(f"Yahtzee: {self.name}")
      case "prime":  
        self.prime(token)
      case "update":
        for i,(player,widgets) in enumerate(zip(token, self.widgets)):
          self.dices[i].set(player.turn, player.dice, player.keep, player.name == self.name and player.turn)
          if player.name == self.name:
            self.reroll.setEnabled(player.turn and player.rerolls > 0)
          for j,(score,widget,category) in enumerate(zip(player.scores, widgets, categories)):
            widget.setText(category if score == -1 else str(score))
            if player.name == self.name:
              if j not in {6, 14}:
                if player.turn:
                  widget.setEnabled(score == -1)
                else:
                  widget.setEnabled(False)
          widgets[6].setText("Bonus: 35" if sum(player.scores[:6]) >= 63 else "Bonus: 0")      
          widgets[14].setText(f"Total: {str(total(player))}")      
      case "winner":
        self.winner.setText(f"{token} wins!")

  def clicked_(self, index, checked):
    self.socket.put("choice", categories[index])

  def rerolled(self, checked):
    self.socket.put("reroll", ())

  def newgame_(self, checked):
    ret = QMessageBox.warning(self, "New Game", "This aborts the current game. Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    match ret:
      case QMessageBox.Yes:
        self.socket.put("newgame", ())
        
