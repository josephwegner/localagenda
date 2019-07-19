from localagenda.db import BaseModel
from localagenda.models.meeting import Meeting
from peewee import *

class Agenda(BaseModel):
  captured_date = DateField()
  content = CharField()
  content_hash = CharField()
  target = CharField()

  meeting = ForeignKeyField(Meeting, backref='agendas')
