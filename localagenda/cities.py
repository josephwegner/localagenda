import re
from os import listdir
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

cities = []
for file in listdir("./localagenda/city_configs/"):
    stream = open("./localagenda/city_configs/%s" %(file), 'r')
    city = load(stream, Loader=Loader)

    name = re.sub(r"[^A-Za-z]", "", city['Name'].lower())
    state = re.sub(r"[^A-Za-z]", "", city['State'].lower())

    city['slug'] = "%s-%s" %(name, state)
    cities.append(city)
