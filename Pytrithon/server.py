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
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))
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
          for nex in nexus.nexi:
            nexus.nexi[nex].send(AgentPropagation(nex, nexus.name, self.agent))
          pickle.dump(AgentNamed(self.agent), self.wfile, protocol=2)
        if isinstance(primal, MonipulatorAvailable):
          self.moniid = (max(m for m in nexus.monis) + 1) if nexus.monis else 0
          for nex in nexus.nexi:
            nexus.nexi[nex].send(MonipulatorPropagation(nex, nexus.name, self.moniid))
          pickle.dump(MonipulatorConnected(self.moniid), self.wfile, protocol=2)
          self.moni = True
        if isinstance(primal, ConnectNexus):
          if primal.name != "#" and primal.name not in nexus.names:
            self.nexus = primal.name
          else:  
            dignames = {name for name in nexus.names if name.isdigit()}
            self.nexus = str((max(int(name) for name in dignames) if dignames else -1) + 1)
          nexus.names.append(self.nexus)
          for nex in nexus.nexi:
            nexus.nexi[nex].send(NexusPropagation(nex, nexus.name, self.nexus, nexus.names))
          pickle.dump(NexusConnected(nexus.name, self.nexus, nexus.names, nexus.agentlist, [a for a in nexus.agents], {m for m in nexus.monis}, nexus.task, dict(nexus.tasklisteners), dict(nexus.invocationlisteners), dict(nexus.communicationlisteners)), self.wfile, protocol=2)
        break  
      except EOFError:
        sleep(0.001)

  def run(self):
    if self.agent:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except EOFError:
          sleep(0.001)    
        except ConnectionResetError:
          self.server.nexus.agents[self.agent].send = lambda o: None
          return
    elif self.moni:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except EOFError:
          sleep(0.001)  
        except ConnectionResetError:
          self.server.nexus.monis[self.moniid].send = lambda o: None
          return
    elif self.nexus:
      while self.running:
        try:
          self.server.queue.put(pickle.load(self.rfile))
        except EOFError:
          sleep(0.001)
        except ConnectionResetError:
          try:
            self.server.nexus.nexi[self.nexus].send = lambda o: None
          except KeyError:
            pass
          return
