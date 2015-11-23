from pymongo import MongoClient
from base import BaseBackend
from config import config


class MongoBackend(BaseBackend):

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])
        self.db = self.client["flagz"]

    def _close(self):
        self.client.close()

    def getFlags(self):
        flags = self.db.aggregate()
        return flags
