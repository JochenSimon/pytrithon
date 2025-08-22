from collections import defaultdict
from .transition import Transition
from ..ontology import contains_concept
from ..pytriontology import *
from ..utils import purgekeys

class Out(Transition):
  type = "out"
  def fire(self):
    agents = (self.bindings["aid"],) if "aid" in self.bindings else ()
    agents = tuple(agent for agent in self.bindings["aids"]) if "aids" in self.bindings else agents
    purgekeys(self.bindings, ("aid", "aids"))
    for agent in agents:
      if not isinstance(agent, str):
        return print("Illegal aid in out '{}'".format(self.name), file=sys.stderr, hide=True)
    self.bindings["sender"] = self.parent.agentname
    encoded = {a:(repr(o) if isinstance(o, str) or contains_concept(o) else o) for a,o in self.bindings.items()}
    self.parent.core.nexus.send(Communication(self.parent.agentname, agents, self.topic(), encoded))

class In(Transition):
  type = "in"
  sensors = defaultdict(set)
  def init(self):
    super().init()
    In.sensors[self.topic()].add(self)
  
  def offer(self, link):
    self.needs.discard(link)
    if not self.needs and self.parent.core.communications[self.topic()]:
      self.parent.core.ready(self)
      
  def retract(self, link):    
    if not self.needs:
      self.parent.core.doze(self)
    self.needs.add(link)    

  def pending(self):
    if not self.needs and self.parent.core.communications[self.topic()]:
      self.parent.core.ready(self)

  def fire(self):
    self.bindings.update({a:(eval(o, globals(), self.parent.env) if isinstance(o, str) else o) for a,o in self.parent.core.communications[self.topic()].pop(0).items()})
    if not self.parent.core.communications[self.topic()]:
      self.parent.core.doze(self)

  def create_links(self, inscr):
    oldinscr = self.inscr
    super().create_links(inscr)
    In.sensors[self.topic(oldinscr)].discard(self)
    In.sensors[self.topic()].add(self)
    self.parent.core.nexus.send(RegisterListeners("", {Listener(self.parent.agentname, "communication", self.topic())}))
