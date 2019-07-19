from localagenda.db import BaseModel
from peewee import *

class CityRequest(BaseModel):
  city = CharField()
  state = CharField()
  email = CharField()
