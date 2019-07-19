from localagenda.db import BaseModel
from localagenda.models.meeting import Meeting
from peewee import *

class Subscription(BaseModel):
  email = CharField()
  meeting = ForeignKeyField(Meeting, backref='subscriptions')
