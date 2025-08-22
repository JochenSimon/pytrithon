import sys
from collections.abc import Iterable
from random import choice
from .place import Place

class Collection(Place):
  type = "coll"
  def __init__(self, seed, args, pos):
    super().__init__(seed, args, pos)

  @property
  def tokens(self):
    if not self._tokens:
      string = ""
    else:
      string = ",\n".join('"'+tok+'"' if isinstance(tok, str) else str(tok) for tok in self._tokens)
    if len(string) > 300:
      string = string[:300] + "..."
    return string  

  def prime(self):
    self.tokens = self.seed
    if self._tokens:
      for link in self.readers + self.takers + self.writers:
        self.parent[link.trans].offer(link)
      for link in self.givers:
        if "*" not in link.alias:
          self.parent[link.trans].offer(link)
    else:    
      for link in self.givers:
        self.parent[link.trans].offer(link)

  def offers(self, link):
    if link in self.readers:
      return bool(self._tokens)
    elif link in self.takers:    
      return bool(self._tokens)
    elif link in self.givers:
      if "*" in link.alias:
        return not bool(self._tokens)
      else:
        return True
    elif link in self.writers:
      if "*" in link.alias:
        return not bool(self._tokens)
      else:
        assert False

  def take(self):
    token = self.pop()
    self.ontake()
    return token

  def ontake(self):
    if not self._tokens:
      for link in self.readers + self.takers + self.writers:
        self.parent[link.trans].retract(link)
      for link in self.givers:
        if "*" in link.alias:
          found = False
          for clear in self.clearers:  
            if clear.place == link.place:
              found = True
          if not found:    
            self.parent[link.trans].offer(link)

  def give(self, token):
    self.typecheck(token)
    self.ongive()
    self.add(token)

  def ongive(self):
    if not self._tokens:
      for link in self.readers + self.takers + self.writers:
        self.parent[link.trans].offer(link)
      for link in self.givers:
        if "*" in link.alias:
          found = False
          for clear in self.clearers:  
            if clear.place == link.place:
              found = True
          if not found:    
            self.parent[link.trans].retract(link)

class ListCollection(Collection):
  type = "list"
  def __init__(self, seed, args, pos):
    super().__init__(seed, args, pos)
    self._tokens = []
  
  @Collection.tokens.setter
  def tokens(self, tokens):
    if tokens:
      try:
        tokens = eval(tokens, globals(), self.parent.env)
        self._tokens = [tok for tok in tokens] if isinstance(tokens, Iterable) else [tokens]
        for tok in self._tokens:
          self.typecheck(tok)
      except Exception as exc:
        print("Corrupt seed in place '{}' - {}: {}".format(self.name, type(exc).__name__, exc), file=sys.stderr, hide=True)

  def clear(self):
    self._tokens = []

  def write(self, token):
    self._tokens = list(token)
    for tok in self._tokens:
      self.typecheck(tok)
    for link in self.writers:
      self.parent[link.trans].changed(link)

  def add(self, token):
    self._tokens.append(token)
  
  def giveall(self, tokens):
    self.ongive()
    self._tokens = list(tokens)
    for tok in self._tokens:
      self.typecheck(tok)

  def takeall(self):
    tokens = self._tokens
    self._tokens = []
    self.ontake()
    return tokens

  def readall(self):
    return self._tokens

class Pool(ListCollection):
  type = "pool"
  def read(self):
    return choice(self._tokens)

  def pop(self):
    token = choice(self._tokens)
    self._tokens.remove(token)
    return token

class Queue(ListCollection):
  type = "queue"
  def read(self):
    return self._tokens[0]

  def pop(self):
    return self._tokens.pop(0)

class Stack(ListCollection):
  type = "stack"
  def read(self):
    return self._tokens[-1]

  def pop(self):
    return self._tokens.pop()

class Heap(Queue):
  type = "heap"
  @ListCollection.tokens.setter
  def tokens(self, tokens):
    ListCollection.tokens.fset(self, tokens)
    self._tokens.sort()
    
  def write(self, token):
    super().write(token)
    self._tokens.sort()

  def add(self, token):
    super().add(token)
    self._tokens.sort()
  
  def giveall(self, tokens):
    super().giveall(tokens)
    self._tokens.sort()

class Set(Collection):
  type = "set"
  def __init__(self, seed, args, pos):
    super().__init__(seed, args, pos)
    self._tokens = set()
  
  @Collection.tokens.setter
  def tokens(self, tokens):
    if tokens:
      try:
        tokens = eval(tokens, globals(), self.parent.env)
        self._tokens = {tok for tok in tokens} if isinstance(tokens, Iterable) else {tokens}
        for tok in self._tokens:
          self.typecheck(tok)
      except Exception as exc:
        print("Corrupt seed in place '{}' - {}: {}".format(self.name, type(exc).__name__, exc), file=sys.stderr, hide=True)

  def clear(self):
    self._tokens = set()

  def read(self):
    return choice(self._tokens)

  def write(self, token):
    self._tokens = set(token)
    for tok in self._tokens:
      self.typecheck(tok)
    for link in self.writers:
      self.parent[link.trans].changed(link)

  def add(self, token):
    self._tokens.add(token)
  
  def pop(self):
    return self._tokens.pop()
  
  def set(self, tokens):
    self._tokens = set(tokens)
  
  def giveall(self, tokens):
    self.ongive()
    self._tokens = set(tokens)
    for tok in self._tokens:
      self.typecheck(tok)

  def takeall(self):
    tokens = self._tokens
    self._tokens = set()
    self.ontake()
    return tokens
