import re
from collections import OrderedDict

chopper = r"^(\w+) +([^()]+?)? *(?:\((.*)\))?(?:: *(.*)$|;$)((?:\n( +).*)(?:\n\6.*|\n\s*)*)?"
linker = r"^(clears|reads|takes|gives|writes): *(.*)$"
slotter = r"^slot *(.*): *(.*)$"
sorter = ["clears", "reads", "takes", "gives", "writes"]

linked_els = set("python if choice merge timer iterator signal slot nethod call return raise out in task invoke result fail spawn terminate gadget frag".split())
slotted_els = set("concept".split())
noname_els = set("comment".split())
optional_els = set("python if choice merge timer iterator signal slot nethod call return raise out in task invoke result fail spawn terminate gadget".split())
meta_els = set("self module ontology".split())
named_els = set("flow var know phantom pool queue stack heap set frag".split())

def to_pos(coords):
  return tuple(float(c) for c in coords.split(","))

class Node:
  def __init__(self, keyword, name, args, pos, suite): 
    self.keyword = keyword
    self.name = name
    self.args = args
    self.pos = pos
    self.suite = suite
    self.children = []
    self.links = []
    self.slots = []
  def __repr__(self):
    return "keyword: {}\nname: {}\nargs: {}\nlinks: {}\nslots: {}\nsuite: {}\nchildren: {}".format(self.keyword, self.name, self.args, self.links, self.slots, self.suite, self.children)
  def __str__(self):
    return self.__repr__()

def parselinks(suite):
  links = []
  errors = []
  try:
    mainsuite = [bool(re.match(linker, line)) if line != "" else True for line in suite.split("\n")].index(False)
  except ValueError:
    mainsuite = 0
  subelsuite = "\n".join(line for i,line in enumerate(suite.split("\n")) if i < mainsuite or not re.match(linker, line))
  for i,line in enumerate(suite.split("\n")):
    linkline = re.match(linker, line)
    if linkline:
      kind, values = linkline.groups()
      for link in values.split(";"):
        try:
          if ":" in link:
            alias, place = link.split(":")
            if not alias.strip():
              alias = place
          else:
            alias, place = "", link
        except ValueError:    
          errors.append("Corrupt link definition '{}'".format(link.strip()))
          continue
        if place.strip():
          links.append((kind, alias.strip(), place.strip(), i < mainsuite))
        else:
          errors.append("Missing place in link definition")
  links.sort(key=lambda l: (not l[3], sorter.index(l[0])))
  return links, subelsuite, errors

def parse(suite, node=None):
  if node is None:
    node = Node(None, None, None, None, suite)
  serial = 0  
  suite = "\n".join(line for line in suite.split("\n") if not line.startswith("#"))
  for keyword, args, pos, inline, suite, indent in re.findall(chopper, suite, re.M):
    suite = "\n".join(line[len(indent):] if line.strip() else "" for line in suite.strip("\n").split("\n"))
    if inline:
      if suite:
        suite = inline + "\n" + suite
      else:
        suite = inline
    if keyword in slotted_els:
      subel = Node(keyword, args, "(" + pos + ")" if pos else "", None, suite)
    elif keyword in noname_els:
      serial += 1
      subel = Node(keyword, "#{}".format(serial), args, to_pos(pos), suite)
    elif keyword in named_els:
      name, args = args.split(" ", 1) if " " in args else (args, "")
      subel = Node(keyword, name, args, to_pos(pos), suite)
    elif keyword in meta_els:
      if args:
        subel = Node(keyword, args, "", to_pos(pos), suite)
      else:  
        serial += 1
        subel = Node(keyword, "#{}".format(serial), "", to_pos(pos), suite)
    elif keyword in optional_els:
      if "=" in args:
        serial += 1
        subel = Node(keyword, "#{}".format(serial), args[1:], to_pos(pos), suite)
      elif args:
        name, args = args.split(" ", 1) if " " in args else (args, "")
        subel = Node(keyword, name, args, to_pos(pos), suite)
      else:  
        serial += 1
        subel = Node(keyword, "#{}".format(serial), "", to_pos(pos), suite)
    if subel.keyword in linked_els:
      subel.links, subel.suite, _ = parselinks(suite)
    elif subel.keyword in slotted_els:
      subel.suite = "\n".join(line for line in suite.split("\n") if not re.match(slotter, line))
      for line in suite.split("\n"):
        linkline = re.match(slotter, line)
        if linkline:
          slotname, slottype = linkline.groups()
          subel.slots.append((slotname.strip(), slottype.strip()))
    node.children.append(subel)      
  return node

