from localagenda.cities import cities
from localagenda.models.meeting import Meeting
from localagenda.db import database
from playhouse.migrate import *



def add_new_meetings():
    query = (Meeting.select(Meeting.city, Meeting.name)
             .dicts())

    added_cities = {}
    for row in query:
        if row['city'] not in added_cities:
            added_cities[row['city']] = []

        added_cities[row['city']].append(row['name'])

    for city in cities:
        for meeting in city['Meetings']:
            if city['Name'] not in added_cities or meeting['name'] not in added_cities[city['Name']]:
                print("Adding %s meeting %s" %(city['Name'], meeting['name']))
                m = Meeting.create(city=city['Name'], name=meeting['name'])
                m.save()

def migrate():
    migrator = PostgresqlMigrator(database)

#migrate()
add_new_meetings()
