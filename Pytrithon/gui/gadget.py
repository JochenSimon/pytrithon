class Gadget:
  embed = True
  def __init__(self, **kwargs):
    self.row = kwargs["row"] if "row" in kwargs else None
    self.col = kwargs["col"] if "col" in kwargs else 0
    self.rows = kwargs["rows"] if "rows" in kwargs else 1
    self.cols = kwargs["cols"] if "cols" in kwargs else 1
