from pymongo import MongoClient
from base import BaseBackend
from config import config


class MongoBackend(BaseBackend):

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])
        self.db = self.client["submitter"]
        self.flagz = self.db['flagz']

    def _close(self):
        self.client.close()

    def getFlags(self):
        # flags = self.flagz.aggregate()
        flags = []
        return flags
