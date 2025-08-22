from time import sleep
from queue import Queue, Empty
from threading import Thread
import socket
import pickle
from .pytriontology import *
   
class NexusMediator(Thread):
  daemon = True
  def __init__(self, host, port, core=None, moni=None, nexus=None):
    super().__init__()
    self.core = core
    self.moni = moni
    self.nexus = nexus
    self.queue = Queue()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((host, port))
    self.rfile = self.sock.makefile("br")
    self.wfile = self.sock.makefile("bw", 0)

    if core:
      pickle.dump(AgentStarted(self.core.agent.name), self.wfile, protocol=2)
    if moni:  
      pickle.dump(MonipulatorAvailable(), self.wfile, protocol=2)
    if nexus:
      pickle.dump(ConnectNexus(self.nexus.name), self.wfile, protocol=2)

    primal = False
    while 1:
      try:
        primal = pickle.load(self.rfile)
        if isinstance(primal, AgentNamed):
          self.core.agent.name = primal.agent
        if isinstance(primal, MonipulatorConnected):
          self.moni.id = primal.moniid
          self.moni.connected = True
        if isinstance(primal, NexusConnected):
          self.nexus.name = primal.name
          self.nexus.names = primal.names
          for name in primal.names:
            if name != primal.name:
              self.nexus.nexi[name] = self
          for agent in primal.agentlist:    
            self.nexus.agentlist.append(agent)
          for agent in primal.agents:
            self.nexus.agents[agent] = self
          for moni in primal.monis:
            self.nexus.monis[moni] = self
          self.nexus.task = primal.task
          self.nexus.tasklisteners.update(primal.tasklist)
          self.nexus.invocationlisteners.update(primal.involist)
          self.nexus.communicationlisteners.update(primal.commlist)
        break  
      except EOFError:
        sleep(0.01)
      
    if self.nexus:
      self.start()
    else:
      self.sock.setblocking(0)
      self.receive = self.receive_direct

  def send(self, obj):
    try:
      pickle.dump(obj, self.wfile, protocol=2)
    except ConnectionResetError:
      self.send = lambda o: None

  def receive(self):
    try:
      return self.queue.get(False)
    except Empty:
      return None

  def receive_direct(self):
    try:
      return pickle.load(self.rfile)
    except TypeError:
      return None
    except ConnectionResetError:
      return None

  def run(self):
    while 1:
      try:
        self.nexus.server.queue.put(pickle.load(self.rfile))
      except ConnectionResetError:
        self.send = lambda o: None
        return
      except EOFError:
        sleep(0.001)
