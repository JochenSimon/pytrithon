from time import sleep
from queue import Queue, Empty
from threading import Thread
import socket
import pickle
from .pytriontology import *

class AgentMediator:
  def __init__(self, handler, name):
    self.handler = handler
    self.name = name
  
  def send(self, obj):
    try:
      pickle.dump(obj, self.handler.wfile, protocol=2)
    except ConnectionResetError:
      self.send = lambda o: None
      
class MonipulatorMediator:
  def __init__(self, handler, moniid):
    self.handler = handler
    self.moniid = moniid
  
  def send(self, obj):
    try:
      pickle.dump(obj, self.handler.wfile, protocol=2)
    except ConnectionResetError:
      self.send = lambda o: None
      
class MasterMediator:
  def __init__(self, handler, master):
    self.handler = handler
    self.master = master
  
  def send(self, obj):
    try:
      pickle.dump(obj, self.handler.wfile, protocol=2)
    except ConnectionResetError:
      self.send = lambda o: None
      
class Server(Thread):
  daemon = True
  def __init__(self, nexus, host, port, master):
    super().__init__()
    self.queue = Queue()
    self.handlers = set()
    self.nexus = nexus
    self.host = host
    self.port = port
    self.running = True

  def receive(self):
    try:
      return self.queue.get(False)
    except Empty:
      return None

  def run(self):  
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      self.sock.bind((self.host, self.port))
    except OSError:
      print("A Nexus is already running on host '{}' and port '{}'. Only starting Monipulator and Agents if requested.".format(self.host, self.port))
      self.nexus.running = False
      exit(1)
    while self.running:
      self.sock.listen(1)
      conn, addr = self.sock.accept()
      handler = Handler(self, conn)
      handler.init()
      if handler.agent:
        self.nexus.agents[handler.agent] = AgentMediator(handler, handler.agent)
        self.nexus.agentlist.append(handler.agent)
        self.nexus.agentschanged = True
      elif handler.moni:
        self.nexus.monis[handler.moniid] = MonipulatorMediator(handler, handler.moniid)
        self.nexus.newmoni = True
      elif handler.nexus:
        self.nexus.nexi[handler.nexus] = MasterMediator(handler, handler.nexus)
      self.handlers.add(handler)
      handler.start()

class Handler(Thread):
  daemon = True
  def __init__(self, server, conn):
    super().__init__()
    self.agent = None
    self.moni = False
    self.nexus = None
    self.server = server
    self.conn = conn
    self.rfile = self.conn.makefile("br")
    self.wfile = self.conn.makefile("bw", 0)
    self.running = True

  def init(self):
    primal = False
    nexus = self.server.nexus
    while 1:
      try:
        primal = pickle.load(self.rfile)
        if isinstance(primal, AgentStarted):
          agent = primal.agent
          nexus.agentnumbers[agent] += 1
          self.agent = agent + "#" + str(nexus.agentnumbers[agent]) + "@" + nexus.name
          while self.agent in nexus.deadagents:
            nexus.agentnumbers[agent] += 1
            self.agent = agent + "#" + str(nexus.agentnumbers[agent]) + "@" + nexus.name
          for nex in nexus.nexi:
            nexus.nexi[nex].send(AgentPropagation(nex, nexus.name, self.agent))
          pickle.dump(AgentNamed(self.agent), self.wfile, protocol=2)
        if isinstance(primal, MonipulatorAvailable):
          nexus.nextmoni += 1
          self.moniid = str(nexus.nextmoni) + "@" + nexus.name
          while self.moniid in nexus.deadmonis:
            nexus.nextmoni += 1
            self.moniid = str(nexus.nextmoni) + "@" + nexus.name
          for nex in nexus.nexi:
            nexus.nexi[nex].send(MonipulatorPropagation(nex, nexus.name, self.moniid))
          pickle.dump(MonipulatorConnected(nexus.name, self.moniid), self.wfile, protocol=2)
          self.moni = True
        if isinstance(primal, ConnectNexus):
          number = 0
          if primal.name != "#":
            if primal.name not in nexus.nametree.nodes:
              self.nexus = primal.name
            else:
              self.nexus = primal.name + str(number)
              while self.nexus in nexus.nametree.nodes:
                number += 1
                self.nexus = primal.name + str(number)
          else:
            self.nexus = "sub" + str(number)
            while self.nexus in nexus.nametree.nodes:
              number += 1
              self.nexus = "sub" + str(number)
          nexus.nametree.add(self.nexus, nexus.name)
          for nex in nexus.nexi:
            nexus.nexi[nex].send(NexusPropagation(nex, nexus.name, self.nexus, nexus.nametree.tree))
          pickle.dump(NexusConnected(nexus.name, self.nexus, nexus.nametree.tree, nexus.agentlist, [a for a in nexus.agents], nexus.deadagents, {m for m in nexus.monis}, nexus.deadmonis, nexus.task, dict(nexus.tasklisteners), dict(nexus.invocationlisteners), dict(nexus.communicationlisteners), dict(nexus.eventlisteners)), self.wfile, protocol=2)
        break  
      except EOFError:
        return

  def run(self):
    if self.agent:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except (EOFError, ConnectionResetError, ConnectionAbortedError):
          nexus = self.server.nexus
          nexus.remove_agents({self.agent})
          nexus.unregister_agents({self.agent})
          nexus.trigger_agentsdied({self.agent})
          for nex in nexus.nexi:
            nexus.nexi[nex].send(TerminatedAgent(nex, self.agent))
          return
    elif self.moni:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except (EOFError, ConnectionResetError, ConnectionAbortedError):
          nexus = self.server.nexus
          del nexus.monis[self.moniid]
          for nex in nexus.nexi:
            nexus.nexi[nex].send(TerminatedMoni(nex, self.moniid))
          return
    elif self.nexus:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except (EOFError, ConnectionResetError, ConnectionAbortedError):
          nexus = self.server.nexus
          kept, pruned = nexus.nametree.prune(self.nexus, nexus.name)
          agents = {a for a in nexus.agents if any(a.endswith("@"+p) for p in pruned)}
          nexus.remove_agents(agents)
          nexus.unregister_agents(agents)
          nexus.trigger_agentsdied(agents)
          monis = {m for m in nexus.monis if any(m.endswith("@"+p) for p in pruned)}
          for moni in monis:
            del nexus.monis[moni]
          for nex in kept:
            if nex != nexus.name:
              nexus.nexi[nex].send(TerminationCleanup(nex, nexus.nametree.tree, pruned, agents, monis))
          return
