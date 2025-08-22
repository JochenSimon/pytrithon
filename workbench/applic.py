__version__ = "1.3.1"

import webbrowser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Pytrithon import Gadget, Concept, ontologize

exec(ontologize("""
concept Application:
  slot id: int
  slot company: str
  slot title: str
  slot website: str
  slot maps: str
  slot advertisement: str
  slot cv: bool
  slot doc: bool
  slot email: bool
  slot coverletter: str
  def todict(self):
    return {"id": self.id, "company": self.company, "title": self.title, "website": self.website, "maps": self.maps, "advertisement": self.advertisement, "cv": self.cv, "doc": self.doc, "email": self.email, "coverletter": self.coverletter}
concept Applications:
  slot apps: [Application]
  def __iter__(self):
    for app in self.apps:
      yield app
  def __getitem__(self, index):
    return self.apps[index]
  def __setitem__(self, index, app):
    self.apps[index] = app
  def append(self, app):
    self.apps.append(app)
  def toyaml(self):
    return [a.todict() for a in self.apps]
"""))

class Selector(Gadget, QWidget):
  def __init__(self, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)

    self.applications = Applications([])

    self.selector = QListWidget()
    self.new = QPushButton("New")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.selector)
    self.layout.addWidget(self.new)

    self.selector.itemClicked.connect(self.select)
    self.new.clicked.connect(self.clicked_)

  def select(self, item):
    self.socket.put("select", self.applications[self.selector.currentRow()])

  def clicked_(self, checked):
    application = Application(self.selector.count(), "<company>", "<title>", "", "", "", True, False, False, "")
    self.applications.append(application)
    self.selector.insertItem(self.selector.count(), application.company + " : " + application.title)
    self.selector.setCurrentRow(self.selector.count()-1)

  def update(self, alias, token):
    if alias == "update":
      index = [a.id for a in self.applications].index(token.id)
      self.applications[index] = token
      self.selector.item(index).setText(token.company + " : " + token.title)
      self.socket.put("apps", self.applications)
      self.socket.put("save", ())
    elif alias == "apps":
      self.applications = Applications([])
      self.selector.clear()
      for app in token:
        self.applications.append(app)
        self.selector.insertItem(self.selector.count(), app.company + " : " + app.title)
      self.socket.put("apps", self.applications)

class Details(Gadget, QDialog):
  embed = False
  def __init__(self, parent, **kwargs):
    Gadget.__init__(self, **kwargs)
    QDialog.__init__(self, parent)

    self.setWindowTitle("Application Details")
    self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

    self.company = QLineEdit()
    self.title = QLineEdit()
    self.website = QLineEdit()
    self.open_website = QPushButton("Open")
    self.maps = QLineEdit()
    self.open_maps = QPushButton("Open")
    self.advertisement = QTextEdit()
    self.cv = QCheckBox("Curriculum Vitae")
    self.doc = QCheckBox("Documents")
    self.email = QCheckBox("Via Email")
    self.coverletter = QTextEdit()
    self.save = QPushButton("Save")

    self.layout = QGridLayout(self)
    self.layout.addWidget(QLabel("Company: "), 0, 0, 1, 1)
    self.layout.addWidget(self.company, 0, 1, 1, 7)
    self.layout.addWidget(QLabel("Title: "), 1, 0, 1, 1)
    self.layout.addWidget(self.title, 1, 1, 1, 7)
    self.layout.addWidget(QLabel("Website: "), 2, 0, 1, 1)
    self.layout.addWidget(self.website, 2, 1, 1, 6)
    self.layout.addWidget(self.open_website, 2, 7, 1, 1)
    self.layout.addWidget(QLabel("Maps: "), 3, 0, 1, 1)
    self.layout.addWidget(self.maps, 3, 1, 1, 6)
    self.layout.addWidget(self.open_maps, 3, 7, 1, 1)
    self.layout.addWidget(QLabel("Advertisement: "), 4, 0, 1, 8)
    self.layout.addWidget(self.advertisement, 5, 0, 1, 8)
    self.layout.addWidget(self.cv, 6, 0, 1, 1)
    self.layout.addWidget(self.doc, 6, 1, 1, 1)
    self.layout.addWidget(self.email, 6, 2, 1, 1)
    self.layout.addWidget(QLabel("Cover Letter: "), 7, 0, 1, 8)
    self.layout.addWidget(self.coverletter, 8, 0, 1, 8)
    self.layout.addWidget(self.save, 9, 0, 1, 8)

    self.advertisement.setStyleSheet("background-color: #ffffff; color: #000000;")
    self.coverletter.setStyleSheet("background-color: #ffffff; color: #000000;")

    self.open_website.clicked.connect(self.open_website_)
    self.open_maps.clicked.connect(self.open_maps_)
    self.save.clicked.connect(self.save_)

  def open_website_(self, checked):
    webbrowser.open(self.website.text())

  def open_maps_(self, checked):
    webbrowser.open(self.maps.text())

  def save_(self, checked):
    self.socket.put("save", Application(self.id,
                                        self.company.text(),
                                        self.title.text(),
                                        self.website.text(),
                                        self.maps.text(),
                                        self.advertisement.toHtml(),
                                        True if self.cv.checkState() else False,
                                        True if self.doc.checkState() else False,
                                        True if self.email.checkState() else False,
                                        self.coverletter.toHtml()))

  def sizeHint(self):
    return QSize(1280, 1600)
  
  def update(self, alias, token):
    if alias == "app":
      self.id = token.id
      self.company.setText(token.company)
      self.title.setText(token.title)
      self.website.setText(token.website)
      self.maps.setText(token.maps)
      self.advertisement.setHtml(token.advertisement)
      self.cv.setCheckState(Qt.Checked if token.cv else Qt.Unchecked)
      self.doc.setCheckState(Qt.Checked if token.doc else Qt.Unchecked)
      self.email.setCheckState(Qt.Checked if token.email else Qt.Unchecked)
      self.coverletter.setHtml(token.coverletter)
      self.show()
