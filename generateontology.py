with open("Pytrithon/pytriontology.py", "w") as f:
  f.write("\n")

from Pytrithon.ontology import ontologize

with open("Pytrithon/pytriontology.pto") as o, open("Pytrithon/pytriontology.py", "w") as p:
  p.write("from time import sleep\nfrom .ontology import Concept\nfrom .utils import renamekey, flood\n\n")
  p.write(ontologize(o.read()))
