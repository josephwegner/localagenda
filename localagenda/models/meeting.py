from localagenda.db import BaseModel
from peewee import *

class Meeting(BaseModel):
  city = CharField()
  name = CharField()
  latest_agenda_hash = CharField(null=True)
