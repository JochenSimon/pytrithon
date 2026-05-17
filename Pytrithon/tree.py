class Tree:
  def __init__(self, tree=None):
    if tree is None:
      self.tree = []
    else:  
      self.tree = tree

  def __repr__(self):
    return repr(self.tree)

  def _find(self, node, cursor=None):
    if node not in self.nodes:
      raise ValueError("Node '{}' not found".format(node))
    if cursor is not None:
      if cursor[0] == node:
        yield cursor
      else:
        for child in cursor[1]:
          yield from self._find(node, child)
    elif self.tree:
      yield from self._find(node, self.tree)

  def find(self, node):
    return Tree(next(self._find(node), []))

  def _flat(self, cursor=None):
    if cursor:
      yield cursor[0]
      for child in cursor[1]:
        yield from self._flat(child)
    elif self.tree:
      yield from self._flat(self.tree)

  @property
  def flat(self):
    return list(self._flat())

  @property
  def nodes(self):
    return set(self._flat())

  def _parent(self, node, cursor=None):
    if node not in self.nodes:
      raise ValueError("Node '{}' not found".format(node))
    if cursor:
      if node in {child for child,_ in cursor[1]}:
        yield cursor[0]
      else:  
        for child in cursor[1]:
          yield from self._parent(node, child)
    else:
      yield from self._parent(node, self.tree)

  def parent(self, node):
    return next(self._parent(node), None)

  def add(self, node, parent=None):
    if node is None:
      raise ValueError("Node can not be None".format(node))
    if node in self.nodes:
      raise ValueError("Node '{}' already exists".format(node))
    if parent is None:
      self.tree = [node, [self.tree]] if self.tree else [node, []]
    else:
      if parent not in self.nodes:
        raise ValueError("Parent '{}' not found".format(parent))
      next(self._find(parent))[1].append([node, []])

  def prune(self, node, origin):
    if node not in self.nodes:
      raise ValueError("Node '{}' not found".format(node))
    if origin not in self.nodes:
      raise ValueError("Origin '{}' not found".format(origin))
    if node == origin:
      raise ValueError("Node and origin '{}' can not be the same".format(node))
    if origin in self.find(node).nodes:
      top = origin
      parent = self.parent(origin)
      while parent and parent != node:
        top = parent
        parent = self.parent(top)
      kept, pruned = self.find(top).nodes, self.nodes - self.find(top).nodes
      self.tree = self.find(top).tree
      return kept, pruned
    else:
      kept, pruned = self.nodes - self.find(node).nodes, self.find(node).nodes
      self.find(self.parent(node)).tree[1].remove(self.find(node).tree)
      return kept, pruned
