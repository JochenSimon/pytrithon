class Element:
  ismeta = False
  isplace = False
  istrans = False
  isgadget = False
  isfrag = False
  iscomment = False
  def __init__(self, args, pos):
    self.pos = pos
    
  def own(self, parent, name):
    self.parent = parent
    self.name = name

  def load(self): pass
  def init(self): pass
  def create(self): pass
  def prime(self): pass

class Empty: pass    
