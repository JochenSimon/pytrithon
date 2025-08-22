from time import sleep
from .ontology import Concept
from .utils import renamekey, flood

class Initializer(Concept):
  pass
class Relayed(Concept):
  pass
class AgentToNexus(Concept):
  pass
class NexusToAgent(Relayed):
  _slots = [("agent", str)]
  def relay(self, nexus):
    if self.agent in nexus.agents:
      nexus.agents[self.agent].send(self)
class AgentToNexi(Relayed):
  _slots = [("dest", str)]
  def relay(self, nexus):
    if not self.dest:
      for nex in nexus.nexi:
        self.dest = nex
        nexus.nexi[nex].send(self)
      self.execute(nexus)  
    elif "," in self.dest:
      dests = [d.strip() for d in self.dest.split(",")]
      if nexus.name in dests:
        self.execute(nexus)
      for d in dests:
        if d in nexus.nexi:
          self.dest = d
          nexus.nexi[self.dest].send(self)
    elif nexus.name == self.dest or self.dest == "(local)":
      self.execute(nexus)
    elif self.dest in nexus.nexi:
      nexus.nexi[self.dest].send(self)
class MoniToNexi(AgentToNexi):
  pass
class NexusToMoni(Relayed):
  _slots = [("moniid", int)]
  def relay(self, nexus):
    nexus.monis[self.moniid].send(self)
class NexusToNexus(Relayed):
  _slots = [("dest", str)]
  def relay(self, nexus):
    if nexus.name == self.dest:
      self.execute(nexus)
    else:
      nexus.nexi[self.dest].send(self)
class AgentToAgents(Relayed):
  _slots = [("sender", str), ("agents", tuple)]
  def relay(self, nexus):
    if self.agents:
      for agent in self.agents:
        if agent in nexus.agents:
          self.agents = (agent,)
          nexus.agents[agent].send(self)
    else:
      for agent in nexus.agents:
        if agent != self.sender and agent in nexus.listeners(self.type, self.topic):
          if agent in nexus.agents:
            self.agents = (agent,)
            nexus.agents[agent].send(self)
class AgentToAgentsTask(AgentToAgents):
  _slots = [("add", bool), ("task", tuple)]
  def relay(self, nexus):
    if not self.task[0] and self.add:
      self.add = False
      self.task = (nexus.task, self.task[1])
      nexus.task += 1
      for nex in nexus.nexi:
        nexus.nexi[nex].send(TaskPropagation(nex, nexus.task))
    AgentToAgents.relay(self, nexus)  
class AgentToMoni(Relayed):
  _slots = [("agent", str), ("monis", {int})]
  def relay(self, nexus):
    for moniid in {m for m in self.monis}:
      self.monis = {moniid}
      nexus.monis[moniid].send(self)
class AgentToMonis(Relayed):
  _slots = [("agent", str), ("monis", {int})]
  def relay(self, nexus):
    if self.monis:
      for moniid in self.monis:
        nexus.monis[moniid].send(self)
        break
    else:  
      for moniid in nexus.monis:
        self.monis = {moniid}
        nexus.monis[moniid].send(self)
class MoniToAgent(Relayed):
  _slots = [("agent", str), ("moniid", int)]
  def relay(self, nexus):
    nexus.agents[self.agent].send(self)
class AgentStarted(Initializer):
  _slots = [("agent", str)]
class AgentNamed(Initializer):
  _slots = [("agent", str)]
class MonipulatorAvailable(Initializer):
  pass
class MonipulatorConnected(Initializer):
  _slots = [("moniid", int)]
class ConnectNexus(Initializer):
  _slots = [("name", str)]
class NexusConnected(Initializer):
  _slots = [("origin", str), ("name", str), ("names", [str]), ("agentlist", [str]), ("agents", [str]), ("monis", {int}), ("task", int), ("tasklist", dict), ("involist", dict), ("commlist", dict)]
class MonipulatorPropagation(NexusToNexus):
  _slots = [("origin", str), ("moniid", int)]
  def execute(self, nexus):
    nexus.monis[self.moniid] = nexus.nexi[self.origin]
class AgentPropagation(NexusToNexus):
  _slots = [("origin", str), ("agent", str)]
  def execute(self, nexus):
    nexus.agents[self.agent] = nexus.nexi[self.origin]
    nexus.agentlist.append(self.agent)
class NexusPropagation(NexusToNexus):
  _slots = [("origin", str), ("target", str), ("names", [str])]
  def execute(self, nexus):
    nexus.nexi[self.target] = nexus.nexi[self.origin]
    nexus.names = self.names
class TaskPropagation(NexusToNexus):
  _slots = [("task", int)]
  def execute(self, nexus):
    nexus.task = self.task
class FetchNames(Relayed):
  _slots = [("moniid", int), ("names", [str])]
  def relay(self, nexus):
    self.names = nexus.names
    nexus.monis[self.moniid].send(self)
class FetchElsewhere(FetchNames):
  def relay(self, nexus):
    self.names = [n for n in nexus.names if n != nexus.name]
    nexus.monis[self.moniid].send(self)
class TriggerOpen(FetchNames):
  def execute(self, moni):
    moni.show_open(self.names)
class OpenAgent(MoniToNexi):
  _slots = [("agent", str), ("args", [str]), ("delay", int), ("poll", int), ("edit", bool), ("halt", bool), ("secret", bool), ("mute", bool), ("errors", bool)]
  def execute(self, nexus):
    nexus.open_agent(self.agent, self.args, self.delay, self.poll, self.edit, self.halt, self.secret, self.mute, self.errors)
class TriggerPush(FetchNames):
  _slots = [("agent", str)]
  def execute(self, moni):
    moni.show_push(self.agent, self.names)
class PushAgent(MoniToNexi):
  _slots = [("agent", str), ("structure", str)]
  def execute(self, nexus):
    nexus.push_agent(self.agent, self.structure)
class TriggerPushFile(FetchElsewhere):
  def execute(self, moni):
    if self.names:
      moni.show_pushfile(self.names)
class PushFile(MoniToNexi):
  _slots = [("file", str), ("data", bytes)]
  def execute(self, nexus):
    nexus.push_file(self.file, self.data)
class TriggerTerminate(MoniToAgent):
  def execute(self, core):
    core.terminate()
class TerminateAgent(NexusToAgent):
  def execute(self, core):
    exit()
class TerminateMoni(NexusToMoni):
  def execute(self, moni):
    exit()
class TerminatedAgent(AgentToNexi):
  _slots = [("agent", str)]
  def execute(self, nexus):
    if self.agent in nexus.agentlist:
      nexus.agentlist.remove(self.agent)
      nexus.agentschanged = True
    if self.agent in nexus.pings:
      del nexus.pings[self.agent]
class TerminatedTotal(AgentToNexi):
  def execute(self, nexus):
    for agent in nexus.agents:
      nexus.agents[agent].send(TerminateAgent(agent))
    for moni in nexus.monis:
      nexus.monis[moni].send(TerminateMoni(moni))
    exit()
class TerminatedProcess(Relayed):
  def relay(self, nexus):
    pass
  def execute(self, process):
    exit()
class TerminationCleanup(AgentToNexi):
  _slots = [("name", str), ("agents", {str})]
  def execute(self, nexus):
    del nexus.nexi[self.name]
    for agent in self.agents:
      del nexus.agents[agent]
      nexus.agentlist.remove(agent)
    if self.agents:
      nexus.agentschanged = True
class TerminatedLocal(Relayed):
  def relay(self, nexus):
    for moni in nexus.monis:
      nexus.monis[moni].send(TerminatedProcess())
    for agent in nexus.agents:
      nexus.agents[agent].send(TerminatedProcess())
    for nex in nexus.nexi:
      nexus.nexi[nex].send(TerminationCleanup(nex, nexus.name, {a for a in nexus.agents if a.endswith("@"+nexus.name)}))
    sleep(0.1)  
    exit()
class GiveAgentList(NexusToMoni):
  _slots = [("agents", [str])]
  def execute(self, moni):
    moni.give_agent_list(self.agents)
class RequestStructure(MoniToAgent):
  def execute(self, core):
    core.watchers.add(self.moniid)
    core.give_structure(self.moniid)
class Content(Concept):
  _slots = [("place", str), ("content", str)]
class GiveStructure(AgentToMoni):
  _slots = [("structure", str), ("contents", {Content}), ("delay", int), ("halted", bool), ("editmode", bool), ("secret", bool)]
  def execute(self, moni):
    moni.give_structure(self.agent, self.structure, self.contents, self.delay, self.halted, self.editmode, self.secret)
class PlacesChanged(AgentToMoni):
  _slots = [("changes", {Content})]
  def execute(self, moni):
    for change in self.changes:
      moni.agents[self.agent].figures[change.place].change(change.content)
class TransitionFiring(AgentToMoni):
  _slots = [("trans", str), ("firing", bool)]
  def execute(self, moni):
    if self.firing:
      moni.agents[self.agent].firing = self.trans
    else:
      moni.agents[self.agent].firing = None
    toupdate = moni.agents[self.agent].figures[self.trans]
    toupdate.update(toupdate.rect)
class TransitionErrored(AgentToMoni):
  _slots = [("trans", str), ("errored", bool)]
  def execute(self, moni):
    moni.agents[self.agent].figures[self.trans].errored = self.errored
    toupdate = moni.agents[self.agent].figures[self.trans]
    toupdate.update(toupdate.rect)
class Print(AgentToMonis):
  _slots = [("message", str)]
  def execute(self, moni):
    moni.console.print(self.agent, self.message)
class Ping(AgentToNexi):
  _slots = [("agent", str), ("timeout", int)]
  def execute(self, nexus):
    nexus.ping(self.agent, self.timeout)
class Listener(Concept):
  _slots = [("agent", str), ("type", str), ("topic", str)]
class RegisterListeners(AgentToNexi):
  _slots = [("listeners", {Listener})]
  def execute(self, nexus):
    for listener in self.listeners:
      nexus.register_listener(listener.agent, listener.type, listener.topic)
class TaskResult(AgentToAgentsTask):
  _slots = [("topic", str), ("bindings", dict)]
  type = "task"
  def execute(self, core):
    core.results[self.topic, self.task[1]].append((self.task[0], self.bindings))
    core.taskpending(self.topic)
class TaskInvocation(AgentToAgentsTask):
  _slots = [("topic", str), ("bindings", dict)]
  type = "invocation"
  def execute(self, core):
    core.invocations[self.topic].append((self.task, self.bindings))
    core.invocationpending(self.topic)
class Communication(AgentToAgents):
  _slots = [("topic", str), ("bindings", dict)]
  type = "communication"
  def execute(self, core):
    core.communications[self.topic].append(self.bindings)
    core.inpending(self.topic)
class SetDelay(MoniToAgent):
  _slots = [("delay", int)]
  def execute(self, core):
    core.delay = self.delay
class MoveManipulation(MoniToAgent):
  _slots = [("name", str), ("x", float), ("y", float)]
  def execute(self, core):
    core.agent.elements[self.name].pos = self.x, self.y
    core.give_structure(but=self.moniid)
class NameManipulation(MoniToAgent):
  _slots = [("oldname", str), ("newname", str)]
  def execute(self, core):
    element = core.agent.elements[self.oldname]
    element.name = self.newname
    renamekey(core.agent.elements, self.oldname, self.newname)
    for link in core.agent.globallinks:
      if link.place == self.oldname:
        link.place = self.newname
      if link.trans == self.oldname:
        link.trans = self.newname
    flood(core.agent.elements, core.agent.globallinks)    
    if element.isfrag:
      element.load()
      element.init()
    core.give_structure(but=self.moniid)
class InscriptionManipulation(MoniToAgent):
  _slots = [("name", str), ("inscr", str)]
  def execute(self, core):
    if core.agent.elements[self.name].isplace:
      core.agent.elements[self.name].seed = self.inscr
    else:  
      core.agent.elements[self.name].create_links(self.inscr)
    core.give_structure(but=self.moniid)
class TypeManipulation(MoniToAgent):
  _slots = [("name", str), ("type", str)]
  def execute(self, core):
    core.agent.elements[self.name].typing = self.type
    core.give_structure(but=self.moniid)
class PriorityManipulation(MoniToAgent):
  _slots = [("name", str), ("priority", str)]
  def execute(self, core):
    if self.priority:
      core.agent.elements[self.name].priority = float(self.priority)
    elif "priority" in core.agent.elements[self.name].__dict__:
      del core.agent.elements[self.name].priority
    core.give_structure(but=self.moniid)
class AliasManipulation(MoniToAgent):
  _slots = [("serial", int), ("alias", str)]
  def execute(self, core):
    core.agent.globallinks[self.serial].alias = self.alias
    core.give_structure(but=self.moniid)
class DeleteLinkManipulation(MoniToAgent):
  _slots = [("serial", int)]
  def execute(self, core):
    link = core.agent.globallinks[self.serial]
    if link in core.agent.elements[link.place].links:
      core.agent.elements[link.place].links.remove(link)
    trans = core.agent.elements[link.trans]
    trans.delete_link(link)
    core.give_structure(but=self.moniid)
class CreateManipulation(MoniToAgent):
  _slots = [("type", str), ("name", str), ("typing", str), ("pos", tuple)]
  def execute(self, core):
    core.agent.create_element(self.type, self.name, self.typing, self.pos)
    core.give_structure(but=self.moniid)
class DeleteElementManipulation(MoniToAgent):
  _slots = [("name", str)]
  def execute(self, core):
    core.agent.delete_element(self.name)
    core.give_structure(but=self.moniid)
class ChangeManipulation(MoniToAgent):
  _slots = [("place", str), ("type", str)]
  def execute(self, core):
    core.agent.change_to(self.place, self.type)
    core.give_structure(but=self.moniid)
class CommentManipulation(MoniToAgent):
  _slots = [("name", str), ("color", str), ("size", str), ("type", str)]
  def execute(self, core):
    core.agent.elements[self.name].font_color = self.color
    core.agent.elements[self.name].font_size = self.size
    core.agent.elements[self.name].font_type = self.type
    core.give_structure(but=self.moniid)
class CoreEdit(MoniToAgent):
  def execute(self, core):
    core.edit = True
    core.window.hide()
    if core.halted:
      core.state = 0
    else:
      core.state = 1
    core.phase = 0
    core.init()
    core.give_structure()
class CoreInit(MoniToAgent):
  def execute(self, core):
    core.edit = False
    if core.halted:
      core.state = 0
    else:
      core.state = 1
    core.phase = 0
    core.init()
    core.give_structure()
class CoreReset(MoniToAgent):
  def execute(self, core):
    core.phase = 0
    core.init()
    core.give_structure()
class StateChanged(AgentToMoni):
  _slots = [("halted", bool)]
  def execute(self, moni):
    moni.agents[self.agent].halted = self.halted
    if moni.central_widget.canvas == moni.agents[self.agent]:
      moni.agents[self.agent].enable_buttons()
class CoreRun(MoniToAgent):
  def execute(self, core):
    core.state = 1
    core.halted = False
    core.state_changed(self.moniid)
class CoreStep(MoniToAgent):
  def execute(self, core):
    core.state -= 3
class CoreHalt(MoniToAgent):
  def execute(self, core):
    core.state = -[0,2,1][core.phase]
    core.halted = True
    core.state_changed(self.moniid)
