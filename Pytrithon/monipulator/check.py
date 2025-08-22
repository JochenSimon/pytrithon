import os
import sys
import argparse
from collections import defaultdict
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ..pml import *
from ..utils import *

def check(parent, agents):
  for name, agent in agents.items():
    if agent is None:
      if os.path.isfile("workbench/agents/" + name + ".pta"):
        with open("workbench/agents/" + name + ".pta", encoding="utf-8") as f:
          agents[name] = parse(f.read())
      else:
        agents[name] = parse("")
    else:
      agents[name] = parse(agent)

  window = QDialog(parent)
  window.setWindowTitle("Agent Checker")
  window.layout = QVBoxLayout(window)

  textedit = QTextEdit(window)
  textedit.setReadOnly(True)
  window.layout.addWidget(textedit)

  window.resize(600,400)
  window.show()

  global appended
  appended = False
  def append(text):
    global appended
    appended = True
    textedit.append(text)
    textedit.moveCursor(QTextCursor.End)
    textedit.ensureCursorVisible()

  matcher = r"^(\w+) *= *\[(\w+) +for +(\w+) +in +(\w+)\]$"

  topics = set()
  singles = defaultdict(lambda: defaultdict(set))
  duplicity = defaultdict(lambda: defaultdict(int))
  paramcheck = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))  

  keywords = "if choice merge timer iterator nethod call return raise signal slot task invoke result fail out in".split()

  for name, agent in agents.items():
    for node in agent.children:
      if node.keyword in keywords:
        topic = sanitize(node.suite)
        topics.add(topic)
        if node.keyword in "call slot invoke in".split():
          if node.keyword not in singles[name][topic]:
            singles[name][topic].add(node.keyword)
          else:
            append("duplicate {} with topic '{}' in agent {}".format(node.keyword, topic, name))
        for kind,alias,place,hidden in node.links:
          if kind == "clears":
            append("illegal clear in agent {}".format(name))
          if kind == "writes" and node.keyword not in "in".split():
            append("illegal write in agent {}".format(name))
          else:
            if "," in alias:
              for al in alias.split(","):
                if node.keyword in "call return raise".split() and al.strip() in "neth".split(): continue
                elif node.keyword in "task".split() and kind in "reads takes".split() and al.strip() in "aid aids".split(): continue
                elif node.keyword in "task".split() and kind in "gives".split() and al.strip() in "task sender".split(): continue
                elif node.keyword in "invoke".split() and al.strip() in "task sender".split(): continue
                elif node.keyword in "result".split() and al.strip() in "task".split(): continue
                elif node.keyword in "fail".split() and al.strip() in "task".split(): continue
                elif node.keyword in "out".split() and kind in "reads takes".split() and al.strip() in "aid aids".split(): continue
                elif node.keyword in "in".split() and al.strip() in "sender".split(): continue
                paramcheck[node.keyword][topic][duplicity[node.keyword][topic]][kind].add(al.strip())
            else:  
              omit = False
              if alias == "": omit = True
              elif node.keyword in "call return raise".split() and alias in "neth".split(): omit = True
              elif node.keyword in "task".split() and kind in "reads takes".split() and alias in "aid aids".split(): omit = True
              elif node.keyword in "task".split() and kind in "gives".split() and alias in "task sender".split(): omit = True
              elif node.keyword in "invoke".split() and alias in "task sender".split(): omit = True
              elif node.keyword in "result".split() and alias in "task".split(): omit = True
              elif node.keyword in "fail".split() and alias in "task".split(): omit = True
              elif node.keyword in "out".split() and kind in "reads takes".split() and alias in "aid aids".split(): omit = True
              elif node.keyword in "in".split() and alias in "sender".split(): omit = True
              if not omit:    
                paramcheck[node.keyword][topic][duplicity[node.keyword][topic]][kind].add(alias)
        if node.keyword in "iterator".split():
          for i in range(duplicity["iterator"][topic]):
            try:
              output, new, old, input = re.match(matcher, topic).groups()  
            except AttributeError:
              output, new, old, input = "res", "new", "old", "seq"
            if output not in paramcheck[node.keyword][topic][i]["gives"]:
              append("wrong res in iterator '{}'".format(topic))
            if new not in paramcheck[node.keyword][topic][i]["takes"]:
              append("wrong new in iterator '{}'".format(topic))
            if old not in paramcheck[node.keyword][topic][i]["gives"]:
              append("wrong old in iterator '{}'".format(topic))
            if input not in paramcheck[node.keyword][topic][i]["takes"]:
              append("wrong seq in iterator '{}'".format(topic))
        duplicity[node.keyword][topic] += 1

  for topic in topics:
    for i in range(duplicity["nethod"][topic]):
      mismatch = (paramcheck["nethod"][topic][i]["reads"] | paramcheck["nethod"][topic][i]["takes"]) ^ paramcheck["call"][topic][0]["gives"]
      if mismatch:
        append("mismatch of parameters '{}' for nethod '{}'".format(",".join(mismatch), topic))
      mismatch = paramcheck["nethod"][topic][i]["gives"] ^ (paramcheck["return"][topic][0]["reads"] | paramcheck["return"][topic][0]["takes"] | paramcheck["raise"][topic][0]["reads"] | paramcheck["raise"][topic][0]["takes"])
      if mismatch:
        append("mismatch of return values '{}' for nethod '{}'".format(",".join(mismatch), topic))

    for i in range(duplicity["slot"][topic]):
      mismatch = (paramcheck["signal"][topic][i]["reads"] | paramcheck["signal"][topic][i]["takes"]) ^ paramcheck["slot"][topic][0]["gives"]
      if mismatch:
        append("mismatch of parameters '{}' for signal '{}'".format(",".join(mismatch), topic))

    for i in range(duplicity["task"][topic]):
      mismatch = (paramcheck["task"][topic][i]["reads"] | paramcheck["task"][topic][i]["takes"]) ^ paramcheck["invoke"][topic][0]["gives"]
      if mismatch:
        append("mismatch of parameters '{}' for task '{}'".format(",".join(mismatch), topic))
      mismatch = paramcheck["task"][topic][i]["gives"] ^ (paramcheck["result"][topic][0]["reads"] | paramcheck["result"][topic][0]["takes"] | paramcheck["fail"][topic][0]["reads"] | paramcheck["fail"][topic][0]["takes"])
      if mismatch:
        append("mismatch of return values '{}' for task '{}'".format(",".join(mismatch), topic))

    for i in range(duplicity["in"][topic]):
      mismatch = (paramcheck["out"][topic][i]["reads"] | paramcheck["out"][topic][i]["takes"]) ^ paramcheck["in"][topic][0]["gives"] ^ paramcheck["in"][topic][0]["writes"]
      if mismatch:
        append("mismatch of parameters '{}' for out '{}'".format(",".join(mismatch), topic))

  if not appended:
    append("everything seems to be ok")

  return window
