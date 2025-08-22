from .base import Element
from ..stringify import stringify_comment

class Comment(Element):
  type = "comment"
  iscomment = True
  def __init__(self, inscription, args, pos):
    super().__init__(args, pos)
    if args.count(",") == 2:
      self.font_color = args.split(",")[0]
      self.font_size = args.split(",")[1]
      self.font_type = args.split(",")[2]
    elif "," in args:
      self.font_color = args.split(",")[0]
      self.font_size = args.split(",")[1]
      self.font_type = None
    elif args:
      self.font_color = args
      self.font_size = None
      self.font_type = None
    else:  
      self.font_color = None
      self.font_size = None
      self.font_type = None
    self.inscr = inscription

  def create_links(self, inscr):
    self.inscr = inscr

  def __str__(self):
    return stringify_comment(self)
