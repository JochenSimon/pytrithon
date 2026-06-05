import os
from time import sleep, monotonic
import subprocess
from collections import defaultdict, OrderedDict
from threading import Thread
from .nexusmediator import *
from .server import *
from .pytriontology import *
from .tree import Tree

class After(Thread):
  def __init__(self, after):
    super().__init__()
    self.after = after
  def run(self):
    self.after()

class Nexus:
  def __init__(self, name, host, port, master, isolate, config, after):
    self.isolate = isolate
    self.config = config
    self.name = "#" if name is None else name
    self.nametree = Tree()

    self.nexi = {}

    self.agents = {}
    self.agentlist = []
    self.agentnumbers = defaultdict(int)
    self.deadagents = set()
    self.nextmoni = 0
    self.deadmonis = set()
    self.agentschanged = False
    self.running = True
    self.server = Server(self, host, port, master)
    self.after = After(after)
    self.monis = {}
    self.newmoni = False

    self.task = 1

    self.tasklisteners = defaultdict(set)
    self.invocationlisteners = defaultdict(set)
    self.communicationlisteners = defaultdict(set)
    self.eventlisteners = defaultdict(set)

    if master:
      self.master = NexusMediator(master[0], master[1], nexus=self)
    else:
      self.name = "main" if self.name == "#" else self.name
      self.nametree.add(self.name)

  def run(self):
    self.server.start()
    self.after.start()
    try:
      while self.running:
        communication = self.server.receive()
        if communication is not None:
          if isinstance(communication, Relayed):
            communication.relay(self)
            continue
          communication.execute(self)
          continue
        if self.agentschanged or self.newmoni:
          for moniid, moni in self.monis.items():
            moni.send(GiveAgentList(moniid, self.agentlist))
          self.agentschanged = False
          self.newmoni = False
          continue
        sleep(0.001)
    except KeyboardInterrupt:
      self.running = False
      self.server.running = False
      for handler in self.server.handlers:
        handler.running = False

  def register_listener(self, agent, type, topic, oldtopic):
    if type == "task":
      if oldtopic:
        self.tasklisteners[oldtopic].remove(agent)
      if topic:
        self.tasklisteners[topic].add(agent)
    elif type == "invocation":
      if oldtopic:
        self.invocationlisteners[oldtopic].remove(agent)
      if topic:
        self.invocationlisteners[topic].add(agent)
    elif type == "communication":
      if oldtopic:
        self.communicationlisteners[oldtopic].remove(agent)
      if topic:
        self.communicationlisteners[topic].add(agent)
    elif type == "event":
      if oldtopic:
        self.eventlisteners[oldtopic].remove(agent)
      if topic:
        self.eventlisteners[topic].add(agent)

  def unregister_agents(self, agents):
    for registry in (v for r in (self.tasklisteners, self.invocationlisteners, self.communicationlisteners, self.eventlisteners) for v in r.values()):
      for agent in agents:
        if agent in registry:
          registry.remove(agent)

  def listeners(self, type, topic):
    if type == "task":
      return self.tasklisteners[topic]
    elif type == "invocation":
      return self.invocationlisteners[topic]
    elif type == "communication":
      return self.communicationlisteners[topic]
    elif type == "event":
      return self.eventlisteners[topic]

  def remove_agents(self, agents):
    for agent in agents:
      self.deadagents.add(agent)
      if agent in self.agentlist:
        self.agentlist.remove(agent)
        self.agentschanged = True
      if agent in self.agents:  
        del self.agents[agent]

  def trigger_agentsdied(self, agents):
    if agents:
      for target in tuple(self.listeners("event", "agentsdied")):
        if target in self.agents:
          self.agents[target].send(EventTrigger("", (target,) , "agentsdied", {"aids": agents}))

  def open_agent(self, agent, args, delay, poll, edit, halt, secret, mute, errors):
    if not self.isolate:
      edit = not edit if self.config and "edit" in self.config and self.config["edit"] else edit
      halt = not halt if self.config and "halt" in self.config and self.config["halt"] else halt
      secret = not secret if self.config and "secret" in self.config and self.config["secret"] else secret
      mute = not mute if self.config and "mute" in self.config and self.config["mute"] else mute
      errors = errors if self.config and "errors" in self.config and self.config["errors"] or not self.config or "errors" not in self.config else not errors
      subprocess.Popen(["python", "agent", "-P", str(self.server.port)] + (["-d", str(delay)] if delay is not None else []) + (["-p", str(poll)] if poll is not None else []) + (["-e"] if edit else []) + (["-H"] if halt else []) + (["-s"] if secret else []) + (["-M"] if mute else []) + (["-E"] if not errors else []) + [agent] + args)

    def push_agent(self, agent, structure):  
      if not self.isolate:
        filename = "workbench/fragments/"+agent[1:].replace(".", "/")+".ptf" if agent.startswith("$") else "workbench/agents/"+agent.replace(".", "/")+".pta"
        os.makedirs("/".join(filename.split("/")[:-1]), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
          f.write(structure)

  def push_file(self, file, data):  
    if not self.isolate:
      if os.path.abspath("workbench/"+file).replace("\\", "/").startswith(os.path.abspath("workbench").replace("\\", "/")):
        os.makedirs(os.path.dirname("workbench/"+file), exist_ok=True)
        if not data.strip():
          try:
            os.remove("workbench/"+file)
          except FileNotFoundError:
            pass
        else:
          with open("workbench/"+file, "wb") as f:
            f.write(data)
