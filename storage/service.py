import logging
from os import path, listdir
from pickle import load
from random import randint

from jsonpickle import dumps, loads


class StorageService:

    def __init__(self, directory):
        self.directory = directory
        self.log = logging.getLogger("StorageService")

    def list(self):
        return [f for f in listdir(self.directory) if path.isfile(path.join(self.directory, f))]

    def generate_name(self):
        name = "%s-%s-%s-%s"
        parts = []
        for i in range(0, 4):
            parts.append("%d%d%d%d" % (randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9)))

        return name % tuple(parts)

    def store(self, o, name=None):
        serialized = dumps(o, unpicklable=False)
        try:
            filename = path.join(self.directory, name + ".json" if name is not None else self.generate_name() + ".json")
            file_handle = open(filename, "w")
            file_handle.write(serialized)
            file_handle.close()
            return filename
        except:
            return None

    def load(self, name):
        filename = path.join(self.directory, name + ".json")
        try:
            file_handle = open(filename, "r")
            deserialized = loads(file_handle.read())
            file_handle.close()
            return deserialized
        except:
            self.log.error("Cannot load [ %s ]" % filename, exc_info=1)
            return None
