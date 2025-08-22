import sys
from .base import Empty
from .place import Place

class Variable(Place):
  type = "var"
  def __init__(self, seed, args, pos):
    super().__init__(seed, args, pos)
    self._tokens = Empty

  @property
  def tokens(self):
    if self._tokens is Empty:
      string = ""
    elif isinstance(self._tokens, str):
      string = '"{}"'.format(self._tokens)
    elif isinstance(self._tokens, tuple) and self._tokens == ():
      string = "()"
    elif isinstance(self._tokens, tuple):
      string = str(self._tokens)[1:-1]
    else:
      string = str(self._tokens)
    if len(string) > 100:
      string = string[:100] + "..."
    return string  
  
  @tokens.setter
  def tokens(self, tokens):
    if tokens:
      try:
        token = eval(tokens, globals(), self.parent.env)
        self.typecheck(token)
        self._tokens = token
      except Exception as exc:
        print("Corrupt seed in place '{}' - {}: {}".format(self.name, type(exc).__name__, exc), file=sys.stderr, hide=True)

  def prime(self):
    self.tokens = self.seed
    if self._tokens is not Empty:
      for link in self.readers + self.takers + self.writers:
        self.parent[link.trans].offer(link)
    else:    
      for link in self.givers:
        self.parent[link.trans].offer(link)

  def offers(self, link):
    if link in self.readers:
      return self._tokens is not Empty
    elif link in self.takers:
      return self._tokens is not Empty
    elif link in self.givers:
      return self._tokens is Empty
    elif link in self.writers:
      return self._tokens is not Empty

  def clear(self):
    self._tokens = Empty

  def read(self):
    return self._tokens

  def take(self):
    token = self._tokens
    self._tokens = Empty
    for link in self.readers + self.takers + self.writers:
      self.parent[link.trans].retract(link)
    for link in self.givers:
      found = False
      for clear in self.clearers:  
        if clear.place == link.place:
          found = True
      if not found:    
        self.parent[link.trans].offer(link)
    return token

  def give(self, token):
    self.typecheck(token)
    self._tokens = token
    for link in self.readers + self.takers + self.writers:
      self.parent[link.trans].offer(link)
    for link in self.givers:
      found = False
      for clear in self.clearers:  
        if clear.place == link.place:
          found = True
      if not found:    
        self.parent[link.trans].retract(link)

  def write(self, token):
    self.typecheck(token)
    self._tokens = token
    for link in self.writers:
      self.parent[link.trans].changed(link)
