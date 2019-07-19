import os
import pw_database_url
from peewee import PostgresqlDatabase, Model

config = pw_database_url.config()
database = PostgresqlDatabase(config['name'], host=config['host'], port=config['port'], user=config['user'], password=config['password'])
database.connect()

class BaseModel(Model):
    class Meta:
        database = database
