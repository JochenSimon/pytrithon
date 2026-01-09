__version__ = "1.0.0"

from datetime import datetime
from sqlmodel import Field
from sqlmodel_repository import SQLModelEntity
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Pytrithon import Gadget

TIMESTAMP_FORMAT = "%b %e %Y %H:%M:%S"        

class Record(SQLModelEntity, table=True):
    """Record model"""
    id: int = Field(index=True, default=None, primary_key=True)
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    firstname: str = Field(default_factory=lambda: "<firstname>")
    lastname: str = Field(default_factory=lambda: "<lastname>")
    email: str = Field(default_factory=lambda: "")
    phone: str = Field(default_factory=lambda: "")
    website: str = Field(default_factory=lambda: "")
    street: str = Field(default_factory=lambda: "")
    zipcode: str = Field(default_factory=lambda: "")
    city: str = Field(default_factory=lambda: "")
    country: str = Field(default_factory=lambda: "")

class Selector(Gadget, QWidget):
  def __init__(self, **kwargs):
    Gadget.__init__(self, **kwargs)
    QWidget.__init__(self)

    self.records = []

    self.selector = QListWidget()
    self.new = QPushButton("New")
    self.delete = QPushButton("Delete")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.selector)
    self.layout.addWidget(self.new)
    self.layout.addWidget(self.delete)

    self.selector.itemClicked.connect(self.do_select)
    self.new.clicked.connect(self.do_new)
    self.delete.clicked.connect(self.do_delete)

  def do_select(self, item):
    self.socket.put("select", self.records[self.selector.currentRow()])

  def do_new(self, checked):
    record = Record()
    self.records.append(record)
    self.selector.insertItem(self.selector.count(), record.firstname + " " + record.lastname)
    self.selector.setCurrentRow(self.selector.count()-1)
    self.socket.put("create", record)
    self.socket.put("select", record)

  def do_delete(self, checked):
    self.socket.put("delete", self.records[self.selector.currentRow()])
    del self.records[self.selector.currentRow()]
    self.selector.takeItem(self.selector.currentRow())
    self.socket.put("hide", ())

  def update(self, alias, token):
    match alias:
      case "records":
        self.records = []
        self.selector.clear()
        for record in sorted(token, key=lambda r: (r.lastname.lower(), r.firstname.lower())):
          self.records.append(record)
          self.selector.insertItem(self.selector.count(), record.firstname + " " + record.lastname)
      case "change":  
        self.records[[r.id for r in self.records].index(token.id)] = token
        records = list(self.records)
        self.records = []
        self.selector.clear()
        for record in sorted(records, key=lambda r: (r.lastname.lower(), r.firstname.lower())):
          self.records.append(record)
          self.selector.insertItem(self.selector.count(), record.firstname + " " + record.lastname)
        self.selector.setCurrentRow([r.id for r in self.records].index(token.id))
        self.socket.put("select", token)
      case "move":
        row = self.selector.currentRow()
        match token:
          case "|<":
            row = 0
          case "<":
            row = (row - 1) % self.selector.count()
          case ">":
            row = (row + 1) % self.selector.count()
          case ">|":
            row = self.selector.count() - 1
        self.selector.setCurrentRow(row)
        self.socket.put("select", self.records[row])

class Details(Gadget, QDialog):
  embed = False
  def __init__(self, parent, **kwargs):
    Gadget.__init__(self, **kwargs)
    QDialog.__init__(self, parent)

    parent.sub_windows.append(self)

    self.setWindowTitle("Address Details")
    self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

    self.firstname = QLineEdit()
    self.lastname = QLineEdit()
    self.email = QLineEdit()
    self.phone = QLineEdit()
    self.website = QLineEdit()
    self.street = QLineEdit()
    self.zipcode = QLineEdit()
    self.city = QLineEdit()
    self.country = QLineEdit()
    self.created = QLabel("")
    self.updated = QLabel("")
    self.first = QPushButton("|<")
    self.previous = QPushButton("<")
    self.save = QPushButton("Save")
    self.next = QPushButton(">")
    self.last = QPushButton(">|")

    self.labels = [QLabel(label) for label in ("First names: ", "Last name: ",
                                               "E-Mail: ", "Phone number: ",
                                               "Website: ", "Street address: ",
                                               "Zip code: ", "City: ", "Country: ",
                                               "Created: ", "Updated: ")]

    for label in self.labels:
      label.setAlignment(Qt.AlignRight)

    self.layout = QGridLayout(self)

    self.layout.addWidget(self.labels[0], 0, 0, 1, 1)
    self.layout.addWidget(self.firstname, 0, 1, 1, 3)
    self.layout.addWidget(self.labels[1], 0, 4, 1, 1)
    self.layout.addWidget(self.lastname, 0, 5, 1, 3)
    self.layout.addWidget(self.labels[2], 1, 0, 1, 1)
    self.layout.addWidget(self.email, 1, 1, 1, 3)
    self.layout.addWidget(self.labels[3], 1, 4, 1, 1)
    self.layout.addWidget(self.phone, 1, 5, 1, 3)
    self.layout.addWidget(self.labels[4], 2, 0, 1, 1)
    self.layout.addWidget(self.website, 2, 1, 1, 7)
    self.layout.addWidget(self.labels[5], 3, 0, 1, 1)
    self.layout.addWidget(self.street, 3, 1, 1, 7)
    self.layout.addWidget(self.labels[6], 4, 0, 1, 1)
    self.layout.addWidget(self.zipcode, 4, 1, 1, 1)
    self.layout.addWidget(self.labels[7], 4, 2, 1, 1)
    self.layout.addWidget(self.city, 4, 3, 1, 2)
    self.layout.addWidget(self.labels[8], 4, 5, 1, 1)
    self.layout.addWidget(self.country, 4, 6, 1, 2)

    self.layout.addWidget(self.labels[9], 5, 0, 1, 1)
    self.layout.addWidget(self.created, 5, 1, 1, 3)
    self.layout.addWidget(self.labels[10], 5, 4, 1, 1)
    self.layout.addWidget(self.updated, 5, 5, 1, 3)

    self.layout.addWidget(self.first, 6, 0, 1, 1)
    self.layout.addWidget(self.previous, 6, 1, 1, 1)
    self.layout.addWidget(self.save, 6, 2, 1, 4)
    self.layout.addWidget(self.next, 6, 6, 1, 1)
    self.layout.addWidget(self.last, 6, 7, 1, 1)

    for i in range(8):
      self.layout.setColumnStretch(i, 1)

    self.first.clicked.connect(lambda c,d="|<": self.do_move(c,d))
    self.previous.clicked.connect(lambda c,d="<": self.do_move(c,d))
    self.save.clicked.connect(self.do_save)
    self.next.clicked.connect(lambda c,d=">": self.do_move(c,d))
    self.last.clicked.connect(lambda c,d=">|": self.do_move(c,d))

  def do_move(self, checked, direction):
    self.socket.put("move", direction)

  def do_save(self, checked):
    self.socket.put("save", (self.record, {"firstname": self.firstname.text(),
                                           "lastname": self.lastname.text(),
                                           "email": self.email.text(),
                                           "phone": self.phone.text(),
                                           "website": self.website.text(),
                                           "street": self.street.text(),
                                           "zipcode": self.zipcode.text(),
                                           "city": self.city.text(),
                                           "country": self.country.text()}))

  def sizeHint(self):
    return QSize(800, 0)

  def update(self, alias, token):
    match alias:
      case "record":
        self.record = token
        self.firstname.setText(token.firstname)
        self.lastname.setText(token.lastname)
        self.email.setText(token.email)
        self.phone.setText(token.phone)
        self.website.setText(token.website)
        self.street.setText(token.street)
        self.zipcode.setText(token.zipcode)
        self.city.setText(token.city)
        self.country.setText(token.country)
        self.created.setText(token.created.strftime(TIMESTAMP_FORMAT))
        self.updated.setText(token.updated.strftime(TIMESTAMP_FORMAT))
        self.show()
      case "hide":
        self.hide()
