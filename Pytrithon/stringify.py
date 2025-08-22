import re

linker = r"^(clears|reads|takes|gives|writes): *(.*)$"

def stringify_meta(element):    
  x = int(element.pos[0]) if str(element.pos[0]).endswith(".0") else element.pos[0]
  y = int(element.pos[1]) if str(element.pos[1]).endswith(".0") else element.pos[1]
  string = "{} {}({},{}):".format(element.type, "" if "#" in element.name else element.name + " ", x, y)
  if "\n" in element.inscr:
    string += "\n  " + "\n  ".join(line for line in element.inscr.split("\n"))
  else:
    string += " " + element.inscr
  return string  

def stringify_comment(element):
  x = int(element.pos[0]) if str(element.pos[0]).endswith(".0") else element.pos[0]
  y = int(element.pos[1]) if str(element.pos[1]).endswith(".0") else element.pos[1]
  font = (element.font_color if element.font_color else "") + ("," + element.font_size if element.font_size else "") + ("," + element.font_type if element.font_type else "")
  string = "{} {}({},{}):".format(element.type, font + " " if font else "", x, y)
  if "\n" in element.inscr:
    string += "\n  " + "\n  ".join(line for line in element.inscr.split("\n"))
  else:
    string += " " + element.inscr
  return string  

def stringify_place(element):
  x = int(element.pos[0]) if str(element.pos[0]).endswith(".0") else element.pos[0]
  y = int(element.pos[1]) if str(element.pos[1]).endswith(".0") else element.pos[1]
  seed = ":" + ("\n  " + "\n  ".join(element.seed.split("\n")) if "\n" in element.seed else " " + element.seed)
  return "{} {} {}({},{}){}".format(element.type, element.name, (element.typing + " ") if element.typing and element.type != "flow" else "", x, y, seed if element.seed else ";")

def stringify_transition(element):
  x = int(element.pos[0]) if str(element.pos[0]).endswith(".0") else element.pos[0]
  y = int(element.pos[1]) if str(element.pos[1]).endswith(".0") else element.pos[1]
  if "priority" in element.__dict__ and element.priority != "":
    prio = str(int(element.priority)) if str(element.priority).endswith(".0") else str(element.priority)
    if "#" in element.name:
      prio = "=" + prio
  else:
    prio = ""
  string = "{} {}{}({},{}):".format(element.type, "" if "#" in element.name else element.name + " ", prio + " " if prio else "", x, y)
  if [conn for conn in element.clears if conn.hidden]:
    string += "\n  clears: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.clears if conn.hidden)
  if [conn for conn in element.reads if conn.hidden]:
    string += "\n  reads: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.reads if conn.hidden)
  if [conn for conn in element.takes if conn.hidden]:
    string += "\n  takes: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.takes if conn.hidden)
  if [conn for conn in element.gives if conn.hidden]:
    string += "\n  gives: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.gives if conn.hidden)
  if [conn for conn in element.writes if conn.hidden]:
    string += "\n  writes: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.writes if conn.hidden)
  if "\n" in element.inscr:
    string += "\n  " + "\n  ".join(line for line in element.inscr.split("\n") if not re.match(linker, line))
  else:
    string += " " + element.inscr
  if [conn for conn in element.clears if not conn.hidden]:
    string += "\n  clears: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.clears if not conn.hidden)
  if [conn for conn in element.reads if not conn.hidden]:
    string += "\n  reads: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.reads if not conn.hidden)
  if [conn for conn in element.takes if not conn.hidden]:
    string += "\n  takes: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.takes if not conn.hidden)
  if [conn for conn in element.gives if not conn.hidden]:
    string += "\n  gives: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.gives if not conn.hidden)
  if [conn for conn in element.writes if not conn.hidden]:
    string += "\n  writes: " + "; ".join(":"+conn.place if conn.alias == conn.place else conn.alias+":"+conn.place if conn.alias else conn.place for conn in element.writes if not conn.hidden)
  return string
