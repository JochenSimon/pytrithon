import os
os.chdir("tmwoty2")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
del os

import warnings
warnings.filterwarnings("ignore", message=r"SCALED|OPENGL", category=FutureWarning)

import pygame
from OpenGL.GL import *
from random import randint
from math import sqrt

from Pytrithon import Concept, ontologize

exec(ontologize("""
concept CreateSprite:
  slot handle: str
  slot shape: str
  slot layer: float
  slot speed: float
  slot row: int
concept CreateText:
  slot handle: str
  slot shape: str
  slot layer: float
concept DrawSprite:
  slot x: float
  slot y: float
  slot row: int
  slot color: int
  slot width: int
  slot height: int
concept DrawText:
  slot text: str
  slot x: float
  slot y: float
  slot color: int

concept Key:
  slot pressed: bool
concept LeftKey(Key): pass
concept RightKey(Key): pass
concept MenuKey(Key): pass
concept UpKey(Key): pass
concept DownKey(Key): pass
concept BackKey(Key): pass
concept LetterKey(Key):
  slot key: int

concept Player:
  slot position: float
  slot min_x: float
  slot max_x: float
  slot level: int
  slot score: float
  slot lives: int
  slot credits: int
  slot extras: [float]
  slot sprite: str
  slot warp: float
  slot size: int
  slot speed: int
  slot invul: bool
  slot inverted: bool
  @classmethod
  def default(cls, level=1):
    return cls(376, 0, 752, level, 0, 3, 0, [0]*8, "player", 1, 48, 300, False, False)
  def buy(self, item):
    if item in {6,7,8,9} and self.extras[item-2] >= 600:
      return
    if self.credits >= inventory[item][0]:
      self.credits -= inventory[item][0]
      match item:
        case 0: self.lives += 1
        case 1: self.lives += 4
        case 2: self.lives += 10
        case 3: self.score += 2000
        case 4: self.score += 8000
        case 5: self.score += 20000
        case 6:
          self.extras[4] += 60
          self.handle_extra(4)
        case 7:
          self.extras[5] += 60
          return self.handle_extra(5)
        case 8:
          self.extras[6] += 60
          self.handle_extra(6)
        case 9:
          self.extras[7] += 60
          self.handle_extra(7)
  def handle_extra(self, type):
    match type:
      case 0 | 4:
        self.warp = (1.5 if self.extras[0] else 2/3) if bool(self.extras[0]) ^ bool(self.extras[4]) else 1
      case 1 | 5:
        if bool(self.extras[1]) ^ bool(self.extras[5]):
          if self.extras[1]:
            self.size, self.min_x, self.max_x, shape = 64, 8, 744, "spherebig"
          else:
            self.size, self.min_x, self.max_x, shape = 32, -8, 760, "spheresmall"
        else:    
          self.size, self.min_x, self.max_x, shape = 48, 0, 752, "sphere"
        self.position = max(self.min_x, min(self.max_x, self.position))  
        return shape  
      case 2 | 6:
        self.speed = (200 if self.extras[2] else 450) if bool(self.extras[2]) ^ bool(self.extras[6]) else 300
      case 3:
        self.inverted = bool(self.extras[3])
      case 7:
        self.invul = bool(self.extras[7])
      case 8:
        self.lives += 1
      case 9:
        self.score += 1000
      case 10:
        self.credits += 1
      case 11:
        self.credits += 5
      case 12:
        self.credits += 20
      case 13:
        self.credits += 50
  def handle_expired(self, expired):
    last_return = None
    for exp in expired:
      if shape := self.handle_extra(exp):
        last_return = shape
    return last_return  
  def reset_extras(self):
    self.extras = [0]*8
    self.warp = 1
    self.size, self.min_x, self.max_x = 48, 0, 752
    self.position = max(self.min_x, min(self.max_x, self.position))
    self.speed = 300
    self.inverted = False
    self.invul = False

concept Enemy:
  slot id: int
  slot stride: int
  slot color: int
  slot x: float
  slot y: float
concept EnemySnake(Enemy):
  slot width: float
  slot growing: bool
  def collides(self, x, s):
    return self.y >= 1032 - s/2 and any(sqrt((x - (self.x + o*(self.width-32)/4))**2 + (1048 - self.y)**2) < 16 + s / 2 for o in (-2,2,0,-1,1))
concept EnemySphere(Enemy):
  def collides(self, x, s):
    return self.y >= 1024 - s/2 and sqrt((x - self.x)**2 + (1048 - self.y)**2) < 24 + s / 2
concept EnemySmall(Enemy):
  def collides(self, x, s):
    return self.y >= 1032 - s/2 and sqrt((x - self.x)**2 + (1048 - self.y)**2) < 16 + s / 2
concept EnemyCannon:
  slot id: int
  slot time: float
  slot x: float
  def collides(self, x, s):
    return 3 < self.time < 5 and abs(self.x - x) < 24 + s / 2
concept Extra:
  slot id: int
  slot type: int
  slot x: float
  slot y: float
  def collides(self, x, s):
    if self.type <= 9:
      check = self.y >= 1032 - s/2 and any(sqrt((x - (self.x + o))**2 + (1048 - self.y)**2) < 16 + s / 2 for o in (-16,16,0))
      if check:
        return check
    else:
      if 1048 < self.y < 1048 + s/3:
        if abs(x - self.x) <= (80 - s) / 2:
          return True
        if abs(x - self.x) <= 40 + s / 2:  
          return False

"""))  

class gs:
  hvpw = 1920 // 2
  hvph = 1080 // 2
  t = 0
  dt = 0

def setup_opengl():
  glShadeModel(GL_SMOOTH)
  glClearColor(0.0, 0.0, 0.0, 0.5)
  glEnable(GL_COLOR_MATERIAL)
  glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
  glEnable(GL_TEXTURE_2D)
  glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

def prepare_draw():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glLoadIdentity()
  glPushMatrix()
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  glDepthMask(GL_FALSE)
  glDisable(GL_DEPTH_TEST)

def finish_draw():
  glEnable(GL_DEPTH_TEST)
  glDepthMask(GL_TRUE);
  glPopMatrix();

class Shape:
  def __init__(self, file_path, cols=1, rows=1):
    self.cols = cols
    self.rows = rows

    texture_surface = pygame.image.load(file_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA")
    self.width = texture_surface.get_width()
    self.height = texture_surface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    self.texture = texture
  
  def draw(self, x, y, col=None, row=None, color=None, width=None, height=None):
    if col is None:
      col = 0
    if row is None:
      row = 0
    if width is None:
      width = self.width/self.cols
    if height is None:
      height = self.height/self.rows
    if x > -self.width and y > -self.height and x < gs.hvpw*2 and y < gs.hvph*2:
      if color is None:
        glColor4ub(255, 255, 255, 255)
      else:  
        glColor4ub((color >> 16) & 255 , (color >> 8) & 255, color & 255, 255)
      tl, tu, tr, td = col/self.cols, row/self.rows, (col+1)/self.cols, (row+1)/self.rows  
      pl, pu, pr, pd = x/gs.hvpw-1, 1-y/gs.hvph, x/gs.hvpw-1+width/gs.hvpw, 1-y/gs.hvph-height/gs.hvph 
      glBindTexture(GL_TEXTURE_2D, self.texture)
      glBegin(GL_QUADS)
      glTexCoord2d(tl, tu)
      glVertex2d(pl, pu)
      glTexCoord2d(tr, tu)
      glVertex2d(pr, pu)
      glTexCoord2d(tr, td)
      glVertex2d(pr, pd)
      glTexCoord2d(tl, td)
      glVertex2d(pl, pd)
      glEnd()
  
  def drawText(self, text, x, y, color=None):
    if color is None:
      color = 0xFFFFFF
    px, py, dx, dy = x, y, self.width / self.cols, self.height / self.rows
    glColor4ub((color >> 16) & 255 , (color >> 8) & 255, color & 255, 255)
    for ch in text:
      if ch == "\n":
        px = x
        py += dy
        continue
      if ch != " ":
        self.draw(px, py, ord(ch) - 32, 0, color=color)
      px += dx
    glColor4ub(255, 255, 255, 255)

class Sprite:
  def __init__(self, shape, speed, row=None):
    if row is None:
      row = 0
    self.shape = shape
    self.speed = speed
    self.row = row
    self.ticks = 0.0

  def draw(self, x, y, row=None, color=None, width=None, height=None):
    self.ticks += gs.dt / self.speed * self.shape.cols
    self.shape.draw(x, y, int(self.ticks % self.shape.cols), row if row is not None else self.row, color, width, height)

def handle_events():
  quit = False
  keys = []
  for event in pygame.event.get():
    match event.type:
      case pygame.QUIT:
        pygame.quit()
        quit = True
      case pygame.KEYDOWN | pygame.KEYUP:
        if event.key == 27:
          pygame.quit()
          quit = True
        pressed = event.type == pygame.KEYDOWN
        match event.key:
          case 1073742049 | 1073742048 | 1073742050: keys.append(LeftKey(pressed))
          case 1073742053 | 1073742052 | 1073742054: keys.append(RightKey(pressed))
          case 13 | 32: keys.append(MenuKey(pressed))
          case 1073741906: keys.append(UpKey(pressed))
          case 1073741905: keys.append(DownKey(pressed))
          case 8: keys.append(BackKey(pressed))
          case key if key in range(97, 123): keys.append(LetterKey(pressed, key))
          #case key: print(key)
  return quit, keys

def random_color():
  return randint(64, 255) * 0x10000 + randint(64, 255) * 0x100 + randint(64, 255)

def filter_collected(collected, items):
  for id in list(collected):
    if id in {item.id for item in items}:
      items.remove(next(item for item in items if item.id == id))
    else:
      collected.remove(id)

def adjust_extras(player, dt):
  expired = set()
  for extra in range(8):
    if 0 < player.extras[extra] <= dt:
      expired.add(extra)
    player.extras[extra] = max(0, player.extras[extra] - dt)
  return expired  

def rot13(string):
  return "".join([chr((ord(c)-84) % 26 + 97) for c in string])

passwords = [rot13(pw) for pw in ('ubbovrfn', 'tnenzbaq', 'ergheany', 'gerrebbg', 'cnenobyn', 'rnfgjneq', 'jrngurel', 'lneaonyy', 'onfgneqb', 'ivbyrapr', 'dhrfgvba', 'bhgrevfu', 'abibpnva', 'nentbtvn', 'ulcrevba', 'ababmbar', 'znyobytr', 'xnxnebgf', 'fhofcnpr')]

def load_high_scores():
  with open("highscores") as f:
    return [((s := score.split(","))[0], int(s[1])) for score in f.read().strip().split("\n")]

def store_high_score(tag, score):
  scores = load_high_scores()
  if scores[-1][1] < score:
    with open("highscores", "w") as f:
      f.write("\n".join(f"{t}, {s}" for t,s in sorted(scores+[(tag, score)], key=lambda e: -e[1])[:10]) + "\n")

inventory = list(zip([15, 50, 100, 15, 50, 100, 5, 5, 5, 10], ["1 extra life", "4 extra lives", "10 extra lives", "2000 points", "8000 points", "20000 points", "1 minute of slow", "1 minute of tiny", "1 minute of fast", "1 minute of invulnerabity"]))
