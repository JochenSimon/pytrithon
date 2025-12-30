from .window import Window
from .gadget import Gadget
from .label import Label
from .pushbutton import PushButton
from .pushbuttongroup import PushButtonGroup
from .checkbox import CheckBox
from .checkboxgroup import CheckBoxGroup
from .spinbox import SpinBox
from .lineedit import LineEdit
from .textedit import TextEdit
from .image import Image
from .slider import Slider
from .fileselect import FileSelect

allgadgets = {}

for gadget in [Label, PushButton, PushButtonGroup, CheckBox, CheckBoxGroup, LineEdit, SpinBox, TextEdit, Image, Slider, FileSelect]:
  allgadgets[gadget.__name__] = gadget
