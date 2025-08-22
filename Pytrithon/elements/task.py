import sys
from collections import defaultdict
from .transition import Transition
from ..ontology import contains_concept
from ..pytriontology import *
from ..utils import purgekeys

class Task(Transition):
  type = "task"
  tasks = defaultdict(set)
  otask = 1
  origins = {}
  def init(self):
    Task.tasks[self.topic()].add(self)
    for link in self.links:
      link.connect(self)
    self.needs = {link for link in self.reads + self.takes}
    self.rooms = {link for link in self.gives}

  def offer(self, link):
    if link in self.reads + self.takes:
      self.needs.discard(link)
      if not self.needs:
        self.parent.core.ready(self)
    elif link in self.gives:
      self.rooms.discard(link)
      self.pending()
    else:
      assert False, "illegal write in task"
  
  def retract(self, link):
    if link in self.reads + self.takes:
      if not self.needs:
        self.parent.core.doze(self)
      self.needs.add(link)
    elif link in self.gives:
      self.rooms.add(link)
    else:
      assert False, "illegal write in task"

  def pending(self):
    for inscr, otask in list(self.parent.core.results):
      if inscr == self.topic():
        if otask in Task.origins and Task.origins[otask] == self:
          if not self.rooms and self.parent.core.results[self.topic(), otask]:
            self.receive(otask)
            break

  def receive(self, otask):
    gtask, bindings = self.parent.core.results[self.topic(), otask].pop(0)
    if not self.parent.core.results[self.topic(), otask]:
      del self.parent.core.results[self.topic(), otask]
    bindings = {a:(eval(o, globals(), self.parent.env) if isinstance(o, str) else o) for a,o in bindings.items()}
    self.bindings = bindings
    self.distribute()
    self.parent.core.places_changed({self.parent[l.place] for l in self.gives + self.writes})

  def fire(self):
    agents = (self.bindings["aid"],) if "aid" in self.bindings else ()
    agents = tuple(agent for agent in self.bindings["aids"]) if "aids" in self.bindings else agents
    purgekeys(self.bindings, ("aid", "aids"))
    for agent in agents:
      if not isinstance(agent, str):
        return print("Illegal aid in task '{}'".format(self.name), file=sys.stderr, hide=True)
    Task.origins[Task.otask] = self
    task = (0, Task.otask)
    Task.otask += 1
    self.bindings["sender"] = self.parent.agentname
    encoded = {a:(repr(o) if isinstance(o, str) or contains_concept(o) else o) for a,o in self.bindings.items()}
    self.parent.core.nexus.send(TaskInvocation(self.parent.agentname, agents, True, task, self.topic(), encoded))

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    Task.tasks[self.topic(oldinscr)].discard(self)
    Task.tasks[self.topic()].add(self)
    self.parent.core.nexus.send(RegisterListeners("", {Listener(self.parent.agentname, "task", self.topic(), "")}))

class Invocation(Transition):
  type = "invoke"
  invocations = {}
  origins = {}
  def init(self):
    super().init()
    Invocation.invocations[self.topic()] = self
  
  def offer(self, link):
    self.needs.discard(link)
    if not self.needs and self.parent.core.invocations[self.topic()]:
      self.receive()
      
  def retract(self, link):    
    self.needs.add(link)    

  def pending(self):
    if not self.needs and self.parent.core.invocations[self.topic()]:
      self.receive()

  def receive(self):
    self.collect()
    task, bindings = self.parent.core.invocations[self.topic()].pop(0)
    bindings = {a:(eval(o, globals(), self.parent.env) if isinstance(o, str) else o) for a,o in bindings.items()}
    bindings.update(self.bindings)
    if task[0] not in Invocation.origins:
      Invocation.origins[task[0]] = bindings["sender"]
    bindings["task"] = task
    self.bindings = bindings
    self.distribute()
    self.parent.core.places_changed({self.parent[l.place] for l in self.gives + self.writes})

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    del Invocation.invocations[self.topic(oldinscr)]
    Invocation.invocations[self.topic()] = self
    self.parent.core.nexus.send(RegisterListeners("", {Listener(self.parent.agentname, "invocation", self.topic(), "")}))

class Result(Transition):
  type = "result"
  def fire(self):
    agents = (self.bindings["aid"],) if "aid" in self.bindings else ()
    agents = tuple(agent for agent in self.bindings["aids"]) if "aids" in self.bindings else agents
    purgekeys(self.bindings, ("aid", "aids"))
    for agent in agents:
      if not isinstance(agent, str):
        return print("Illegal aid in result '{}'".format(self.name), file=sys.stderr, hide=True)
    if "task" in self.bindings:
      task = self.bindings["task"]
      agents = (Invocation.origins[task[0]],)
      del self.bindings["task"]
    else:
      task = (0, Task.otask)
      Task.otask += 1
    self.bindings["sender"] = self.parent.agentname
    encoded = {a:(repr(o) if isinstance(o, str) or contains_concept(o) else o) for a,o in self.bindings.items()}
    self.parent.core.nexus.send(TaskResult(self.parent.agentname, agents, True, task, self.topic(), encoded))

class Fail(Result):
  type = "fail"
